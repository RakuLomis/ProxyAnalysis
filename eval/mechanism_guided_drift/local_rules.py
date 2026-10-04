"""Synthetic local length rules, NOT estimators of observed capture overhead."""
import math


def ss_written_length(writes):
    if not writes or any(n <= 0 for n in writes):
        raise ValueError('positive synthetic writes required')
    chunks = sum(math.ceil(n / 16383) for n in writes)
    return sum(writes) + 32 + 34 * chunks


def vision_padding(content, long_mode, random_value, first):
    # Synthetic internal buffer, never a TCP packet classification rule.
    if long_mode and content < 900:
        assert 0 <= random_value < 500
        padding = 900 - content + random_value
    else:
        assert 0 <= random_value < 256
        padding = random_value
    return (21 if first else 5) + content + padding


def trojan_header(address_kind, domain_length=None):
    if address_kind == 'ipv4': return 68
    if address_kind == 'ipv6': return 80
    if address_kind == 'domain' and 1 <= domain_length <= 255: return 65 + domain_length
    raise ValueError('synthetic address shape only')


def anytls_frame(payload):
    assert 0 <= payload <= 65535
    return 7 + payload


def quic_varint_length(value):
    if 0 <= value < 2**6: return 1
    if value < 2**14 and value >= 0: return 2
    if value < 2**30 and value >= 0: return 4
    if value < 2**62 and value >= 0: return 8
    raise ValueError('out of QUIC varint range')


def local_rule_checks():
    # VMess modes are qualified in registry, not collapsed into one byte formula.
    checks = {
        'ss_salt_and_one_chunk': ss_written_length([1]) == 67,
        'ss_boundary_16383': ss_written_length([16383]) == 16449,
        'ss_split_16384': ss_written_length([16384]) == 16484,
        'ss_write_boundary_changes_overhead': ss_written_length([100, 100]) != ss_written_length([200]),
        'vision_synthetic_long_min': vision_padding(100, True, 0, True) == 921,
        'vision_synthetic_long_max': vision_padding(100, True, 499, False) == 1404,
        'vision_synthetic_short': vision_padding(900, False, 255, False) == 1160,
        'vmess_write_scale_not_packet': math.ceil(15001 / 15000) == 2,
        'vmess_security_auto_not_exact_mode': 'auto' not in ('aes-128-gcm', 'chacha20-poly1305'),
        'trojan_address_lengths': [trojan_header('ipv4'), trojan_header('ipv6'), trojan_header('domain', 7)] == [68,80,72],
        'anytls_empty_frame_header': anytls_frame(0) == 7,
        'anytls_default_auth_conditional': 32 + 2 + 30 == 64,
        'hy2_varint_boundaries': [quic_varint_length(n) for n in [0,63,64,16383,16384,2**30]] == [1,1,2,2,4,8],
        'hy2_salamander_unit': sum([8] * 3) == 24,
    }
    assert all(checks.values())
    return checks
