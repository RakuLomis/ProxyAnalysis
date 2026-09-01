from proxy_analysis.quality.reports import _close


def test_quality_numeric_comparison() -> None:
    assert _close(10, 10.0)
    assert not _close(10, 11)
    assert not _close(None, 0)

