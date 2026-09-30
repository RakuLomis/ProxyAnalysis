"""Pure single-side transformations and descriptive statistics.

No function here accepts an opposite-side stream or a business label.
"""
import heapq
import numpy as np
import pandas as pd
from scipy.stats import wasserstein_distance, ks_2samp
from scipy.spatial.distance import jensenshannon
from ..early_stage_mechanism.records import tls_prefix

TIME = ['first_ns', 'all_ns', 'prefix_ns']
SIGNATURE = ['record_index', 'start', 'end', 'content_type', 'legacy_version', 'record_payload_length']


def assemble(fragments, origin):
    """Sweep first-observation ownership; reject conflicting overlap, stop at gap.

    Same contract as the frozen assembler; independent implementation is tested
    against it and byte-for-byte on every frozen VLESS stream.
    """
    if origin is None:
        return b'', [], 'missing_syn_origin'
    f = [(a-origin, bytes(b), int(t), int(o)) for a,b,t,o in fragments if len(b)]
    if not f:
        return b'', [], 'empty'
    assert min(a for a,_,_,_ in f) >= 0
    data = bytearray(); cursor = 0; gap = False
    for a,b,_,_ in sorted(f, key=lambda x:x[0]):
        if a > cursor:
            gap = True; break
        overlap = min(len(b), cursor-a)
        if bytes(data[a:a+overlap]) != b[:overlap]:
            return b'', [], 'overlap_conflict'
        if overlap < len(b):
            data.extend(b[overlap:]); cursor = a+len(b)
    # Only the observable prefix is mapped; a gap is never filled.
    events = {}
    for i,(a,b,t,o) in enumerate(f):
        if a >= cursor: continue
        events.setdefault(a, []).append(i)
        events.setdefault(min(a+len(b),cursor), [])
    positions = sorted(events); active = []; mapping = []
    for a,z in zip(positions,positions[1:]):
        for i in events[a]:
            p,b,t,o=f[i]; heapq.heappush(active,(t,o,i,p+len(b)))
        while active and active[0][3] <= a: heapq.heappop(active)
        if not active: break
        t,o,_,_=active[0]
        if mapping and mapping[-1]['end']==a and (mapping[-1]['time_ns'],mapping[-1]['packet_ordinal'])==(t,o):
            mapping[-1]['end']=z
        else: mapping.append(dict(start=a,end=z,time_ns=t,packet_ordinal=o))
    return bytes(data),mapping,'gap_or_unobserved_prefix' if gap else 'contiguous'


def interval_times(starts, ends, mapping):
    m=pd.DataFrame(mapping).sort_values('start')
    ms=m.start.to_numpy(); me=m.end.to_numpy(); mt=m.time_ns.to_numpy()
    assert len(m) and ms[0]==0 and np.array_equal(ms[1:],me[:-1])
    result=[]
    for a,b in zip(starts,ends):
        lo=np.searchsorted(me,a,side='right'); hi=np.searchsorted(ms,b,side='left')
        assert hi>lo and me[hi-1]>=b
        result.append((int(mt[lo:hi].min()),int(mt[lo:hi].max())))
    arr=np.asarray(result,dtype=np.int64).reshape(-1,2)
    return arr[:,0],arr[:,1],np.maximum.accumulate(arr[:,1])


def parse_records(body, mapping, expected_hello):
    # Frozen syntax parser unchanged. A single sentinel interval avoids quadratic
    # source searches; actual first/all/prefix times are reconstructed separately.
    if not body:return pd.DataFrame(), 'empty_prefix'
    sentinel=[dict(start=0,end=len(body),time_ns=0,packet_ordinal=0)]
    records,status=tls_prefix(body,sentinel,expected_hello)
    out=pd.DataFrame(records)
    if len(out):
        out['first_ns'],out['all_ns'],out['prefix_ns']=interval_times(out.start,out.end,mapping)
    return out,status


def units_from_intervals(intervals, mapping):
    """Single-side record/chunk encoding; mapping must cover own-side intervals."""
    out=intervals.copy()
    out['length']=out.end-out.start
    out['first_ns'],out['all_ns'],out['prefix_ns']=interval_times(out.start,out.end,mapping)
    return out


def chunks(total, mapping, size=1024):
    a=np.arange(0,int(total),size,dtype=np.int64)
    return units_from_intervals(pd.DataFrame({'start':a,'end':np.minimum(a+size,total),'unit_index':np.arange(len(a))}),mapping)


def cdf(times, weights, grid):
    order=np.argsort(times,kind='stable'); t=np.asarray(times)[order]; w=np.asarray(weights)[order]
    s=np.r_[0,np.cumsum(w,dtype=float)]
    return s[np.searchsorted(t,grid,side='right')]/s[-1] if s[-1] else np.zeros(len(grid))


def switching(units, time):
    x=units[['direction',time]].copy()
    mixed=x.groupby(time).direction.nunique(); values=set(mixed[mixed>1].index)
    result={'mixed_tie_unit_fraction':float(x[time].isin(values).mean()),'mixed_tie_groups':len(values)}
    for ascending,label in [(True,'down_first'),(False,'up_first')]:
        d=x.sort_values([time,'direction'],ascending=[True,ascending],kind='stable').direction.to_numpy()
        result['switches_'+label]=int(np.count_nonzero(d[1:]!=d[:-1]))
    return result


def distances(a,b,bins):
    a=np.asarray(a); b=np.asarray(b)
    ha=np.histogram(a,bins)[0]; hb=np.histogram(b,bins)[0]
    return dict(w_log2=float(wasserstein_distance(np.log2(1+a),np.log2(1+b))),
                w_bytes=float(wasserstein_distance(a,b)),ks=float(ks_2samp(a,b).statistic),
                js_bits=float(jensenshannon(ha/ha.sum(),hb/hb.sum(),base=2)**2))


def estimate_pre(post_bytes, training_center):
    """No clipping, pre values, or content means at inference."""
    return np.asarray(post_bytes)-np.asarray(training_center)


def signature(records):
    return [tuple(int(row[c]) for c in SIGNATURE) for row in records.to_dict('records')]
