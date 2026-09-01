from pathlib import Path

import pyarrow.parquet as pq

from proxy_analysis.pipeline.batch import FEATURE_RECORD_SCHEMA, _atomic_parquet


def test_feature_record_parquet_preserves_group_keys(tmp_path: Path) -> None:
    path = tmp_path / "features.parquet"
    row = {
        "session_id": "session-1",
        "protocol_dataset": "HYSTERIA2",
        "record_id": "carrier-1",
        "record_level": "hysteria2_carrier_window",
        "capture_side": "pre_post",
        "transport_protocol": "tcp_aggregate->udp_carrier",
        "group_site": "example.com",
        "group_session_id": "session-1",
        "group_carrier_id": "carrier-1",
        "feature_schema_version": 1,
        "feature_config_sha256": "a" * 64,
        "features_json": "{}",
    }
    _atomic_parquet(path, [row])
    table = pq.read_table(path)
    assert table.schema == FEATURE_RECORD_SCHEMA
    assert table["group_carrier_id"].to_pylist() == ["carrier-1"]

