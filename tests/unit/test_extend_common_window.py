from proxy_analysis.extend_calibration.common_window import outside_reason


def test_only_independent_complete_lifecycle_can_exclude():
    assert outside_reason([{'type':'tcp_connect','ts_ns':1},{'type':'tcp_close','ts_ns':9}],10,20)=='logical_closed_before_common_start'
    assert outside_reason([{'type':'tcp_connect','ts_ns':21}],10,20)=='logical_connect_after_common_end'
    assert outside_reason([{'type':'tcp_connect','ts_ns':1}],10,20) is None
    assert outside_reason([{'type':'tcp_close','ts_ns':9}],10,20) is None
    assert outside_reason([{'type':'logical_carrier_bind','ts_ns':21}],10,20) is None
    assert outside_reason([{'type':'tcp_connect','ts_ns':1},{'type':'tcp_connect','ts_ns':21}],10,20) is None
