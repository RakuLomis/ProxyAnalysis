import inspect
import numpy as np
import pandas as pd
import pytest
from proxy_analysis.protocol_normalization.record_representation.core import (
    assemble,parse_records,interval_times,chunks,units_from_intervals,cdf,switching,
    estimate_pre,signature,distances)
from proxy_analysis.protocol_normalization.record_representation.run import segment_case
from proxy_analysis.protocol_normalization.early_stage_mechanism.records import reassemble

def body():
    hello=b'\x01\x00\x00\x26'+bytes(38)
    return b'\x16\x03\x03'+len(hello).to_bytes(2,'big')+hello+b'\x17\x03\x03\x10\x00'+bytes(4096)

@pytest.mark.parametrize('scenario',['fixed_256','fixed_1460','fixed_4096','irregular','header_cross','multi_record','duplicate_overlap_reorder'])
def test_resegmentation(scenario):
    b=body();f=segment_case(b,scenario,20260926);rebuilt,m,status=assemble(f,0)
    old,oldmap,_,_,oldstatus=reassemble(f,0)
    assert rebuilt==old==b and status==oldstatus=='contiguous'
    r,reason=parse_records(b,m,1);reference,_=parse_records(b,[dict(start=0,end=len(b),time_ns=0,packet_ordinal=0)],1)
    assert reason=='syntax_prefix_complete' and signature(r)==signature(reference)
    for col in ['start','end']:
        assert int(r.iloc[-1]['end'])==len(b)
    assert (r.first_ns<=r.all_ns).all() and (r.all_ns<=r.prefix_ns).all()

def test_negative_cases():
    b=body()
    assert assemble([(0,b,0,0)],None)[-1]=='missing_syn_origin'
    assert assemble([(0,b,0,0),(2,b'x',1,1)],0)[-1]=='overlap_conflict'
    prefix,m,status=assemble([(0,b[:2],0,0),(3,b[3:],1,1)],0)
    assert prefix==b[:2] and status=='gap_or_unobserved_prefix'
    b=b[:-1];m=[dict(start=0,end=len(b),time_ns=0,packet_ordinal=0)]
    assert parse_records(b,m,1)[1]=='partial_record_body'

def test_prefix_time_not_record_completion():
    m=[dict(start=0,end=10,time_ns=9,packet_ordinal=2),dict(start=10,end=20,time_ns=1,packet_ordinal=1)]
    first,alltime,prefix=interval_times([0,10],[10,20],m)
    assert first.tolist()==alltime.tolist()==[9,1] and prefix.tolist()==[9,9]

def test_partial_overlap_ownership():
    f=[(100,b'abcd',3,2),(102,b'cdef',1,1),(100,b'abcdef',5,3)]
    b,m,st=assemble(f,100);old,om,*_=reassemble(f,100)
    assert b==old==b'abcdef'
    assert interval_times([0,2],[2,6],m)[0].tolist()==[3,1]

def test_chunks_conserve_terminal_remainder():
    m=[dict(start=0,end=2050,time_ns=1,packet_ordinal=1)]
    c=chunks(2050,m);assert c.length.tolist()==[1024,1024,2]

def test_curve_end_and_duplicates():
    np.testing.assert_allclose(cdf([1,1,3],[2,3,5],[0,1,2,3]),[0,.5,.5,1])

def test_tie_order_not_causal():
    x=pd.DataFrame({'direction':[1,1,-1,1],'first_ns':[0,1,1,2]})
    s=switching(x,'first_ns');assert s['mixed_tie_unit_fraction']==.5
    assert s['switches_down_first']==s['switches_up_first']==2

def test_no_pre_in_estimator_and_no_clipping():
    assert list(inspect.signature(estimate_pre).parameters)==['post_bytes','training_center']
    assert estimate_pre([1,10],[3,3]).tolist()==[-2,7]
    assert list(inspect.signature(units_from_intervals).parameters)==['intervals','mapping']

def test_distance_identity():
    d=distances([1,2,8],[1,2,8],[0,4,16,np.inf]);assert all(v==0 for v in d.values())

@pytest.mark.parametrize('seed',range(5))
def test_sweep_matches_frozen_random_overlap(seed):
    rng=np.random.default_rng(seed);b=bytes(rng.integers(0,256,400,dtype=np.uint8))
    f=[(0,b,99,0)]
    for i in range(50):
        a=int(rng.integers(0,399));z=int(rng.integers(a+1,401));f.append((a,b[a:z],int(rng.integers(0,100)),i+1))
    rebuilt,m,s=assemble(f,0);old,om,*_=reassemble(f,0)
    assert rebuilt==old==b
    for a in range(400):
        assert interval_times([a],[a+1],m)[0][0]==interval_times([a],[a+1],om)[0][0]
