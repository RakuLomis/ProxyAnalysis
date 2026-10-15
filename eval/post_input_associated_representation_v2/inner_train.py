"""Source-only deterministic matrix, caching only accepted complete models."""
from common import *
from teacher import fit_batch as teachers
from train import fit_batch as residuals
from models import logits

def prediction(r,arm,lam,seed):
    reader=cfg_arm(arm,lam)
    root=OUT/'inner-models'/r['id']/tag(reader,lam,seed)
    m=own(PARENT/'base-models'/r['id']/'P-small.pt','branch',reader)
    state=own(root/'terminal.pt','branch',reader)['state']
    q=oldpackage(PREP/'packages'/r['id']/'query.parquet',r,'inner-predict')
    x=(tensor(q[HIST])-m['mu'])/m['scale']
    with torch.no_grad():z=logits(state,x,m);z0=logits(None,x,m)
    d=pd.DataFrame(z.softmax(1).cpu().numpy(),columns=[f'p{i}' for i in range(6)])
    for j in range(6):d[f'l{j}']=F.log_softmax(z,1)[:,j].cpu().numpy();d[f'bp{j}']=z0.softmax(1)[:,j].cpu().numpy()
    d['visit_id']=q.visit_id.to_numpy();d['role_id']=r['id'];d['arm']=arm;d['lambda']=lam;d['seed']=seed
    d['calibration']=r['calibration'];d['group']=r['group'];d['outer']=r['outer'];d['actual_target']=r['target'];d['inner']=r['inner']
    return d

def run():
    with stage('P2_inner_train',training=True):
        verifyseal(OUT/'manifests/engineering-code.json');require(read(OUT/'pilot/summary.json')['within_preflight'],'Pilot gate')
        rs=contract()['inner_roles'];parts=[]
        for batch in range(0,len(rs),12):
            chunk=rs[batch:batch+12];budget()
            missing=[r for r in chunk if not (OUT/'teachers'/r['id']/'teacher.pt').exists()]
            if missing:teachers(missing)
            jobs=[(r,arm,lam,seed) for r in chunk for arm,lam in CONFIGS for seed in SEEDS
                  if not (OUT/'inner-models'/r['id']/tag(arm,lam,seed)/'terminal.pt').exists()]
            for k in range(0,len(jobs),32):residuals(jobs[k:k+32])
            for r in chunk:
                for arm,lam in CONFIGS:
                    for seed in SEEDS:parts.append(prediction(r,arm,lam,seed))
            progress('P2_source_matrix',roles=min(batch+12,len(rs)),total=len(rs),residual_fits=read(OUT/'ledger.json')['residual_fits'])
        d=pd.concat(parts,ignore_index=True);require(len(d)==720*5*3*24,'Inner prediction count')
        save(d,OUT/'inner-predictions/post-only.parquet')
        seal(OUT/'inner-predictions/complete.json',[OUT/'inner-predictions/post-only.parquet'],passed=True,rows=len(d),H_reads=0)

if __name__=='__main__':run()
