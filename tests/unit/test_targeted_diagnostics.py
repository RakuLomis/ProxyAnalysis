import numpy as np
import pandas as pd
import pytest

from proxy_analysis.protocol_normalization.targeted_diagnostics.core import (
    pair_ledger, contrast, cohorts, visits_and_items, reason_flags, position, size_bin, event_runs)
from proxy_analysis.protocol_normalization.byte_runs import multiscale


def ledger():
    return pd.DataFrame([dict(session_id='s',connection_id='c',side=side,direction=d,epoch_id=side,
         batch='0916',item_id='i',protocol='VLESS',repetition=1,main_route='proxy',observed_unique_valid=True,
         closed_contiguous_capture_candidate=True,unique_payload_bytes=10)
         for side in ['pre','post'] for d in [-1,1]])


def test_pair_keys_and_four_rows():
    z=pair_ledger(ledger());assert len(z)==2 and z.S_all4.all()
    with pytest.raises(AssertionError):pair_ledger(pd.concat([ledger(),ledger().iloc[:1]]))
    with pytest.raises(AssertionError):pair_ledger(ledger().iloc[:-1])


@pytest.mark.parametrize('pre,post,status',[(True,True,'both'),(True,False,'pre_only'),(False,True,'post_only'),(False,False,'neither')])
def test_four_strata(pre,post,status):
    a=ledger();a.loc[a.side=='pre','closed_contiguous_capture_candidate']=pre
    a.loc[a.side=='post','closed_contiguous_capture_candidate']=post
    z=pair_ledger(a);assert set(z.stratum)=={status}
    assert bool(z.S_all4.all())==(pre and post)


def test_all_four_not_same_direction():
    a=ledger();a.loc[0,'closed_contiguous_capture_candidate']=False
    z=pair_ledger(a);assert z.S_both.sum()==1 and not z.S_all4.any()


def test_invalid_bytes_cannot_be_zero_filled():
    a=ledger();a.loc[0,'observed_unique_valid']=False
    with pytest.raises(AssertionError):pair_ledger(a)
    a.loc[0,'unique_payload_bytes']=np.nan
    z=pair_ledger(a);assert not z.loc[z.direction==-1,'S_valid'].iloc[0]


def test_ratios_zero_missing():
    x=contrast(pd.DataFrame({'pre':[0.,0.,5.,5.],'post':[0.,4.,0.,10.]}))
    assert x.ratio.isna().tolist()==[True,True,False,False]
    assert x.ratio.iloc[2]==0 and np.isnan(x.log_ratio.iloc[2])
    assert x.difference.tolist()==[0,4,-5,5]


def test_cohort_empty_and_same_visits():
    a=ledger();a.loc[0,'closed_contiguous_capture_candidate']=False
    z=pair_ledger(a);rows=cohorts(z)
    assert 'S_all4' not in set(rows.cohort)
    assert rows[rows.cohort=='S_both'].direction.tolist()==[1]
    assert rows[rows.cohort=='S_valid_on_S_both_visits'].direction.tolist()==[1]
    v,i=visits_and_items(rows);assert len(v)==len(i)==4


def test_reasons_overlap_not_sum():
    r=dict(prefix_observed=False,suffix_observed=False,final_internal_gap_count=0,rst_count=1,
           sequence_epoch_ambiguous=False,overlap_content_conflicts=0,observed_unique_valid=True)
    assert reason_flags(r)==['prefix_unobserved','suffix_unobserved','rst']


@pytest.mark.parametrize('size,label',[(1,'(0,64)'),(63,'(0,64)'),(64,'[64,256)'),(256,'[256,1024)'),(1024,'[1024,inf)')])
def test_bins(size,label):assert size_bin(size)==label


def test_stable_event_order_and_positions():
    e=pd.DataFrame(dict(relative_time_ns=[1,0,0,1],packet_ordinal=[4,2,1,3],direction=[-1,1,-1,1],new_payload_bytes=[4,2,1,3]))
    r=event_runs(e)
    assert [x['direction'] for x in r]==[-1,1,-1]
    assert [x['new_bytes'] for x in r]==[1,5,4]
    assert [x['position'] for x in r]==['first','interior','last']
    assert r[-1]['cumulative_byte_end']==1
    assert r[1]['first_event']==1 and r[1]['last_event']==2


def test_zero_and_singleton():
    e=pd.DataFrame(columns=['relative_time_ns','packet_ordinal','direction','new_payload_bytes'])
    assert event_runs(e)==[]
    assert position(0,1)=='singleton'
    e.loc[0]=[0,1,1,5]
    r=event_runs(e);assert len(r)==1 and r[0]['position']=='singleton'


def test_threshold_boundary_and_conservation():
    results=multiscale([(1,63),(-1,64),(1,256),(-1,1024)])
    assert [r['threshold_bytes'] for r in results]==[0,64,256,1024]
    assert results[0]['retained_bytes']==1407
    assert results[1]['directions']==[-1,1,-1]
    assert results[3]['new_bytes']==[1024]


def test_direction_position_count_decomposition():
    a=[(1,4),(-1,9),(1,3)];b=[(1,8)]
    cells={}
    for sign,seq in [(-1,a),(1,b)]:
        for i,(d,_) in enumerate(seq):
            key=(d,position(i,len(seq)));cells[key]=cells.get(key,0)+sign
    assert sum(cells.values())==len(b)-len(a)


def test_no_training_entrypoint():
    from proxy_analysis.protocol_normalization.targeted_diagnostics import run
    text=__import__('pathlib').Path(run.__file__).read_text(encoding='utf-8')
    assert 'sklearn' not in text and 'torch' not in text and '.fit(' not in text
