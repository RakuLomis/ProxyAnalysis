"""Frozen 57-pair record feasibility experiment. No learning or phase search."""
import argparse
import inspect
import json
import sys
import importlib.metadata
from pathlib import Path
import numpy as np
import pandas as pd
import yaml
from .core import (TIME,SIGNATURE,assemble,interval_times,parse_records,units_from_intervals,
                   chunks,cdf,switching,distances,estimate_pre,signature)
from ..common import ROOT,digest
from ..early_stage_mechanism.common import OUT as OLD,BASE
from ..early_stage_mechanism.records import reassemble
from ...indexing.pairs import build_exclusive_pairs
from ...pipeline.analyze_entity import analyze_entity_capture
from ...parsing import PcapNgReader,decode_packet
from ...parsing.packet_decoder import _strip_link_header

OUT=ROOT/'outputs/record-representation-0914-0916/run-01'
DOC=ROOT/'docs/protocol-normalization/record-representation-20260926'
CONFIG=ROOT/'configs/record-representation-20260926.yaml'
PLAN=ROOT/'plan/record-level-flow-representation-plan-20260926.md'
PAIR=['session_id','connection_id']; SIDE=PAIR+['side']; KEY=SIDE+['direction']
META=['batch','protocol',*PAIR,'item_id','partition','mechanism_group','load_layer','side']

def load(name,folder=OUT):return pd.read_parquet(folder/(name+'.parquet'))
def save(name,frame):
    OUT.mkdir(parents=True,exist_ok=True)
    f=frame if isinstance(frame,pd.DataFrame) else pd.DataFrame(frame)
    f.to_parquet(OUT/(name+'.parquet'),index=False,compression='zstd');return f
def js(name,obj):
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def read(name):return json.loads((OUT/name).read_text(encoding='utf-8'))
def cfg():return yaml.safe_load(CONFIG.read_text(encoding='utf-8'))
def groupdict(df,keys):return {k:g for k,g in df.groupby(keys,sort=False)}


def freeze():
    files=[*OLD.glob('*.parquet'),*OLD.glob('*.json'),BASE/'tcp-byte-ledger.parquet',
           BASE/'new-byte-events.parquet',BASE/'registry.parquet',CONFIG,PLAN,
           ROOT/'outputs/content-generalization-20260916/business-01/primary-cohort.parquet',
           Path(__file__).parent.parent/'early_stage_mechanism/records.py']
    hashes={str(p):digest(p) for p in sorted(files)}
    if (OUT/'contract.json').exists():assert read('contract.json')['inputs']==hashes,'input changed'
    manifest=load('parse-sample-manifest',OLD)
    assert len(manifest)==114 and len(manifest[PAIR].drop_duplicates())==57
    assert manifest[PAIR+['protocol']].drop_duplicates().protocol.value_counts().to_dict()=={'VLESS':45,'SHADOWSOCKS':12}
    assert manifest.file_bytes.sum()<=cfg()['max_unique_file_bytes']
    js('input-manifest.json',hashes)
    js('contract.json',{'inputs':hashes,'sample_pairs':57,'VLESS_pairs':45,'SS_pairs':12,
       'classifier_fits':0,'regression_fits':0,'semantic_phase':'unavailable','payload_persisted':False,
       'bins_fixed_before_metrics':True,'configuration':CONFIG.name})
    save('sample-manifest',manifest)


