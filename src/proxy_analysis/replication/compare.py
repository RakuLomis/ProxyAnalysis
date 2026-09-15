"""Conservative old/new repeat contract mapping and matched descriptive summaries."""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path
import numpy as np
import pyarrow.parquet as pq
from .contract import target_contract
from ..reproducibility.registry import read_json
from ..reproducibility.preflight import write_json, write_table
from ..alignment.urls import stable_hash
from ..statistical.config import StatisticalConfig
from ..statistical.page import _value


def common_repeat(root, old_root, comparable, dest):
    indexed=[]
    for folder in [old_root,root/'repeat/audit']:
        indexed.append({(r['protocol'],r['scope'],r['metric'],r['target_domain']):r
            for r in pq.read_table(folder/'within_protocol_repeatability.parquet').to_pylist()
            if r['stratum']=='all5' and r['selection']=='observed' and r['cohort']=='page_proxy'
            and r['complete'] and r['target_domain'] in comparable})
    paired=[]; grouped=defaultdict(list)
    for key in sorted(set(indexed[0])&set(indexed[1])):
        a,b=indexed[0][key],indexed[1][key]
        r=dict(zip(['protocol','scope','metric','domain'],key))
        r.update(old_mean_delta=a['mean'],new_mean_delta=b['mean'],old_mad=a['mad_raw'],new_mad=b['mad_raw'],
                 old_repetitions=a['n'],new_repetitions=b['n'],new_minus_old_mean_delta=b['mean']-a['mean'])
        paired.append(r); grouped[key[:3]].append(r)
    summaries=[]
    for key,rows in grouped.items():
        summaries.append({**dict(zip(['protocol','scope','metric'],key)), 'n_matched_complete_urls':len(rows),
            'domains':[r['domain'] for r in rows],
            **{name:float(np.median([r[name] for r in rows])) for name in
               ['old_mean_delta','new_mean_delta','old_mad','new_mad','new_minus_old_mean_delta']},
            'interpretation':'same declared workload and complete in both; descriptive batch association, not causal'})
    write_table(dest/'repeat-common-complete-url-pairs.parquet',paired)
    write_table(dest/'repeat-common-complete-summary.parquet',summaries)
    return {'paired_metric_url_rows':len(paired),'summary_rows':len(summaries)}


def broad_comparison(root,dest):
    old_manifests=[read_json(Path('Datasets/TrafficTracer-Protocol-Datasets-raw/batch-manifests')/(p+'.json'))
                   for p in ['SHADOWSOCKS','VLESS','HYSTERIA2']]
    if any(m['targets']!=old_manifests[0]['targets'] for m in old_manifests):
        raise ValueError('old broad protocol target contracts differ')
    m=old_manifests[0]
    old=target_contract({'pipeline_id':m['batch_id'],'targets':m['targets']})['sites']
    new=read_json(root/'broad/audit/target-contract.json')['sites']
    a={t['content_key']:t for t in old};b={t['content_key']:t for t in new}
    mapping=[]; comparable=set()
    for key in sorted(set(a)|set(b)):
        x,y=a.get(key),b.get(key);t=y or x
        status='new_only' if x is None else 'old_only' if y is None else (
            'same_declared_workload' if x['workload_contract_sha256']==y['workload_contract_sha256'] else 'changed_declared_workload')
        if status=='same_declared_workload': comparable.add(stable_hash(t['url']))
        mapping.append({'domain':t['domain'],'url':t['url'],'status':status,
                        'old_duration':(x or {}).get('duration_seconds'),'new_duration':(y or {}).get('duration_seconds'),
                        'old_contract_json':json.dumps(x),'new_contract_json':json.dumps(y)})
    write_table(dest/'broad-target-contract-comparison.parquet',mapping)
    paths=[Path('outputs/statistics/url-aligned/marts/page-available-pairs.parquet'),
           root/'broad/statistics/marts/page-available-pairs.parquet']
    indexes=[]
    for path in paths:
        values=pq.read_table(path).to_pylist()
        index={(r['protocol_dataset'],r['target_url_hash']):r for r in values}
        if len(index)!=len(values):raise ValueError('duplicate broad protocol/URL')
        indexes.append(index)
    config=StatisticalConfig.load('configs/statistical-analysis.yaml')
    paired=[]; summaries=[]
    for metric in config.metrics:
        for protocol in metric.protocols:
            rows=[]
            for key in sorted(set(indexes[0])&set(indexes[1])):
                if key[0]!=protocol or key[1] not in comparable:continue
                a,b=(_value(index[key],metric,'delta') for index in indexes)
                if a is None or b is None:continue
                r={'protocol':protocol,'metric':metric.metric_id,'target_url_hash':key[1],
                   'old_delta':a,'new_delta':b,'new_minus_old_delta':b-a}
                paired.append(r);rows.append(r)
            if rows:summaries.append({'protocol':protocol,'metric':metric.metric_id,'n_matched_urls':len(rows),
                **{name:float(np.median([r[name] for r in rows])) for name in ['old_delta','new_delta','new_minus_old_delta']},
                'interpretation':'same declared workload; time/network/version differ; descriptive only'})
    write_table(dest/'broad-common-url-pairs.parquet',paired)
    write_table(dest/'broad-common-summary.parquet',summaries)
    return dict(Counter(r['status'] for r in mapping))


