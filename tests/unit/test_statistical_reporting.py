from pathlib import Path

from proxy_analysis.statistical.reporting import _write_csv


def test_csv_writer_uses_union_of_columns(tmp_path: Path) -> None:
    output = tmp_path / "table.csv"
    _write_csv(output, [{"a": 1}, {"b": 2}])
    rendered = output.read_text(encoding="utf-8-sig")
    assert "a,b" in rendered
    assert "1," in rendered
    assert ",2" in rendered
