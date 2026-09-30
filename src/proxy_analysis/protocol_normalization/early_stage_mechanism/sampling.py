import numpy as np
import pandas as pd
from .common import *
from ..targeted_diagnostics.core import PAIR, event_runs

def sample():
    z=load('connection-load-table')
    q=z[z.pre_total_runs.notna()].groupby(PAIR,as_index=False).agg(batch=('batch','first'),protocol=('protocol','first'),
        item_id=('item_id','first'),content_group=('content_group','first'),partition=('partition','first'),pre_total=('pre','sum'),difference=('run_difference','first'))
    choices=[];cells=[];bounds=[]
    for (b,p),g in q.groupby(['batch','protocol']):
        g=g.copy();lo,hi=g.pre_total.quantile([1/3,2/3]);g['load_layer']=np.where(g.pre_total<=lo,'low',np.where(g.pre_total<=hi,'mid','high'))
        tail=float(abs(g.loc[g.difference!=0,'difference']).quantile(.9)) if (g.difference!=0).any() else None
        bounds.append(dict(batch=b,protocol=p,lower=float(lo),upper=float(hi),ss_nonzero_abs_q90=tail))
        if p=='VLESS':
            g['mechanism_group']=np.where(g.difference==2,'plus2',np.where(g.difference==0,'zero','other_nonzero'));groups=['plus2','other_nonzero','zero']
        else:
            g['mechanism_group']=np.where(g.difference==0,'zero',np.where(abs(g.difference)>=tail,'nonzero_tail','not_sampled'));groups=['zero','nonzero_tail']
        for mg in groups:
            for layer in ['low','mid','high']:
                candidates=g[(g.mechanism_group==mg)&(g.load_layer==layer)].copy()
                candidates['selection_hash']=[stable(s+'|'+c) for s,c in zip(candidates.session_id,candidates.connection_id)]
                selected=[]
                if p=='VLESS':
                    for part in ['discovery','verification']:
                        selected.extend(candidates[candidates.partition==part].sort_values('selection_hash').head(1).to_dict('records'))
                else:selected=candidates.sort_values('selection_hash').head(1).to_dict('records')
                choices.extend(selected);cells.append(dict(batch=b,protocol=p,mechanism_group=mg,load_layer=layer,available=len(candidates),selected=len(selected)))
    chosen=pd.DataFrame(choices);assert len(chosen)<=72 and not chosen.duplicated(PAIR).any()
    audit=pd.read_parquet(BASE/'capture-audit.parquet')
    manifest=chosen.merge(audit[PAIR+['side','capture_path','sha256']],on=PAIR,validate='one_to_many')
    assert len(manifest)==2*len(chosen) and not manifest.duplicated(PAIR+['side']).any()
    manifest['file_bytes']=manifest.capture_path.map(lambda f:Path(f).stat().st_size)
    unique=manifest.drop_duplicates('capture_path')
    budget=dict(pairs=len(chosen),files=len(unique),bytes=int(unique.file_bytes.sum()),max_pairs=72,max_files=144,max_bytes=2**31)
    budget['within_budget']=budget['pairs']<=72 and budget['files']<=144 and budget['bytes']<=2**31
    # Hashes originate from frozen capture audit; validate before decoding, never sample adaptively.
    frozen=OUT/'parse-sample-manifest.parquet'
    if frozen.exists():
        old=pd.read_parquet(frozen);pd.testing.assert_frame_equal(old,manifest.reset_index(drop=True))
    save('parse-sample-manifest',manifest);save('sample-cell-coverage',cells);js('sample-boundaries.json',bounds);js('budget.json',budget)
    assert manifest.groupby('content_group').partition.nunique().eq(1).all()
    if not budget['within_budget']:raise RuntimeError('Frozen sample exceeds budget; user confirmation required; no PCAP decoded')
    events=pd.read_parquet(BASE/'new-byte-events.parquet')
    oldruns=pd.read_parquet(PREVIOUS/'zero-threshold-runs.parquet')
    # All qualified rows retained in metadata; render only bounded atlas, no selective cutpoint.
    timeline=oldruns.copy()
    starts=timeline.groupby(PAIR+['side']).first_time_ns.transform('min')
    timeline['first_time_from_first_data_ns']=timeline.first_time_ns-starts
    timeline['last_time_from_first_data_ns']=timeline.last_time_ns-starts
    timeline['in_fixed_early_view']=timeline.run_index<12
    timeline_groups={key:g.sort_values('run_index') for key,g in timeline.groupby(PAIR+['side'],sort=False)}
    for key,g in events.merge(q[PAIR],on=PAIR,validate='many_to_one').groupby(PAIR+['side'],sort=False):
        rebuilt=event_runs(g);r=timeline_groups[key]
        assert [e['new_bytes'] for e in rebuilt]==r.new_bytes.tolist()
        assert [e['direction'] for e in rebuilt]==r.direction.tolist()
    save('event-timelines',timeline)
    print('E4-E5',budget,flush=True)
