import math
from types import SimpleNamespace

import numpy as np
import pytest

from proxy_analysis.config import FeatureConfig
from proxy_analysis.features.models import PacketMeasure
from proxy_analysis.reproducibility.extract import compare, describe
from proxy_analysis.reproducibility.statistics import (
    bh, classify, dispersion, icc, separability, signflip_p,
)


def test_dispersion_and_degenerate_icc():
    d=dispersion([1,2,3,4,5])
    assert d['mad_raw']==1 and d['iqr']==2 and d['variance']==2.5
    assert icc(np.ones((4,5)))==(None,None)


def test_absolute_agreement_icc_penalizes_round_shift():
    constant=np.repeat(np.arange(5.)[:,None],5,axis=1)
    assert icc(constant)==pytest.approx((1,1))
    shifted=constant+np.arange(5.)[None,:]*10
    assert icc(shifted)[0]<.1


def test_local_separation_can_cancel_across_urls():
    x=np.array([[[0,0,0],[10,10,10]],[[10,10,10],[0,0,0]]])
    b,w,local,global_s=separability(x,1e-6)
    assert np.all(w==0) and np.all(b==50)
    assert local>1e6 and global_s==0


def test_nonsignificant_is_not_practical_equivalence():
    metric={'transform':'log_ratio'}
    assert classify([-1,1,-1,1,0],metric)['classification']=='uncertain'
    assert classify([0,.001,-.001,0,0],metric)['classification']=='practically_stable'
    assert classify([.5,.5,.5,.5,.5],metric)['classification']=='increase'
    assert classify([.2]*5,{'transform':'distance'})['classification']=='distance_above_threshold'


def test_exact_sign_symmetry_and_bh():
    assert signflip_p([1,1,1])==.25
    assert signflip_p([0,0,0])==1
    assert bh([.01,.02,.9])==pytest.approx([.03,.03,.9])


def test_stream_boundaries_do_not_create_iats_or_reversals():
    config=FeatureConfig.load('configs/feature-defaults.yaml')
    groups=[[PacketMeasure('a',0,1,1,100,140,154)],
            [PacketMeasure('b',1000,1,-1,100,140,154)]]
    d=describe(groups,config)
    assert d['iat_count']==0 and d['fr_runs']==2 and d['fr_switches']==0
    assert d['transition_p_pm'] is None
    assert d['burst_count']==2
    assert sum(d['length_hist'])==2


def test_zero_ratios_remain_missing_and_tcp_fr_not_hy2():
    metrics=[{'id':'fr_runs','family':'interaction','transform':'log_ratio','unit':'runs','tcp_only':True},
             {'id':'packet_count','family':'workload','transform':'log_ratio','unit':'packets'}]
    result=compare({'fr_runs':2,'packet_count':0},{'fr_runs':3,'packet_count':5},metrics,False)
    assert result[0]['reason']=='tcp_fr_not_comparable_to_shared_udp'
    assert result[1]['delta'] is None
    assert result[1]['delta_smoothed']==pytest.approx(math.log(6))


def test_histogram_overflow_is_preserved():
    config=FeatureConfig.load('configs/feature-defaults.yaml')
    d=describe([[PacketMeasure('a',0,1,1,70000,70040,70054)]],config)
    assert d['length_hist'][-1]==1
    assert sum(d['length_hist'])==1


def test_carrier_direction_uses_declared_migrating_paths(tmp_path, monkeypatch):
    import json
    from proxy_analysis.reproducibility import extract
    (tmp_path/'raw').mkdir()
    path1={'src_ip':'client','src_port':100,'dst_ip':'server1','dst_port':200}
    path2={'src_ip':'client','src_port':101,'dst_ip':'server2','dst_port':201}
    event={'event_seq':1,'carrier_id':'carrier','carrier_paths':[path2]}
    (tmp_path/'raw/mihomo-trace.jsonl').write_text(json.dumps(event)+'\n')
    def read(path):
        if path.name=='flow-index.json':
            return {'items':[{'carrier_binding':{'carrier_id':'carrier','physical_paths':[path1]}}]}
        return {'trace_snapshot':{'traces':[{'barrier_verified':True,'cutoff_event_seq':1}]}}
    monkeypatch.setattr(extract,'read_json',read)
    records=[SimpleNamespace(link_type=101,packet_data=bytes([i]),packet_ordinal=i,
                             timestamp_ns=i,captured_len=50) for i in (1,2)]
    monkeypatch.setattr(extract,'PcapNgReader',lambda _: records)
    def decode(_,data):
        if data==b'\x01': ips,ports=('client','server1'),(100,200)
        else: ips,ports=('server2','client'),(201,101)
        return SimpleNamespace(ip_src=ips[0],ip_dst=ips[1],src_port=ports[0],dst_port=ports[1],
                               transport_protocol='udp',transport_payload_len=10,ip_total_len=38)
    monkeypatch.setattr(extract,'decode_packet',decode)
    descriptor=SimpleNamespace(entity_id='carrier',artifact_id='artifact',capture_path=tmp_path/'post')
    analysis=extract.analyze_carrier(descriptor,tmp_path)
    assert [p.direction for p in analysis.packet_measures]==[1,-1]
