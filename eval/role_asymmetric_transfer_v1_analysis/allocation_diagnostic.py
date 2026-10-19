"""AD1 read-only allocation diagnosis: saved weights, gradients and sealed predictions.

No optimizer, fit, calibration, target-U package or H feature/pre read is used.
H labels/probabilities have already been scored in the sealed full NR2 run.
"""
import os
os.environ.setdefault('CUBLAS_WORKSPACE_CONFIG', ':4096:8')
import time
START = time.perf_counter()
from pathlib import Path
import ast
import hashlib
import json
import numpy as np
import pandas as pd
import torch

ROOT = Path(__file__).resolve().parents[2]
RUN = ROOT/'outputs/role-asymmetric-transfer-v1-20261017/full-nr2-01'
OUT = RUN/'allocation-diagnostic-20261018'
POL = ['P__m025__UPR', 'P__m010__SYM', 'P__m025__SYM']
NAMES = dict(zip(POL, ['P-U50', 'P-small', 'P-SYM25']))
LABELS = ['bing.com::search_results_view', 'developer.mozilla.org::document_view',
          'github.com::repository_view', 'wikipedia.org::article_view',
          'youtube.com::search_results_view', 'youtube.com::video_playback']
MASKS = {'G0':[2,4], 'G1':[0,3], 'G2':[1,5]}
READS = {}

def require(ok, msg):
    if not bool(ok):
        raise RuntimeError(msg)

def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def track(p, expected=None):
    p = Path(p); s = sha(p)
    if expected is not None:
        require(s == expected, 'Source hash changed: '+str(p))
    READS[p.relative_to(ROOT).as_posix()] = s
    return p

def read(p):
    return json.loads(track(p).read_text(encoding='utf-8-sig'))

def load(p, expected=None):
    return torch.load(track(p, expected), map_location='cuda:0', weights_only=True)

def tensor(a, dtype=torch.float64):
    return torch.as_tensor(a, device='cuda:0', dtype=dtype)

def weighted(y, w, k):
    return torch.zeros(k, device=y.device, dtype=w.dtype).scatter_add_(0, y, w)

def tofloat(x):
    return float(x.detach())

def evaluate(x, y, mass, model):
    z = x@model['weight'].T+model['bias']
    ce = z.logsumexp(1)-z.gather(1, y[:,None]).flatten()
    err = (z.softmax(1)-torch.nn.functional.one_hot(y, 6))*mass[:,None]
    grad = torch.cat([(err.T@x).flatten(), err.sum(0)])
    return (mass*ce).sum(), grad

