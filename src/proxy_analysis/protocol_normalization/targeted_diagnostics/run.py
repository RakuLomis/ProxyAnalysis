"""D0-D10: consume frozen tables, write a separate descriptive experiment."""
import argparse
import json
import platform
import sys
from pathlib import Path
import xml.etree.ElementTree as ET

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from ..common import ROOT, OUT as INPUT, digest
from .core import PAIR, KEY, META, pair_ledger, reason_flags, cohorts, visits_and_items, event_runs

OUT = ROOT/'outputs/protocol-normalization-targeted-diagnostics-0914-0916/run-01'
DOC = ROOT/'docs/protocol-normalization/targeted-diagnostics-20260923'
CONFIG = ROOT/'configs/protocol-normalization-targeted-diagnostics-20260923.yaml'
PLAN = ROOT/'plan/protocol-normalization-targeted-diagnostics-plan-20260923.md'


def js(name, value):
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT/name).write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False)+'\n', encoding='utf-8')


def save(name, rows):
    frame = rows if isinstance(rows, pd.DataFrame) else pd.DataFrame(rows)
    frame.to_parquet(OUT/(name+'.parquet'), index=False, compression='zstd')
    return frame


def load(name): return pd.read_parquet(OUT/(name+'.parquet'))


def freeze():
    OUT.mkdir(parents=True, exist_ok=True)
    files = list(INPUT.glob('*.parquet')) + list(INPUT.glob('*.json'))
    legacy = ROOT/'outputs/content-generalization-20260916/business-01/primary-cohort.parquet'
    files += [legacy, CONFIG, PLAN]
    hashes = {str(f): digest(f) for f in sorted(files)}
    contract = {'version': 1, 'inputs': hashes, 'model_fits': 0, 'thresholds': [0,64,256,1024]}
    if (OUT/'contract.json').exists():
        assert json.loads((OUT/'contract.json').read_text(encoding='utf-8')) == contract, 'frozen input changed'
    js('contract.json', contract); js('input-manifest.json', hashes)
    print('D0 frozen inputs:', len(hashes), flush=True)


def evidence():
    source = 'operator_retrospective_confirmation'
    raw = {
        'SS': ('原生 SS、无 plugin、无 mux、原生 UDP、cipher 未保存',
               {'native_ss':True, 'plugin':False, 'mux':False, 'native_udp':True, 'cipher':None}),
        'VLESS': ('TCP + TLS + REALITY + Vision、无 mux',
                  {'transport':'tcp','tls_enabled':True,'reality_enabled':True,'flow':'vision','mux':False}),
        'Hy2': ('QUIC/UDP、无 Salamander、共享 carrier、启用端口范围/跳跃',
                {'transport':'quic_udp','salamander':False,'shared_carrier':True,'port_range_or_hopping':True})}
    records=[]
    for protocol,(label, fields) in raw.items():
        records.append({'protocol':protocol,'overall_status':'partially_confirmed','original_label':label,
                        'source_type':source,'confirmation_date':'2026-09-23','applicable_batches':['0914-broad','0914-repeat','0916'],
                        'scope_basis':'operator_statement_not_per_session_snapshot',
                        'fields':{k:{'value':v,'status':'confirmed' if v is not None else 'historical_evidence_insufficient',
                                     'source_type':source} for k,v in fields.items()},
                        'unknown_fields':['exact_historical_nonsecret_parameters']+(['cipher'] if protocol=='SS' else []),
                        'conflicts':[], 'conflict_check_limit':'no_historical_config_values_available_for_independent_comparison'})
    js('protocol-evidence.json', records)
    js('correction-capability.json', {'exact_observables':['qualified_TCP_unique_sequence_bytes','duplicate_bytes','fixed_definition_runs'],
       'descriptive_only':['post_minus_pre','post_over_pre','candidate_flags','run_location'],
       'unavailable':['SS_exact_cipher_chunk_overhead','VLESS_exact_TLS_REALITY_Vision_overhead','Hy2_STREAM_bytes'],
       'numeric_bounds_generated':False,'K_generated':False,'historical_snapshots_reconstructed':False})


