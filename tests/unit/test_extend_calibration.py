import json
from pathlib import Path

import pytest

from proxy_analysis.extend_calibration.audit import (
    bounded_trace, child, content_key, path_identity, resolve_selected, route_evidence,
)


def test_relative_paths_and_traversal():
    assert child(Path('root'), 'a/b.json') == Path('root/a/b.json')
    for value in ['../x', '/data/x', 'C:/x', '..\\x']:
        with pytest.raises(ValueError):
            child(Path('root'), value)


def test_selected_attempt_not_prior():
    run = {'selected_attempt': 2, 'session_ids': ['new'],
           'attempts': [{'ordinal': 1, 'session_ids': ['old']}, {'ordinal': 2, 'session_ids': ['new']}]}
    entries, issues = resolve_selected(run, {'entries': [{'session_id': 'old'}, {'session_id': 'new'}]})
    assert entries == [{'session_id': 'new'}] and not issues
    run['session_ids'] = ['old']
    assert resolve_selected(run, {'entries': entries})[1]


def test_url_identity_preserves_query_and_video_part():
    assert content_key('https://www.youtube.com/watch?v=abc') == 'youtube_video:abc'
    assert content_key('https://www.bilibili.com/video/BV1/?p=2') != content_key('https://www.bilibili.com/video/BV1/?p=3')
    assert content_key('https://www.bing.com/search?q=a') != content_key('https://www.bing.com/search?q=b')


def test_successful_document_resolves_failed_retry_but_not_unknown_success():
    req = [dict(resource_type='Document', url='https://a.test/', response_status=200,
                connection_id='c', failure={'failed': False}),
           dict(resource_type='Document', url='https://a.test/', response_status=None,
                connection_id=None, failure={'failed': True})]
    conn = [{'connection_id': 'c', 'egress': {'mode': 'proxy'}}]
    assert route_evidence(req, conn, {'url': 'https://a.test'}, {})[0] == 'proxy_success'
    req[1]['response_status'] = 200
    req[1]['failure']['failed'] = False
    assert route_evidence(req, conn, {'url': 'https://a.test'}, {})[0] == 'unresolved_mixed_success_routes'


def test_media_not_primary_document_and_no_same_domain_fallback():
    req = [{'resource_type': 'Media', 'url': 'https://a.test/video', 'response_status': 200, 'connection_id': 'c'},
           {'resource_type': 'Document', 'url': 'https://a.test/other', 'response_status': 200, 'connection_id': 'c'}]
    decision, rows = route_evidence(req, [{'connection_id': 'c', 'egress': {'mode': 'proxy'}}], {'url': 'https://a.test'}, {})
    assert decision == 'unresolved_no_successful_document'
    assert len(rows) == 1 and rows[0]['kind'] == 'media_resource'


def test_bounded_trace_preserves_only_authorized_events(tmp_path):
    path = tmp_path / 'trace.jsonl'
    events = [dict(carrier_id='c', event_seq=n, type='logical_carrier_bind') for n in [1, 2, 3, 4]]
    path.write_text('\n'.join(json.dumps(e) for e in events), encoding='utf-8')
    summary = {'trace_snapshot': {'traces': [{'barrier_verified': True, 'cutoff_event_seq': 2, 'causal_tail_event_seqs': [4]}]}}
    evidence, audit = bounded_trace(path, summary, {'c'})
    assert [e['event_seq'] for e in evidence] == [1, 2, 4]
    assert audit['outside_barrier_carrier_lines'] == 1
    assert bounded_trace(path, {}, {'c'})[1]['status'] == 'unverified_barrier'


def test_path_identity_is_direction_sensitive_and_redacted():
    flow = dict(network='tcp', src_ip='a', src_port=1, dst_ip='b', dst_port=2)
    assert len(path_identity(flow)) == 64
    assert path_identity(flow) != path_identity({**flow, 'src_ip': 'b', 'dst_ip': 'a'})
    assert path_identity({}) is None
