"""Canonical reasons for a missing or inapplicable value."""

from enum import StrEnum


class ReasonCode(StrEnum):
    NOT_APPLICABLE_TRANSPORT = "not_applicable_transport"
    SHARED_CARRIER = "shared_carrier"
    MISSING_POST = "missing_post"
    EMPTY_SEQUENCE = "empty_sequence"
    INSUFFICIENT_PACKETS = "insufficient_packets"
    DIRECTION_UNKNOWN = "direction_unknown"
    INCOMPLETE_HANDSHAKE = "incomplete_handshake"
    DECODE_FAILED = "decode_failed"
    IP_FRAGMENT_INCOMPLETE = "ip_fragment_incomplete"
    AMBIGUOUS_ATTRIBUTION = "ambiguous_attribution"
    NOT_PROXY_EGRESS = "not_proxy_egress"
    UNSUPPORTED_LINK_TYPE = "unsupported_link_type"
    UNSUPPORTED_IP_PROTOCOL = "unsupported_ip_protocol"

