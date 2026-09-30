"""P5 exact packet/run accounting, cross-checked against separate cached selections."""
import argparse
from collections import defaultdict
from pathlib import Path

import numpy as np

from .paired_structure_contract import CONFIG, verify, seal, validate_complete, read
from ..paired_information.prepare import table, digest
from ..reproducibility.preflight import write_json, write_table

KEYS=('N_all','N_data','N_empty','R_all','R_data','G_R')


def counts(summary):
    raw=[summary[k] for k in ('packet_count','nonempty_packets','burst_count','fr_runs')]
    if any(not isinstance(v,int) or v<0 for v in raw): raise ValueError('Invalid integer count')
    n,d,r,f=raw
    if d>n or f>r: raise ValueError('Subsequence inequality violated')
    return dict(zip(KEYS,(n,d,n-d,r,f,r-f)))


def decompose(pre,post):
    a,b=counts(pre),counts(post)
    delta={k:b[k]-a[k] for k in KEYS}
    if delta['N_all']!=delta['N_data']+delta['N_empty'] or delta['R_all']!=delta['R_data']+delta['G_R']:
        raise ValueError('Additivity failed')
    return a,b,delta


def dispersion(values):
    x=np.asarray(values,dtype=float); m=float(np.median(x))
    return {'mean':float(x.mean()),'median':m,'mad':float(np.median(np.abs(x-m))),
            'iqr':float(np.quantile(x,.75)-np.quantile(x,.25)),
            'positive':int(sum(x>0)),'zero':int(sum(x==0)),'negative':int(sum(x<0))}


def grouped(rows,keys):
    groups=defaultdict(list)
    for r in rows: groups[tuple(r[k] for k in keys)].append(r)
    return sorted(groups.items())