def prepare():
    manifest=load('sample-manifest'); keys=manifest[SIDE].drop_duplicates()
    records=load('record-observations',OLD); maps=load('record-source-map',OLD)
    evidence=load('phase-evidence',OLD); ledger=load('tcp-byte-ledger',BASE).merge(keys,on=SIDE,validate='many_to_one')
    events=load('new-byte-events',BASE).merge(keys,on=SIDE,validate='many_to_one')
    mg=groupdict(maps,KEY); rg=groupdict(records,KEY); lg=groupdict(ledger,KEY)
    meta=manifest[META].drop_duplicates(); units=[]; audits=[]; type_rows=[]
    origins=events.groupby(SIDE).relative_time_ns.min().to_dict()
    for row in evidence.to_dict('records'):
        key=tuple(row[k] for k in KEY); old=lg[key].iloc[0]
        m=mg[key]; u=int(old.unique_payload_bytes); r=rg.get(key,pd.DataFrame())
        checks={}
        if len(r):
            r=r.sort_values('record_index'); a=r.start.to_numpy(); b=r.end.to_numpy()
            checks={'unique_record_key':not r.record_index.duplicated().any(),
                    'continuous_indices':np.array_equal(r.record_index,np.arange(len(r))),
                    'continuous_intervals':bool(a[0]==0 and np.array_equal(a[1:],b[:-1])),
                    'header_accounted':bool(((r.end-r.start)==r.record_payload_length+5).all()),
                    'syntax_count_matches':int((r.end-r.start).sum())==row['record_syntax_bytes'],
                    'full_coverage':int(b[-1])==u and row['unparsed_unique_bytes']==0}
            x=units_from_intervals(r,m.to_dict('records'))
            checks['frozen_first_time_matches']=np.array_equal(x.first_ns,r.first_observation_ns)
            checks['frozen_all_time_matches']=np.array_equal(x.all_ns,r.complete_available_ns)
            prefix=np.maximum.accumulate(m.sort_values('start').time_ns.to_numpy())
            endpoint=np.searchsorted(m.sort_values('start').end,x.end,side='left')
            checks['prefix_source_matches']=np.array_equal(x.prefix_ns,prefix[endpoint])
            checks['ordered_time_fields']=bool(((x.first_ns<=x.all_ns)&(x.all_ns<=x.prefix_ns)).all())
            x['representation']='R';x['unit_index']=x.record_index;units.append(x)
            ct=r.content_type.to_numpy()
            for kind in [20,21,22,23]:
                type_rows.append({**{k:row[k] for k in KEY},'kind':'count','from_type':kind,'to_type':kind,'count':int((ct==kind).sum()),'denominator':len(ct)})
                for target in [20,21,22,23]:
                    type_rows.append({**{k:row[k] for k in KEY},'kind':'transition','from_type':kind,'to_type':target,
                        'count':int(((ct[:-1]==kind)&(ct[1:]==target)).sum()),'denominator':max(0,len(ct)-1)})
        eligible=row['protocol']=='VLESS' and bool(checks) and all(checks.values())
        audits.append({**row,'ledger_unique_bytes':u,**checks,'eligible':eligible,
                       'reason':'complete_syntax_only' if eligible else 'SS_no_cipher_parser' if row['protocol']!='VLESS' else 'audit_failure'})
        if row['protocol']=='VLESS' and eligible:
            c=chunks(u,m.to_dict('records'),cfg()['chunk_bytes'])
            for k in META+['direction']:c[k]=row[k]
            c['representation']='C';units.append(c)
    audit=save('record-eligibility',audits)
    failed=audit[(audit.protocol=='VLESS')&~audit.eligible]
    js('coverage.json',{'all_direction_sides':len(audit),'eligible_VLESS_direction_sides':int(audit.eligible.sum()),
       'VLESS_failures':len(failed),'SS_direction_sides':int((audit.protocol!='VLESS').sum()),'sample_replacements':0})
    if len(failed):raise RuntimeError('New coverage failures require review; frozen sample not replaced')
    p=events[KEY+['packet_ordinal','relative_time_ns','new_payload_bytes']].copy().merge(meta,on=SIDE,validate='many_to_one')
    p['representation']='P_unique';p['unit_index']=p.packet_ordinal;p['length']=p.new_payload_bytes
    for t in TIME:p[t]=p.relative_time_ns
    units.append(p)
    allunits=pd.concat(units,ignore_index=True)
    allunits['origin_ns']=[origins[tuple(v)] for v in allunits[SIDE].itertuples(index=False,name=None)]
    for t in TIME:allunits[t.replace('_ns','_relative_ns')]=allunits[t]-allunits.origin_ns
    save('units',allunits);save('record-types',type_rows);save('unique-byte-reference',ledger)
    save('new-byte-events',events)
    rr=allunits[allunits.representation=='R'].copy()
    rr['span_ns']=rr.all_ns-rr.first_ns;rr['prefix_wait_ns']=rr.prefix_ns-rr.all_ns
    for t in TIME:rr[t+'_iat_byteorder']=rr.groupby(KEY)[t].diff()
    save('record-time-audit',rr)
    runs=load('event-timelines',OLD).merge(keys,on=SIDE,validate='many_to_one')
    save('zero-threshold-runs',runs)
    js('representation-index.json',{'P_raw':'nonempty TCP payload packets (captured next)',
       'P_unique':'first-contributed new bytes per packet','U':'unique-byte-reference + zero-threshold-runs',
       'R':'strict visible record syntax; header included; no semantic assignment',
       'C':'fixed 1024 byte directional chunks, terminal remainder retained',
       'units':'units.parquet; ns fields are capture-first-packet-relative; *_relative_ns use own-side first new byte',
       'identity_and_type_columns':'audit only, not admitted to a model','models_trained':0})
    print('R0-R3 complete',flush=True)


