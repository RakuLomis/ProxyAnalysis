"""Typed allowlist for historical protocol evidence. No free text is exported."""
import math
import re

BOOL_FIELDS = {'tls', 'reality', 'vision', 'smux_enabled', 'plugin_mux', 'plugin_tls',
    'udp', 'udp_over_tcp', 'tcp_fast_open', 'multipath_tcp', 'dialer_proxy_enabled',
    'secondary_shadowsocks', 'authenticated_length', 'global_padding', 'port_hopping',
    'disable_reuse'}
NUMBER_FIELDS = {'udp_over_tcp_version', 'hop_interval_seconds', 'udp_mtu',
    'idle_session_check_interval_seconds', 'idle_session_timeout_seconds',
    'minimum_idle_sessions', 'alter_id', 'up_mbps', 'down_mbps', 'initial_stream_window',
    'maximum_stream_window', 'initial_connection_window', 'maximum_connection_window'}
CIPHERS = {'auto', 'none', 'zero', 'aes-128-cfb', 'aes-128-gcm', 'aes-192-gcm', 'aes-256-gcm',
    'chacha20-ietf-poly1305', 'chacha20-poly1305', 'xchacha20-ietf-poly1305',
    '2022-blake3-aes-128-gcm', '2022-blake3-aes-256-gcm', '2022-blake3-chacha20-poly1305'}
ENUM_FIELDS = {
    'cipher': CIPHERS, 'secondary_cipher': CIPHERS,
    'transport': {'tcp', 'tls', 'udp', 'quic', 'ws', 'grpc', 'http', 'h2'},
    'plugin': {'none', 'obfs', 'v2ray-plugin', 'gost-plugin', 'shadow-tls', 'restls'},
    'plugin_mode': {'tls', 'http', 'websocket', 'none'},
    'smux_protocol': {'smux', 'yamux', 'h2mux', 'none'},
    'flow': {'none', 'xtls-rprx-vision', 'xtls-rprx-vision-udp443'},
    'packet_encoding': {'none', 'xudp', 'packetaddr'},
    'obfs': {'none', 'salamander'}, 'ip_version': {'dual', 'ipv4', 'ipv6', 'ipv4-prefer', 'ipv6-prefer'},
    'congestion': {'bbr', 'brutal', 'reno', 'cubic'},
}
LIST_FIELDS = {'alpn': {'h2', 'http/1.1', 'h3'}}
DIGEST_FIELDS = {'padding_scheme_sha256'}
FIELDS = BOOL_FIELDS | NUMBER_FIELDS | set(ENUM_FIELDS) | set(LIST_FIELDS) | DIGEST_FIELDS
STATES = {'known', 'unknown', 'not_applicable'}
STATUS = {'known': 'confirmed', 'unknown': 'insufficient', 'not_applicable': 'not_applicable'}
PROTOCOLS = {'shadowsocks', 'vless', 'vmess', 'trojan', 'anytls', 'hysteria2'}


def normalize_protocol(value):
    # The captured core uses ss, whereas the experiment ledger uses shadowsocks.
    if value == 'ss':
        return 'shadowsocks'
    return value if value in PROTOCOLS else None


def valid_value(field, value):
    if field in BOOL_FIELDS:
        return type(value) is bool
    if field in NUMBER_FIELDS:
        return type(value) in {int, float} and math.isfinite(value) and 0 <= value <= 2**53
    if field in ENUM_FIELDS:
        return type(value) is str and value in ENUM_FIELDS[field]
    if field in LIST_FIELDS:
        return type(value) is list and len(value) <= 10 and all(type(v) is str and v in LIST_FIELDS[field] for v in value)
    if field in DIGEST_FIELDS:
        return type(value) is str and re.fullmatch(r'[0-9a-f]{64}', value) is not None
    return False


def extract_layer(layer):
    """Return selected values and rejection counts; never copy reasons/extra members."""
    out, rejected = {}, {'non_allowlisted_fields': 0, 'invalid_typed_values': 0}
    if not isinstance(layer, dict):
        return out, {'non_allowlisted_fields': 0, 'invalid_typed_values': 1}
    for field, node in layer.items():
        if field not in FIELDS:
            rejected['non_allowlisted_fields'] += 1
            continue
        if not isinstance(node, dict) or node.get('state') not in STATES:
            rejected['invalid_typed_values'] += 1
            out[field] = {'state': 'unknown', 'value': None, 'status': 'insufficient', 'reason_code': 'invalid_evidence_node'}
            continue
        state = node['state']
        value = node.get('value')
        if state == 'known' and not valid_value(field, value):
            rejected['invalid_typed_values'] += 1
            out[field] = {'state': 'unknown', 'value': None, 'status': 'insufficient', 'reason_code': 'invalid_typed_value'}
            continue
        out[field] = {'state': state, 'value': value if state == 'known' else None,
                      'status': STATUS[state], 'reason_code': 'capture_reported_' + state}
    return out, rejected


def public_schema():
    return {'schema_version': 1, 'additional_properties': False,
        'boolean_fields': sorted(BOOL_FIELDS), 'nonnegative_numeric_fields': sorted(NUMBER_FIELDS),
        'enumeration_fields': {k: sorted(v) for k, v in ENUM_FIELDS.items()},
        'list_fields': {k: sorted(v) for k, v in LIST_FIELDS.items()},
        'digest_fields': sorted(DIGEST_FIELDS), 'evidence_states': sorted(STATES),
        'raw_reasons_exported': False, 'unknown_false_null_not_applicable_distinct': True}
