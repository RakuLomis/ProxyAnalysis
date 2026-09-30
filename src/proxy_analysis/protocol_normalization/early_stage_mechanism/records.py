"""Conservative plaintext record syntax; never infer a Vision transition from shape."""
from .. import tcp_ledger


def reassemble(fragments,origin):
    """Chronological first-observation ownership, conflict checked before prefix assembly.

    fragments: (offset, bytes, time_ns, packet_ordinal), origin established by SYN.
    Returns contiguous prefix, source interval map, unique total and remaining unique bytes.
    """
    if origin is None:return b'',[],0,0,'missing_syn_origin'
    if tcp_ledger.conflicts([(a,data) for a,data,_,_ in fragments]):
        return b'',[],0,0,'overlap_conflict'
    owned=[];intervals=[]
    for start,data,t,ordinal in sorted(fragments,key=lambda r:(r[2],r[3])):
        end=start+len(data);cursor=start
        for left,right in intervals:
            if right<=cursor:continue
            if left>=end:break
            if left>cursor:owned.append((cursor,min(left,end),data[cursor-start:min(left,end)-start],t,ordinal))
            cursor=max(cursor,right)
            if cursor>=end:break
        if cursor<end:owned.append((cursor,end,data[cursor-start:],t,ordinal))
        intervals=tcp_ledger.interval_union(intervals+[(start,end)])
    unique=sum(b-a for a,b in intervals)
    blocks=[];mapping=[];cursor=origin
    for a,b,data,t,ordinal in sorted(owned):
        if b<=cursor:continue
        if a>cursor:break
        skip=max(0,cursor-a);blocks.append(data[skip:])
        mapping.append(dict(start=cursor-origin,end=b-origin,time_ns=t,packet_ordinal=ordinal));cursor=b
    body=b''.join(blocks)
    return body,mapping,unique,unique-len(body),'contiguous' if len(body)==unique else 'gap_or_unobserved_prefix'


def tls_prefix(body,mapping,expected_hello):
    """TLS-like record stream strictly from offset zero. No decryption/resync.

    Establish a plaintext ClientHello/ServerHello message header at the prefix.
    Later records are syntax candidates, not authenticated outer-record attribution.
    """
    if not body:return [],'empty_prefix'
    records=[];offset=0;handshake=b'';hello=False
    while offset<len(body):
        if len(body)-offset<5:return records,'partial_record_header'
        kind=body[offset];version=int.from_bytes(body[offset+1:offset+3],'big');length=int.from_bytes(body[offset+3:offset+5],'big')
        if kind not in [20,21,22,23] or version not in [0x301,0x302,0x303] or length>16640:
            return records,'invalid_header_no_resynchronization'
        if not records and kind!=22:return [],'no_initial_handshake_record'
        end=offset+5+length
        if end>len(body):return records,'partial_record_body'
        if not hello:
            if kind!=22:return [],'hello_not_established'
            handshake+=body[offset+5:end]
            if len(handshake)>=4:
                msglen=int.from_bytes(handshake[1:4],'big')
                if handshake[0]!=expected_hello or msglen<38:return [],'wrong_or_short_initial_hello'
                if len(handshake)>=4+msglen:hello=True
        covering=[m for m in mapping if m['start']<end and m['end']>offset]
        if not covering:raise AssertionError('record source mapping missing')
        records.append(dict(record_index=len(records),start=offset,end=end,content_type=kind,legacy_version=version,
            record_payload_length=length,first_observation_ns=min(m['time_ns'] for m in covering),
            complete_available_ns=max(m['time_ns'] for m in covering),first_packet_ordinal=min(m['packet_ordinal'] for m in covering),
            syntax_only=True,hello_established=hello))
        offset=end
    if not hello:return [],'partial_initial_hello'
    return records,'syntax_prefix_complete'


def post_only_phase(post_records):
    """No phase marker has been established. No pre parameter or fallback allowed."""
    return {'permission':'unavailable','boundary':None,'reason':'record_syntax_does_not_identify_Vision_initial_relay_transition'}
