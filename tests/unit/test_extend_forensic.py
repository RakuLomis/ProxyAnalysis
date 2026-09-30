from copy import deepcopy

import pytest

from proxy_analysis.extend_calibration.forensic import endpoint, successful_socket, utc_ns


def sample():
    def ev(source, kind, phase, params):
        return dict(source={'id': source}, type=kind, phase=phase, time='1234', params=params)
    return {'constants': {'timeTickOffset': '1000000', 'logEventTypes': {
        'HTTP2_SESSION_INITIALIZED': 1, 'TCP_CONNECT': 2,
        'HTTP2_SESSION_SEND_HEADERS': 3, 'HTTP2_SESSION_RECV_HEADERS': 4}},
        'events': [ev(20, 1, 0, {'source_dependency': {'id': 30}}),
                   ev(30, 2, 2, {'local_address': '10.0.0.1:1000', 'remote_address': '10.0.0.2:443'}),
                   ev(20, 3, 0, {'stream_id': 1, 'headers': [':path: /a?q=b', ':authority: a.test']}),
                   ev(20, 4, 0, {'stream_id': 1, 'headers': [':status: 200']})]}


def test_direct_socket_dependency_and_exact_stream():
    result = successful_socket(sample(), 20, 'https://a.test/a?q=b')
    assert result['socket_source'] == 30
    assert result['pre_flow']['src_port'] == 1000
    assert result['successful_stream_ids'] == [1]


def test_wrong_content_and_wrong_stream_are_not_accepted():
    with pytest.raises(ValueError):
        successful_socket(sample(), 20, 'https://a.test/a?q=c')
    data = sample()
    data['events'][-1]['params']['stream_id'] = 3
    with pytest.raises(ValueError):
        successful_socket(data, 20, 'https://a.test/a?q=b')


def test_ambiguous_socket_is_not_repaired_by_nearest_time():
    data = sample()
    data['events'].append(deepcopy(data['events'][1]))
    with pytest.raises(ValueError):
        successful_socket(data, 20, 'https://a.test/a?q=b')


def test_failed_connect_not_used():
    data = sample()
    data['events'][1]['params']['net_error'] = -7
    with pytest.raises(ValueError):
        successful_socket(data, 20, 'https://a.test/a?q=b')


def test_integer_time_and_ipv6_endpoint():
    assert utc_ns('1234', '1000000') == 1001234000000
    assert endpoint('[::1]:443') == ('::1', 443)
