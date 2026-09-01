from proxy_analysis.statistical.sensitivity import _comparison_row


def test_sensitivity_direction_flags_conflict() -> None:
    stable = _comparison_row(
        check="x",
        protocol="VLESS",
        metric_id="m",
        primary_values=[1.0, 2.0],
        sensitivity_values=[3.0, 4.0],
    )
    conflict = _comparison_row(
        check="x",
        protocol="VLESS",
        metric_id="m",
        primary_values=[1.0, 2.0],
        sensitivity_values=[-3.0, -4.0],
    )
    assert stable["direction_stable"] is True
    assert conflict["direction_stable"] is False
