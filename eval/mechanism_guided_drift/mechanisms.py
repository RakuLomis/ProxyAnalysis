"""Source-backed local rules. Applicability never implies exact capture overhead."""
from common import ROOT, SOURCE, OUT, read_json, file_hash


def source_reference(scope, path, needle):
    base = SOURCE / scope if scope != 'instrumentation' else OUT / 'source-supplement'
    filename = base / path
    lines = filename.read_text(encoding='utf-8').splitlines()
    matches = [i + 1 for i, text in enumerate(lines) if needle in text]
    if not matches:
        raise AssertionError('source_marker_missing:' + scope + '/' + path)
    return {'scope': scope, 'source_path': path, 'line_numbers': matches,
            'local_path': filename.relative_to(ROOT).as_posix(), 'sha256': file_hash(filename),
            'marker': needle}


def make_rules():
    definitions = [
        ('ss-aead-chunk', 'shadowsocks', 'encrypted_chunk',
         'Classic AEAD: 2-byte length and two 16-byte tags; 34 bytes per chunk, salt once per direction.',
         {'cipher': 'aes-256-gcm', 'plugin': 'none', 'udp_over_tcp': False, 'smux_enabled': False},
         'Chunk count and application write boundaries are not TCP packet counts.',
         [('captured-sing-shadowsocks2', 'internal/shadowio/reader.go', 'Overhead = 16'),
          ('captured-sing-shadowsocks2', 'internal/shadowio/writer.go', '2*Overhead'),
          ('captured-sing-shadowsocks2', 'shadowaead/protocol.go', '16*1024 - 1'),
          ('captured-sing-shadowsocks2', 'shadowaead/method.go', 'm.keySaltLength = 32')]),
        ('vless-request', 'vless', 'logical_connection_request',
         'Non-mux request: 22 + encoded addons length + address bytes; this is local framing only.',
         {'transport': 'tcp', 'flow': 'none', 'smux_enabled': False},
         'Outer TLS lifecycle and record boundaries remain separate.',
         [('captured-build', 'transport/vless/conn.go', 'requestLen += 16'),
          ('captured-build', 'adapter/outbound/vless.go', 'StreamTLSConn')]),
        ('vless-vision-padding', 'vless', 'internal_buffer_and_direction_state',
         'Content <900: long mode content+padding 900..1399; short mode padding 0..255; first header21 then5.',
         {'vision': True}, 'Inactive in Extend; do not seek an unobserved Vision direct boundary.',
         [('captured-build', 'transport/vless/vision/padding.go', 'randv2.Int32N(500)'),
          ('captured-build', 'transport/vless/vision/conn.go', 'commandPaddingDirect')]),
        ('vmess-chunk', 'vmess', 'encrypted_chunk_and_security_mode',
         'Write chunk scale 15000; request padding0..15; security-dependent chunk framing.',
         {'transport': 'ws', 'tls': True, 'global_padding': False, 'authenticated_length': False},
         'Auto is unresolved security; alterId is absent; WS/TLS are active outer layers.',
         [('captured-sing-vmess', 'protocol.go', 'WriteChunkSize'),
          ('captured-sing-vmess', 'client.go', 'AutoSecurityType()'),
          ('captured-sing-vmess', 'client.go', 'mRand.Intn(16)')]),
        ('trojan-request', 'trojan', 'logical_connection_request',
         'TCP request61+SOCKS address bytes: IPv4 68, IPv6 80, domain65+n.',
         {'transport': 'tcp', 'tls': True, 'secondary_shadowsocks': False},
         'Address values are prohibited model inputs; TLS overhead and server implementation are unknown.',
         [('captured-build', 'transport/trojan/trojan.go', 'WriteHeader')]),
        ('anytls-framing', 'anytls', 'physical_session_and_framed_write',
         'Frame header7; startup auth32+length2+initial padding; default initial padding30.',
         {'transport': 'tls', 'tls': True},
         'Scheme can update; writeConn counter is session-local, not TCP packet number.',
         [('captured-build', 'transport/anytls/client.go', 'GenerateRecordPayloadSizes(0)'),
          ('captured-build', 'transport/anytls/session/session.go', 'pktCounter.Add(1)'),
          ('captured-build', 'transport/anytls/padding/padding.go', '0=30-30')]),
        ('anytls-idle-normalization', 'anytls', 'library_constructor_parameter',
         'Option check/timeout <=5 seconds normalizes to30 seconds in the client constructor.',
         {'transport': 'tls'},
         'Recorded effective zero is an adapter option, not an observed zero-second library timer.',
         [('instrumentation', 'adapter/semantics.go', 'option.IdleSessionTimeout'),
          ('captured-build', 'transport/anytls/session/client.go', 'time.Second * 30')]),
        ('hy2-stream-padding', 'hysteria2', 'quic_connection_and_stream',
         'Local request padding[64,512); library response[128,1024); auth[256,2048).',
         {'transport': 'quic'},
         'Server library identity and runtime negotiated congestion/state are not established.',
         [('captured-sing-quic', 'hysteria2/internal/protocol/padding.go', 'tcpRequestPadding'),
          ('captured-sing-quic', 'hysteria2/client.go', 'func (c *Client) offer(')]),
        ('hy2-salamander', 'hysteria2', 'outer_udp_datagram',
         'Salamander adds an8-byte salt per wrapped UDP datagram, not per logical TCP stream.',
         {'obfs': 'salamander'},
         'Unknown QUIC contents remain opaque; no automatic classification qualification.',
         [('captured-sing-quic', 'hysteria2/salamander.go', 'salamanderSaltLen = 8')]),
    ]
    return [{'rule_id': key, 'protocol': protocol, 'call_unit': unit, 'local_rule': formula,
             'requirements': requirements, 'boundary': boundary,
             'exact_observed_visit_overhead_claimed': False,
             'sources': [source_reference(*ref) for ref in refs]}
            for key, protocol, unit, formula, requirements, boundary, refs in definitions]


def qualify_rule(rule, effective):
    states = []
    for field, value in rule['requirements'].items():
        node = effective.get(field, {})
        if node.get('state') != 'known':
            states.append('unresolved')
        elif node.get('value') != value:
            states.append('inactive')
    if 'inactive' in states:
        return {'applicability': 'inactive_configuration_branch', 'diagnostic_grade': 'unavailable'}
    if states:
        return {'applicability': 'configuration_unresolved', 'diagnostic_grade': 'range-diagnostic'}
    return {'applicability': 'confirmed_adapter_option_branch', 'diagnostic_grade': 'exact-local-rule',
            'internal_counts_observed': False, 'capture_prediction_grade': 'empirical-only'}