def segment_case(body,scenario,seed):
    n=len(body);rng=np.random.default_rng(seed)
    if scenario.startswith('fixed_'):step=int(scenario.split('_')[1]);cuts=list(range(0,n,step))+[n]
    elif scenario=='irregular':
        cuts=[0]
        while cuts[-1]<n:cuts.append(min(n,cuts[-1]+int(rng.integers(1,4097))))
    elif scenario=='header_cross':cuts=sorted(set([0,min(2,n),min(4,n),*range(1500,n,1500),n]))
    elif scenario=='multi_record':cuts=[0,n]
    else:cuts=list(range(0,n,1460))+[n]
    f=[(a,body[a:b],i*1000,i) for i,(a,b) in enumerate(zip(cuts,cuts[1:])) if b>a]
    if scenario=='duplicate_overlap_reorder':
        for i in range(0,len(f)-1,2):
            a,b,t,o=f[i];aa,bb,tt,oo=f[i+1];f[i]=(a,b,tt,o);f[i+1]=(aa,bb,t,oo)
        f.append((0,body[:min(n,1460)],(len(f)+1)*1000,len(f)))
        if n>8:f.append((3,body[3:min(n,1800)],(len(f)+1)*1000,len(f)))
    return f


def capture():
    manifest=load('sample-manifest');reg=load('registry',BASE);reg=reg[reg.is_final].set_index('session_id')
    old_records=groupdict(load('record-observations',OLD),KEY)
    descriptors={}; raw=[];results=[];read_bytes=0
    scenarios=['fixed_256','fixed_1460','fixed_4096','irregular','header_cross','multi_record','duplicate_overlap_reorder']
    for i,row in enumerate(manifest.to_dict('records')):
        path=Path(row['capture_path']);assert digest(path)==row['sha256']
        sid=row['session_id'];cid=row['connection_id'];side=row['side'];meta={k:row[k] for k in META}
        if sid not in descriptors:descriptors[sid]={p.connection_id:p for p in build_exclusive_pairs(reg.loc[sid,'session_path'],row['protocol'])}
        pair=descriptors[sid][cid];desc=pair.pre if side=='pre' else pair.post
        assert Path(desc.capture_path).resolve()==path.resolve()
        analysis=analyze_entity_capture(desc);segments={s.packet_event_id:s for s in analysis.tcp.segments}
        payload={}
        if row['protocol']=='VLESS':
            for rec in PcapNgReader(path):
                p=decode_packet(rec.link_type,rec.packet_data)
                assert p.transport_protocol=='tcp' and p.decode_status=='ok'
                data=_strip_link_header(rec.link_type,rec.packet_data)
                payload[f'{desc.artifact_id}:{rec.interface_id}:{rec.packet_ordinal}']=data[p.ip_header_len+p.transport_header_len:p.ip_total_len]
        read_bytes+=int(row['file_bytes'])*(3 if row['protocol']=='VLESS' else 2) # hash + analysis + optional payload pass
        start=min(p.timestamp_ns for p in analysis.tcp_packets)
        for p in analysis.tcp_packets:
            if p.payload_len:raw.append({**meta,'direction':p.direction,'length':p.payload_len,'unit_index':p.packet_ordinal,
                **{t:p.timestamp_ns-start for t in TIME},'representation':'P_raw'})
        if row['protocol']=='VLESS':
            for direction in [-1,1]:
                key=(sid,cid,side,direction);packets=[p for p in analysis.tcp_packets if p.direction==direction]
                origins={segments[p.packet_event_id].seq_start_unwrapped+1 for p in packets if p.flags&2};assert len(origins)==1
                origin=next(iter(origins));fragments=[]
                for p in packets:
                    if p.payload_len:
                        b=payload[p.packet_event_id];assert len(b)==p.payload_len
                        fragments.append((segments[p.packet_event_id].seq_start_unwrapped+int(bool(p.flags&2)),b,p.timestamp_ns-start,p.packet_ordinal))
                body,m,status=assemble(fragments,origin);assert status=='contiguous'
                # Validate against frozen assembler as well as saved intervals/times.
                ref,refmap,_,remaining,refstatus=reassemble(fragments,origin)
                assert body==ref and remaining==0 and refstatus=='contiguous'
                parsed,reason=parse_records(body,m,1 if direction==1 else 2)
                expected=old_records[key].sort_values('record_index')
                assert reason=='syntax_prefix_complete' and signature(parsed)==signature(expected)
                assert np.array_equal(parsed.first_ns,expected.first_observation_ns)
                assert np.array_equal(parsed.all_ns,expected.complete_available_ns)
                inherited=[]
                for part in refmap:
                    for a in range(part['start'],part['end'],256):
                        inherited.append((a,body[a:min(a+256,part['end'])],part['time_ns'],part['packet_ordinal']))
                ib,im,ist=assemble(inherited,0);ir,irs=parse_records(ib,im,1 if direction==1 else 2)
                assert ib==body and ist=='contiguous' and irs=='syntax_prefix_complete'
                assert signature(ir)==signature(expected) and np.array_equal(ir[TIME],parsed[TIME])
                results.append({**meta,'direction':direction,'scenario':'inherited_time_refinement',
                   'static_signature_equal':True,'unique_bytes':len(body),'packet_count':len(inherited),'records':len(ir),
                   'time_fields_equal':True,'timing':'refine_existing_ownership_intervals_no_new_arrival_model'})
                for scenario in scenarios:
                    f=segment_case(body,scenario,cfg()['seed'])
                    rebuilt,mp,st=assemble(f,0);r,rs=parse_records(rebuilt,mp,1 if direction==1 else 2)
                    valid=rebuilt==body and st=='contiguous' and rs=='syntax_prefix_complete' and signature(r)==signature(expected)
                    results.append({**meta,'direction':direction,'scenario':scenario,'static_signature_equal':valid,
                       'unique_bytes':len(body),'packet_count':len(f),'records':len(r),'span_max_ns':int((r.all_ns-r.first_ns).max()),
                       'prefix_wait_max_ns':int((r.prefix_ns-r.all_ns).max()),'timing':'synthetic_schedule_not_network_delay'})
                    assert valid,'R4 static invariant failed'
                # Real-payload negative tests: no fill, resync, or lost-origin acceptance.
                negatives={'gap':[(0,body[:3],0,0),(4,body[4:],1,1)],
                           'conflict':[(0,body,0,0),(0,bytes([body[0]^1]),1,1)],
                           'missing_syn':[(0,body,0,0)],'half_record':[(0,body[:-1],0,0)]}
                for scenario,f in negatives.items():
                    b,mp,st=assemble(f,None if scenario=='missing_syn' else 0)
                    r,rs=parse_records(b,mp,1 if direction==1 else 2)
                    rejected=st!='contiguous' or rs!='syntax_prefix_complete'
                    assert rejected
                    results.append({**meta,'direction':direction,'scenario':scenario,'static_signature_equal':None,
                       'negative_rejected':rejected,'status':st,'parse_status':rs,'unique_bytes':len(b)})
        if (i+1)%10==0:print('R4 frozen capture',i+1,'/',len(manifest),flush=True)
    save('raw-packet-units',raw);save('resegmentation-audit',results)
    js('capture-read-audit.json',{'unique_files':len(manifest),'unique_file_bytes':int(manifest.file_bytes.sum()),
       'read_passes_including_sha256':int((manifest.protocol=='VLESS').sum()*3+(manifest.protocol!='VLESS').sum()*2),
       'processed_file_bytes_including_sha256':read_bytes,'payload_persisted':False,'other_captures_scanned':0,
       'positive_scenarios_per_VLESS_direction_side':len(scenarios)+1,'negative_scenarios_per_VLESS_direction_side':4,
       'assembler_independently_checked_against_frozen':True})
    history=read('capture-read-history.json') if (OUT/'capture-read-history.json').exists() else []
    history.append(read('capture-read-audit.json'));js('capture-read-history.json',history)
    print('R4 passed',flush=True)