def audit():
    ledger=pd.read_parquet(INPUT/'tcp-byte-ledger.parquet')
    paired=pair_ledger(ledger)
    assert len(ledger)==26384 and len(paired)==13192
    assert ledger.observed_unique_valid.sum()==26358
    assert set(ledger.quality)<= {'Q0','Q1'}
    save('all-pair-membership',paired[KEY+META+['S_valid','S_both','S_all4','stratum','pre','post','difference','ratio','log_ratio']])
    coverage=pd.read_parquet(INPUT/'coverage.parquet')
    save('all-route-coverage',coverage.groupby(['batch','protocol','main_route'],dropna=False).agg(
        visits=('session_id','size'),pairs=('eligible_pair_count','sum')).reset_index())
    js('input-audit.json',{'passed':True,'direction_rows':len(ledger),'pair_directions':len(paired),
        'Q0_rows':int((~ledger.observed_unique_valid).sum()),'Q2_rows':0,'selected_visits':len(coverage),
        'model_fits':0,'keys_unique':True,'side_metadata_equal':True,'all_connections_have_four_rows':True})
    return ledger,paired


def completeness():
    ledger,paired=audit()
    v=paired[(paired.protocol=='VLESS')&(paired.main_route=='proxy')].copy()
    save('vless-cohort-membership',v[KEY+META+['S_valid','S_both','S_all4','stratum','pre','post']])
    strata=[]
    for (batch,direction),g in v.groupby(['batch','direction']):
        for status in ['both','pre_only','post_only','neither','Q0_excluded']:
            q=g[g.stratum==status]
            strata.append(dict(batch=batch,direction=direction,stratum=status,pair_directions=len(q),
                connections=len(q[PAIR].drop_duplicates()),visits=q.session_id.nunique(),items=q.item_id.nunique(),
                fraction_all=len(q)/len(g),fraction_valid=len(q)/g.S_valid.sum() if status!='Q0_excluded' else np.nan))
    save('vless-completeness-strata',strata)
    reasons=[]
    lv=ledger[(ledger.protocol=='VLESS')&(ledger.main_route=='proxy')].merge(
        v[KEY+['stratum']],on=KEY,validate='many_to_one')
    for r in lv.to_dict('records'):
        flags=reason_flags(r)
        common={k:r[k] for k in ['batch','side','direction','stratum','session_id','connection_id','item_id']}
        reasons.append({**common,'reason_combination':'+'.join(flags) if flags else 'candidate_no_failure',
                        'gap_bytes':r['final_internal_gap_bytes'] if r['observed_unique_valid'] else np.nan})
    rr=save('vless-reason-membership',reasons)
    groups=['batch','direction','side','stratum']
    save('vless-reason-combinations',rr.groupby(groups+['reason_combination'],as_index=False).agg(
        rows=('session_id','size'),gap_bytes=('gap_bytes',lambda x:x.sum(min_count=1))))
    overlaps=rr.assign(reason=rr.reason_combination.str.split('+')).explode('reason')
    save('vless-reason-overlaps',overlaps.groupby(groups+['reason'],as_index=False).agg(rows=('session_id','size')))
    allrows=cohorts(v)
    save('vless-byte-contrasts',allrows[KEY+META+['cohort','pre','post','difference','ratio','log_ratio','zero_pre','zero_post']])
    visits,items=visits_and_items(allrows)
    save('vless-visit-summary',visits);save('vless-item-summary',items)
    # Empty candidate subsets remain absent, with explicit zeros only for membership counts.
    base=visits[visits.cohort=='S_valid']
    coverage=[]
    for name in ['S_valid','S_both','S_all4']:
        sub=visits[visits.cohort==name]
        x=base.merge(sub,on=['session_id','direction'],suffixes=('_base','_subset'),how='left',validate='one_to_one')
        for r in x.to_dict('records'):
            coverage.append(dict(batch=r['batch_base'],item_id=r['item_id_base'],session_id=r['session_id'],direction=r['direction'],cohort=name,
                available=pd.notna(r['pairs_subset']),base_pairs=int(r['pairs_base']),subset_pairs=int(r['pairs_subset']) if pd.notna(r['pairs_subset']) else 0,
                pair_fraction=r['pairs_subset']/r['pairs_base'],
                pre_byte_fraction=r['pre_subset']/r['pre_base'] if r['pre_base']>0 else np.nan,
                post_byte_fraction=r['post_subset']/r['post_base'] if r['post_base']>0 else np.nan))
    save('vless-coverage',coverage)
    summary=[]
    for (batch,direction,cohort),g in items.groupby(['batch','direction','cohort']):
        summary.append(dict(batch=batch,direction=direction,cohort=cohort,items=len(g),visits=int(g.visits.sum()),
                            median_item_difference=float(g.median_difference.median()),typical_ratio=float(np.exp(g.median_log_ratio.median()))))
    save('vless-summary',summary)
    dist=[]
    for (batch,direction,cohort),g in allrows.groupby(['batch','direction','cohort']):
        r=dict(batch=batch,direction=direction,cohort=cohort,pair_directions=len(g),zero_pre=int(g.zero_pre.sum()),
               positive_fraction=float((g.difference>0).mean()),negative_fraction=float((g.difference<0).mean()),zero_fraction=float((g.difference==0).mean()))
        for col in ['difference','ratio']:
            for q in [.05,.25,.5,.75,.95]:r[f'{col}_q{int(100*q)}']=g[col].quantile(q)
        dist.append(r)
    save('vless-connection-distribution',dist)
    old=pd.read_parquet(INPUT/'visit-dedup-comparison.parquet')
    old=old[(old.protocol=='VLESS')&(old.view=='U')]
    check=base.merge(old,on=['session_id','direction'],suffixes=('_new','_old'),validate='one_to_one')
    assert len(check)==len(base)==len(old)
    for col in ['pre','post']:assert np.array_equal(check[col+'_new'],check[col+'_old'])
    js('vless-validation.json',{'passed':True,'old_visit_direction_checks':len(check),'strata_partition':True,'Q0_excluded_not_zero_filled':True})
    print('D3-D5 complete:',len(check),'old visit directions reproduced',flush=True)


