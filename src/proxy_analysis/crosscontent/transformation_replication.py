"""P4: six prespecified descriptive transformation measures; no new model/PCAP parsing."""
from collections import defaultdict
import hashlib
import json
import math
from pathlib import Path

import numpy as np

from .mechanism_contract import verify, read
from .business_features import resource_identity
from ..config import FeatureConfig
from ..features.pairwise import js_divergence
from ..paired_information.prepare import table, digest
from ..reproducibility.preflight import write_json, write_table

SCALES=('packet_count','transport_bytes','burst_count','fr_runs')
METRICS=(*SCALES,'length_js','iat_js')
LOW,HIGH=math.log(.9),math.log(1.1)


def identity(url):
    return json.dumps(resource_identity(url),ensure_ascii=False)


def values(before,after):
    result=[]
    for metric in METRICS:
        pre,post=before.get(metric),after.get(metric)
        if metric in SCALES:
            if pre is None or post is None: value=None; reason='missing_scalar'
            elif pre<=0 or post<=0: value=None; reason='nonpositive_ratio_operand'
            else: value=math.log(post/pre); reason=None
        else:
            field='length_hist' if metric=='length_js' else 'iat_hist'
            a,b=before[field],after[field]
            if len(a)!=(19 if metric=='length_js' else 23) or len(b)!=len(a):
                raise ValueError('Unexpected frozen histogram dimensions')
            if any(not np.isfinite(v) or v<0 for v in a+b): raise ValueError('Invalid histogram')
            value=js_divergence(a,b); reason='empty_distribution' if value is None else None
            pre=post=None
        result.append({'metric':metric,'pre':pre,'post':post,'delta':value,'undefined_reason':reason,
            'transform':'strict_ln_post_pre' if metric in SCALES else 'base2_js_divergence'})
    return result


def category(metric,value):
    if value is None: return 'undefined'
    if metric in SCALES: return 'below_0.9' if value<LOW else 'above_1.1' if value>HIGH else 'within_0.9_1.1'
    return 'within_0.05' if value<=.05 else 'above_0.05'


def summarize(group):
    valid=[r['delta'] for r in group if r['delta'] is not None]
    if not valid: return {'valid_repetitions':0,'undefined_repetitions':len(group),
        'median_delta':None,'mad_delta':None,'iqr_delta':None,'median_post_pre_ratio':None,
        'median_category':'undefined','repetition_band_fraction':None,'all_positive':False,'all_negative':False}
    x=np.asarray(valid); med=float(np.median(x)); metric=group[0]['metric']
    return {'valid_repetitions':len(x),'undefined_repetitions':len(group)-len(x),
        'median_delta':med,'mad_delta':float(np.median(np.abs(x-med))),
        'iqr_delta':float(np.quantile(x,.75,method='linear')-np.quantile(x,.25,method='linear')),
        'median_post_pre_ratio':math.exp(med) if metric in SCALES else None,
        'median_category':category(metric,med),
        'repetition_band_fraction':float(np.mean((x>=LOW)&(x<=HIGH))) if metric in SCALES else float(np.mean(x<=.05)),
        'all_positive':bool(np.all(x>0)),'all_negative':bool(np.all(x<0))}