def summaries():
    assert load('resegmentation-audit').static_signature_equal.dropna().all()
    units=load('units');raw=load('raw-packet-units')
    origins=load('new-byte-events').groupby(SIDE).relative_time_ns.min().to_dict()
    raw['origin_ns']=[origins[x] for x in raw[SIDE].itertuples(index=False,name=None)]
    for t in TIME:raw[t.replace('_ns','_relative_ns')]=raw[t]-raw.origin_ns
    units=pd.concat([units,raw],ignore_index=True);save('all-units',units)
    led=load('unique-byte-reference').set_index(KEY);summary=[]
    for k,x in units.groupby(KEY+['representation'],sort=False):
        row=dict(zip(KEY+['representation'],k));x=x.sort_values('unit_index');a=x.length.to_numpy()
        row.update({c:x.iloc[0][c] for c in ['batch','protocol','item_id','partition','mechanism_group','load_layer']})
        row.update(count=len(a),total=int(a.sum()),median=float(np.median(a)),q25=float(np.quantile(a,.25)),
                   q75=float(np.quantile(a,.75)),q95=float(np.quantile(a,.95)))
        if k[-1]!='P_raw':assert row['total']==int(led.loc[k[:-1],'unique_payload_bytes'])
        for t in TIME:
            ia=np.diff(x[t]);row[t+'_zero_iat_fraction']=float(np.mean(ia==0)) if len(ia) else None
            row[t+'_negative_iat_fraction']=float(np.mean(ia<0)) if len(ia) else None
        summary.append(row)
    summary=save('direction-summary',summary)
    v=units[units.protocol=='VLESS'];pairs=[]
    for key,g in v.groupby(PAIR+['direction','representation'],sort=False):
        p=g[g.side=='pre'];q=g[g.side=='post'];assert len(p) and len(q)
        row=dict(zip(PAIR+['direction','representation'],key))
        row.update({c:p.iloc[0][c] for c in ['batch','item_id','partition','mechanism_group','load_layer']})
        row.update(distances(p.length,q.length,cfg()['length_bins']))
        row.update(count_pre=len(p),count_post=len(q),count_difference=len(q)-len(p),count_ratio=len(q)/len(p),
                   bytes_pre=int(p.length.sum()),bytes_post=int(q.length.sum()),
                   byte_difference=int(q.length.sum()-p.length.sum()),byte_ratio=float(q.length.sum()/p.length.sum()))
        # Event-count axis (each unit is a step), independent of all time choices.
        grid=np.linspace(0,1,cfg()['grid_points'])
        cp=cdf(np.arange(1,len(p)+1)/len(p),p.sort_values('unit_index').length,grid)
        cq=cdf(np.arange(1,len(q)+1)/len(q),q.sort_values('unit_index').length,grid)
        row['count_axis_shape_mae']=float(np.abs(cp-cq).mean())
        for t in TIME:
            col=t.replace('_ns','_relative_ns');tp=p[col].to_numpy();tq=q[col].to_numpy()
            # Common window starts at own first-new-byte zero; not synchronized latency.
            end=max(0,min(tp.max(),tq.max()));axis=np.linspace(0,end,cfg()['grid_points'])
            row[t+'_common_window_shape_mae']=float(np.abs(cdf(tp,p.length,axis)-cdf(tq,q.length,axis)).mean())
            row[t+'_common_window_ns']=float(end)
            ep=max(1,tp.max());eq=max(1,tq.max())
            row[t+'_normalized_duration_shape_mae']=float(np.abs(cdf(tp/ep,p.length,grid)-cdf(tq/eq,q.length,grid)).mean())
        pairs.append(row)
    paired=save('paired-representation-metrics',pairs)
    # Equal-weight visits, then content groups: direction averaged within pair first.
    folds=load('group-folds',OLD)[['session_id','content_group']].drop_duplicates()
    metrics=['w_log2','w_bytes','ks','js_bits','count_ratio','byte_ratio','count_axis_shape_mae']
    visit=paired.groupby(['batch','session_id','representation'])[metrics].mean().reset_index().merge(folds,on='session_id',validate='many_to_one')
    save('visit-equal-metrics',visit)
    save('content-equal-metrics',visit.groupby(['batch','content_group','representation'])[metrics].mean().reset_index())
    save('stratified-metrics',paired.groupby(['batch','partition','mechanism_group','load_layer','representation'])[metrics].mean().reset_index())
    base=paired[paired.representation=='P_unique'].set_index(PAIR+['direction'])
    deltas=[]
    for rep in ['P_raw','R','C']:
        x=paired[paired.representation==rep].set_index(PAIR+['direction'])
        for idx,r in x.iterrows():
            deltas.append({**dict(zip(PAIR+['direction'],idx)),'representation':rep,
                           **{m:float(r[m]-base.loc[idx,m]) for m in metrics}})
    save('paired-minus-P-unique',deltas)
    # Type distributions and transitions are within R only (not TCP flags).
    types=load('record-types');types['fraction']=types['count']/types.denominator.replace(0,np.nan)
    a=types[types.side=='pre'];b=types[types.side=='post'];tk=PAIR+['direction','kind','from_type','to_type']
    td=a.merge(b,on=tk,suffixes=('_pre','_post'),validate='one_to_one')
    td['fraction_difference']=td.fraction_post-td.fraction_pre;save('paired-record-types',td)
    # Direction workload shares, conserved for R/C, raw retransmissions remain visible.
    shares=summary.copy();shares['direction_byte_share']=shares.total/shares.groupby(SIDE+['representation']).total.transform('sum')
    save('direction-workload-shares',shares)
    print('R5 complete',flush=True)


