"""Read-only RA1 stop analysis: no fits, H query, labels or old-result writes."""
from pathlib import Path
import os
os.environ.setdefault('CUBLAS_WORKSPACE_CONFIG', ':4096:8')
import collections
import hashlib
import json
import time
import numpy as np
import pandas as pd
import torch
import torch.nn.functional as F

ROOT=Path(__file__).resolve().parents[2]
RUN=ROOT/'outputs/role-asymmetric-transfer-v1-20261017/run-01'
OUT=ROOT/'outputs/role-asymmetric-transfer-v1-20261017/closeout-20261018'

def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    started=time.perf_counter();torch.set_num_threads(1);torch.use_deterministic_algorithms(True)
    torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False
    paths=list((RUN/'failures').rglob('*.json'));assert len(paths)==1
    fp=paths[0];failure=read(fp);rid=failure['role_id'];arm=failure['arm']
    slotpath=RUN/'numeric-slots'/rid/(arm+'.pt');statepath=fp.with_suffix('.pt')
    bound={str(p.relative_to(ROOT)):sha(p) for p in [RUN/'failure.json',RUN/'cost-ledger.json',fp,statepath,slotpath]}
    assert sha(slotpath)==failure['input_sha256']
    s=torch.load(slotpath,map_location='cuda',weights_only=True);state=torch.load(statepath,map_location='cuda',weights_only=True)
    theta=state['last_original_parameters'];x=s['x'];y=s['y'];mass=s['mass'];w=theta[:,:96];b=theta[:,96]
    z=x@w.T+b;prob=z.softmax(1);coef=.0005*(1+failure['t'])
    value=(mass*(z.logsumexp(1)-z.gather(1,y[:,None]).squeeze(1))).sum()+coef*w.square().sum()
    error=(prob-F.one_hot(y,6))*mass[:,None]
    gradient=torch.cat([error.T@x+2*coef*w,error.sum(0)[:,None]],1)
    maximum=float(gradient.abs().max());objerr=abs(float(value)-failure['objective']);graderr=abs(maximum-failure['max_gradient'])
    assert objerr<1e-10 and graderr<1e-10
    # Geometry only. No parameter update, extra Newton step or LR solve.
    a=torch.cat([x,torch.ones(len(x),1,device=x.device,dtype=x.dtype)],1);regdiag=torch.tensor([2*coef]*96+[0.],device=x.device,dtype=x.dtype)
    ref=a.T@(a*mass[:,None])/6+torch.diag(regdiag);l=state['cholesky'];eigen=torch.linalg.eigvalsh(ref)
    basis=torch.cat([torch.eye(5,device=x.device,dtype=x.dtype),-torch.ones(1,5,device=x.device,dtype=x.dtype)],0)
    q,_=torch.linalg.qr(basis,mode='reduced')
    cp=torch.diag_embed(prob)-prob[:,:,None]*prob[:,None,:];c5=q.T@cp@q
    h=torch.einsum('nij,na,nb,n->iajb',c5,a,a,mass).reshape(485,485)+torch.diag(regdiag.repeat(5))
    eh=torch.linalg.eigvalsh((h+h.T)/2)
    li=torch.linalg.solve_triangular(l,torch.eye(97,device=x.device,dtype=x.dtype),upper=False)
    transform=torch.kron(torch.eye(5,device=x.device,dtype=x.dtype),li.T.contiguous());hp=transform.T@h@transform
    ep=torch.linalg.eigvalsh((hp+hp.T)/2)
    geometry=dict(reference_eigen_min=float(eigen[0]),reference_eigen_max=float(eigen[-1]),reference_condition=float(eigen[-1]/eigen[0]),
        cholesky_residual_max=float((l@l.T-ref).abs().max()),max_abs_training_coordinate=float(x.abs().max()),
        contrast_hessian_eigen_min=float(eh[0]),contrast_hessian_eigen_max=float(eh[-1]),contrast_hessian_condition=float(eh[-1]/eh[0]),
        preconditioned_hessian_eigen_min=float(ep[0]),preconditioned_hessian_eigen_max=float(ep[-1]),preconditioned_hessian_condition=float(ep[-1]/ep[0]),
        reference_geometry_not_full_Hessian=True,bias_translation_removed=True,new_fit_or_update=False)
    logs=[]
    for p in (RUN/'fit-logs').rglob('*.json'):
        v=read(p);logs.append(dict(role_id=v['role_id'],policy_id=v['arm'],source=v['arm'].split('__')[0],accepted=v['accepted'],iterations=v['iterations'],
                                 evaluations=v['function_evaluations'],gradient=v['max_gradient'],objective=v['objective'],seconds=v['seconds']))
    frame=pd.DataFrame(logs);accepted=frame[frame.accepted];diagnostic=list((RUN/'diagnostic-fit-logs').rglob('*.json'))
    assert len(accepted)==len(list((RUN/'models').rglob('*.pt')))
    p2=pd.read_parquet(RUN/'manifests/P2-endpoints.parquet');partial=pd.read_parquet(RUN/'manifests/P3-partial-endpoints.parquet')
    lines=failure['actual_optimizer_break']['line_searches'];cost=read(RUN/'cost-ledger.json')
    complete_outputs={p:(RUN/p).exists() for p in ['completion.json','verification.json','manifests/endpoint-seal.json','predictions/visits.parquet','predictions/complete.json','scores']}
    reads=[]
    for p in (RUN/'stages').glob('*.json'):reads.extend(read(p).get('reads',[]))
    for p in (RUN/'audits').glob('*reads-on-stop.json'):reads.extend(read(p).get('reads',[]))
    hreads=[r for r in reads if r['purpose'] in ['query','score','historical-probability-replay']]
    assert not hreads and not any(complete_outputs.values())
    notes=dict(initial_ad_hoc_readonly_replay_failed_before_matmul=True,
               initial_replay_reason='Missing CUBLAS_WORKSPACE_CONFIG in diagnostic process, not in training process; retried with recorded CUDA deterministic environment.',
               second_readonly_diagnostic_stopped_on_deterministic_cuda_bincount=True,
               diagnostic_repair='Use deterministic one-hot matrix multiplication for mass audit, same as original training; no numerical policy changed.',
               original_training_failure_unchanged=True,training_restarts=0)
    report=dict(status='stopped_numeric_iteration_budget_no_business_result',program_complete=False,H_scored=False,
        completed_stages=['P0','P1','P2'],new_scientific_accepted=len(accepted),scientific_attempts=len(frame),scientific_failed=int((~frame.accepted).sum()),
        unattempted=1920-len(frame),remaining_endpoints_including_failed=1920-len(accepted),additional_diagnostic_fits=len(diagnostic),
        total_fit_attempts=len(frame)+len(diagnostic),historical_aliases_verified=420,P2_completed=len(p2),P3_accepted=len(accepted)-len(p2),P3_partial_ledger_rows=len(partial),
        accepted_by_source=accepted.groupby('source').size().to_dict(),accepted_by_role=accepted.groupby('role_id').size().to_dict(),
        max_accepted_iterations=int(accepted.iterations.max()),max_accepted_gradient=float(accepted.gradient.max()),
        activity_seconds=cost['active_seconds'],activity_limit_seconds=28800,activity_remaining_seconds=28800-cost['active_seconds'],
        accepted_solver_seconds=float(accepted.seconds.sum()),failed_fit_log_seconds=float(frame[~frame.accepted].seconds.sum()),failed_failure_snapshot_seconds=failure['seconds'],
        failure={k:v for k,v in failure.items() if k!='actual_optimizer_break'},
        stop={k:v for k,v in failure['actual_optimizer_break'].items() if k!='line_searches'},
        line_search_summary=dict(count=len(lines),reasons=dict(collections.Counter(t['reason'] for t in lines)),armijo_failed=sum(not t['armijo'] for t in lines),curvature_failed=sum(not t['curvature'] for t in lines),last8_steps=[t['step'] for t in lines[-8:]]),
        independent_replay=dict(objective=float(value),gradient_inf=maximum,objective_error=objerr,gradient_error=graderr,rows=len(x),dtype=str(x.dtype),device=str(x.device),
                                bias_gradient_inf=float(gradient[:,-1].abs().max()),max_gradient_class_coordinate=torch.nonzero(gradient.abs()==gradient.abs().max())[0].cpu().tolist(),class_mass=(F.one_hot(y,6).double().T@mass).cpu().tolist()),
        geometry=geometry,completion_outputs=complete_outputs,H_query_or_label_read_events=len(hreads),new_training_during_analysis=0,notes=notes,source_hashes=bound)
    for p,h in bound.items():assert sha(ROOT/p)==h
    OUT.mkdir(parents=True,exist_ok=True);frame.to_parquet(OUT/'fit-inventory.parquet',index=False)
    report['analysis_seconds']=time.perf_counter()-started
    (OUT/'stop-analysis.json').write_text(json.dumps(report,ensure_ascii=False,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k not in ['failure','stop','accepted_by_role','source_hashes','notes']},ensure_ascii=False,indent=2))

if __name__=='__main__':main()
