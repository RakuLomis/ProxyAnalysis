"""Uniform common observation interval and evidence-only lifecycle exclusion."""
from decimal import Decimal
from collections import defaultdict
import json
import pandas as pd

from .audit import read, file_hash

COLLECTOR_COMMIT='1be20b929ba8454678f5a33b68fd7f3b97edadf4'
CHROME_COMMIT='8f5d36bc16f57115aeeff34baf4ad6aa964d509c'


def define_window(manifest, context, netlog):
    coverage=context['packet_coverage']
    assert manifest['component_versions']['traffictracer']['commit']==COLLECTOR_COMMIT
    client=netlog['constants']['clientInfo']
    assert client['os_type'].startswith('Linux:') and client['cl'].startswith(CHROME_COMMIT)
    assert coverage['clock']=='monotonic_seconds' and coverage['status']=='passed' and not coverage['errors']
    assert all(coverage['exit'][s]['code']==0 and not coverage['exit'][s]['killed'] for s in ['tun','physical'])
    start=max(Decimal(str(coverage['ready'][s])) for s in ['tun','physical'])
    end=Decimal(str(coverage['browser_quiescent']))
    stop=min(Decimal(str(coverage['stopped'][s])) for s in ['tun','physical'])
    assert start < end <= stop
    assert start <= Decimal(str(coverage['browser_start_requested'])) <= Decimal(str(coverage['navigation_requested'])) < end
    offset=Decimal(str(netlog['constants']['timeTickOffset']))*1_000_000
    a,b=int(start*1_000_000_000+offset),int(end*1_000_000_000+offset)
    assert int(pd.Timestamp(manifest['started_at']).value) <= a < b <= int(pd.Timestamp(manifest['completed_at']).value)
    return {'start_ns':a,'end_ns':b,'tick_offset_ms':str(netlog['constants']['timeTickOffset']),
        'clock_basis':'verified collector time.monotonic and Chromium CLOCK_MONOTONIC on same Linux host',
        'start_rule':'max capture header readiness','end_rule':'browser_quiescent before health check and either capture shutdown',
        'stopped_is_shutdown_completion_not_live_capture_boundary':True,
        'UTC_precision':'NetLog integer-ms offset; not nanosecond-accurate wall-clock calibration',
        'suspend_or_wall_clock_jump_independently_ruled_out':False}


def bounded_lifecycles(base, summary):
    snap=summary['trace_snapshot']['traces'][0]
    assert snap['barrier_verified']
    tail=set(snap.get('causal_tail_event_seqs',[]));by_id=defaultdict(list)
    for line in (base/'raw/mihomo-trace.jsonl').open(encoding='utf-8'):
        e=json.loads(line);seq=e.get('event_seq')
        if not isinstance(seq,int) or not (seq<=snap['cutoff_event_seq'] or seq in tail):continue
        ident=e.get('conn_id') or e.get('logical_conn_id')
        if ident and e.get('type') in ['tcp_connect','tcp_close']:
            by_id[ident].append({'type':e['type'],'ts_ns':int(pd.Timestamp(e['ts']).value),'event_seq':seq})
    return by_id


def outside_reason(events,start,end):
    opens=[e['ts_ns'] for e in events if e['type']=='tcp_connect']
    closes=[e['ts_ns'] for e in events if e['type']=='tcp_close']
    # No filtering based only on bind time, absence of packets or aliases.
    if len(opens)!=1 or len(closes)>1:return None
    if closes and closes[0]<opens[0]:return None
    if opens[0]>=end:return 'logical_connect_after_common_end'
    if closes and closes[0]<=start:return 'logical_closed_before_common_start'
    return None


def prepare_scope(base, manifest, flows):
    context=read(base/'raw/capture-context.json');netlog=read(base/'raw/netlog.json')
    window=define_window(manifest,context,netlog)
    lifecycle=bounded_lifecycles(base,read(base/'analysis/summary.json'))
    excluded={}
    for f in flows:
        events=lifecycle.get(f['conn_id'],[])
        reason=outside_reason(events,window['start_ns'],window['end_ns'])
        if reason:excluded[f['conn_id']]={'reason':reason,'evidence':events}
    window['evidence_hashes']={p:file_hash(base/p) for p in ['raw/capture-context.json','raw/netlog.json']}
    return window,excluded