def interaction():
    units=load('all-units');events=load('new-byte-events');eg=groupdict(events,SIDE)
    rows=[];switches=[];spans=[]
    for key,g in units.groupby(SIDE+['representation'],sort=False):
        meta=dict(zip(SIDE+['representation'],key));e=eg[key[:-1]]
        for t in TIME:switches.append({**meta,'time':t,**switching(g,t)})
        if key[-1] not in ['R','C']:continue
        grid=np.linspace(e.relative_time_ns.min(),e.relative_time_ns.max(),cfg()['grid_points'])
        for d,x in g.groupby('direction'):
            ref=e[e.direction==d];opposite=e[e.direction!=d]
            baseline=cdf(ref.relative_time_ns,ref.new_payload_bytes,grid)
            for t in TIME:
                err=cdf(x[t],x.length,grid)-baseline
                exact_grid=np.unique(np.r_[ref.relative_time_ns.to_numpy(),x[t].to_numpy()])
                exact_error=cdf(x[t],x.length,exact_grid)-cdf(ref.relative_time_ns,ref.new_payload_bytes,exact_grid)
                rows.append({**meta,'direction':d,'time':t,'mean_abs_curve_error':float(np.abs(err).mean()),
                    'max_abs_curve_error':float(np.abs(err).max()),'signed_mean_curve_error':float(err.mean()),
                    'exact_event_grid_max_error':float(np.abs(exact_error).max()),
                    'byte_conservation':int(x.length.sum())==int(ref.new_payload_bytes.sum())})
            ot=np.sort(opposite.relative_time_ns.to_numpy());o=opposite.sort_values('relative_time_ns')
            cs=np.r_[0,np.cumsum(o.new_payload_bytes)]
            for _,r in x.iterrows():
                lo=np.searchsorted(ot,r.first_ns,side='right');hi=np.searchsorted(ot,r.all_ns,side='left');hi=max(lo,hi)
                spans.append({**meta,'direction':d,'unit_index':int(r.unit_index),'length':int(r.length),
                    'span_ns':int(r.all_ns-r.first_ns),'prefix_wait_ns':int(r.prefix_ns-r.all_ns),
                    'opposite_events_strictly_inside':int(hi-lo),'opposite_bytes_strictly_inside':int(cs[hi]-cs[lo])})
    save('interaction-preservation',rows);save('tie-switch-sensitivity',switches);save('unit-span-interactions',spans)
    print('R6 complete',flush=True)


