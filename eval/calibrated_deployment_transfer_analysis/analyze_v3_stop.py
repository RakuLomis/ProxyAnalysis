"""Read-only CUDA replay after the bounded v3 pilot stop; no optimization."""
from pathlib import Path
import sys
import json
from datetime import datetime, timezone, timedelta
from collections import Counter

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'eval/calibrated_deployment_transfer_v3'))
import common as c
import torch

OUT=ROOT/'outputs/calibrated-deployment-business-transfer-analysis-20261006/run-03'

def replay(p,slot,failed=False):
    model=torch.load(p,map_location=c.device(),weights_only=True)
    info=c.read(p.with_suffix('.json'));log=info if failed else info['optimizer']
    if failed:
        theta=model['last_original_parameters'];w,b=theta[:,:96],theta[:,96]
    else:
        assert torch.equal(model['mu'],slot['mu']) and torch.equal(model['scale'],slot['scale'])
        w,b=model['weight'],model['bias']
        assert info['sha256']==c.sha(p) and log['accepted'] and all(log['gates'].values())
    w=w.detach().clone().requires_grad_();b=b.detach().clone().requires_grad_()
    value=c.objective(w,b,slot['x'],slot['y'],slot['mass'],log['t'])
    gw,gb=torch.autograd.grad(value,(w,b));gradient=max(float(gw.abs().max()),float(gb.abs().max()))
    return {'objective':float(value.detach()),'gradient_max':gradient,
        'objective_difference':abs(float(value.detach())-log['objective']),
        'gradient_difference':abs(gradient-log['max_gradient'])}

def run():
    scientific=c.start('v3_analysis_only');contract=c.v3contract();checks={}
    for name,files in [('historical_baseline',scientific['baseline_sha256']),
        ('role_packages',{p:i['sha256'] for p,i in scientific['packages'].items()}),
        ('adopted_artifacts',c.read(c.OUT/'manifests/adopted-artifacts.json')['files']),
        ('original_snapshots',contract['original_snapshots'])]:
        changed=[p for p,h in files.items() if c.sha(ROOT/p)!=h]
        assert not changed,(name,changed);checks[name]={'files':len(files),'changed':changed}
        print('verified',name,len(files),flush=True)
    accepted=[]
    for p in sorted((c.OUT/'pilot/models').rglob('*.pt')):
        log=c.read(p.with_suffix('.json'))['optimizer']
        sp=c.PREP/'slots'/log['role_id']/(log['arm']+'.pt')
        assert log['input_sha256']==c.sha(sp)
        values=replay(p,c.artifact(sp))
        assert values['gradient_max']<=1e-5 and values['objective_difference']<1e-10
        accepted.append({'role_id':log['role_id'],'arm':log['arm'],'t':log['t'],
            'iterations':log['iterations'],'function_evaluations':log['function_evaluations'],**values})
    failed=[]
    for p in sorted((c.OUT/'failures').rglob('*.pt')):
        log=c.read(p.with_suffix('.json'));sp=c.PREP/'slots'/log['role_id']/(log['arm']+'.pt')
        assert log['input_sha256']==c.sha(sp)
        assert not (c.OUT/'pilot/models'/log['role_id']/p.name).exists()
        failed.append({'log':log,'replay':replay(p,c.artifact(sp),True),
            'state_sha256':c.sha(p),'log_sha256':c.sha(p.with_suffix('.json'))})
    assert len(accepted)==24 and len(failed)==1
    missing={p:not (c.OUT/p).exists() for p in ['completion.json','verification.json',
        'pilot/complete.json','pilot/deterministic-replay.json','selection/choices.json',
        'predictions/complete.json','predictions/visits.parquet']}
    assert all(missing.values())
    progress=c.read(c.OUT/'progress.json')
    old=c.read(c.PREVIOUS/'failures'/failed[0]['log']['role_id']/'CT1-t0.json')
    result={'status':'pilot_engineering_stop','stop_time_Asia_Shanghai':datetime.fromtimestamp(
        progress['time_unix'],timezone(timedelta(hours=8))).isoformat(),
        'synthetic_fits':4,'accepted_pilot':24,'failed_pilot':1,'planned_pilot':300,
        'published_main_models':len(list((c.OUT/'models').rglob('*.pt'))),
        'deterministic_diagnostic_fits':0,'by_role':dict(Counter(r['role_id'] for r in accepted)),
        'by_arm':dict(Counter(r['arm'] for r in accepted)),
        'accepted':accepted,'failed':failed,'hash_audit':checks,'missing_final_artifacts':missing,
        'source_checks':len(scientific['source_sha256'])+len(contract['previous_source_sha256'])+len(contract['source_sha256']),
        'prior_same_role':{k:old[k] for k in ['iterations','function_evaluations','objective','max_gradient']},
        'accepted_objective_replay_error_max':max(r['objective_difference'] for r in accepted),
        'new_analysis_fits':0,'optimizer_steps':0,'test_package_reads':0,
        'device':torch.cuda.get_device_name(),'dtype':'float64'}
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/'pilot-stop-audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    summary={k:result[k] for k in ['status','stop_time_Asia_Shanghai','synthetic_fits',
        'accepted_pilot','failed_pilot','published_main_models','by_role','by_arm','accepted_objective_replay_error_max']}
    print(json.dumps(summary,ensure_ascii=False,indent=2),flush=True)
    print('failed replay',json.dumps(failed[0]['replay'],indent=2),flush=True)

if __name__=='__main__':run()
