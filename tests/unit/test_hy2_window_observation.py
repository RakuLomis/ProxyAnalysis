import importlib.util
import sys
from pathlib import Path

DIRECTORY=Path(__file__).resolve().parents[2]/'eval/hy2_carrier_calibration'
sys.path.insert(0,str(DIRECTORY))
spec=importlib.util.spec_from_file_location('window_extract',DIRECTORY/'window_extract.py')
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def test_global_runs_not_sum_of_flow_runs():
    events=[(1,1,1,10),(2,2,1,20),(3,3,-1,30),(4,4,1,40)]
    summary=module.summarize(events)
    assert summary==dict(W_up=70,W_down=30,P_up=3,P_down=1,R_up=2,R_down=1)


def test_same_timestamp_uses_raw_ordinal():
    assert module.summarize([(1,3,1,5),(1,1,1,5),(1,2,-1,5)])['R_up']==2


def test_observed_payload_preserves_repeated_sends():
    summary=module.summarize([(1,1,1,5),(2,2,1,5)])
    assert summary['W_up']==10 and summary['P_up']==2


def test_reverse_tuple_and_membership_no_packet_duplication():
    key=('tcp','192.0.2.1',1234,'192.0.2.2',443)
    assert module.reverse(module.reverse(key))==key
    mapping={}
    module.add(mapping,key,('a',1)); module.add(mapping,key,('b',1))
    assert {direction for _,direction in mapping[key]}=={1}


def test_empty_observation_not_fabricated():
    assert all(value==0 for value in module.summarize([]).values())