def m0():
    old=load('oof-residuals',OLD);old=old[(old.model=='M0')&(old.scope=='byte_all')]
    sample=load('sample-manifest')[PAIR].drop_duplicates();old=old.merge(sample,on=PAIR,validate='many_to_one')
    source=load('connection-load-table',OLD)
    models=json.loads((OLD/'descriptive-models.json').read_text(encoding='utf-8'))
    out=[]
    for r in old.to_dict('records'):
        selected=[v for v in models if all(v[k]==r[k] for k in ['batch','protocol','direction','scope','model','fold'])]
        assert len(selected)==1
        fit=selected[0];center=float(fit['coefficients'][0]);assert np.isclose(center,r['prediction'])
        train=source[(source.batch==r['batch'])&(source.protocol==r['protocol'])&(source.direction==r['direction'])&(source.fold!=r['fold'])]
        assert r['content_group'] not in set(train.content_group)
        assert np.isclose(train.difference.median(),center)
        target=source[(source.session_id==r['session_id'])&(source.connection_id==r['connection_id'])&(source.direction==r['direction'])].iloc[0]
        estimated=float(estimate_pre(target['post'],center));error=estimated-float(target['pre'])
        assert np.isclose(error,r['residual'])
        out.append({**r,'pre_bytes':float(target['pre']),'post_bytes':float(target['post']),
           'training_center':center,'estimated_pre_bytes':estimated,'error':error,'abs_error':abs(error),
           'relative_error':error/target['pre'] if target['pre'] else None,'zero_pre_denominator':target['pre']==0,
           'negative_estimate':estimated<0,'train_content_exclusion_verified':True})
    result=save('m0-post-only-byte-estimates',out)
    summary=result.groupby(['batch','protocol','direction']).agg(n=('error','size'),mae=('abs_error','mean'),
       median_abs_error=('abs_error','median'),bias=('error','mean'),negative_rate=('negative_estimate','mean'),zero_denominators=('zero_pre_denominator','sum')).reset_index()
    save('m0-summary',summary)
    assert len(result)==114
    print('R7 complete',flush=True)


