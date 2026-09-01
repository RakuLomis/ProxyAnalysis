"""Read-only inventory of TrafficTracer sessions and their artifacts."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import json
import os
from pathlib import Path
from typing import Any, Iterable

from .pathutils import filesystem_path


REQUIRED_RELATIVE_PATHS = (
    "manifest.json",
    "raw/tun.pcap",
    "raw/phys.pcap",
    "raw/netlog.json",
    "raw/cdp.json",
    "raw/mihomo-trace.jsonl",
    "raw/capture-context.json",
    "analysis/summary.json",
    "analysis/connection-index-v2.json",
    "analysis/request-index-v2.json",
    "analysis/flow-index.json",
    "analysis/pcap-index-v1.json",
)


@dataclass(frozen=True, slots=True)
class ArtifactIssue:
    code: str
    severity: str
    relative_path: str
    detail: str


@dataclass(frozen=True, slots=True)
class SessionInventory:
    protocol_dataset: str
    session_id: str
    session_path: str
    target_domain: str
    target_url: str
    state: str
    traffictracer_version: str | None
    traffictracer_commit: str | None
    artifact_count: int
    issues: tuple[ArtifactIssue, ...]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class InventoryError(RuntimeError):
    """Raised for a dataset-wide inventory contract violation."""


class InventoryScanner:
    """Discover sessions through manifests and validate declared artifacts."""

    def __init__(self, dataset_root: Path | str) -> None:
        self.dataset_root = Path(dataset_root)

    def scan(self) -> list[SessionInventory]:
        datasets_root = self.dataset_root / "datasets"
        if not datasets_root.is_dir():
            raise InventoryError(f"missing datasets directory: {datasets_root}")

        sessions: list[SessionInventory] = []
        seen_ids: set[str] = set()
        for manifest_path in sorted(datasets_root.glob("*/*/*/manifest.json")):
            protocol = manifest_path.relative_to(datasets_root).parts[0]
            session = self._read_session(protocol, manifest_path)
            if session.session_id in seen_ids:
                raise InventoryError(f"duplicate session_id: {session.session_id}")
            seen_ids.add(session.session_id)
            sessions.append(session)
        if not sessions:
            raise InventoryError(f"no manifests found under {datasets_root}")
        return sessions

    def _read_session(self, protocol: str, manifest_path: Path) -> SessionInventory:
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise InventoryError(f"cannot read {manifest_path}: {exc}") from exc

        session_dir = manifest_path.parent
        issues = list(_validate_required_files(session_dir))
        issues.extend(_validate_declared_artifacts(session_dir, manifest.get("artifacts", [])))
        component = manifest.get("component_versions", {}).get("traffictracer", {})
        target = manifest.get("target", {})
        return SessionInventory(
            protocol_dataset=protocol,
            session_id=str(manifest.get("session_id", "")),
            session_path=str(session_dir.resolve()),
            target_domain=str(target.get("domain", "")),
            target_url=str(target.get("url", "")),
            state=str(manifest.get("state", "")),
            traffictracer_version=_optional_string(component.get("version")),
            traffictracer_commit=_optional_string(component.get("commit")),
            artifact_count=len(manifest.get("artifacts", [])),
            issues=tuple(issues),
        )


def _optional_string(value: Any) -> str | None:
    return None if value is None else str(value)


def _validate_required_files(session_dir: Path) -> Iterable[ArtifactIssue]:
    for relative in REQUIRED_RELATIVE_PATHS:
        path = session_dir / relative
        if not _is_file(path):
            yield ArtifactIssue("missing_required_file", "error", relative, "file does not exist")


def _validate_declared_artifacts(
    session_dir: Path, artifacts: Any
) -> Iterable[ArtifactIssue]:
    if not isinstance(artifacts, list):
        yield ArtifactIssue(
            "invalid_manifest_artifacts", "error", "manifest.json", "artifacts is not a list"
        )
        return
    for artifact in artifacts:
        if not isinstance(artifact, dict):
            yield ArtifactIssue(
                "invalid_artifact", "error", "manifest.json", "artifact is not an object"
            )
            continue
        relative = artifact.get("path")
        if not isinstance(relative, str):
            yield ArtifactIssue(
                "invalid_artifact_path", "error", "manifest.json", "path is missing"
            )
            continue
        path = session_dir / Path(relative)
        if not _is_file(path):
            yield ArtifactIssue(
                "missing_declared_artifact", "error", relative, "file does not exist"
            )
            continue
        declared_size = artifact.get("size_bytes")
        actual_size = _file_size(path)
        if isinstance(declared_size, int) and actual_size != declared_size:
            is_late_trace_growth = (
                relative == "raw/mihomo-trace.jsonl" and actual_size > declared_size
            )
            yield ArtifactIssue(
                "artifact_grew_after_manifest" if is_late_trace_growth else "artifact_size_mismatch",
                "warning" if is_late_trace_growth else "error",
                relative,
                f"declared={declared_size}, actual={actual_size}",
            )


def _is_file(path: Path) -> bool:
    return os.path.isfile(filesystem_path(path))


def _file_size(path: Path) -> int:
    return os.path.getsize(filesystem_path(path))


def inventory_summary(sessions: Iterable[SessionInventory]) -> dict[str, Any]:
    items = list(sessions)
    protocols: dict[str, int] = {}
    issue_counts: dict[str, int] = {}
    severity_counts: dict[str, int] = {}
    for session in items:
        protocols[session.protocol_dataset] = protocols.get(session.protocol_dataset, 0) + 1
        for issue in session.issues:
            issue_counts[issue.code] = issue_counts.get(issue.code, 0) + 1
            severity_counts[issue.severity] = severity_counts.get(issue.severity, 0) + 1
    return {
        "session_count": len(items),
        "protocol_session_counts": dict(sorted(protocols.items())),
        "sessions_with_issues": sum(bool(item.issues) for item in items),
        "sessions_with_errors": sum(
            any(issue.severity == "error" for issue in item.issues) for item in items
        ),
        "issue_counts": dict(sorted(issue_counts.items())),
        "severity_counts": dict(sorted(severity_counts.items())),
    }