def run(config=CONFIG):
    cfg,source,legacy,root=verify(config); out=root/'p5-counts'
    if out.exists(): validate_complete(out); return
    summaries=table(source/'side-summaries.parquet')
    lookup={(r['session_id'],r['selection']):r for r in summaries}
    capture=defaultdict(list)
    for r in table(source/'capture-audit.parquet'): capture[(r['session_id'],r['side'])].append(r)
    manifest=read(root/'contract/manifest.json'); result=[]; checked=0
    for cohort,ids in [('240',manifest['primary_ids']),('299',manifest['conservative_ids'])]:
        for sid in ids:
            row=lookup[sid,'observed']; nonempty=lookup[sid,'nonempty']
            cache=read(source/'sessions'/f'{sid}.json')
            if cache['errors']: raise ValueError('Cache extraction errors')
            original=next(r for r in cache['summaries'] if r['selection']=='observed')
            if original!=row: raise ValueError('Cache/summary mismatch')
            if row['pre']['entity_count']!=row['post']['entity_count']:
                raise ValueError('Side entity set size mismatch')
            for side in ('pre','post'):
                s=row[side]; t=nonempty[side]; records=capture[sid,side]
                if (s['nonempty_packets']!=t['packet_count'] or s['fr_runs']!=t['burst_count']
                    or s['fr_runs']!=t['fr_runs']): raise ValueError('Nonempty selection disagreement')
                if s['entity_count']!=len(records): raise ValueError('Entity count disagreement')
                for key in ('packet_count','nonempty_packets'):
                    if s[key]!=sum(c[key] for c in records): raise ValueError('Capture audit mismatch')
                cached=[c for c in cache['captures'] if c['side']==side]
                if cached!=records: raise ValueError('Capture/cache disagreement')
                checked+=1
            a,b,d=decompose(row['pre'],row['post'])
            meta={k:row[k] for k in ('session_id','content_id','label_id','protocol','repetition')}
            for metric in KEYS:
                result.append({**meta,'cohort':cohort,'metric':metric,'pre':a[metric],
                               'post':b[metric],'delta':d[metric]})
    content=[]
    keys=['cohort','protocol','label_id','content_id','metric']
    for key,rs in grouped(result,keys):
        content.append({**dict(zip(keys,key)), 'repetitions':len(rs),
            'pre_mean':float(np.mean([r['pre'] for r in rs])),
            'post_mean':float(np.mean([r['post'] for r in rs])),
            **dispersion([r['delta'] for r in rs])})
    summary=[]
    for level in ('all','business'):
        keys=['cohort','protocol']+(['label_id'] if level=='business' else [])
        for key,rs in grouped(content,keys):
            values={m:[r for r in rs if r['metric']==m] for m in KEYS}
            means={m:float(np.mean([r['mean'] for r in values[m]])) for m in KEYS}
            for whole,left,right in [('N_all','N_data','N_empty'),('R_all','R_data','G_R')]:
                if not np.isclose(means[whole],means[left]+means[right],atol=1e-9):
                    raise ValueError('Content-equal summary not additive')
            for metric in KEYS:
                vs=values[metric]; denom=means['N_all' if metric.startswith('N_') else 'R_all']
                total_metric='N_all' if metric.startswith('N_') else 'R_all'
                absolute=float(np.mean([abs(r['mean']) for r in values[total_metric]]))
                # Conservative descriptive cancellation flag; not a fitted threshold.
                unstable=abs(denom)<=1e-12 or abs(denom)<.1*absolute
                summary.append({**dict(zip(keys,key)),'level':level,'metric':metric,
                    'contents':len(vs),'mean_delta':means[metric],
                    'median_content_delta':float(np.median([r['median'] for r in vs])),
                    'median_MAD':float(np.median([r['mad'] for r in vs])),
                    'median_IQR':float(np.median([r['iqr'] for r in vs])),
                    'positive_contents':sum(r['median']>0 for r in vs),
                    'negative_contents':sum(r['median']<0 for r in vs),
                    'all_repetitions_positive_contents':sum(r['positive']==r['repetitions'] for r in vs),
                    'contribution_to_total':None if unstable else means[metric]/denom,
                    'undefined_reason':'zero_or_cancelling_total' if unstable else None})
    out.mkdir()
    write_table(out/'session-count-decomposition.parquet',result)
    write_table(out/'content-count-summary.parquet',content)
    write_json(out/'group-count-summary.json',summary)
    write_json(out/'validation.json',{'passed':True,'cohort_counts':{'240':240,'299':299},
        'checked_side_records':checked,'unique_sessions':len(manifest['conservative_ids']),
        'raw_pcap_parses':0,'fits':0,'scope':'entity_local_counts_aggregated_per_visit',
        'crosschecks':['nonempty_selection','capture_audit','session_cache'],
        'cancellation_ratio_threshold':.1,'code_sha256':digest(Path(__file__))})
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    for whole,parts,name in [('N_all',('N_data','N_empty'),'packets'),('R_all',('R_data','G_R'),'runs')]:
        selected=[r for r in summary if r['cohort']=='240' and r['level']=='business']
        groupkeys=sorted({(r['protocol'],r['label_id']) for r in selected})
        fig,ax=plt.subplots(figsize=(12,6)); x=np.arange(len(groupkeys))
        for j,m in enumerate((*parts,whole)):
            vals=[next(r['mean_delta'] for r in selected if (r['protocol'],r['label_id'])==k and r['metric']==m) for k in groupkeys]
            ax.bar(x+(j-1)*.25,vals,.25,label=m)
        ax.axhline(0,color='black',linewidth=.5); ax.legend()
        ax.set_xticks(x,[' / '.join(k).replace('SHADOWSOCKS','SS') for k in groupkeys],rotation=65,ha='right')
        ax.set_ylabel('Content-equal mean post - pre'); fig.tight_layout()
        fig.savefig(out/f'{name}-decomposition.png',dpi=160); plt.close(fig)
    seal(out,passed=True)
    print({'P5':'passed','rows':len(result),'content_rows':len(content)},flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--config',default=str(CONFIG));run(p.parse_args().config)
