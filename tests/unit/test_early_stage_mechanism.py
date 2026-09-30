import inspect
import numpy as np
import pytest
from proxy_analysis.protocol_normalization.early_stage_mechanism.statistics import load_bin,lad_fit
from proxy_analysis.protocol_normalization.early_stage_mechanism.records import reassemble,tls_prefix,post_only_phase

@pytest.mark.parametrize('value,label',[(0,'zero'),(1,'(0,4KiB)'),(4095,'(0,4KiB)'),(4096,'[4,16KiB)'),(16384,'[16,64KiB)'),(65536,'[64,256KiB)'),(262144,'[256KiB,1MiB)'),(1048576,'[1MiB,inf)')])
def test_bins(value,label):assert load_bin(value)==label

def test_lad_and_rank():
    x=np.column_stack([np.ones(10),np.arange(10),np.arange(10)*2])
    c,keep=lad_fit(x,3+np.arange(10)*2)
    assert keep==[0,1];np.testing.assert_allclose(x@c,3+np.arange(10)*2,atol=1e-7)

def test_reassembly_order_overlap_and_provenance():
    body,mapping,total,tail,status=reassemble([(104,b'ef',1,1),(100,b'abcd',2,2),(102,b'cdef',3,3)],100)
    assert body==b'abcdef' and total==6 and tail==0 and status=='contiguous'
    assert mapping[0]['time_ns']==2 and mapping[-1]['time_ns']==1

def test_gap_conflict_origin():
    assert reassemble([(10,b'a',0,1),(12,b'c',1,2)],10)[0]==b'a'
    assert reassemble([(10,b'a',0,1),(10,b'b',1,2)],10)[-1]=='overlap_conflict'
    assert reassemble([(10,b'a',0,1)],None)[-1]=='missing_syn_origin'

def hello(kind=1):
    body=bytes([kind])+bytes([0,0,38])+bytes(38)
    return bytes([22,3,3])+len(body).to_bytes(2,'big')+body

def test_record_cross_packet_timing():
    data=hello();body,mapping,*_=reassemble([(0,data[:8],2,1),(8,data[8:],1,2)],0)
    r,status=tls_prefix(body,mapping,1)
    assert status=='syntax_prefix_complete' and len(r)==1
    assert r[0]['first_observation_ns']==1 and r[0]['complete_available_ns']==2

def test_multiple_records_partial_no_resync():
    data=hello()+b'\x17\x03\x03\x00\x02xx'
    mapping=[dict(start=0,end=len(data),time_ns=0,packet_ordinal=0)]
    assert len(tls_prefix(data,mapping,1)[0])==2
    assert tls_prefix(data[:-1],mapping,1)[1]=='partial_record_body'
    assert not tls_prefix(b'junk'+data,mapping,1)[0]

def test_wrong_hello_and_protected_first_record():
    data=hello(2);m=[dict(start=0,end=len(data),time_ns=0,packet_ordinal=0)]
    assert not tls_prefix(data,m,1)[0]
    assert not tls_prefix(b'\x17\x03\x03\x00\x01x',m,1)[0]

def test_unavailable_phase_no_pre_interface():
    assert list(inspect.signature(post_only_phase).parameters)==['post_records']
    assert post_only_phase([])==post_only_phase([{'content_type':23}])
    assert post_only_phase([])['boundary'] is None

def test_partition_determinism():
    from proxy_analysis.protocol_normalization.early_stage_mechanism.common import stable
    assert stable('same-content')==stable('same-content')
    assert stable('a')!=stable('b')
