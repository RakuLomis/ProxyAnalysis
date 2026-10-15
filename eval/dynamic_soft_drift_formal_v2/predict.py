"""Two-stage sealing: all endpoints before H input, all predictions before labels."""
from common import *

def seal_models():
    with stage('seal_models'):
        rows=[];files={}
        for r in contract()['roles']:
            for arm in ARMS:
                p=OUT/'models'/r['id']/(arm+'.pt');m=own(p);info=read(p.with_suffix('.json'))
                require(info['optimizer']['accepted'],'Final model not accepted')
                q=OUT/'q'/r['id']/(arm+'.pt');qi=read(q.with_suffix('.json'));require(qi['updates']==20 and qi['selected_state']==20,'Wrong q checkpoint')
                for path in [p,p.with_suffix('.json'),q,q.with_suffix('.json'),OUT/'trajectories'/r['id']/(arm+'.parquet')]:files[rel(path)]=sha(path)
                for k in range(21):
                    point=OUT/'trajectories'/r['id']/arm/f'q{k:02d}.pt';require(read(point.with_suffix('.json'))['accepted'],'Incomplete trajectory');files[rel(point)]=sha(point);files[rel(point.with_suffix('.json'))]=sha(point.with_suffix('.json'))
                rows.append(dict(role_id=r['id'],arm=arm,model_path=rel(p),model_sha256=sha(p),new_fit=True))
        for row in contract()['references']:
            p=ROOT/row['model_path'];checked(p,row['model_sha256'],'old-endpoint-seal');files[rel(p)]=sha(p);files[rel(p.with_suffix('.json'))]=sha(p.with_suffix('.json'));rows.append(dict(row,new_fit=False))
        require(len(rows)==600 and read(OUT/'ledger.json')['new_final_LR']==180,'Endpoint coverage')
        for p in (OUT/'tasks').rglob('*.pt'):files[rel(p)]=sha(p)
        for p in (OUT/'C-coefficients').rglob('*.pt'):files[rel(p)]=sha(p)
        save(pd.DataFrame(rows),OUT/'manifests/endpoints.parquet');files[rel(OUT/'manifests/endpoints.parquet')]=sha(OUT/'manifests/endpoints.parquet')
        write(OUT/'manifests/models-complete.json',dict(passed=True,new_models=180,old_models=420,files=files,H_numeric_read=False))

def run():
    with stage('predict'):
        c=contract();verify_seal(OUT/'manifests/models-complete.json');refs={(r['role_id'],r['arm']):r for r in c['references']};rows=[]
        for r in c['roles']:
            q=package(PREP/'packages'/r['id']/'query.parquet','H-query','post-only-query',r)
            for arm in ALL_ARMS:
                if arm in ARMS:m=own(OUT/'models'/r['id']/(arm+'.pt'))
                else:m=artifact(ROOT/refs[(r['id'],arm)]['model_path'],'shared','reference',r)
                cuda(m['weight'],m['bias'],m['mu'],m['scale'])
                with torch.no_grad():
                    x=(tensor(q[HIST])-m['mu'])/m['scale'];z=x@m['weight'].T+m['bias'];lp=F.log_softmax(z,1);p=lp.exp()
                require(torch.isfinite(lp).all() and torch.isfinite(p).all(),'Nonfinite frozen inference')
                d=pd.DataFrame(p.cpu().numpy(),columns=[f'p{k}' for k in range(6)])
                for k in range(6):d[f'l{k}']=lp[:,k].cpu().numpy()
                d['prediction']=z.argmax(1).cpu().numpy();d['visit_id']=q.visit_id.to_numpy()
                for key in ['id','outer','target','group']:d['role_id' if key=='id' else key]=r[key]
                d['arm']=arm;rows.append(d)
        result=pd.concat(rows,ignore_index=True)
        require(len(result)==14400 and result.visit_id.nunique()==480 and not result.duplicated(['role_id','arm','visit_id']).any(),'Prediction coverage')
        save(result,OUT/'predictions/visits.parquet');p=OUT/'predictions/visits.parquet'
        write(OUT/'predictions/complete.json',dict(passed=True,files={rel(p):sha(p)},rows=14400,models_sealed=True,H_labels_read=False,test_pre_read=False,device='cuda:0',dtype='float64'))

if __name__=='__main__':{'seal':seal_models,'query':run}[sys.argv[1]]()

