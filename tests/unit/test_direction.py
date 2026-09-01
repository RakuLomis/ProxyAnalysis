from proxy_analysis.sequences.direction import Endpoint, SequenceEvent, enrich_sequence


def _event(event_id: str, ts: int, ordinal: int, src: str, sport: int, dst: str, dport: int):
    return SequenceEvent(event_id, ts, ordinal, src, dst, sport, dport)


def test_direction_stable_order_relative_time_and_iat() -> None:
    initiator = Endpoint("192.0.2.1", 50000)
    responder = Endpoint("198.51.100.1", 443)
    events = [
        _event("b", 20, 2, responder.ip, 443, initiator.ip, 50000),
        _event("a", 10, 1, initiator.ip, 50000, responder.ip, 443),
        _event("c", 20, 3, initiator.ip, 50000, responder.ip, 443),
    ]
    result = enrich_sequence(events, initiator, responder)
    assert [item.packet_event_id for item in result] == ["a", "b", "c"]
    assert [item.direction for item in result] == [1, -1, 1]
    assert [item.relative_time_ns for item in result] == [0, 10, 10]
    assert [item.packet_iat_ns for item in result] == [None, 10, 0]


def test_endpoint_can_match_varying_remote_carrier_port() -> None:
    initiator = Endpoint("192.0.2.1", 50000)
    responder = Endpoint("198.51.100.1", None)
    event = _event("a", 1, 1, initiator.ip, 50000, responder.ip, 37123)
    assert enrich_sequence([event], initiator, responder)[0].direction == 1


def test_fragment_without_ports_uses_indexed_endpoint_ips() -> None:
    initiator = Endpoint("192.0.2.1", 50000)
    responder = Endpoint("198.51.100.1", 443)
    event = SequenceEvent("fragment", 1, 1, initiator.ip, responder.ip, None, None)
    assert enrich_sequence([event], initiator, responder)[0].direction == 1
