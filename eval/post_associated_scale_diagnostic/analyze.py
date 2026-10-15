"""Frozen-checkpoint diagnostics only: gradients but no optimizer or parameter updates."""
from pathlib import Path
import hashlib
import json
import os
import sys
import time

os.environ.setdefault('CUBLAS_WORKSPACE_CONFIG', ':4096:8')
sys.dont_write_bytecode = True
import numpy as np
import pandas as pd
import torch
import torch.nn.functional as F

ROOT = Path(__file__).resolve().parents[2]
PARENT = ROOT/'outputs/post-input-associated-representation-20261014/run-01'
RUN = ROOT/'outputs/post-input-associated-representation-20261014/run-02'
OUT = ROOT/'outputs/post-associated-scale-diagnostic-20261014/run-01'
ACCESS = {}
CONFIGS = [('A1',0.),('A2',.1),('A2',1.),('A3',.1),('A3',1.)]
SEEDS = [20261014,20261015,20261016]
KEYS = ['w0','b0','w1','b1','w2','b2']


def sha(p):
    h = hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
    return h.hexdigest()


def record(p, purpose):
    key = p.relative_to(ROOT).as_posix()
    ACCESS[key] = dict(sha256=sha(p),purpose=purpose)


def read(p):
    record(p,'metadata')
    return json.loads(p.read_text(encoding='utf-8'))


def load(p):
    side = read(p.with_suffix('.json'))
    assert sha(p) == side['sha256']
    record(p,'frozen-source-tensor')
    return torch.load(p,map_location='cuda',weights_only=True)


def stats(a):
    a=np.asarray(a,float)
    return dict(n=len(a),minimum=float(a.min()),median=float(np.median(a)),mean=float(a.mean()),maximum=float(a.max()))


def vec(parts): return torch.cat([v.reshape(-1) for v in parts])
def norm(v): return float(torch.linalg.vector_norm(v).detach())
def cosine(a,b):
    den=norm(a)*norm(b)
    return None if den<1e-20 else float((a@b).detach())/den


def parts(grads):
    return dict(G=vec(grads[:4]),head_x=grads[4][:,:96].reshape(-1),
                head_g=grads[4][:,96:].reshape(-1),head_weight=grads[4].reshape(-1),
                head_bias=grads[5].reshape(-1),all=vec(grads))


def gforward(s,x): return F.linear(F.relu(F.linear(x,s['w0'],s['b0'])),s['w1'],s['b1'])


def evaluate(state,train,base,target,lv):
    # Detached clones; autograd evaluates the saved point, never updates it.
    s={k:state[k].detach().clone().requires_grad_() for k in KEYS};ps=[s[k] for k in KEYS]
    x=train['x'].float();mass=train['mass'].float();y=train['y']
    z0=train['x']@base['weight'].T+base['bias']
    g=gforward(s,x);h=torch.cat([x,g],1);r=F.linear(h,s['w2'],s['b2'])
    z=z0+.1*(r-r.mean(-1,keepdim=True)).double()
    ce=(F.cross_entropy(z,y,reduction='none')*mass).sum()
    mse=((gforward(s,train['real_x'].float())-target).square().mean(1)*train['real_mass'].float()).sum() if lv else torch.zeros((),device='cuda')
    reg=.01*sum(s[k].square().sum() for k in ['w0','w1','w2'])
    terms=[ce,torch.tensor(lv,device='cuda',dtype=torch.float32)*mse,reg]
    gradients=[]
    for term in terms:
        gg=torch.autograd.grad(term,ps,retain_graph=True,allow_unused=True) if term.requires_grad else [None]*len(ps)
        gradients.append(parts([torch.zeros_like(p) if v is None else v for p,v in zip(ps,gg)]))
    gradient={}
    for block in gradients[0]:
        c,m,l=[g[block] for g in gradients]
        gradient[block]=dict(CE_norm=norm(c),lambda_MSE_norm=norm(m),L2_norm=norm(l),
            total_norm=norm(c+m+l),CE_MSE_cosine=cosine(c,m),CE_L2_cosine=cosine(c,l))
    with torch.no_grad():
        realg=gforward(s,train['real_x'].float()).double();wm=train['real_mass']
        mu=(realg*wm[:,None]).sum(0);variance=((realg-mu).square()*wm[:,None]).sum(0).mean()
        weight_stats=dict(G_weight_squared=float(s['w0'].square().sum()+s['w1'].square().sum()),
            head_x_squared=float(s['w2'][:,:96].square().sum()),
            head_g_squared=float(s['w2'][:,96:].square().sum()),
            effective_head_x_norm=norm(.1*(s['w2'][:,:96]-s['w2'][:,:96].mean(0))),
            effective_head_g_norm=norm(.1*(s['w2'][:,96:]-s['w2'][:,96:].mean(0))),
            G_training_variance=float(variance))
    return dict(CE=float(ce.detach()),MSE=float(mse.detach()),regularizer=float(reg.detach()),
        objective=float((terms[0]+terms[1]+terms[2]).detach()),gradients=gradient,weights=weight_stats)


