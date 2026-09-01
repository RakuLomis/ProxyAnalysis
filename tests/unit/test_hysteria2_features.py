from proxy_analysis.features.hysteria2 import select_time_envelope
from proxy_analysis.features.models import PacketMeasure


def p(event: str, ts: int, ordinal: int) -> PacketMeasure:
    return PacketMeasure(event, ts, ordinal, 1, 10, 50, 64)


def test_time_envelope_is_inclusive_and_stably_sorted() -> None:
    packets = [p("c", 20, 3), p("a", 10, 1), p("b", 15, 2)]
    selected = select_time_envelope(packets, 10, 15)
    assert [item.packet_event_id for item in selected] == ["a", "b"]

