import importlib.util
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[2] / 'eval/hy2_carrier_calibration/prepare.py'
spec = importlib.util.spec_from_file_location('hfc_prepare', SCRIPT)
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


def test_canonical_mihomo_identity_not_request_connection_key():
    connections = [{'connection_id':'request-key', 'mihomo_connection_id':'logical-key',
                    'carrier_binding':{'carrier_id':'carrier'}}]
    flows = [{'conn_id':'logical-key','carrier_binding':{'carrier_id':'carrier'}}]
    events = [{'type':'logical_carrier_bind','carrier_id':'carrier','logical_conn_id':'logical-key'},
              {'type':'tcp_connect','conn_id':'logical-key'},
              {'type':'carrier_open','carrier_id':'carrier'}]
    result = audit.carrier_evidence('carrier', connections, flows, events, {'carrier':{'open'}})
    assert result['indexed_not_bound']==0
    assert result['members_absent_request_index']==0
    assert result['member_starts_missing']==0
    assert result['local_open_count']==1


def test_unindexed_members_and_missing_lifecycle_remain_visible():
    events = [{'type':'logical_carrier_bind','carrier_id':'c','logical_conn_id':'unindexed'}]
    result = audit.carrier_evidence('c', [], [], events, {})
    assert result['members_absent_request_index']==1
    assert result['members_absent_flow_index']==1
    assert result['member_starts_missing']==1
    assert result['global_open_count']==0


def test_trace_boundary_does_not_use_late_unapproved_members():
    events = [{'event_seq':2,'type':'tcp_connect'}, {'event_seq':4,'type':'tcp_close'},
              {'event_seq':6,'type':'logical_carrier_bind'}]
    summary = {'trace_snapshot':{'traces':[{'barrier_verified':True,'cutoff_event_seq':3,
                                         'causal_tail_event_seqs':[4]}]}}
    assert [e['event_seq'] for e in audit.bounded_events(events,summary)]==[2,4]


def test_path_fingerprint_is_directional_and_has_no_plaintext_endpoint():
    path = dict(network='udp',src_ip='192.0.2.1',src_port=1,dst_ip='192.0.2.2',dst_port=2)
    reverse = dict(network='udp',src_ip='192.0.2.2',src_port=2,dst_ip='192.0.2.1',dst_port=1)
    assert audit.path_key(path)!=audit.path_key(reverse)
    assert '192.0.2' not in audit.path_key(path)
    assert audit.path_key({}) is None