def main():
    started=time.perf_counter();assert not OUT.exists();assert torch.cuda.is_available()
    torch.set_num_threads(1);torch.backends.cuda.matmul.allow_tf32=False;torch.use_deterministic_algorithms(True)
    c=read(RUN/'manifests/experiment-contract.json')
    assert sha(RUN/'manifests/experiment-contract.json')==read(RUN/'manifests/seal.json')['sha256']
    code=read(RUN/'manifests/engineering-code.json')
    for name,h in code['files'].items(): assert sha(ROOT/name)==h;record(ROOT/name,'unchanged-source-code')
    for name in ['completion.json','ledger.json','selections/decisions.json','selections/candidate-metrics.json']:
        read(RUN/name)
    order=['shadowsocks','vless','trojan','vmess']
    wanted={f'main/f0/{pr}/G{g}/i1/{order[(j+1)%4]}' for j,pr in enumerate(order) for g in range(3)}
    roles=[r for r in c['inner_roles'] if r['id'] in wanted]
    assert len(roles)==12 and len(wanted)==12
    prediction_path=RUN/'inner-predictions/post-only.parquet'
    sealed=read(RUN/'inner-predictions/complete.json')
    assert sha(prediction_path)==sealed['files'][prediction_path.relative_to(ROOT).as_posix()]
    record(prediction_path,'source-only-predictions')
    saved=pd.read_parquet(prediction_path);saved=saved[saved.role_id.isin(wanted)]
    rows=[];maximum_replay_error=0.
    for ri,r in enumerate(roles):
        train=load(PARENT/'packages'/r['id']/'classification.pt')
        base=load(PARENT/'base-models'/r['id']/'P-small.pt')
        key=f"outputs/calibrated-deployment-business-transfer-20261006/run-01/packages/{r['id']}/query.parquet"
        info=c['packages'][key];assert r['inner'] is not None and info['kind']=='main-query'
        querypath=ROOT/key;assert sha(querypath)==info['sha256'];record(querypath,'source-only-post-query')
        q=pd.read_parquet(querypath);assert len(q)==24 and set(q)=={'visit_id',*[f'h{j:02}_{i:02}' for j in range(10) for i in range(9 if j<4 else 10)]}
        raw=torch.as_tensor(q.drop(columns='visit_id').to_numpy(),device='cuda',dtype=torch.float64)
        x=(raw-base['mu'])/base['scale'];z0=x@base['weight'].T+base['bias'];margin=z0.topk(2,1).values;gap=margin[:,0]-margin[:,1]
        for arm,lv in CONFIGS:
            target=load(RUN/'targets'/r['id']/(arm+'.pt'))['target'] if lv else None
            for seed in SEEDS:
                path=RUN/'inner-models'/r['id']/f'{arm}-lambda{lv:g}-seed{seed}'
                state=load(path/'terminal.pt')['state'];initial=load(path/'initial.pt')
                a=evaluate(initial,train,base,target,lv);b=evaluate(state,train,base,target,lv)
                with torch.no_grad():
                    xf=x.float();g=gforward(state,xf);rval=F.linear(torch.cat([xf,g],1),state['w2'],state['b2'])
                    delta=.1*(rval-rval.mean(1,keepdim=True)).double();z=z0+delta
                    lp=F.log_softmax(z,1);p=z.softmax(1)
                    stored=saved[saved.role_id.eq(r['id'])&saved.arm.eq(arm)&saved['lambda'].eq(lv)&saved.seed.eq(seed)].set_index('visit_id').loc[q.visit_id]
                    assert len(stored)==24
                    err=float((lp-torch.as_tensor(stored[[f'l{i}' for i in range(6)]].to_numpy(),device='cuda')).abs().max())
                    maximum_replay_error=max(maximum_replay_error,err);assert err==0
                    def projected(v): return .1*(v-v.mean(1,keepdim=True)).double()
                    dx=projected(F.linear(xf,state['w2'][:,:96],None));dg=projected(F.linear(g,state['w2'][:,96:],None))
                    db=projected(state['b2'][None,:].expand(len(x),-1))
                    rms=lambda v:float(v.square().mean().sqrt())
                    denom=float(delta.square().sum())
                    zero_mse=float((target.square().mean(1)*train['real_mass'].float()).sum()) if lv else None
                    held=dict(delta_RMS=rms(delta),x_component_RMS=rms(dx),G_component_RMS=rms(dg),bias_component_RMS=rms(db),
                        base_margin_median=float(gap.median()),max_abs_delta=float(delta.abs().max()),
                        guaranteed_unchanged=int((2*delta.abs().max(1).values<gap).sum()),
                        class_changes=int((z.argmax(1)!=z0.argmax(1)).sum()),
                        mean_boundary_bound_ratio=float((2*delta.abs().max(1).values/gap.clamp_min(1e-15)).mean()),
                        decomposition_rounding_max_error=float((delta-dx-dg-db).abs().max()),
                        G_component_energy_over_total=None if denom==0 else float(dg.square().sum())/denom)
                rows.append(dict(role_id=r['id'],actual_target=r['target'],pseudo_target=r['calibration'],group=r['group'],
                    arm=arm,lambda_value=lv,seed=seed,base_L2=.0005*(1+r['t']),
                    initial=a,terminal=b,heldout_post=held,target_zero_predictor_MSE=zero_mse,
                    frozen_point_objective_change=b['objective']-a['objective']))
        print('frozen_role_diagnostic_complete',ri+1,12,flush=True)
    groups={}
    for arm,lv in CONFIGS:
        ss=[r for r in rows if r['arm']==arm and r['lambda_value']==lv]
        result=dict(n=len(ss),initial={},terminal={},heldout={},gradients={})
        for phase in ['initial','terminal']:
            for k in ['CE','MSE','regularizer','objective']:result[phase][k]=stats([s[phase][k] for s in ss])
            result[phase]['weights']={k:stats([s[phase]['weights'][k] for s in ss]) for k in ss[0][phase]['weights']}
        for k in ss[0]['heldout_post']:
            values=[s['heldout_post'][k] for s in ss if s['heldout_post'][k] is not None]
            result['heldout'][k]=stats(values) if values else None
        for block in ss[0]['terminal']['gradients']:
            result['gradients'][block]={}
            for k in ss[0]['terminal']['gradients'][block]:
                values=[s['terminal']['gradients'][block][k] for s in ss if s['terminal']['gradients'][block][k] is not None]
                result['gradients'][block][k]=stats(values) if values else None
        groups[f'{arm}-lambda{lv:g}']=result
    # Recheck every decoded/hashed source asset after diagnostics. No historical writes.
    for name,info in ACCESS.items():assert sha(ROOT/name)==info['sha256'],name
    OUT.mkdir(parents=True)
    result=dict(passed=True,scope='source-only frozen checkpoint evaluation, no parameter updates or fitting',
        selection_rule='first outer fold, first inner fold, all four actual targets and three masks; cyclic next protocol pseudo-target',
        source_roles=12,models=180,evaluated_points=360,source_query_predictions=4320,
        replay_logprob_max_error=maximum_replay_error,new_training_fits=0,optimizer_steps=0,
        actual_H_reads=0,actual_U_reads=0,teacher_refits=0,
        alpha=.1,raw_head_L2=.01,effective_head_L2=1.,
        full_source_base_L2_range=[.0005,.0025],device=torch.cuda.get_device_name(0),
        elapsed_seconds=time.perf_counter()-started,groups=groups,rows=rows,source_files=ACCESS,
        caveats=['Structural source subset, not full-population estimates or H results.',
                 'L2 is in raw weight coordinates; effective coefficient 1 applies to projected output-head weights, not bias or the whole nonlinear model.',
                 'Component RMS energies are not additive when components correlate.',
                 'Stored step1000 losses precede the last Adam update; this evaluates the saved post-update terminal point.'])
    (OUT/'diagnostic.json').write_text(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
    print('diagnostic_complete',json.dumps(dict(source_roles=12,models=180,source_predictions=4320,
        replay_error=maximum_replay_error,new_training_fits=0,seconds=result['elapsed_seconds'])),flush=True)


if __name__=='__main__':main()
