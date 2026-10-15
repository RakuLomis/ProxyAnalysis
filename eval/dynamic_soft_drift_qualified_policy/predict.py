"""All H-post predictions, with exact baseline alias memoization."""
from common import *

def run():
    verify_seal(OUT/'manifests/models-complete.json');index=pd.read_parquet(OUT/'manifests/endpoints.parquet').set_index(['role_id','arm']);rows=[];aliases=0
    for r in contract()['roles']:
        query=package(PREP/'packages'/r['id']/'query.parquet','H-query','post-only-query',r);memo={}
        for arm in ALL_ARMS:
            ep=index.loc[(r['id'],arm)];key=ep['model_sha256'];p=ROOT/ep['model_path']
            checked(p,key,'frozen-endpoint-query');require(len(query)==24,'H-query count')
            if key not in memo:
                m=own(p) if p.is_relative_to(OUT) else registered_load(p,'reference',r);cuda(m['weight'],m['bias'],m['mu'],m['scale'])
                with torch.no_grad():
                    x=(tensor(query[HIST])-m['mu'])/m['scale'];z=x@m['weight'].T+m['bias'];lp=F.log_softmax(z,1);prob=lp.exp()
                require(torch.isfinite(lp).all() and torch.isfinite(prob).all(),'Finite frozen inference')
                d=pd.DataFrame(prob.cpu().numpy(),columns=[f'p{k}' for k in range(6)])
                for k in range(6):d[f'l{k}']=lp[:,k].cpu().numpy()
                d['prediction']=z.argmax(1).cpu().numpy();memo[key]=d
            else:aliases+=1
            d=memo[key].copy();d['visit_id']=query.visit_id.to_numpy()
            for name in ['id','outer','target','group']:d['role_id' if name=='id' else name]=r[name]
            d['arm']=arm;d['model_sha256']=key;rows.append(d)
    df=pd.concat(rows,ignore_index=True);require(len(df)==14400 and df.visit_id.nunique()==480 and not df.duplicated(['role_id','arm','visit_id']).any(),'Prediction coverage')
    cols=[f'p{i}' for i in range(6)]+[f'l{i}' for i in range(6)]+['prediction'];identical=0
    for (rid,arm),ep in index.iterrows():
        if arm not in ARMS or not ep['identity']:continue
        a=df[df.role_id.eq(rid)&df.arm.eq(arm)].sort_values('visit_id');b=df[df.role_id.eq(rid)&df.arm.eq(ep['alias_arm'])].sort_values('visit_id')
        require(np.array_equal(a[cols].to_numpy(),b[cols].to_numpy()),'Fallback inference not bitwise identical');identical+=1
    p=OUT/'predictions/visits.parquet';save(df,p);write(OUT/'predictions/complete.json',dict(passed=True,files={rel(p):sha(p)},rows=14400,visits=480,models_sealed=True,H_labels_read=False,test_pre_read=False,device='cuda:0',dtype='float64',exact_aliases=identical,memo_hits=aliases))
