"""Deployed computation consumes post values and model parameters only."""
from common import *
from models import logits
from deploy import predict_post

def run():
    with stage('P4_predict'):
        verifyseal(OUT/'manifests/engineering-code.json');verifyseal(OUT/'manifests/models-complete.json')
        endpoints=read(OUT/'manifests/endpoints.json');rows=[]
        for r in contract()['roles']:
            q=oldpackage(PREP/'packages'/r['id']/'query.parquet',r,'H-predict');require(set(q)=={'visit_id',*HIST},'Post-only query schema')
            raw=tensor(q[HIST]);m=own(OUT/'base-models'/r['id']/'P-small.pt','inference')
            for e in [e for e in endpoints if e['role_id']==r['id']]:
                state=None if e['residual_path'] is None else own(ROOT/e['residual_path'],'inference')['state']
                lp=predict_post(raw,m,state);p=lp.exp()
                d=pd.DataFrame(p.cpu().numpy(),columns=[f'p{i}' for i in range(6)])
                for i in range(6):d[f'l{i}']=lp[:,i].cpu().numpy()
                d['visit_id']=q.visit_id.to_numpy();d['prediction']=lp.argmax(1).cpu().numpy()
                d['role_id']=r['id'];d['arm']=e['arm'];d['seed']=e['seed'];d['target']=r['target'];d['group']=r['group'];d['outer']=r['outer'];rows.append(d)
        result=pd.concat(rows,ignore_index=True);require(len(result)==17280,'H predictions count')
        save(result,OUT/'predictions/visits.parquet');seal(OUT/'predictions/complete.json',[OUT/'predictions/visits.parquet'],passed=True,rows=17280,H_pre_reads=0)

if __name__=='__main__':run()