def runs():
    ledger,paired=audit()
    eligible=paired.groupby(PAIR).S_valid.all()
    good=set(eligible[eligible].index)
    old=pd.read_parquet(INPUT/'byte-direction-runs.parquet')
    old=old[(old.main_route=='proxy')&pd.Series(list(zip(old.session_id,old.connection_id)),index=old.index).isin(good)].copy()
    assert not old.duplicated(PAIR+['side','threshold_bytes']).any()
    assert set(old.threshold_bytes)=={0,64,256,1024}
    assert old.groupby(PAIR).size().eq(8).all()
    base=old[old.threshold_bytes==0]
    events=pd.read_parquet(INPUT/'new-byte-events.parquet')
    event_groups={k:g for k,g in events.groupby(PAIR+['side'],sort=False)}
    expanded=[];endpoints=[]
    for r in base.to_dict('records'):
        key=(r['session_id'],r['connection_id'],r['side'])
        e=event_groups.get(key,events.iloc[:0])
        rows=event_runs(e)
        assert [x['direction'] for x in rows]==list(r['directions'])
        assert [x['new_bytes'] for x in rows]==list(r['new_bytes'])
        assert len(rows)==r['run_count'] and sum(x['new_bytes'] for x in rows)==r['retained_bytes']
        meta={k:r[k] for k in PAIR+META+['side']}
        expanded.extend({**meta,**x} for x in rows)
        endpoints.append({**meta,'run_count':len(rows),'first_direction':rows[0]['direction'] if rows else 0,
                          'last_direction':rows[-1]['direction'] if rows else 0})
    expanded=save('zero-threshold-runs',expanded)
    ends=save('run-endpoints',endpoints)
    # Dense grid includes zero-count positions and directions on both sides.
    cells=expanded.groupby(PAIR+['side','direction','position'],as_index=False).agg(count=('run_index','size'),bytes=('new_bytes','sum'))
    grid=base[PAIR+META+['side']].merge(pd.MultiIndex.from_product([[-1,1],['first','interior','last','singleton']],names=['direction','position']).to_frame(index=False),how='cross')
    grid=grid.merge(cells,on=PAIR+['side','direction','position'],how='left',validate='one_to_one').fillna({'count':0,'bytes':0})
    a=grid[grid.side=='pre'];b=grid[grid.side=='post']
    loc=a.merge(b,on=PAIR+['direction','position'],suffixes=('_pre','_post'),validate='one_to_one')
    for col in META:loc[col]=loc[col+'_pre']
    loc['count_difference']=loc.count_post-loc.count_pre
    loc['byte_difference']=loc.bytes_post-loc.bytes_pre
    loc=save('run-localization',loc[PAIR+META+['direction','position','count_pre','count_post','bytes_pre','bytes_post','count_difference','byte_difference']])
    totals=base[base.side=='pre'].merge(base[base.side=='post'],on=PAIR,suffixes=('_pre','_post'),validate='one_to_one')
    sums=loc.groupby(PAIR).count_difference.sum()
    for r in totals.to_dict('records'):
        assert sums.loc[(r['session_id'],r['connection_id'])]==r['run_count_post']-r['run_count_pre']
    pairrows=[]
    for r in totals.to_dict('records'):
        pairrows.append({**{k:r[k] for k in PAIR},**{k:r[k+'_pre'] for k in META},
                         'pre_runs':r['run_count_pre'],'post_runs':r['run_count_post'],
                         'difference':r['run_count_post']-r['run_count_pre']})
    pp=save('run-pair-differences',pairrows);pp['absolute_difference']=abs(pp.difference)
    concentration=[]
    for (batch,protocol),g in pp.groupby(['batch','protocol']):
        values=np.sort(g.absolute_difference.to_numpy())[::-1]; total=values.sum()
        byvisit=g.groupby('session_id').absolute_difference.sum()
        byitem=g.groupby('item_id').absolute_difference.sum()
        concentration.append(dict(batch=batch,protocol=protocol,pairs=len(g),visits=len(byvisit),items=len(byitem),
            mean_signed_difference=g.difference.mean(),median_signed_difference=g.difference.median(),sum_absolute_difference=int(total),
            nonzero_pair_fraction=float((g.difference!=0).mean()),nonzero_visit_fraction=float((byvisit>0).mean()),nonzero_item_fraction=float((byitem>0).mean()),
            top10pct_pairs_absolute_share=float(values[:max(1,int(np.ceil(.1*len(g))))].sum()/total) if total else np.nan))
    save('run-concentration',concentration)
    save('run-location-summary',loc.groupby(['batch','protocol','direction','position'],as_index=False).agg(
        count_pre=('count_pre','sum'),count_post=('count_post','sum'),difference=('count_difference','sum'),
        absolute_cell_difference=('count_difference',lambda x:abs(x).sum()),bytes_pre=('bytes_pre','sum'),bytes_post=('bytes_post','sum')))
    sizes=expanded.groupby(['batch','protocol','side','direction','position','size_bin'],as_index=False).agg(
        runs=('run_index','size'),bytes=('new_bytes','sum'),median_bytes=('new_bytes','median'),p95_bytes=('new_bytes',lambda x:x.quantile(.95)))
    save('run-size-summary',sizes)
    size_counts=expanded.groupby(['batch','protocol','direction','position','size_bin','side']).size().unstack('side',fill_value=0).reset_index()
    size_counts['difference']=size_counts['post']-size_counts['pre']
    save('run-size-count-differences',size_counts)
    location_profile=expanded.groupby(['batch','protocol','side','direction','position'],as_index=False).agg(
        runs=('run_index','size'),median_normalized_position=('normalized_run_position','median'),
        median_first_time_ns=('first_time_ns','median'),median_last_time_ns=('last_time_ns','median'),
        median_cumulative_byte_start=('cumulative_byte_start','median'))
    save('run-position-profile',location_profile)
    endpoint_pairs=ends[ends.side=='pre'].merge(ends[ends.side=='post'],on=PAIR,suffixes=('_pre','_post'),validate='one_to_one')
    save('run-endpoint-combinations',endpoint_pairs.groupby(['batch_pre','protocol_pre','first_direction_pre','first_direction_post','last_direction_pre','last_direction_post'],as_index=False).size())
    fixed=[]
    for (batch,protocol,t),g in old.groupby(['batch','protocol','threshold_bytes']):
        a=g[g.side=='pre'];b=g[g.side=='post'];p=a.merge(b,on=PAIR,suffixes=('_pre','_post'),validate='one_to_one')
        r=dict(batch=batch,protocol=protocol,threshold_bytes=int(t),pairs=len(p),visits=a.session_id.nunique(),items=a.item_id.nunique(),
               median_difference=float((p.run_count_post-p.run_count_pre).median()),median_absolute_difference=float(abs(p.run_count_post-p.run_count_pre).median()))
        for side,q in [('pre',a),('post',b)]:
            r[side+'_zero_fraction']=float(q.zero_run.mean());r[side+'_single_fraction']=float(q.single_run.mean())
            r[side+'_retained_fraction']=float(q.retained_fraction.median())
            for direction,prefix in [(1,'up'),(-1,'down')]:
                r[side+'_'+prefix+'_runs_median']=float(q.directions.apply(lambda arr:sum(x==direction for x in arr)).median())
                r[side+'_'+prefix+'_retained_fraction']=float(q[prefix+'_retained_fraction'].median())
        fixed.append(r)
    save('fixed-threshold-summary',fixed)
    qual=[]
    for (batch,protocol),g in paired[paired.main_route=='proxy'].groupby(['batch','protocol']):
        sub=pp[(pp.batch==batch)&(pp.protocol==protocol)]
        qual.append(dict(batch=batch,protocol=protocol,valid_pair_directions=int(g.S_valid.sum()),
                         connections_with_any_valid_direction=len(g[g.S_valid][PAIR].drop_duplicates()),
                         run_eligible_pairs=len(sub),run_eligible_visits=sub.session_id.nunique()))
    save('run-qualification',qual)
    js('run-validation.json',{'passed':True,'reconstructed_side_tables':len(base),'expanded_runs':len(expanded),
                             'pairs':len(pp),'byte_and_count_conserved':True,'cell_decomposition_exact':True,'thresholds':[0,64,256,1024]})
    print('D6-D8 complete:',len(expanded),'runs;',len(pp),'pairs',flush=True)


