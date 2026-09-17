"""Fixed-cohort robustness, pairing perturbations and legacy recovery controls."""
import argparse
from collections import defaultdict
import hashlib
import json
from pathlib import Path

import numpy as np
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, r2_score
import yaml

from ..information_validation.experiments import pipeline, dropped_columns, bit_loss
from ..reproducibility.preflight import write_json, write_table
from .experiments import evaluate
from .pairing import matrix
from .prepare import load_config, table, metrics, digest
from .report import audit_map, audit_predictions, cluster_interval


def choose_rows(sides, members, selection, min_round):
    rows = [r for r in sides if r['scope']=='exclusive_page' and r['selection']==selection
            and r['repetition'] >= min_round]
    expected = {r['session_id'] for r in members if r['repetition']>=min_round}
    if {r['session_id'] for r in rows} != expected or len(rows)!=len(expected):
        raise ValueError('sensitivity cohort mismatch')
    return rows


def recovery_controls(rows, spec, out, old_predictions):
    scalar = [m['id'] for m in spec if m['transform']!='distance' and m['id']!='entity_count']
    delta = [m['id'] for m in spec if m['id']!='entity_count']
    families = {m['id']:m['family'] for m in spec}
    x, _ = matrix(rows, spec, 'post'); d, _ = matrix(rows, spec, 'delta_distribution')
    predictions = []
    targets = ['packet_count','transport_bytes','burst_count','fr_runs','length_js','iat_js']
    for target in targets:
        y = d[:,delta.index(target)]
        keep = dropped_columns(target, scalar, families)
        columns = [scalar.index(m) for m in keep]
        for url in sorted({r['target_url'] for r in rows}):
            train = [i for i,r in enumerate(rows) if r['target_url']!=url]
            test = [i for i,r in enumerate(rows) if r['target_url']==url]
            model = pipeline(Ridge(alpha=1.))
            model.fit(x[train][:,columns],y[train])
            estimates = {'ridge_legacy_strong_drop':model.predict(x[test][:,columns]),
                         'global_median':np.repeat(np.median(y[train]),len(test))}
            if target not in {'length_js','iat_js'}:
                pre = np.array([r['pre'][target] for r in rows],dtype=float)
                post = np.array([r['post'][target] for r in rows],dtype=float)
                if np.any(pre<=0) or np.any(post<=0): raise ValueError('algebra requires positive operands')
                estimates['algebra_global'] = np.log(post[test])-np.mean(np.log(pre[train]))
                estimates['algebra_known_deployment_oracle'] = [np.log(post[i])-
                    np.mean([np.log(pre[j]) for j in train if rows[j]['protocol']==rows[i]['protocol']]) for i in test]
            for name, values in estimates.items():
                predictions.extend({'target':target,'model':name,'session_id':rows[i]['session_id'],
                    'target_url':url,'truth':float(y[i]),'prediction':float(value),
                    'kept_features':keep if name=='ridge_legacy_strong_drop' else []}
                    for i,value in zip(test,values))
    reference = {(r['session_id'],r['metric']):r for r in old_predictions
                 if r['setting']=='primary' and r['scheme']=='LOUO' and r['target_view']=='delta'
                 and r['model']=='ridge_post_drop_family'}
    checks = 0
    for r in predictions:
        if r['model']=='ridge_legacy_strong_drop':
            expected = reference[(r['session_id'],r['target'])]
            if not np.isclose(r['prediction'],expected['prediction'],rtol=1e-8,atol=1e-10):
                raise ValueError('legacy strong-drop prediction mismatch')
            checks += 1
    write_table(out/'recovery-controls-oof.parquet',predictions)
    grouped=defaultdict(list)
    for r in predictions: grouped[(r['target'],r['model'])].append(r)
    summary=[]
    for (target,name),group in grouped.items():
        y,p=[r['truth'] for r in group],[r['prediction'] for r in group]
        summary.append({'target':target,'model':name,'n':len(group),
                        'mae':float(mean_absolute_error(y,p)), 'r2':float(r2_score(y,p)) if np.var(y)>0 else None})
    write_table(out/'recovery-controls-summary.parquet',summary)
    return checks


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--config',default='configs/paired-information-0914-sensitivity.yaml')
    args=p.parse_args(); settings=yaml.safe_load(Path(args.config).read_text())
    cfg=load_config(settings['base_config']); root=Path(cfg['output_root'])
    manifest=json.loads((root/'source-manifest.json').read_text())
    for path,value in manifest['sources'].items():
        if digest(Path(path))!=value: raise ValueError('source changed')
    sides=table(root/'side-summaries.parquet'); members=table(root/'cohort.parquet')
    spec=yaml.safe_load(Path(cfg['spec']).read_text())['metrics']
    out=root/settings['output_name']; out.mkdir(exist_ok=True)
    inputs={str(path):digest(path) for path in [Path(args.config),Path(settings['base_config']),
        Path(cfg['spec']),root/'side-summaries.parquet',root/'cohort.parquet',Path(__file__),
        Path(__file__).with_name('experiments.py'),Path(__file__).with_name('pairing.py'),
        Path(__file__).with_name('report.py')]}
    fingerprint=hashlib.sha256(json.dumps(inputs,sort_keys=True).encode()).hexdigest()
    state=out/'contract.json'
    if state.exists() and json.loads(state.read_text())['fingerprint']!=fingerprint:
        raise ValueError('sensitivity contract changed; use a new output_name')
    write_json(state,{'fingerprint':fingerprint,'inputs':inputs,'settings':settings})
    results=[]; mapped=0

    def job(variant,rows,view,train_wrong,test_wrong,seed_index):
        nonlocal mapped
        name=f'{variant}-{view}-train{int(train_wrong)}-test{int(test_wrong)}-{seed_index:03d}'
        folder=out/name
        if (folder/'complete.json').exists():
            saved=json.loads((folder/'complete.json').read_text()); results.append(saved['summary'])
            mapped+=saved['mapping_rows']; return
        folder.mkdir(exist_ok=False)
        preds,maps,tuning=evaluate(rows,spec,view,cfg,cfg['seed']+seed_index*1000,train_wrong,test_wrong=test_wrong)
        registry={r['session_id']:r for r in rows}
        mapped+=audit_map(maps,registry); audit_predictions(preds,registry)
        write_table(folder/'oof.parquet',preds); write_table(folder/'pair-map.parquet',maps)
        write_json(folder/'tuning.json',tuning)
        result={'variant':variant,'view':view,'train_wrong':train_wrong,'test_wrong':test_wrong,
                'seed_index':seed_index,**metrics(preds)}
        write_json(folder/'complete.json',{'summary':result,'mapping_rows':len(maps)})
        results.append(result)
        print(json.dumps(result),flush=True)

    for variant in settings['variants']:
        rows=choose_rows(sides,members,variant['selection'],variant['min_round'])
        for view in ['pre','post','joint_scalar','joint_distribution','delta_scalar','delta_distribution']:
            job(variant['id'],rows,view,False,False,0)
        for seed_index in range(settings['wrong_repetitions']):
            for view in ['delta_scalar','delta_distribution']:
                job(variant['id'],rows,view,True,True,seed_index)
    primary=choose_rows(sides,members,'observed',1)
    for seed_index in range(settings['perturbation_repetitions']):
        for train_wrong,test_wrong in [(False,True),(True,False)]:
            for view in ['delta_scalar','delta_distribution']:
                job('primary_perturbation',primary,view,train_wrong,test_wrong,seed_index)
    original=Path(cfg['input_root'])/'repeat/information-validation/recoverability-oof.parquet'
    checks=recovery_controls(primary,spec,out,table(original))
    write_table(out/'summary.parquet',results)
    advantages=[]
    for variant in settings['variants']:
        for view in ['delta_scalar','delta_distribution']:
            path=out/f'{variant["id"]}-{view}-train0-test0-000'/'oof.parquet'
            true=sorted(table(path),key=lambda r:r['session_id'])
            baseline=bit_loss([r['truth'] for r in true],[r['prob_vless'] for r in true])
            wrong=[]
            for seed_index in range(settings['wrong_repetitions']):
                path=out/f'{variant["id"]}-{view}-train1-test1-{seed_index:03d}'/'oof.parquet'
                r=sorted(table(path),key=lambda r:r['session_id'])
                wrong.append(bit_loss([v['truth'] for v in r],[v['prob_vless'] for v in r]))
            wrong=np.array(wrong)
            center,lo,hi=cluster_interval(wrong.mean(axis=0)-baseline,[r['target_url'] for r in true],
                                         cfg['seed'],settings['bootstrap_repetitions'])
            advantages.append({'variant':variant['id'],'view':view,'n':len(true),
                'wrong_repetitions':len(wrong),'true_loss':float(baseline.mean()),
                'wrong_mean_loss':float(wrong.mean()),'advantage':center,'ci_low':lo,'ci_high':hi})
    write_table(out/'pairing-sensitivity.parquet',advantages)
    write_json(out/'validation.json',{'passed':True,'jobs':len(results),'pair_map_rows_checked':mapped,
               'legacy_strong_drop_predictions_reproduced':checks,'old_data_used':False,
               'legacy_reference':str(original),'legacy_reference_sha256':digest(original)})
    print(json.dumps(advantages),flush=True)


if __name__=='__main__': main()