def model_comparison(root,dest):
    formal=[]; information=[]
    for batch,folder in [('old',Path('outputs/experiments/formal')),('new',root/'broad/formal')]:
        for path in sorted(folder.glob('nested-*.json')):
            r=read_json(path)
            formal.append({'batch':batch,'job':path.stem,'n_sessions':r['session_count'],'n_sites':r['site_count'],
                'feature_count':r['feature_count'],'mean_fold_macro_f1':r['summary']['macro_f1']['mean'],
                'pooled_oof_macro_f1':r.get('pooled_oof_macro_f1'),'outer_splits':r['outer_splits'],
                'outer_repeats':r['outer_repeats'],'inner_splits':r['inner_splits'],
                'note':'three deployments; whole-batch score comparison, not matched-cohort retraining'})
    for batch,folder in [('old',Path('outputs/information-theory-validation/20260907-full-01')),
                         ('new',root/'repeat/information-validation')]:
        for r in pq.read_table(folder/'classification-summary.parquet').to_pylist():
            if r['setting']=='primary' and r['model']=='logistic':
                information.append({'batch':batch,**r,'note':'two deployments; pooled OOF, not three-class mean-fold F1'})
    write_table(dest/'formal-classification-comparison.parquet',formal)
    write_table(dest/'information-classification-comparison.parquet',information)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output-root',type=Path,required=True)
    p.add_argument('--old-root',type=Path,default=Path('outputs/detailed-5reps'))
    p.add_argument('--old-raw',type=Path,default=Path('Datasets/TrafficTracer-Detailed-5Reps'))
    args=p.parse_args(); root=args.output_root; dest=root/'comparison'; dest.mkdir(exist_ok=True)
    old=target_contract(read_json(args.old_raw/'pipeline-manifest.json'))['sites']
    new=read_json(root/'repeat/audit/target-contract.json')['sites']
    a={t['content_key']:t for t in old}; b={t['content_key']:t for t in new}
    rows=[]
    for key in sorted(set(a)|set(b)):
        x,y=a.get(key),b.get(key); t=y or x
        status='new_only' if x is None else 'old_only' if y is None else (
            'same_declared_workload' if x['workload_contract_sha256']==y['workload_contract_sha256'] else 'changed_declared_workload')
        fields=['duration_seconds','wait_load_timeout','playback','network','page_type','run_label']
        rows.append({'content_key':key,'domain':t['domain'],'url':t['url'],'status':status,
            'changed_fields':[k for k in fields if (x or {}).get(k)!=(y or {}).get(k)],
            'old_contract_json':json.dumps(x,ensure_ascii=False),'new_contract_json':json.dumps(y,ensure_ascii=False),
            'interpretation':'matching configured workload does not control network/time/version'})
    write_table(dest/'repeat-target-contract-comparison.parquet',rows)
    old_contract=read_json(args.old_root/'feature-contract.json')
    new_contract=read_json(root/'repeat/audit/feature-contract.json')
    specs_equal=old_contract['specification']==new_contract['specification']
    features_equal=old_contract['feature_config_sha256']==new_contract['feature_config_sha256']
    write_json(dest/'feature-contract-comparison.json',{'representative_specification_equal':specs_equal,
        'feature_config_equal':features_equal,'old':old_contract,'new':new_contract,
        'warning':'source implementation hashes differ; matching numerical definitions is not bitwise identity'})
    comparable={r['domain'] for r in rows if r['status']=='same_declared_workload'} if specs_equal and features_equal else set()
    summaries=[]
    for cohort,domains in [('matched_declared_workload',comparable),('all_available',None)]:
        for label,folder in [('old',args.old_root),('new',root/'repeat/audit')]:
            grouped=defaultdict(list)
            for r in pq.read_table(folder/'within_protocol_repeatability.parquet').to_pylist():
                if r['stratum']=='all5' and r['selection']=='observed' and r['cohort']=='page_proxy' and r['n']>=3:
                    if domains is None or r['target_domain'] in domains:
                        grouped[(r['protocol'],r['scope'],r['metric'])].append(r)
            for (protocol,scope,metric),values in grouped.items():
                summaries.append({'batch':label,'cohort':cohort,'protocol':protocol,'scope':scope,'metric':metric,
                    'n_urls':len(values),'median_of_url_medians':float(np.median([r['median'] for r in values])),
                    'median_within_url_mad':float(np.median([r['mad_raw'] for r in values])),
                    'domains':sorted(r['target_domain'] for r in values),
                    'interpretation':'descriptive; eligibility may differ; not a paired cross-batch causal effect'})
    write_table(dest/'repeat-descriptive-comparison.parquet',summaries)
    counts=dict(Counter(r['status'] for r in rows))
    common=common_repeat(root,args.old_root,comparable,dest)
    broad=broad_comparison(root,dest)
    model_comparison(root,dest)
    write_json(dest/'comparison-summary.json',{'target_contracts':counts,'matching_declared_workload_domains':sorted(comparable),
        'not_pooled_as_extra_repetitions':True,'descriptive_summary_rows':len(summaries),
        'repeat_common_complete':common,'broad_target_contracts':broad})
    lines=['# 新旧重复批次对照','','## 目标与观察契约','',str(counts),'',
           '匹配 URL 不自动表示匹配观测窗口；两批未合并为更多重复轮次。',
           '下面的匹配仅描述采集配置，不消除日期、网络、节点状态或采集版本差异。','',
           '| domain | 契约状态 | 改变字段 |','|---|---|---|']
    for r in rows: lines.append(f"| {r['domain']} | {r['status']} | {', '.join(r['changed_fields'])} |")
    lines+=['','数值对照见 repeat-descriptive-comparison.parquet；各批有效 URL 分母单列，不能把 all_available 的差异归因于代理。',
            '新增 repeat-common-complete-summary.parquet：仅相同声明 workload 且两批均有完整5轮的共同URL，分母逐指标明确。',
            f'广域目标契约：{broad}。broad-common-summary.parquet 仅比较两批共同有效且相同声明 workload 的URL，不能作因果解释。',
            'formal-classification-comparison.parquet 保留三分类 mean-fold 与 pooled 的区别；未做共同cohort模型重训。',
            'information-classification-comparison.parquet 是重复批次二分类的 pooled OOF，仅作同类实验描述对照。',
            '旧 broad 是独立的单次访问批次，与 repeat 的二分类信息论 OOF 不可直接比较。']
    (dest/'comparison-report.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(counts)


if __name__=='__main__':main()
