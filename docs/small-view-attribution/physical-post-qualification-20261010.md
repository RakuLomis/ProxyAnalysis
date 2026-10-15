# 物理post输入资格审计

当前模型是post-only，但输入连接集与窗口仍依赖离线整理，物理输入资格未通过。

```json
{
  "PCAP_reads": 0,
  "cache_only_inference_scope": "offline-associated visit input, model post-only",
  "complete_physical_connection_reconstruction_verified": false,
  "end_rules": [
    "browser_quiescent before health check and either capture shutdown"
  ],
  "existing_windows": 600,
  "future_requirements": [
    "attacker-independent external window",
    "all physical connections including unpaired/background",
    "single-side direction and dedup state",
    "fixed truncation/concurrency policy",
    "separate finite-PCAP budget if needed"
  ],
  "independent_external_window_verified": false,
  "inventory_complete": true,
  "known_endpoint_filter_allowed_as_metadata": true,
  "new_fits": 0,
  "physical_input_qualified": false,
  "schemas": [
    {
      "columns": [
        "P_down",
        "P_up",
        "R_down",
        "R_up",
        "W_down",
        "W_up",
        "session_id",
        "side"
      ],
      "path": "outputs/extend-calibration-20260930/run-01/extraction-03/full-W-features.parquet",
      "rows": 1200
    },
    {
      "columns": [
        "E_down",
        "E_up",
        "F",
        "R_down",
        "R_up",
        "U_down",
        "U_up",
        "session_id",
        "side"
      ],
      "path": "outputs/extend-calibration-20260930/run-01/extraction-03/full-T-features.parquet",
      "rows": 1200
    }
  ],
  "start_rules": [
    "max capture header readiness"
  ]
}
```

继续需要攻击者独立窗口、全部物理连接（含背景和未配对）、单侧方向与去重状态、固定截断和并发规则。若需要读取PCAP，先限定文件与读盘预算由用户确认。本轮仅盘点缓存及窗口来源，没有构造新的测试输入。