def main():
    require(torch.cuda.is_available(), 'CUDA required for saved-model replay')
    torch.set_num_threads(4)
    torch.backends.cuda.matmul.allow_tf32 = False
    torch.backends.cudnn.allow_tf32 = False
    verification = read(RUN/'verification.json')
    completion = read(RUN/'completion.json')
    require(verification['passed'] and completion['program_complete'], 'Incomplete full experiment')
    track(RUN/'verification.json', completion['verification_sha256'])
    original = ROOT/'docs/role-asymmetric-transfer-v1-20261017/full-nr2/complete-report.md'
    track(original, verification['report_sha256'])
    c = read(RUN/'manifests/contract.json')
    track(RUN/'manifests/contract.json', read(RUN/'manifests/seal.json')['sha256'])
    ends = pd.read_parquet(track(RUN/'manifests/endpoints.parquet', read(RUN/'manifests/endpoint-seal.json')['sha256']))
    # Reuse exact frozen slot producer, not its historical solver/audit imports.
    path = ROOT/'eval/role_asymmetric_transfer_nr2_full/weight_schedule.py'
    track(path, c['code'][path.relative_to(ROOT).as_posix()])
    tr = ast.parse(track(path).read_text())
    tr.body = [n for n in tr.body if isinstance(n, ast.FunctionDef) and n.name in ['registry','selection','slot']]
    ns = dict(torch=torch, np=np, tensor=tensor, weighted=weighted, require=require)
    exec(compile(ast.fix_missing_locations(tr), str(path), 'exec'), ns)
    registry = {p['id']:p for p in ns['registry']()}
    ledgers=[]; risks=[]; totals=[]; crosses=[]; gr=[]; biases={}; masses=[]
    for ii, r in enumerate(c['roles']):
        vp = ROOT/'outputs/role-asymmetric-transfer-v1-20261017/run-01/packages'/r['id']/'training.pt'
        v = load(vp)
        expected = c['artifacts'].get(vp.relative_to(ROOT).as_posix())
        require(isinstance(expected, str), 'Training package absent from full contract')
        require(sha(vp) == expected, 'Training package differs from full contract')
        models={}; slots={}; part={}
        base = dict(role_id=r['id'], target=r['target'], group=r['group'], outer=r['outer'])
        for pid in POL:
            e = ends[ends.role_id.eq(r['id']) & ends.policy_id.eq(pid)]
            require(len(e) == 1, 'Ambiguous endpoint')
            e=e.iloc[0];m=load(ROOT/e.path, e.sha256);models[pid]=m
            require(float(e.t)==r['t'] and float(e.eta)==r['eta'], 'Hyperparameter mismatch')
            require(torch.equal(m['mu'],v['mu']) and torch.equal(m['scale'],v['scale']), 'Coordinate mismatch')
            s, rows=ns['slot'](v, registry[pid], r['missing'], ledger=True);slots[pid]=s
            for row in rows:
                ledgers.append(dict(**base, policy_id=pid, **row))
            for k in ['C','U']:
                u = torch.isin(s['y'], tensor(r['missing'], torch.long))
                masses.append(dict(**base, policy_id=pid, scope=k,
                    class_mass=tofloat(s['mass'][u if k=='U' else ~u].sum()),
                    retained_rows=len(s['y']), weight_sq=tofloat(s['mass'].square().sum())))
            biases[(r['id'],pid)] = m['bias'].cpu().numpy()
            pp={}
            for nm in ['main','S','P','C']:
                x,y,w=v[nm+'_x'],v[nm+'_y'],v[nm+'_mass']
                for scope in ['C','U']:
                    take=torch.isin(y,tensor(r['missing'],torch.long))
                    if scope=='C': take=~take
                    if not bool(take.any()):continue
                    val, grad=evaluate(x[take],y[take],w[take],m)
                    mass=tofloat(w[take].sum());pp[(nm,scope)]=(val,grad)
                    risks.append(dict(**base, policy_id=pid, view=nm, scope=scope,
                        view_mass=mass, weighted_CE=tofloat(val), conditional_CE=tofloat(val)/mass))
            part[pid]=pp
            own,g=evaluate(s['x'],s['y'],s['mass'],m)
            penalty=.0005*(1+r['t'])*m['weight'].square().sum()
            g[:576]+=.001*(1+r['t'])*m['weight'].flatten()
            gi=tofloat(g.abs().max());require(gi<=1e-5,'Saved endpoint fails original gradient')
            obj=tofloat(own+penalty)
            require(abs(obj-float(e.objective))<1e-10,'Training objective replay')
            totals.append(dict(**base, policy_id=pid, objective=obj, weighted_CE=tofloat(own),
                L2=tofloat(penalty), gradient_inf=gi, t=r['t'], eta=r['eta'],
                weight_norm=tofloat(m['weight'].norm()), bias_contrast_norm=tofloat((m['bias']-m['bias'].mean()).norm())))
        for theta_pid,m in models.items():
            for objective_pid,s in slots.items():
                loss,_=evaluate(s['x'],s['y'],s['mass'],m)
                value=tofloat(loss+.0005*(1+r['t'])*m['weight'].square().sum())
                crosses.append(dict(**base, theta_policy=theta_pid, objective_policy=objective_pid, objective=value))
        for ref in POL[1:]:
            m=models[ref]; a=registry[POL[0]];b=registry[ref];p=part[ref]
            dc=(a['rho_C']-b['rho_C'])*(p[('P','C')][1]-p[('S','C')][1])
            du=(a['rho_U']-b['rho_U'])*(p[('P','U')][1]-p[('S','U')][1])
            both=dc+du
            lossdelta=(a['rho_C']-b['rho_C'])*(p[('P','C')][0]-p[('S','C')][0])+(a['rho_U']-b['rho_U'])*(p[('P','U')][0]-p[('S','U')][0])
            actual=evaluate(slots[POL[0]]['x'],slots[POL[0]]['y'],slots[POL[0]]['mass'],m)[1]-evaluate(slots[ref]['x'],slots[ref]['y'],slots[ref]['mass'],m)[1]
            require(tofloat((both-actual).abs().max())<1e-12,'Weight gradient decomposition')
            step=torch.cat([(models[POL[0]]['weight']-m['weight']).flatten(),models[POL[0]]['bias']-m['bias']])
            cosine=lambda aa,bb: tofloat(torch.dot(aa,bb)/(aa.norm()*bb.norm()).clamp_min(1e-300))
            gr.append(dict(**base,reference=ref, C_change_norm=tofloat(dc.norm()),U_change_norm=tofloat(du.norm()),
                C_U_cosine=cosine(dc,du),U_norm_over_C_norm=tofloat(du.norm()/dc.norm()),
                delta_theta_negative_C_cosine=cosine(step,-dc),delta_theta_negative_U_cosine=cosine(step,-du),
                delta_theta_negative_total_cosine=cosine(step,-both),exact_CE_policy_change_at_reference=tofloat(lossdelta)))
        if (ii+1)%12==0:print('Read-only saved-model roles',ii+1,'/ 60',flush=True)
    OUT.mkdir(parents=True,exist_ok=True)
    for name, rows in [('weight-ledger',ledgers),('view-risks',risks),('training-objectives',totals),
                       ('cross-objectives',crosses),('gradient-decomposition',gr),('mass-audit',masses)]:
        pd.DataFrame(rows).to_parquet(OUT/(name+'.parquet'),index=False)
    d=pd.read_parquet(track(RUN/'scores/labeled-predictions.parquet'))
    d=d[d.policy_id.isin(POL)].copy();d['label_index']=d.label_id.map(dict(zip(LABELS,range(6))))
    a=d[d.policy_id.eq(POL[0])];pairs=[]
    for ref in POL[1:]:
        b=d[d.policy_id.eq(ref)];q=a.merge(b,on=['role_id','visit_id'],suffixes=('_a','_b'),validate='one_to_one')
        for row in q.to_dict('records'):
            y=int(row['label_index_a']);pa=int(row['prediction_a']);pb=int(row['prediction_b']);rid=row['role_id']
            k=pa if pa!=y else pb if pb!=y else int(np.argmax([row[f'logit{j}_b'] if j!=y else -np.inf for j in range(6)]))
            score=lambda arm,j:float(row[f'logit{j}_{arm}'])
            db=biases[(rid,POL[0])]-biases[(rid,ref)]
            delta_margin=score('a',y)-score('a',k)-score('b',y)+score('b',k)
            biaspart=float(db[y]-db[k]);group=row['group_a'];scope='U' if y in MASKS[group] else 'C'
            state='both_correct' if pa==y and pb==y else 'new_error' if pb==y else 'repaired' if pa==y else 'both_wrong'
            ta=-row[f'logp{y}_a'];tb=-row[f'logp{y}_b']
            pairs.append(dict(role_id=rid,visit_id=row['visit_id'],reference=ref,target=row['target_a'],group=group,
                content_id=row['content_id_a'],label_index=y,scope=scope,state=state,prediction=pa,reference_prediction=pb,
                wrong_destination_role='U' if pa in MASKS[group] else 'C', delta_CE=ta-tb,
                candidate_confidence=max(row[f'p{j}_a'] for j in range(6)),reference_confidence=max(row[f'p{j}_b'] for j in range(6)),
                candidate_true_p=row[f'p{y}_a'],reference_true_p=row[f'p{y}_b'],
                delta_fixed_competitor_margin=delta_margin,delta_bias_margin=biaspart,
                delta_feature_margin=delta_margin-biaspart,competitor=k))
    pd.DataFrame(pairs).to_parquet(OUT/'margin-flips.parquet',index=False)
    z=pd.DataFrame(crosses);diag=z[z.theta_policy.eq(z.objective_policy)].set_index(['role_id','objective_policy']).objective
    z['own_optimum']=np.array([diag.loc[(r.role_id,r.objective_policy)] for r in z.itertuples()])
    z['excess_vs_own_fit']=z.objective-z.own_optimum
    z.to_parquet(OUT/'cross-objectives.parquet',index=False)
    own=pd.DataFrame(totals);vr=pd.DataFrame(risks);fl=pd.DataFrame(pairs);gd=pd.DataFrame(gr)
    summary=dict(status='read_only_diagnosis_complete',new_fits=0,optimizer_updates=0,calibration_fits=0,
        actual_target_U_reads=0,H_feature_reads=0,H_pre_reads=0,uses_already_scored_H_predictions=True,
        device=torch.cuda.get_device_name(0),roles=60,endpoints=180,
        min_cross_objective_excess=float(z.excess_vs_own_fit.min()),
        cross_objective_positive=(z[z.theta_policy.ne(z.objective_policy)].excess_vs_own_fit>0).sum().item(),
        max_saved_original_gradient=float(own.gradient_inf.max()),
        objective_mean=own.groupby('policy_id').mean(numeric_only=True).to_dict(),
        gradient_mean=gd.groupby('reference').mean(numeric_only=True).to_dict(),
        view_CE_mean=vr.groupby(['policy_id','view','scope']).conditional_CE.mean().reset_index().to_dict('records'),
        U_flips=fl[fl.scope.eq('U')].groupby(['reference','state']).agg(
            n=('state','size'),delta_CE=('delta_CE','mean'),confidence=('candidate_confidence','mean'),
            ref_confidence=('reference_confidence','mean'),delta_bias=('delta_bias_margin','mean'),
            delta_feature=('delta_feature_margin','mean')).reset_index().to_dict('records'))
    torch.cuda.synchronize()
    summary['active_seconds']=time.perf_counter()-START
    summary['source_hashes']=READS
    summary['source_code_sha256']=sha(Path(__file__))
    require(sha(original)==verification['report_sha256'],'Original report changed')
    (OUT/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in summary.items() if k in ['status','new_fits','active_seconds','min_cross_objective_excess','cross_objective_positive','max_saved_original_gradient','U_flips','gradient_mean']},ensure_ascii=False,indent=2))

if __name__=='__main__':
    main()
