import struct
from proxy_analysis.parsing.pcapng import CaptureRecord
from proxy_analysis.parsing import decode_packet
from proxy_analysis.extend_calibration.reassembly import StrictIPv4


def fragment(offset, more, data, ordinal=1, ident=7):
    header=struct.pack('!BBHHHBBH4s4s',69,0,20+len(data),ident,(8192 if more else 0)+offset//8,
                       64,17,0,b'\x01\x01\x01\x01',b'\x02\x02\x02\x02')
    ip=header+data
    return CaptureRecord(0,0,101,ordinal,ordinal*100,len(ip),len(ip),ip),ip


def test_complete_and_provenance():
    r=StrictIPv4(); payload=struct.pack('!HHHH',10,20,24,0)+b'abcdefghijklmnop'
    assert r.feed(*fragment(0,True,payload[:16])) is None
    out=r.feed(*fragment(16,False,payload[16:],2))
    assert decode_packet(101,out.packet_data).transport_payload_len==16
    assert out.timestamp_ns==200 and r.provenance[0]['source_ordinals']==[1,2]
    assert not r.finish()


def test_no_padding_no_orphan_guessing():
    r=StrictIPv4(); r.feed(*fragment(0,True,b'12345678'))
    assert 'incomplete_datagrams' in r.finish()
    s=StrictIPv4(); assert s.feed(*fragment(8,False,b'abcdefgh')) is None
    assert 'orphan_nonzero_fragment' in s.finish()


def test_conflict_and_reuse_poison_key():
    r=StrictIPv4(); r.feed(*fragment(0,True,b'12345678abcdefgh'))
    assert r.feed(*fragment(8,False,b'XXXXXXXX',2)) is None
    assert 'overlap_content_conflict' in r.finish()
    assert r.feed(*fragment(0,True,b'12345678abcdefgh',3)) is None


def test_id_reuse_only_after_complete():
    r=StrictIPv4(); payload=struct.pack('!HHHH',10,20,24,0)+b'abcdefghijklmnop'
    for i in [1,3]:
        assert r.feed(*fragment(0,True,payload[:16],i)) is None
        assert r.feed(*fragment(16,False,payload[16:],i+1)) is not None
    assert r.stats['complete_datagrams']==2


def test_udp_length_must_match():
    r=StrictIPv4(); payload=struct.pack('!HHHH',10,20,32,0)+b'abcdefghijklmnop'
    r.feed(*fragment(0,True,payload[:16]))
    assert r.feed(*fragment(16,False,payload[16:],2)) is None
    assert 'invalid_reassembled_transport' in r.finish()
