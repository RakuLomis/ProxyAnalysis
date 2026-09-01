"""Flatten numeric features and attach deterministic leakage-safe split labels."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any, Iterable

import pyarrow as pa
import pyarrow.parquet as pq


BASE_COLUMNS = (
    "session_id",
    "protocol_dataset",
    "record_id",
    "record_level",
    "capture_side",
    "transport_protocol",
    "group_site",
    "group_session_id",
    "group_carrier_id",
    "feature_schema_version",
    "feature_config_sha256",
)

SPLIT_COLUMNS = ("split_by_site", "split_by_session", "split_by_carrier")

TABLE_FILES = {
    "entity": "entity-wide.parquet",
    "exclusive_pair": "exclusive_pair-wide.parquet",
    "hysteria2_window": "hysteria2_window-wide.parquet",
    "web_session": "web_session-wide.parquet",
}


def deterministic_split(
    group_value: str,
    *,
    seed: str = "proxy-analysis-v1",
    train_fraction: float = 0.7,
    validation_fraction: float = 0.15,
) -> str:
    if not 0 < train_fraction < 1:
        raise ValueError("train_fraction must be between 0 and 1")
    if not 0 <= validation_fraction < 1 or train_fraction + validation_fraction >= 1:
        raise ValueError("invalid validation_fraction")
    digest = hashlib.sha256(f"{seed}\0{group_value}".encode("utf-8")).digest()
    value = int.from_bytes(digest[:8], "big") / (1 << 64)
    if value < train_fraction:
        return "train"
    if value < train_fraction + validation_fraction:
        return "validation"
    return "test"


def flatten_numeric(
    value: Any, *, prefix: str = "", output: dict[str, int | float | bool | None] | None = None
) -> dict[str, int | float | bool | None]:
    result = output if output is not None else {}
    if value is None or isinstance(value, (bool, int, float)):
        if prefix:
            result[prefix] = value
    elif isinstance(value, dict):
        for key, child in value.items():
            # Histogram edges are frozen configuration, not sample features.
            if key in {"edges", "logical_connection_ids"}:
                continue
            child_prefix = f"{prefix}__{key}" if prefix else str(key)
            flatten_numeric(child, prefix=child_prefix, output=result)
    elif isinstance(value, (list, tuple)):
        if all(item is None or isinstance(item, (bool, int, float)) for item in value):
            for index, child in enumerate(value):
                flatten_numeric(child, prefix=f"{prefix}__{index:03d}", output=result)
    return result


def _source_files(feature_root: Path, filename: str) -> list[Path]:
    return sorted(feature_root.glob(f"*/*/{filename}"))


def _read_rows(paths: Iterable[Path]) -> Iterable[dict[str, Any]]:
    for path in paths:
        for row in pq.read_table(path).to_pylist():
            yield row


def _atomic_write_inferred(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    if not rows:
        table = pa.table({})
    else:
        # ``Table.from_pylist`` uses the first row to choose field names and silently
        # drops keys that occur only in later heterogeneous records (for example TCP
        # FR fields after a UDP carrier row). Build the complete column union first.
        all_columns = set().union(*(row.keys() for row in rows))
        ordered = [name for name in BASE_COLUMNS if name in all_columns]
        ordered.extend(sorted(all_columns - set(ordered) - set(SPLIT_COLUMNS)))
        ordered.extend(name for name in SPLIT_COLUMNS if name in all_columns)
        table = pa.table({name: [row.get(name) for row in rows] for name in ordered})
    pq.write_table(table, temporary, compression="zstd")
    os.replace(temporary, path)


def validate_ml_tables(output_root: Path | str) -> dict[str, Any]:
    """Validate output types and prove that grouping keys do not cross splits."""
    root = Path(output_root)
    report: dict[str, Any] = {"state": "passed", "tables": {}, "errors": []}
    allowed_metadata = set(BASE_COLUMNS) | set(SPLIT_COLUMNS)
    dimensions = {
        "site": ("group_site", "split_by_site"),
        "session": ("group_session_id", "split_by_session"),
        "carrier": ("group_carrier_id", "split_by_carrier"),
    }
    for table_name, filename in TABLE_FILES.items():
        path = root / filename
        if not path.is_file():
            report["errors"].append(f"missing table: {filename}")
            continue
        table = pq.read_table(path)
        table_report: dict[str, Any] = {
            "row_count": table.num_rows,
            "feature_column_count": 0,
            "split_counts": {},
            "group_counts": {},
            "cross_split_group_counts": {},
        }
        invalid_feature_types = []
        for field in table.schema:
            if field.name in allowed_metadata:
                continue
            table_report["feature_column_count"] += 1
            if not (
                pa.types.is_boolean(field.type)
                or pa.types.is_integer(field.type)
                or pa.types.is_floating(field.type)
                or pa.types.is_null(field.type)
            ):
                invalid_feature_types.append(f"{field.name}:{field.type}")
        if invalid_feature_types:
            report["errors"].append(
                f"{table_name}: non-numeric feature columns: "
                + ", ".join(invalid_feature_types)
            )

        rows = table.select(
            ["group_site", "group_session_id", "group_carrier_id", *SPLIT_COLUMNS]
        ).to_pylist()
        for dimension, (group_column, split_column) in dimensions.items():
            split_counts: dict[str, int] = {}
            groups: dict[str, set[str]] = {}
            for row in rows:
                split = str(row[split_column])
                split_counts[split] = split_counts.get(split, 0) + 1
                group = row[group_column]
                if group is None:
                    group = row["group_session_id"]
                groups.setdefault(str(group), set()).add(split)
            crossing = sum(len(splits) > 1 for splits in groups.values())
            table_report["split_counts"][dimension] = split_counts
            table_report["group_counts"][dimension] = len(groups)
            table_report["cross_split_group_counts"][dimension] = crossing
            if crossing:
                report["errors"].append(
                    f"{table_name}: {crossing} {dimension} groups cross splits"
                )
        report["tables"][table_name] = table_report
    report["error_count"] = len(report["errors"])
    report["state"] = "passed" if not report["errors"] else "failed"
    return report


def export_ml_tables(
    feature_root: Path | str,
    output_root: Path | str,
    *,
    seed: str = "proxy-analysis-v1",
) -> dict[str, int]:
    source_root = Path(feature_root)
    destination = Path(output_root)
    mappings = {
        "entity": "entity-features.parquet",
        "exclusive_pair": "exclusive-pair-features.parquet",
        "hysteria2_window": "hysteria2-window-features.parquet",
        "web_session": "web-features.parquet",
    }
    counts: dict[str, int] = {}
    for name, filename in mappings.items():
        wide_rows = []
        for row in _read_rows(_source_files(source_root, filename)):
            features = json.loads(row["features_json"])
            wide = {key: row.get(key) for key in BASE_COLUMNS}
            wide.update(flatten_numeric(features))
            site_group = str(row.get("group_site") or row["group_session_id"])
            session_group = str(row["group_session_id"])
            carrier_group = str(row.get("group_carrier_id") or session_group)
            wide["split_by_site"] = deterministic_split(site_group, seed=seed + ":site")
            wide["split_by_session"] = deterministic_split(
                session_group, seed=seed + ":session"
            )
            wide["split_by_carrier"] = deterministic_split(
                carrier_group, seed=seed + ":carrier"
            )
            wide_rows.append(wide)
        _atomic_write_inferred(destination / f"{name}-wide.parquet", wide_rows)
        counts[name] = len(wide_rows)
    validation = validate_ml_tables(destination)
    manifest = {
        "seed": seed,
        "train_fraction": 0.7,
        "validation_fraction": 0.15,
        "test_fraction": 0.15,
        "tables": counts,
        "metadata_columns_excluded": True,
        "full_url_excluded": True,
        "validation": validation,
    }
    temporary = destination / "ml-export-manifest.json.tmp"
    destination.mkdir(parents=True, exist_ok=True)
    temporary.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    os.replace(temporary, destination / "ml-export-manifest.json")
    if validation["state"] != "passed":
        raise ValueError(
            f"ML export validation failed with {validation['error_count']} error(s)"
        )
    return counts
