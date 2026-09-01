from proxy_analysis.schemas import ReasonCode, packet_event_schema


def test_packet_schema_uses_integer_nanoseconds_and_no_payload() -> None:
    schema = packet_event_schema()
    assert str(schema.field("timestamp_ns").type) == "int64"
    assert schema.metadata[b"timestamp_unit"] == b"ns"
    assert "payload" not in schema.names
    assert "transport_payload_len" in schema.names


def test_reason_codes_are_stable_strings() -> None:
    assert ReasonCode.SHARED_CARRIER.value == "shared_carrier"
    assert ReasonCode.DECODE_FAILED.value == "decode_failed"