def main():
    cfg,business,source,root=verify()
    old=Path('outputs/paired-information-0914/run-01')
    old_cohort=table(old/'cohort.parquet'); old_sides=table(old/'side-summaries.parquet')
    old_lookup={r['session_id']:r for r in old_cohort}
    if len(old_cohort)!=140 or len({r['target_url'] for r in old_cohort})!=14: raise ValueError('0914 scope changed')
    fc=FeatureConfig.load(business['feature_config'])
    extract_hash=digest(Path('src/proxy_analysis/reproducibility/extract.py'))
    paths=[Path(__file__),Path(business['feature_config']),Path(business['metric_spec']),
        old/'cohort.parquet',old/'side-summaries.parquet',old/'source-manifest.json',old/'config.json',
        old/'true-pair-replay-audit.json',source/'candidates.parquet',source/'side-summaries.parquet',
        source/'conservative-299/cohort.parquet',source/'contract.json']
    cache_lookup={}; audits={r['session_id']:r for r in read(old/'true-pair-replay-audit.json')}
    for sid in old_lookup:
        path=old/'sessions'/f'{sid}.json'; cache=read(path); paths.append(path)
        if cache['sources']['feature_config']!=fc.sha256 or cache['sources']['extract_code']!=extract_hash:
            raise ValueError('0914/0916 extraction or histogram contract mismatch')
        fingerprint=hashlib.sha256(json.dumps(cache['sources'],sort_keys=True).encode()).hexdigest()
        if fingerprint!=cache['fingerprint'] or audits[sid]['fingerprint']!=fingerprint or not audits[sid]['passed']:
            raise ValueError('0914 cached replay identity mismatch')
        selected=[r for r in cache['side_summaries'] if r['selection']=='observed' and r['scope']=='exclusive_page']
        if len(selected)!=1: raise ValueError('0914 observed scope ambiguous')
        cache_lookup[sid]=selected[0]
    old_observed=[r for r in old_sides if r['selection']=='observed' and r['scope']=='exclusive_page']
    if len(old_observed)!=140 or {r['session_id'] for r in old_observed}!=set(old_lookup): raise ValueError('0914 summary membership')
    for r in old_observed:
        if any(r[side]!=cache_lookup[r['session_id']][side] for side in ('pre','post')):
            raise ValueError('0914 table differs from per-session cache')
    candidate={r['session_id']:r for r in table(source/'candidates.parquet')}
    new_observed=[r for r in table(source/'side-summaries.parquet') if r['selection']=='observed']
    eligible={r['session_id'] for r in table(source/'conservative-299/cohort.parquet')}
    newer=[r for r in new_observed if r['primary_candidate']]
    conservative=[r for r in new_observed if r['session_id'] in eligible]
    if (len(newer),len(conservative))!=(240,299): raise ValueError('0916 cohorts changed')
    old_urls={identity(r['target_url']):r['target_url'] for r in old_cohort}
    new_urls={identity(r['target_url']):r['target_url'] for r in candidate.values()}
    common=set(old_urls)&set(new_urls)
    overlap=[{'resource_identity':key,'0914_url':old_urls[key],'0916_url':new_urls[key],
              'exact_string_match':old_urls[key]==new_urls[key]} for key in sorted(common)]
    out=root/'p4-transformation'; out.mkdir(exist_ok=False)
    write_json(out/'contract.json',{'metrics':list(METRICS),'primary':'0916_240','sensitivity':'0916_299',
        'historical':'0914_140','selection':'observed','scope':'exclusive_page_TCP_only',
        'ratio_bounds':[.9,1.1],'log_bounds':[LOW,HIGH],'js_threshold':.05,
        'MAD':'unscaled median absolute deviation','IQR':'numpy linear quantile 0.75 minus 0.25',
        'aggregation':'median across repeated visits within content, then equal-content descriptive summaries',
        'inference':'no_ICC_no_hypothesis_test_no_new_classifier',
        'old_cache_validation':'all140 cached config/extractor fingerprints and exact side-summary replay; no raw reparse',
        'limits':'not full equality of capture environments; old cached helper dependency history not independently reconstructed',
        'sources':{str(p):digest(p) for p in paths}})
    write_json(out/'overlap-resources.json',overlap)
    sessions=[]
    for cohort_name,data,meta in [('0914_140',old_observed,old_lookup),('0916_240',newer,candidate),('0916_299',conservative,candidate)]:
        for r in data:
            url=meta[r['session_id']]['target_url']; key=identity(url)
            label=meta[r['session_id']].get('label_id',meta[r['session_id']]['target_domain']+'::historical_resource')
            if cohort_name=='0914_140' and key in common:
                label=next(v['label_id'] for v in candidate.values() if identity(v['target_url'])==key)
            for item in values(r['pre'],r['post']):
                sessions.append({'cohort':cohort_name,'session_id':r['session_id'],'target_url':url,
                    'resource_identity':key,'label_id':label,'protocol':r['protocol'],'repetition':r['repetition'],
                    'overlap':'shared_resource' if key in common else 'batch_specific_resource',**item})
    content_groups=defaultdict(list)
    for r in sessions: content_groups[(r['cohort'],r['protocol'],r['resource_identity'],r['metric'])].append(r)
    contents=[]
    for key,group in content_groups.items():
        if len({r['repetition'] for r in group})!=len(group): raise ValueError('Duplicate repetition')
        minimum=4 if key[0].startswith('0916') else 5
        if len(group)<minimum: raise ValueError('Missing repeated visit')
        contents.append({k:group[0][k] for k in ('cohort','protocol','target_url','resource_identity','label_id','overlap','metric','transform')}
                        |{'repetitions':len(group)}|summarize(group))
    aggregate_groups=defaultdict(list)
    for r in contents:
        for level,key in [('all','all'),('overlap',r['overlap']),('business',r['label_id'])]:
            aggregate_groups[(r['cohort'],r['protocol'],r['metric'],level,key)].append(r)
    aggregated=[]
    for key,group in aggregate_groups.items():
        valid=[r for r in group if r['median_delta'] is not None]
        med=float(np.median([r['median_delta'] for r in valid])) if valid else None
        aggregated.append(dict(zip(('cohort','protocol','metric','level','group'),key))|
            {'contents':len(group),'valid_contents':len(valid),'median_content_delta':med,
             'exp_median_content_delta':math.exp(med) if med is not None and key[2] in SCALES else None,
             'median_within_content_MAD':float(np.median([r['mad_delta'] for r in valid])) if valid else None,
             'median_within_content_IQR':float(np.median([r['iqr_delta'] for r in valid])) if valid else None,
             'content_category_counts':{c:sum(r['median_category']==c for r in group) for c in sorted({r['median_category'] for r in group})},
             'positive_median_contents':sum(r['median_delta']>0 for r in valid),
             'negative_median_contents':sum(r['median_delta']<0 for r in valid),
             'all_repetitions_positive_contents':sum(r['all_positive'] for r in valid),
             'all_repetitions_negative_contents':sum(r['all_negative'] for r in valid),
             'mean_content_repetition_band_fraction':float(np.mean([r['repetition_band_fraction'] for r in valid])) if valid else None})
    indexed={(r['cohort'],r['protocol'],r['resource_identity'],r['metric']):r for r in contents}
    comparisons=[]
    for c in ('0916_240','0916_299'):
        for prot in ('SHADOWSOCKS','VLESS'):
            for key in sorted(common):
                for metric in METRICS:
                    a=indexed[('0914_140',prot,key,metric)]; b=indexed[(c,prot,key,metric)]
                    comparisons.append({'new_cohort':c,'protocol':prot,'resource_identity':key,'metric':metric,
                        '0914_url':a['target_url'],'0916_url':b['target_url'],'old_median':a['median_delta'],
                        'new_median':b['median_delta'],'old_MAD':a['mad_delta'],'new_MAD':b['mad_delta'],
                        'old_category':a['median_category'],'new_category':b['median_category'],
                        'category_agrees':a['median_category']==b['median_category'],
                        'interpretation':'shared_resource_descriptive_not_same_action_or_environment'})
    write_table(out/'session-transformations.parquet',sessions)
    write_table(out/'content-repeatability.parquet',contents)
    write_json(out/'group-summary.json',aggregated)
    write_table(out/'shared-resource-comparison.parquet',comparisons)
    write_json(out/'validation.json',{'passed':True,'0914_sessions':140,'0916_primary_sessions':240,
        '0916_sensitivity_sessions':299,'normalized_shared_resources':len(common),
        'exact_shared_urls':sum(r['exact_string_match'] for r in overlap),'session_metric_rows':len(sessions),
        'content_metric_rows':len(contents),'undefined_session_metrics':sum(r['delta'] is None for r in sessions),
        'model_fits':0,'raw_pcap_parses':0,'scope':'descriptive_six_metrics_only'})
    write_json(out/'complete.json',{'artifacts':{p.name:digest(p) for p in out.iterdir() if p.is_file()}})
    print(json.dumps(read(out/'validation.json')),flush=True)


if __name__=='__main__': main()