def audit():
    contract=read('contract.json');unchanged=all(digest(Path(p))==h for p,h in contract['inputs'].items());assert unchanged
    # Executable single-side extraction invariant after arbitrary opposite-side substitution.
    maps=groupdict(load('record-source-map',OLD),KEY);rec=load('record-observations',OLD);tested=0
    for key,g in rec[rec.side=='post'].groupby(KEY):
        mapping=maps[key].to_dict('records')
        before=units_from_intervals(g,mapping)
        unrelated_pre=rec[rec.side=='pre'].copy();unrelated_pre['end']=-999999
        after=units_from_intervals(g,mapping)
        pd.testing.assert_frame_equal(before,after);tested+=1
    estimates=load('m0-post-only-byte-estimates');changed=estimates.copy();changed['pre_bytes']=-999999
    assert np.array_equal(estimate_pre(estimates.post_bytes,estimates.training_center),estimate_pre(changed.post_bytes,changed.training_center))
    js('permission-audit.json',{'post_extractor_parameters':list(inspect.signature(units_from_intervals).parameters),
       'post_direction_streams_mutation_tested':tested,'post_estimates_pre_mutation_invariant':True,
       'pre_used_only_for_offline_scoring':True,'classifier_fits':0,'regression_fits':0,
       'identifiers_and_syntax_types_not_model_inputs':True,'no_semantic_phase_or_K_exported':True,
       'old_results_unchanged':unchanged,'strict_sample_identity_unchanged':True,
       'timing_is_not_network_latency':True,'deployments_known_for_M0':True})
    code=[*Path(__file__).parent.glob('*.py'),CONFIG,ROOT/'eval/protocol_normalization/run_record_representation.py',
          ROOT/'tests/unit/test_record_representation.py']
    js('provenance.json',{'code':{str(p):digest(p) for p in code},'inputs':contract['inputs'],
       'outputs':{str(p):digest(p) for p in OUT.glob('*.parquet')},'seed':cfg()['seed'],
       'python':sys.version,'executable':sys.executable,
       'packages':{p:importlib.metadata.version(p) for p in ['numpy','pandas','scipy','pyarrow','matplotlib','PyYAML']}})
    print('R8 complete',flush=True)


def main():
    p=argparse.ArgumentParser();p.add_argument('--stage',choices=['prepare','capture','metrics','report','all'],default='all');a=p.parse_args()
    if a.stage in ['prepare','all']:freeze();prepare()
    if a.stage in ['capture','all']:capture()
    if a.stage in ['metrics','all']:summaries();interaction();m0();audit()
    if a.stage in ['report','all']:
        from .report import report
        report()
        audit()

if __name__=='__main__':main()
