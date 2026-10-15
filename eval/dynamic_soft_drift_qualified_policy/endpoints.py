"""Fit only enabled nonidentity endpoints; exact aliases otherwise."""
from common import *

def run():
    verify_seal(OUT/'manifests/policy-complete.json');decisions=pd.read_parquet(OUT/'manifests/policy-decisions.parquet').set_index(['role_id','arm']);rows=[];files={}
    _,u,_,_=production()
    for r in contract()['roles']:
        for arm in ARMS:
            d=decisions.loc[(r['id'],arm)].to_dict();q=own(ROOT/d['q_path'])['q']
            if d['identity']:
                p=ROOT/d['baseline_path'];m=registered_load(p,'reference',r);require(sha(p)==d['baseline_sha256'],'Fallback alias changed')
                row=dict(role_id=r['id'],arm=arm,model_path=rel(p),model_sha256=sha(p),new_fit=False,alias_arm=d['baseline_arm'],enabled=bool(d['enabled']),fallback=bool(d['fallback']),identity=True)
            else:
                require(d['enabled'],'Cannot fit unqualified endpoint');kind=kind_for(arm)
                v=parent_asset(PARENT/'tasks'/r['id']/(kind+'.pt'),'task',kind,r['id'],arm)['view']
                s=u.pack(v,{'P':'D-P','G':'D-G'}[kind],q);require(len(s['x'])==928 and abs(float(s['mass'].sum())-1)<1e-12 and float((weighted(s['y'],s['mass'],6)-1/6).abs().max())<1e-12,'Final training slot')
                put(s,OUT/'final-slots'/r['id']/(arm+'.pt'),role_id=r['id'],arm=arm,kind=kind,rows=928,q_path=d['q_path'])
                ledger(new_final_LR=1);m,log=solver().fit_preconditioned(s['x'],s['y'],s['mass'],r['t'],dict(role_id=r['id'],arm=arm))
                m.update(mu=v['mu'],scale=v['scale']);p=OUT/'models'/r['id']/(arm+'.pt');put(m,p,role_id=r['id'],arm=arm,kind=kind,t=r['t'],optimizer=log)
                row=dict(role_id=r['id'],arm=arm,model_path=rel(p),model_sha256=sha(p),new_fit=True,alias_arm='',enabled=True,fallback=False,identity=False)
                raw=production()[0].adjust(v['pre_x'],v['mapped_x'],q)*v['scale']+v['mu'];fmt=[]
                for j in range(10):
                    b=raw[:,block(j)];fmt.append(dict(role_id=r['id'],arm=arm,feature=FEATURES[j],q=float(q[j]),negative_rows=int((b<0).any(1).sum()),max_sum_error=float((b.sum(1)-1).abs().max()),rows=len(b)))
                save(pd.DataFrame(fmt),OUT/'audits/format'/r['id']/(arm+'.parquet'))
            rows.append(row)
            for path in [p,p.with_suffix('.json')]:files[rel(path)]=sha(path)
        progress('final_endpoints',roles_complete=len(rows)//3,new_fits=read(OUT/'ledger.json')['new_final_LR'])
    for ref in contract()['references']:
        p=ROOT/ref['model_path'];registered_load(p,'reference');rows.append(dict(ref,alias_arm='',enabled=False,fallback=False,identity=False,new_fit=False))
        for path in [p,p.with_suffix('.json')]:files[rel(path)]=sha(path)
    require(len(rows)==600 and len({(x['role_id'],x['arm']) for x in rows})==600,'All endpoint coverage')
    require(sum(x['new_fit'] for x in rows)==read(OUT/'ledger.json')['new_final_LR'],'Actual fit count')
    save(pd.DataFrame(rows),OUT/'manifests/endpoints.parquet');files[rel(OUT/'manifests/endpoints.parquet')]=sha(OUT/'manifests/endpoints.parquet')
    files[rel(OUT/'manifests/policy-complete.json')]=sha(OUT/'manifests/policy-complete.json')
    write(OUT/'manifests/models-complete.json',dict(passed=True,files=files,logical_endpoints=600,new_models=sum(x['new_fit'] for x in rows),unique_models=len({x['model_sha256'] for x in rows}),policy_aliases=sum(x['arm'] in ARMS and x['identity'] for x in rows),H_numeric_read=False))
