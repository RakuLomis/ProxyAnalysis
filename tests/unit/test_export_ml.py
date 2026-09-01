import json

import pyarrow as pa
import pyarrow.parquet as pq

from proxy_analysis.pipeline.export_ml import (
    TABLE_FILES,
    _atomic_write_inferred,
    deterministic_split,
    flatten_numeric,
    validate_ml_tables,
)


def test_deterministic_split_keeps_same_group_together() -> None:
    assert deterministic_split("example.com") == deterministic_split("example.com")
    assert deterministic_split("example.com", seed="a") == deterministic_split(
        "example.com", seed="a"
    )


def test_flatten_numeric_excludes_strings_and_histogram_edges() -> None:
    result = flatten_numeric(
        {
            "scalar": {"x": 1.5, "reason": "metadata"},
            "curve": [0, 1, 2],
            "hist": {"edges": [0, 10], "counts": [2]},
            "missing": None,
        }
    )
    assert result["scalar__x"] == 1.5
    assert "scalar__reason" not in result
    assert result["curve__002"] == 2
    assert "hist__edges__000" not in result
    assert result["hist__counts__000"] == 2
    assert "missing" in result and result["missing"] is None


def test_validate_ml_tables_detects_cross_split_group(tmp_path) -> None:
    rows = [
        {
            "group_site": "same.example",
            "group_session_id": "s1",
            "group_carrier_id": None,
            "split_by_site": "train",
            "split_by_session": "train",
            "split_by_carrier": "train",
            "numeric_feature": 1.0,
        },
        {
            "group_site": "same.example",
            "group_session_id": "s2",
            "group_carrier_id": None,
            "split_by_site": "test",
            "split_by_session": "test",
            "split_by_carrier": "test",
            "numeric_feature": 2.0,
        },
    ]
    table = pa.Table.from_pylist(rows)
    for filename in TABLE_FILES.values():
        pq.write_table(table, tmp_path / filename)
    report = validate_ml_tables(tmp_path)
    assert report["state"] == "failed"
    assert report["tables"]["entity"]["cross_split_group_counts"]["site"] == 1


def test_atomic_wide_write_preserves_union_of_heterogeneous_row_keys(tmp_path) -> None:
    path = tmp_path / "wide.parquet"
    _atomic_write_inferred(path, [{"udp_only": 1}, {"tcp_only": 2}])
    table = pq.read_table(path)
    assert table.column_names == ["tcp_only", "udp_only"]
    assert table["udp_only"].to_pylist() == [1, None]
    assert table["tcp_only"].to_pylist() == [None, 2]