def mdtable(frame):
    def fmt(v):
        if pd.isna(v):return 'NA'
        if isinstance(v,(float,np.floating)):return f'{v:.5g}'
        return str(v)
    return '\n'.join(['| '+' | '.join(frame.columns)+' |','| '+' | '.join(['---']*len(frame.columns))+' |']+
                     ['| '+' | '.join(fmt(v) for v in row)+' |' for row in frame.itertuples(index=False,name=None)])


def report():
    DOC.mkdir(parents=True,exist_ok=True);figdir=DOC/'figures';figdir.mkdir(exist_ok=True)
    strata=load('vless-completeness-strata');summary=load('vless-summary');location=load('run-location-summary')
    concentration=load('run-concentration');fixed=load('fixed-threshold-summary')
    combos=load('vless-reason-combinations');coverage=load('vless-coverage')
    cov=coverage.groupby(['batch','direction','cohort'],as_index=False).agg(
        base_visits=('session_id','size'),available_visits=('available','sum'),median_pair_fraction=('pair_fraction','median'),
        median_pre_byte_fraction=('pre_byte_fraction','median'),median_post_byte_fraction=('post_byte_fraction','median'))
    save('vless-coverage-summary',cov)
    fig,axs=plt.subplots(1,2,figsize=(12,4),layout='constrained')
    for ax,direction in zip(axs,[1,-1]):
        p=strata[strata.direction==direction].pivot(index='batch',columns='stratum',values='pair_directions')
        p[['both','pre_only','post_only','neither','Q0_excluded']].plot.bar(stacked=True,ax=ax,rot=0)
        ax.set_title('VLESS '+('upload' if direction==1 else 'download'));ax.set_ylabel('Connection-directions');ax.legend(fontsize=7)
    fig.savefig(figdir/'vless-strata.png',dpi=150);plt.close(fig)
    fig,axs=plt.subplots(2,2,figsize=(13,8),layout='constrained')
    names=['S_valid','S_both','S_valid_on_S_both_visits','S_all4','S_valid_on_S_all4_visits']
    for row,direction in enumerate([1,-1]):
        for col,metric in enumerate(['median_item_difference','typical_ratio']):
            ax=axs[row,col]
            for batch,g in summary[summary.direction==direction].groupby('batch'):
                g=g.set_index('cohort').reindex(names);ax.plot(range(len(names)),g[metric],marker='o',label=batch)
            ax.set_xticks(range(len(names)),['valid','both','valid@both','all4','valid@all4'],fontsize=8)
            ax.set_title(('Upload ' if direction==1 else 'Download ')+('item-equal byte difference' if col==0 else 'item-equal ratio'))
            ax.axhline(0 if col==0 else 1,color='gray',lw=.5);ax.legend(fontsize=8)
    fig.savefig(figdir/'vless-bytes.png',dpi=150);plt.close(fig)
    fig,axs=plt.subplots(2,3,figsize=(14,7),layout='constrained')
    for ax,((batch,protocol),g) in zip(axs.flat,location.groupby(['batch','protocol'])):
        p=g.pivot(index='position',columns='direction',values='difference').reindex(['first','interior','last','singleton'])
        p.rename(columns={-1:'download',1:'upload'}).plot.bar(ax=ax,rot=0)
        ax.set_title(batch+' '+protocol);ax.set_ylabel('Signed sum of run-count differences')
    fig.savefig(figdir/'run-location.png',dpi=150);plt.close(fig)
    rr=load('zero-threshold-runs')
    fig,axs=plt.subplots(2,3,figsize=(14,7),layout='constrained')
    for ax,((batch,protocol),g) in zip(axs.flat,rr.groupby(['batch','protocol'])):
        for (side,direction),q in g.groupby(['side','direction']):
            vals=np.sort(q.new_bytes);ax.step(vals,np.arange(1,len(vals)+1)/len(vals),where='post',label=f'{side}/{direction} n={len(vals)}')
        ax.set_xscale('log');ax.set_title(batch+' '+protocol);ax.set_xlabel('New bytes per run');ax.set_ylabel('Run-weighted ECDF');ax.legend(fontsize=7)
    fig.savefig(figdir/'run-byte-ecdf.png',dpi=150);plt.close(fig)
    pp=load('run-pair-differences')
    fig,axs=plt.subplots(1,2,figsize=(12,4),layout='constrained')
    for (batch,protocol),g in pp.groupby(['batch','protocol']):
        vals=np.sort(abs(g.difference))[::-1]
        if vals.sum():axs[0].plot(np.arange(1,len(vals)+1)/len(vals),np.cumsum(vals)/vals.sum(),label=batch+' '+protocol)
    axs[0].set_xlabel('Fraction of connections, largest |difference| first');axs[0].set_ylabel('Cumulative absolute difference share');axs[0].legend(fontsize=6)
    for (batch,protocol),g in fixed.groupby(['batch','protocol']):
        axs[1].plot(g.threshold_bytes,g.post_retained_fraction,marker='o',label=batch+' '+protocol)
    axs[1].set_xlabel('Fixed threshold (bytes)');axs[1].set_ylabel('Median post retained byte fraction');axs[1].legend(fontsize=6)
    fig.savefig(figdir/'concentration-thresholds.png',dpi=150);plt.close(fig)
    # Additional qualified-connection plots: no implicit matching of run ordinal across sides.
    connections=load('vless-byte-contrasts');connections=connections[connections.cohort=='S_valid']
    fig,axs=plt.subplots(1,2,figsize=(11,4),layout='constrained')
    for ax,direction in zip(axs,[1,-1]):
        for batch,g in connections[connections.direction==direction].groupby('batch'):
            ax.scatter(g.pre,g.post,s=5,alpha=.3,label=f'{batch} n={len(g)}')
        ax.set_xscale('symlog');ax.set_yscale('symlog');ax.set_xlabel('Pre unique bytes');ax.set_ylabel('Post unique bytes');ax.set_title('Upload' if direction==1 else 'Download');ax.legend(fontsize=7)
    fig.savefig(figdir/'vless-connection-scatter.png',dpi=150);plt.close(fig)
    reasons=load('vless-reason-overlaps')
    fig,axs=plt.subplots(1,2,figsize=(13,5),layout='constrained')
    for ax,direction in zip(axs,[1,-1]):
        p=reasons[(reasons.direction==direction)&(reasons.stratum!='both')].groupby(['side','reason']).rows.sum().unstack('side').fillna(0)
        p.plot.barh(ax=ax);ax.set_title('Upload' if direction==1 else 'Download');ax.set_xlabel('Overlapping direction-side reason counts (all batches)')
    fig.savefig(figdir/'vless-reasons.png',dpi=150);plt.close(fig)
    fig,axs=plt.subplots(1,2,figsize=(12,4),layout='constrained')
    for (batch,protocol),g in fixed.groupby(['batch','protocol']):
        for ax,side in zip(axs,['pre','post']):
            ax.plot(g.threshold_bytes,g[side+'_zero_fraction']+g[side+'_single_fraction'],marker='o',label=batch+' '+protocol)
            ax.set_title(side+' zero/single run fraction');ax.set_xlabel('Fixed threshold (bytes)');ax.legend(fontsize=6)
    fig.savefig(figdir/'threshold-degeneracy.png',dpi=150);plt.close(fig)
    testpath=OUT/'tests.xml'
    tests={'status':'not_run'}
    if testpath.exists():
        root=ET.parse(testpath).getroot();suites=list(root.iter('testsuite'))
        tests={k:sum(int(s.attrib.get(k,0)) for s in suites) for k in ['tests','failures','errors','skipped']}
        assert tests['failures']==tests['errors']==0
    js('tests.json',tests)
    verification=json.loads((OUT/'contract.json').read_text(encoding='utf-8'))
    assert all(digest(f)==h for f,h in verification['inputs'].items()),'old input modified'
    js('provenance.json',{'python':sys.version,'platform':platform.platform(),'old_inputs_unchanged':True,'model_fits':0,
       'code':{str(f):digest(f) for f in [*sorted(Path(__file__).parent.glob('*.py')),
              ROOT/'eval/protocol_normalization/run_targeted_diagnostics.py',ROOT/'tests/unit/test_targeted_diagnostics.py']},
       'outputs':{p.name:digest(p) for p in OUT.glob('*.parquet')}})
    text=['# 协议规范化定点诊断报告','',
        '日期：2026-09-23。只使用 0914/0916 既有 run-01 测量表；没有重读 PCAP、训练模型、生成 K 校正、改变阈值或修改旧 240 访问队列。',
        '', '## 核心结果与判断','',
        '1. 配置不确定性已收敛为有来源的部分确认，而非已恢复历史快照。SS cipher 缺口仍在；本轮不产生精确开销 K。',
        '2. VLESS 的候选不对称主要体现为 pre 上行 RST，而不是大量有效方向存在内部字节缺口。0916 上行 1,471 条有效连接方向中，1,433 条（97.42%）仅 post 为候选，且对应 pre 均有 RST；下行 1,318 条（89.60%）为双侧候选。RST 标记的来源/触发机制未定位，不能归因为丢包或转发失败。',
        '3. 0916 上行主集合典型倍率 1.4145、条目等权差值 13,471 bytes；双侧候选倍率反而为 1.9950、差值 1,843.75 bytes。后者仅 34 条连接方向、32 次访问、16 个条目。相同 32 次访问保留全部有效连接时，倍率为 1.4479、差值 14,286 bytes。说明筛选改变了连接构成，不能用子集更完整来代替主要测量。',
        '4. 0916 下行 S_both 覆盖全部 150 次访问，倍率 1.0468→1.0433，差值 47,758→44,072 bytes；S_all4 则只保留 33 条连接、32 次访问，倍率为 1.8812。方向候选与整连接候选不能混用。',
        '5. VLESS 三批次零阈值段数差中位均为 +2，约 98.7% 的连接有非零段差；SS 中位均为 0，非零连接约 7.0%、7.0%、12.1%。0916 SS 前 10% 连接贡献 92.89% 的绝对段差，VLESS 对应为 14.57%，两者在连接间的集中程度不同。',
        '6. 计数差主要落在 interior 类别，但 interior 只表示非首末段，并不证明差异遍布整个时间轴；也可能包含早期交互。VLESS 的 +2 不能解释为已经识别了两个可删除协议段。当前未建立独立阶段证据，本轮不设计固定减段校正。',
        '7. 固定阈值本身能改变比较：SS 三批次段数差中位在 0-byte 阈值为 0、64-byte 为 +2、256-byte 又为 0。故不能把更小段差视为更可靠，也不能重选阈值。',
        '', '## 1. 证据与权限','',
        '三种部署的标签已按采集者 2026-09-23 追溯确认记录。SS 原生、无 plugin/mux、原生 UDP，cipher 未保存；VLESS TCP、TLS/REALITY、Vision、无 mux；Hy2 QUIC/UDP、无 Salamander、共享 carrier、端口范围/跳跃。整体均为部分确认，因为精确历史参数/快照不全。此记录不能当作逐会话配置快照；TLS/REALITY 标签不表示两套开销相加。',
        '', '唯一 TCP 字节及固定定义方向段可测；精确协议开销仍不可给出。Hy2 不适用于本轮严格 TCP 配对分析，不将缺少结果写成没有流量。没有数值开销上下界，也不把 U 当成功业务交付；Q2 仍为 0。',
        '', '## 2. 覆盖与 VLESS 候选构成','',
        mdtable(load('all-route-coverage')), '',
        '以下主要统计只使用 main_route=proxy。方向 +1=上行、−1=下行。每个方向的配对表有 pre/post 两行；候选方向数不是完整连接数。四格外单列 Q0。', '',
        mdtable(strata), '', '![四格](figures/vless-strata.png)', '',
        '### 原因组合（互斥）','',mdtable(combos), '',
        '组合表每条方向侧记录仅属于一种组合；另存的 reason-overlaps 表允许重叠，不应相加作总数。Q0_excluded 是配对资格：其中正常的一侧仍可能为 candidate_no_failure。Q0 方向的 gap_bytes 不作为可靠缺口大小输出，避免序号歧义生成的巨大间隙被误认为丢失字节。prefix/suffix 缺失、RST 和 gap 是观测条件，不证明采集失败或某协议阶段。application_delivery_not_proven 是全局限制，没有当成解释不对称的原因。',
        '', '![原因](figures/vless-reasons.png)', '',
        '## 3. VLESS 字节差与倍率','',
        'S_valid：同方向两侧 U 均有效；S_both：再要求同方向两侧闭合连续候选；S_all4：整个连接四条方向侧记录均候选。valid_on 子集 visits 表示保留对应子集有覆盖的访问，但使用这些访问全部有效连接。后两者不替换主集合。',
        '', '每访问先求和，再按条目重复取中位差值/中位 log-ratio，最后按条目等权取中位；typical_ratio 为最终中位 log-ratio 的指数。零分母不填 1；空子集访问不填零字节。', '',
        mdtable(summary), '', '![字节对照](figures/vless-bytes.png)', '',
        '### 子集覆盖','',mdtable(cov),'',
        '覆盖比例的中位数只针对有定义的访问；available_visits 明示缺失。闭合子集的数值变化混有连接选择效应，不是协议校正，也不代表它更适合作为主队列。', '',
        '### 连接方向分布','',mdtable(load('vless-connection-distribution')),'',
        '![连接散点](figures/vless-connection-scatter.png)','',
        '## 4. 零阈值方向段定位','',mdtable(load('run-qualification')),'',
        '两侧两个方向均 U 有效才纳入段比较。从新字节事件按各侧相对时间和 packet_ordinal 重建，与旧段表逐条精确相等。没有跨侧时钟对齐，也没有按段序号建立段对应。', '',
        mdtable(location),'','![方向位置](figures/run-location.png)','',
        'difference 是该格 post 段数减 pre 段数的和，可正负抵消；absolute_cell_difference 是各连接该格差值绝对值之和。first/interior/last/singleton 互斥，分解逐连接严格守恒。first/last 不等于握手/关闭阶段。', '',
        mdtable(concentration),'','![集中度](figures/concentration-thresholds.png)','',
        '集中度分母是连接级 sum|Δrun|，不是格子级绝对差总量；前 10% 按绝对差排序取向上整数量。非零访问/条目表示其中至少一条连接有段数差，不因连接间抵消而归零。', '',
        '![段字节 ECDF](figures/run-byte-ecdf.png)','',
        'ECDF 为段加权描述，不是访问等权推断。固定字节箱与首尾方向组合分别见 run-size-summary.parquet、run-endpoint-combinations.parquet。', '',
        '## 5. 全部四阈值','',mdtable(fixed),'','![退化率](figures/threshold-degeneracy.png)','',
        '四阈值均报告；更少段差可能伴随删除大量字节或退化为零/单段，不能据此选一个更有利阈值。', '',
        '## 6. 验证与停止门','',
        '输入资格、配对唯一性、旧访问总量复现、段序列/字节重建、格子分解守恒均通过。测试：'+json.dumps(tests,ensure_ascii=False), '',
        '输入哈希复核通过，旧产物未改。结果只支持描述性定位，不新增显著性、等效、因果或分类收益结论。后续协议解析器、K 校正、阈值搜索、分类训练需另行确认。', '',
        '运行：`python eval/protocol_normalization/run_targeted_diagnostics.py all`；分阶段可用 evidence、completeness、runs、report。新数据位于 outputs/protocol-normalization-targeted-diagnostics-0914-0916/run-01。']
    (DOC/'report.md').write_text('\n'.join(text)+'\n',encoding='utf-8')
    (DOC/'next-gate.md').write_text('# 本轮停止门\n\nD0–D10 测量已完成；没有新增训练或校正。历史配置从完全未知收敛为有来源的部分确认，精确开销仍不可声称。\n\n首尾位置不是协议阶段。即使出现集中差异，也需独立实现/阶段证据才可提出校正，不直接删除固定头部或两段。先审阅 report.md；本轮在此停止。\n',encoding='utf-8')
    (DOC/'sanitized-config-guidance.md').write_text('# 未来脱敏配置建议（不是历史快照）\n\n采用明确类型白名单：schema_version、capture_time、implementation_version、protocol、cipher、transport、tls/reality/vision、mux、plugin/obfs 类型、port_hopping_enabled。缺失值为 null，不能猜默认值。\n\n禁止复制原节点对象或自由文本配置；不写 endpoint、域名、端口值/范围值、UUID、密码、密钥、原始插件参数。不将任意字典递归复制。写盘前测试禁止字段和非白名单字段均被拒绝；仅在未来采集时生成 sanitized-proxy-config-v1.json。本轮未修改采集程序，也未创建伪历史配置。\n',encoding='utf-8')
    js('stage-status.json',{'D0_D10':'complete' if tests.get('tests',0)>0 else 'measurement_complete_tests_pending',
                            'model_fits':0,'K_generated':False,'next_action':'user_review_before_new_method'})
    print('D10 report:',DOC/'report.md',flush=True)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('stage',choices=['all','evidence','completeness','runs','report'],default='all',nargs='?')
    args=parser.parse_args();freeze()
    if args.stage in ['all','evidence']:evidence()
    if args.stage in ['all','completeness']:completeness()
    if args.stage in ['all','runs']:runs()
    if args.stage in ['all','report']:report()


if __name__=='__main__':main()
