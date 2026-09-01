"""Checkpointed session and dataset feature extraction."""

from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import platform
import subprocess
import time
from typing import Any, Callable, Iterable

import pyarrow as pa
import pyarrow.parquet as pq

from .. import __version__
from ..config import FeatureConfig
from ..features.core import extract_core_entity_features
from ..features.hysteria2 import extract_hysteria2_window_features
from ..features.pairwise import extract_pairwise_features
from ..features.web import extract_web_features
from ..indexing.hysteria2 import build_hysteria2_carrier_windows
from ..indexing.identities import EntityDescriptor, build_entity_descriptors
from ..indexing.pairs import build_exclusive_pairs
from ..inventory import InventoryScanner, SessionInventory
from .analyze_entity import EntityAnalysis, analyze_entity_capture
from ..pathutils import filesystem_path


FEATURE_RECORD_SCHEMA = pa.schema(
    [
        pa.field("session_id", pa.string(), nullable=False),
        pa.field("protocol_dataset", pa.string(), nullable=False),
        pa.field("record_id", pa.string(), nullable=False),
        pa.field("record_level", pa.string(), nullable=False),
        pa.field("capture_side", pa.string()),
        pa.field("transport_protocol", pa.string()),
        pa.field("group_site", pa.string()),
        pa.field("group_session_id", pa.string(), nullable=False),
        pa.field("group_carrier_id", pa.string()),
        pa.field("feature_schema_version", pa.int32(), nullable=False),
        pa.field("feature_config_sha256", pa.string(), nullable=False),
        pa.field("features_json", pa.large_string(), nullable=False),
    ]
)

# Increment whenever code changes alter persisted record semantics independently of config.
PIPELINE_IMPLEMENTATION_VERSION = 2


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _descriptor_key(descriptor: EntityDescriptor) -> tuple[str, str, str, str]:
    return (
        descriptor.capture_side,
        descriptor.entity_level,
        descriptor.entity_id,
        str(descriptor.capture_path),
    )


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _atomic_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def _atomic_parquet(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    table = pa.Table.from_pylist(rows, schema=FEATURE_RECORD_SCHEMA)
    pq.write_table(table, temporary, compression="zstd")
    os.replace(temporary, path)


def _git_commit(workspace: Path) -> str | None:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=workspace,
            check=True,
            capture_output=True,
            text=True,
            timeout=5,
        )
        return result.stdout.strip() or None
    except (OSError, subprocess.SubprocessError):
        return None


def _record(
    features: dict[str, Any],
    *,
    record_id: str,
    record_level: str,
    site: str,
    config: FeatureConfig,
    capture_side: str | None = None,
    transport: str | None = None,
    carrier_id: str | None = None,
) -> dict[str, Any]:
    session_id = str(features["session_id"])
    return {
        "session_id": session_id,
        "protocol_dataset": str(features["protocol_dataset"]),
        "record_id": record_id,
        "record_level": record_level,
        "capture_side": capture_side,
        "transport_protocol": transport,
        "group_site": site,
        "group_session_id": session_id,
        # TrafficTracer carrier identifiers are session-local, so namespace them.
        "group_carrier_id": f"{session_id}::{carrier_id}" if carrier_id else None,
        "feature_schema_version": config.schema_version,
        "feature_config_sha256": config.sha256,
        "features_json": _canonical_json(features),
    }


