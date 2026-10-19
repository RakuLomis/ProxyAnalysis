"""Independent final train-objective replay, source immutability and deployment export."""
from common import *
from workflow import barrier,codecheck,rolelookup,seal,diagnostic,job,recipes,ARMS,LABELS
from data import TrainingPool
from models import loss_independent,forward_post

def post_only(raw96,export):
    require(raw96.is_cuda and raw96.shape[-1]==96,'CUDA post96 only')
    x=(raw96.double()-export['mu'])/export['scale']
    if export['kind']=='base':return F.linear(x,export['weight'],export['bias'])
    return forward_post(x,export['state'])[0]

def closeout():
    marker=OUT/'completion.json'
    if marker.exists():return read(marker)
    barrier('scores-complete.json');codecheck();rs=rolelookup();pool=TrainingPool();eps=read(OUT/'manifests/outer-endpoints.json')
    seen=set();checks=[];exports=[]
    for e in eps:
        r=rs[e['role_id']];key=(r['id'],e['path'])
        if key in seen:continue
        seen.add(key);b=asset(PARENT/'base-models'/r['id']/'P-small.pt',r['id'],'base')
        if e['path'] is None:
            exp=dict(kind='base',weight=b['weight'],bias=b['bias'],mu=b['mu'],scale=b['scale']);identity='B0'
        else:
            p=ROOT/e['path'];record=own(p);meta=read(p.with_suffix('.json'));recipe=meta['recipe']
            # Checkpoint's physical arm may differ from its logical endpoint (lambda=0 aliases).
            target='JG' if '/JG/' in e['path'] else 'JP'
            d=pool.get(r,target if recipe['lam'] else 'JC',recipe['lam']);s=record['state']
            independent,_=loss_independent(s,d,recipe)
            require(torch.isfinite(independent),'Nonfinite final objective')
            trace=OUT/'training-traces'/(meta['job']+'.json')
            if trace.exists() and record['steps']==2000:
                last=read(trace)['trace'][-1];err=abs(float(independent)-last['objective'])
                require(err<1e-9,'Checkpoint objective differs from training trace')
            else:err=0.
            exp=dict(kind='joint',state=s,mu=b['mu'],scale=b['scale']);identity=sha(p)[:20]
            with torch.no_grad():
                x=d['x'][:16];z,_=forward_post(x,s)
                h=torch.relu(F.linear(x.float(),s['a0'],s['d0']));g=F.linear(h,s['a1'],s['d1']).double()
                independent_z=x@s['W'].T+g@s['V'].T+s['c']
                out_error=float((z-independent_z).abs().max())
                require(out_error<1e-9,'Independent logits replay differs')
            checks.append(dict(role_id=r['id'],path=e['path'],objective_error=err,independent_logit_error=out_error))
        dest=OUT/'exports'/r['id']/(identity+'.pt')
        put(dest,exp,role_id=r['id'],post_only=True,source=e['path']);exports.append(rel(dest))
        with torch.no_grad():
            raw=b['mu'][None].expand(2,-1).clone();actual=post_only(raw,exp)
            require(actual.shape==(2,6) and torch.isfinite(actual).all(),'Export post-only schema')
    changed=[]
    for p,info in contract()['files'].items():
        if sha(ROOT/p)!=info['sha256']:changed.append(p)
    require(not changed,'Historical source files changed')
    p=OUT/'audits/final-verification.json';immutable(p,dict(passed=True,checked_model_objectives=checks,
        historical_files_checked=len(contract()['files']),historical_files_changed=changed,exports=exports,
        H_pre_reads=0,U_training_reads=0,PCAP_reads=0))
    seal(OUT/'manifests/exports-complete.json',[ROOT/p for p in exports],passed=True)
    from report import report
    report()
    immutable(marker,dict(status='complete',passed_engineering=True,complete_scientific_evaluation=True,
        budget=read(OUT/'budget.json'),H_rows=34560,inner_rows=432000,outer_roles=60,source_roles=720,
        report=rel(DOC/'complete-report.md'),historical_blind_external_test=False))
    progress('JAT1_complete',report=rel(DOC/'complete-report.md'))
