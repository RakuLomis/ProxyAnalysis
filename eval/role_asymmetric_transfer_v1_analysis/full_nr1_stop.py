"""Read-only Full NR1 closeout; no optimizer, model updates or H access."""
from pathlib import Path
import os
os.environ.setdefault('CUBLAS_WORKSPACE_CONFIG', ':4096:8')
import collections
import hashlib
import json
import time
import pandas as pd
import torch
import torch.nn.functional as F

ROOT = Path(__file__).resolve().parents[2]
RUN = ROOT/'outputs/role-asymmetric-transfer-v1-20261017/full-nr1-01'
OUT = ROOT/'outputs/role-asymmetric-transfer-v1-20261017/full-nr1-closeout-20261018'

def read(p):
    return json.loads(p.read_text(encoding='utf-8-sig'))

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    start = time.perf_counter()
    torch.set_num_threads(1)
    torch.use_deterministic_algorithms(True)
    torch.backends.cuda.matmul.allow_tf32 = False
    torch.backends.cudnn.allow_tf32 = False
    failures = list((RUN/'failures').rglob('*.json'))
    assert len(failures) == 1
    fp = failures[0]; fail = read(fp)
    slot = RUN/'numeric-slots'/fail['role_id']/(fail['arm']+'.pt')
    bound_paths = [fp, fp.with_suffix('.pt'), slot, RUN/'cost-final.json',
                   RUN/'failure.json', RUN/'manifests/contract.json', RUN/'manifests/numeric-policy.json']
    hashes = {str(p.relative_to(ROOT)): sha(p) for p in bound_paths}
    assert sha(slot) == fail['input_sha256']
    s = torch.load(slot, map_location='cuda', weights_only=True)
    state = torch.load(fp.with_suffix('.pt'), map_location='cuda', weights_only=True)
    theta = state['last_original_parameters']
    x, y, mass = s['x'], s['y'], s['mass']
    w, b = theta[:, :96], theta[:, 96]
    z = x@w.T+b; prob = z.softmax(1)
    coef = .0005*(1+fail['t'])
    value = (mass*(z.logsumexp(1)-z.gather(1,y[:,None]).squeeze(1))).sum()+coef*w.square().sum()
    error = (prob-F.one_hot(y,6))*mass[:,None]
    grad = torch.cat([error.T@x+2*coef*w, error.sum(0)[:,None]],1)
    maximum = float(grad.abs().max())
    oe, ge = abs(float(value)-fail['objective']), abs(maximum-fail['max_gradient'])
    assert oe < 1e-10 and ge < 1e-10
    # Geometry only: no Newton correction, parameter update or fitted predictions.
    a = torch.cat([x, torch.ones(len(x),1,device=x.device,dtype=x.dtype)],1)
    reg = torch.tensor([2*coef]*96+[0.],device=x.device,dtype=x.dtype)
    ref = a.T@(a*mass[:,None])/6+torch.diag(reg)
    l = state['cholesky']
    basis = torch.cat([torch.eye(5,device=x.device,dtype=x.dtype),-torch.ones(1,5,device=x.device,dtype=x.dtype)],0)
    q, _ = torch.linalg.qr(basis,mode='reduced')
    cp = torch.diag_embed(prob)-prob[:,:,None]*prob[:,None,:]
    c5 = q.T@cp@q
    h = torch.einsum('nij,na,nb,n->iajb',c5,a,a,mass).reshape(485,485)+torch.diag(reg.repeat(5))
    eh = torch.linalg.eigvalsh((h+h.T)/2)
    li = torch.linalg.solve_triangular(l,torch.eye(97,device=x.device,dtype=x.dtype),upper=False)
    transform = torch.kron(torch.eye(5,device=x.device,dtype=x.dtype),li.T.contiguous())
    hp = transform.T@h@transform
    ep = torch.linalg.eigvalsh((hp+hp.T)/2)
    logs = []
    for p in (RUN/'fit-logs').rglob('*.json'):
        v = read(p)
        logs.append(dict(role_id=v['role_id'], policy_id=v['arm'], source=v['arm'].split('__')[0],
                         fold=v['role_id'].split('/')[1], deployment=v['role_id'].split('/')[2],
                         accepted=v['accepted'], iterations=v['iterations'], evaluations=v['function_evaluations'],
                         gradient=v['max_gradient'], seconds=v['seconds']))
    frame = pd.DataFrame(logs); accepted = frame[frame.accepted]
    new = [read(p) for p in (RUN/'new-endpoints').rglob('*.json')]
    adopted = pd.read_parquet(RUN/'manifests/adopted-endpoints.parquet')
    assert len(new) == len(accepted) == len(list((RUN/'models').rglob('*.pt'))) == 438
    assert len(frame) == len(list((RUN/'attempts').rglob('*.json'))) == 439
    keys = {(r['role_id'],r['policy_id']) for r in new}
    oldkeys = set(zip(adopted.role_id,adopted.policy_id))
    assert not keys & oldkeys
    contract = read(RUN/'manifests/contract.json')
    role_sizes = collections.Counter(k[0] for k in keys|oldkeys)
    fully_ready = [r['id'] for r in contract['roles'] if role_sizes[r['id']] == 39]
    reads = []
    for p in (RUN/'stages').glob('*.json'):
        reads.extend(read(p).get('reads',[]))
    for p in (RUN/'audits').glob('*reads-on-stop.json'):
        reads.extend(read(p).get('reads',[]))
    purposes = collections.Counter(r['purpose'] for r in reads)
    forbidden = [r for r in reads if r['purpose'] in ['query','score','historical-probability-replay']]
    products = {p:(RUN/p).exists() for p in ['completion.json','verification.json','manifests/endpoint-seal.json',
                                           'manifests/endpoints.parquet','predictions/visits.parquet',
                                           'predictions/complete.json','scores','run.lock']}
    assert not forbidden and not any(products.values())
    record = fail['actual_optimizer_break']; lines = record['line_searches']
    cost = read(RUN/'cost-final.json')
    summary = dict(status='stopped_iteration_budget_no_H_evaluation',
        failure={k:v for k,v in fail.items() if k!='actual_optimizer_break'},
        stop={k:v for k,v in record.items() if k!='line_searches'},
        line_search=dict(count=len(lines), reasons=dict(collections.Counter(r['reason'] for r in lines)),
                         armijo_failed=sum(not r['armijo'] for r in lines),curvature_failed=sum(not r['curvature'] for r in lines),
                         last8_steps=[r['step'] for r in lines[-8:]]),
        independent_replay=dict(objective=float(value),gradient_inf=maximum,objective_error=oe,gradient_error=ge,
                                rows=len(x),mass_sum=float(mass.sum()),class_mass=(F.one_hot(y,6).double().T@mass).cpu().tolist(),
                                dtype=str(x.dtype),device=str(x.device),bias_gradient_inf=float(grad[:,-1].abs().max())),
        geometry=dict(original_contrast_hessian_condition=float(eh[-1]/eh[0]),original_min_eigen=float(eh[0]),original_max_eigen=float(eh[-1]),
                      preconditioned_contrast_hessian_condition=float(ep[-1]/ep[0]),preconditioned_min_eigen=float(ep[0]),preconditioned_max_eigen=float(ep[-1]),
                      cholesky_residual_max=float((l@l.T-ref).abs().max()),max_abs_training_coordinate=float(x.abs().max()),
                      shared_bias_translation_removed=True,fit_or_parameter_update=False),
        inventory=dict(adopted_logical=len(adopted),adopted_scientific=166,historical_aliases=420,new_attempts=len(frame),new_accepted=len(new),new_failed=1,
                       distinct_scientific_accepted=166+len(new),scientific_total=1920,logical_available=len(keys|oldkeys),logical_total=2340,
                       pending_including_failed=1920-166-len(new),not_attempted=1754-len(frame),complete_role_model_coverage=len(fully_ready),
                       fully_ready_roles=fully_ready,primary_candidate_available=sum(k[1]=='P__m025__UPR' for k in keys|oldkeys),
                       accepted_by_source=accepted.groupby('source').size().to_dict(),accepted_by_fold=accepted.groupby('fold').size().to_dict(),
                       new_solver_seconds=float(frame.seconds.sum()),accepted_solver_seconds=float(accepted.seconds.sum()),
                       max_accepted_iterations=int(accepted.iterations.max()),max_accepted_gradient=float(accepted.gradient.max())),
        source_cost=frame.groupby('source').agg(attempts=('source','size'),seconds=('seconds','sum'),max_iterations=('iterations','max')).reset_index().to_dict('records'),
        cost=cost,budget_remaining_seconds=cost['cap_seconds']-cost['cumulative_active_seconds'],
        completion_products=products,H_query_or_label_read_events=len(forbidden),audited_read_purposes=dict(purposes),
        original_stop_unchanged=True,training_restarted=False,new_training_during_analysis=0,source_hashes=hashes)
    assert all(sha(ROOT/p)==digest for p,digest in hashes.items())
    OUT.mkdir(parents=True,exist_ok=True)
    frame.to_parquet(OUT/'new-fit-inventory.parquet',index=False)
    summary['additional_readonly_analysis_seconds'] = time.perf_counter()-start
    (OUT/'stop-analysis.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in summary.items() if k not in ['source_hashes','failure','stop','audited_read_purposes']},ensure_ascii=False,indent=2))

if __name__ == '__main__':
    main()