def process_session(
    session: SessionInventory,
    output_root: Path | str,
    config: FeatureConfig,
    *,
    workspace: Path | str = Path.cwd(),
    force: bool = False,
) -> dict[str, Any]:
    destination = Path(output_root) / session.protocol_dataset / session.session_id
    status_path = destination / "status.json"
    if status_path.is_file() and not force:
        existing = json.loads(status_path.read_text(encoding="utf-8"))
        if (
            existing.get("state") == "complete"
            and existing.get("feature_config_sha256") == config.sha256
            and existing.get("pipeline_implementation_version")
            == PIPELINE_IMPLEMENTATION_VERSION
        ):
            return {**existing, "skipped": True}

    started = time.perf_counter()
    running = {
        "state": "running",
        "session_id": session.session_id,
        "protocol_dataset": session.protocol_dataset,
        "feature_config_sha256": config.sha256,
        "pipeline_implementation_version": PIPELINE_IMPLEMENTATION_VERSION,
        "started_at": _utc_now(),
    }
    _atomic_json(status_path, running)
    try:
        descriptors = build_entity_descriptors(session.session_path, session.protocol_dataset)
        cache: dict[tuple[str, str, str, str], EntityAnalysis] = {}

        def load(descriptor: EntityDescriptor) -> EntityAnalysis:
            key = _descriptor_key(descriptor)
            if key not in cache:
                cache[key] = analyze_entity_capture(descriptor)
            return cache[key]

        entity_rows = []
        for descriptor in descriptors:
            features = extract_core_entity_features(load(descriptor), config)
            entity_rows.append(
                _record(
                    features,
                    record_id=descriptor.entity_id,
                    record_level=descriptor.entity_level,
                    site=session.target_domain,
                    config=config,
                    capture_side=descriptor.capture_side,
                    transport=descriptor.transport_protocol,
                    carrier_id=descriptor.entity_id if descriptor.entity_level == "carrier" else None,
                )
            )

        pair_rows = []
        for pair in build_exclusive_pairs(session.session_path, session.protocol_dataset):
            features = extract_pairwise_features(load(pair.pre), load(pair.post), config)
            pair_rows.append(
                _record(
                    features,
                    record_id=pair.connection_id,
                    record_level="exclusive_pair",
                    site=session.target_domain,
                    config=config,
                    transport=f"{pair.pre.transport_protocol}->{pair.post.transport_protocol}",
                )
            )

        hy2_rows = []
        for window in build_hysteria2_carrier_windows(session.session_path):
            features = extract_hysteria2_window_features(window, config, analysis_loader=load)
            hy2_rows.append(
                _record(
                    features,
                    record_id=window.carrier_id,
                    record_level="hysteria2_carrier_window",
                    site=session.target_domain,
                    config=config,
                    capture_side="pre_post",
                    transport="tcp_aggregate->udp_carrier",
                    carrier_id=window.carrier_id,
                )
            )

        web = extract_web_features(session.session_path, session.protocol_dataset)
        web["feature_schema_version"] = config.schema_version
        web["feature_config_sha256"] = config.sha256
        web_rows = [
            _record(
                web,
                record_id=session.session_id,
                record_level="web_session",
                site=session.target_domain,
                config=config,
            )
        ]

        _atomic_parquet(destination / "entity-features.parquet", entity_rows)
        _atomic_parquet(destination / "exclusive-pair-features.parquet", pair_rows)
        _atomic_parquet(destination / "hysteria2-window-features.parquet", hy2_rows)
        _atomic_parquet(destination / "web-features.parquet", web_rows)

        sources = []
        for descriptor in descriptors:
            source = descriptor.capture_path
            sources.append(
                {
                    "artifact_id": descriptor.artifact_id,
                    "path": str(source),
                    "size_bytes": os.path.getsize(filesystem_path(source)),
                    "integrity": "size_and_manifest_identity",
                }
            )
        lineage = {
            "session_id": session.session_id,
            "protocol_dataset": session.protocol_dataset,
            "feature_schema_version": config.schema_version,
            "feature_config_sha256": config.sha256,
            "proxy_analysis_version": __version__,
            "pipeline_implementation_version": PIPELINE_IMPLEMENTATION_VERSION,
            "git_commit": _git_commit(Path(workspace)),
            "python_version": platform.python_version(),
            "generated_at": _utc_now(),
            "sources": sorted(
                {item["path"]: item for item in sources}.values(), key=lambda item: item["path"]
            ),
        }
        _atomic_json(destination / "lineage.json", lineage)
        completed = {
            **running,
            "state": "complete",
            "completed_at": _utc_now(),
            "elapsed_seconds": time.perf_counter() - started,
            "entity_record_count": len(entity_rows),
            "exclusive_pair_record_count": len(pair_rows),
            "hysteria2_window_record_count": len(hy2_rows),
            "web_record_count": 1,
            "analysis_cache_count": len(cache),
            "skipped": False,
        }
        _atomic_json(status_path, completed)
        return completed
    except Exception as exc:
        failed = {
            **running,
            "state": "failed",
            "failed_at": _utc_now(),
            "elapsed_seconds": time.perf_counter() - started,
            "error_type": type(exc).__name__,
            "error": str(exc),
        }
        _atomic_json(status_path, failed)
        raise


def process_dataset(
    dataset_root: Path | str,
    output_root: Path | str,
    config: FeatureConfig,
    *,
    protocols: Iterable[str] | None = None,
    session_ids: Iterable[str] | None = None,
    limit: int | None = None,
    force: bool = False,
    progress: Callable[[int, int, SessionInventory, dict[str, Any]], None] | None = None,
) -> list[dict[str, Any]]:
    selected_protocols = set(protocols or ())
    selected_session_ids = set(session_ids or ())
    sessions = InventoryScanner(dataset_root).scan()
    if selected_protocols:
        sessions = [item for item in sessions if item.protocol_dataset in selected_protocols]
    if selected_session_ids:
        sessions = [item for item in sessions if item.session_id in selected_session_ids]
    if limit is not None:
        sessions = sessions[:limit]
    results = []
    total = len(sessions)
    for index, session in enumerate(sessions, start=1):
        result = process_session(session, output_root, config, force=force)
        results.append(result)
        if progress:
            progress(index, total, session, result)
    return results
