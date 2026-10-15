"""Read-only engineering checkpoint verification; no models are fitted."""
from pathlib import Path
import hashlib
import json
import torch

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'outputs/post-input-associated-representation-20261014/run-02'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def require(ok,msg):
    if not ok:raise RuntimeError(msg)
def load(p):
    require(sha(p)==read(p.with_suffix('.json'))['sha256'],'Checkpoint changed')
    return torch.load(p,map_location='cpu',weights_only=True)

def run():
    c=read(OUT/'manifests/experiment-contract.json');same=read(OUT/'manifests/repair-scope.json')
    for p,h in same['parent_files'].items():require(sha(ROOT/p)==h,'Old stop/ledger changed')
    for name in ['engineering-code.json']:
        for p,h in read(OUT/'manifests'/name)['files'].items():require(sha(ROOT/p)==h,'Stable source changed')
    for p,h in read(OUT/'pilot/legacy-code.json')['files'].items():require(sha(ROOT/p)==h,'Legacy diagnostic source changed')
    rows=[];initial_equal=False
    for step in [0,1,10,100,1000]:
        name='initial.pt' if step==0 else f'step-{step:04d}.pt'
        a=load(OUT/'pilot/stable/standalone'/name);b=load(OUT/'pilot/stable/batched'/name)
        pe=max(float((a['states'][0][k]-b['states'][0][k]).abs().max()) for k in a['states'][0])
        le=float((a['logits'][0]-b['logits'][0]).abs().max())
        row=dict(step=step,parameter_max=pe,logit_max=le)
        if step==0:
            initial_equal=all(torch.equal(a[k][0],b[k][0]) for k in ['x','y','mass']) and pe==0
        else:
            row['gradient_max']=max(float((a['gradient_before_clip'][k][0]-b['gradient_before_clip'][k][0]).abs().max()) for k in a['states'][0])
            row['Adam_first_moment_max']=max(float((a['Adam'][k]['exp_avg'][0]-b['Adam'][k]['exp_avg'][0]).abs().max()) for k in a['states'][0])
        rows.append(row)
    require(initial_equal and all(r['parameter_max']==0 and r['logit_max']==0 for r in rows),'Stable checkpoint equivalence')
    result=dict(passed=True,initial_input_label_mass_equal=initial_equal,rows=rows,
                original_stop_and_ledger_preserved=True,legacy_and_stable_code_snapshots_unchanged=True,
                science_equal_fields=len(same['science_equal_fields']),new_fits=0,H_reads=0,U_reads=0)
    p=OUT/'pilot/repair-record-verification.json';require(not p.exists(),'Verification overwrite')
    p.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(json.dumps(result),flush=True)

if __name__=='__main__':run()
