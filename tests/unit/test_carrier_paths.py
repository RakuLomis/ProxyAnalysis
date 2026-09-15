import json
import pytest
from proxy_analysis.indexing.carrier_paths import carrier_paths, bounded_events
from proxy_analysis.sequences.direction import Endpoint, SequenceEvent, enrich_sequence
from proxy_analysis.quality.reports import build_quality_report


def test_migrating_direction_and_unknown_are_not_dropped():
    a,b,c=Endpoint('a',1),Endpoint('b',2),Endpoint('c',3)
    events=[SequenceEvent('1',1,1,'a','c',1,3), SequenceEvent('2',2,2,'c','a',3,1),
            SequenceEvent('3',3,3,'a','d',1,4)]
    result=enrich_sequence(events,a,b,physical_paths=((a,b),(a,c)))
    assert [e.direction for e in result]==[1,-1,None]
    assert [e.packet_iat_ns for e in result]==[None,1,1]
    with pytest.raises(ValueError,match='ambiguous'):
        enrich_sequence(events,a,b,physical_paths=((a,c),(c,a)))


def test_trace_paths_bounded_and_ambiguity_rejected(tmp_path):
    (tmp_path/'analysis').mkdir(); (tmp_path/'raw').mkdir()
    snapshot={'trace_snapshot':{'traces':[{'barrier_verified':True,'cutoff_event_seq':1}]}}
    (tmp_path/'analysis/summary.json').write_text(json.dumps(snapshot))
    flow={'src_ip':'a','src_port':1,'dst_ip':'b','dst_port':2}
    events=[{'event_seq':1,'carrier_id':'c','post_flow':flow},
            {'event_seq':2,'carrier_id':'c','post_flow':{**flow,'dst_port':3}}]
    trace=tmp_path/'raw/mihomo-trace.jsonl'
    trace.write_text('\n'.join(map(json.dumps,events)))
    assert len(carrier_paths(tmp_path)['c'])==1
    events.append({'event_seq':1,'carrier_id':'c','post_flow':{'src_ip':'b','src_port':2,'dst_ip':'a','dst_port':1}})
    trace.write_text('\n'.join(map(json.dumps,events)))
    with pytest.raises(ValueError,match='ambiguous'): carrier_paths(tmp_path)
    with pytest.raises(ValueError,match='barrier'): bounded_events(events,{})


def test_empty_dataset_cannot_pass(tmp_path):
    report=build_quality_report(tmp_path,expected_session_ids=['missing'])
    assert report['state']=='failed'
    assert {'empty_feature_dataset','session_selection_mismatch'} <= {e['code'] for e in report['errors']}
