"""Global model/prediction barriers, two-policy source selection, closed H inference."""
from common import *
from deploy import base_logp,branch_logp,mixture
from worker import modelroot

def candidates(arm):return [dict(id=gamma_tag(g),gamma=g,lr=0) for g in GAMMAS] if arm.startswith('R-') else RECIPES

def historical(r,kind):
    require(kind in ['query','labels'],'Closed deferred reader')
    inner=r['inner'] is not None
    barrier(('P2-models-complete.json' if inner else 'P4-models-complete.json') if kind=='query' else ('P2-predictions-complete.json' if inner else 'P5-predictions-complete.json'))
    p=PREP/'packages'/r['id']/(kind+'.parquet');info=contract()['files'][rel(p)]
    require(info['kind']==kind and info['role_id']==r['id'] and sha(p)==info['sha256'],'Deferred source identity/hash')
    READS.append(dict(path=rel(p),role_id=r['id'],kind=kind,phase='inner' if inner else 'H',sha256=info['sha256']))
    d=pd.read_parquet(p)
    require(len(d)==24 and d.visit_id.is_unique,'Deferred query/label cardinality')
    if kind=='query':require(set(d)=={'visit_id',*HIST},'Query has non-post feature fields')
    return d

def base(r):return external(ASSOC/'base-models'/r['id']/'P-small.pt',r['id'],'base')

def source_model_seal():
    barrier('P1-complete.json');files=[]
    for r in contract()['inner_roles']:
        for arm in METHODS:
            for rec in candidates(arm):
                p=modelroot(r,arm,rec['id'],SEEDS[0])/'complete.json';verifyseal(p);files.append(p)
    require(len(files)==21600,'All inner static+dynamic endpoints')
    seal(OUT/'manifests/P2-models-complete.json',files,models=21600,inner_contexts=720,query_reads=0)

def source_predict():
    configure('inference');barrier('P2-models-complete.json');hashes=code_seal('P2-predict');files=[]
    try:
        for i,r in enumerate(contract()['inner_roles']):
            query=historical(r,'query');raw=tensor(query[HIST]);names=['B0'];logs=[]
            with compute('inner-post-inference',role_id=r['id']),torch.no_grad():
                logs.append(base_logp(raw,base(r)))
                for arm in METHODS:
                    for rec in candidates(arm):
                        p=modelroot(r,arm,rec['id'],SEEDS[0])/'export.pt'
                        logs.append(branch_logp(raw,own(p,r['id'])));names.append(arm+'::'+rec['id'])
                lp=torch.stack(logs);require(bool(torch.isfinite(lp).all()),'Nonfinite inner log-probability')
            p=OUT/'inner-predictions'/r['id']/'post.pt'
            put(p,dict(names=names,logp=lp,visit_ids=query.visit_id.tolist()),role_id=r['id'],capability='export',query_rows=24,base_rows=744)
            files.append(p);flush_reads('P2-predict');progress('P2_predictions',completed=i+1,total=720)
        seal(OUT/'manifests/P2-predictions-complete.json',files,base_records=535680,logical_fusion_records=2592000,
            mixtures='closed logaddexp plus exact beta0/beta1 aliases; no label-dependent calculations',labels_read=0)
        codecheck(hashes)
    except BaseException as e:failure('P2-predict',e);raise

def truth(d):
    y=d.label_id.map(dict(zip(LABELS,range(6))));require(y.notna().all(),'Unknown label');return y.to_numpy(int)

def metrics(y,lp,missing):
    z=lp.argmax(1);p=np.exp(lp);cm=np.bincount(y*6+z,minlength=36).reshape(6,6)
    den=cm.sum(0)+cm.sum(1);f=np.divide(2*np.diag(cm),den,out=np.zeros(6),where=den>0)
    use=np.isin(y,missing);ce=-lp[np.arange(len(y)),y];br=((p-np.eye(6)[y])**2).sum(1)
    out=dict(F1_all=float(f.mean()),F1_U=float(f[missing].mean()),F1_C=float(np.delete(f,missing).mean()),
        CE=float(ce.mean()),CE_U=float(ce[use].mean()),CE_C=float(ce[~use].mean()),Brier=float(br.mean()),Brier_U=float(br[use].mean()),Brier_C=float(br[~use].mean()))
    return out,cm,f

def choose(values,policy):
    # Explicit sequential ties at 1e-12: do not replace by rounded sorting.
    best=max(v['F1_U'] for v in values);pool=[v for v in values if v['F1_U']>=best-1e-12]
    ce=min(v['CE_U'] for v in pool);pool=[v for v in pool if v['CE_U']<=ce+1e-12]
    return min(pool,key=lambda v:((v['beta'],) if policy=='FUSE' else ())+(-v['gamma'],v['lr'],v['candidate']))

def selection():
    configure('inference');barrier('P2-predictions-complete.json');hashes=code_seal('P3-select');rows=[];decisions=[];static={};dynamic={}
    for outer in contract()['roles']:
        inners=[r for r in contract()['inner_roles'] if (r['outer'],r['target'],r['group'])==(outer['outer'],outer['target'],outer['group'])]
        require(len(inners)==12,'Twelve source tasks')
        cached={}
        for r in inners:
            p=own(OUT/'inner-predictions'/r['id']/'post.pt',r['id']);labels=historical(r,'labels').set_index('visit_id').loc[p['visit_ids']].reset_index()
            cached[r['id']]=(p,truth(labels))
        for arm in METHODS:
            vals=[]
            for rec in candidates(arm):
                for beta in BETAS:
                    sub=[]
                    for proto in outer['sources']:
                        ys=[];ls=[]
                        for r in inners:
                            if r['calibration']!=proto:continue
                            p,y=cached[r['id']];ix=p['names'].index(arm+'::'+rec['id'])
                            lp=mixture(p['logp'][0],p['logp'][ix],beta);ys.append(y);ls.append(cpu(lp))
                        require(sum(len(y) for y in ys)==96,'Four full inner folds')
                        sub.append(metrics(np.concatenate(ys),np.concatenate(ls),outer['missing'])[0])
                    v=dict(role_id=outer['id'],arm=arm,candidate=rec['id'],beta=beta,gamma=rec['gamma'],lr=rec['lr'],
                        **{k:float(np.mean([x[k] for x in sub])) for k in sub[0]})
                    vals.append(v);rows.append(v)
            for policy in ['PURE','FUSE']:
                win=choose([v for v in vals if v['beta']==1] if policy=='PURE' else vals,policy)
                dec=dict(**win,policy=policy,inactive=policy=='FUSE' and win['beta']==0);decisions.append(dec)
                if dec['inactive']:continue
                if arm.startswith('R-'):
                    key=(outer['id'],arm,win['candidate']);static[key]=dict(role_id=outer['id'],arm=arm,gamma=win['gamma'],candidate=win['candidate'])
                else:
                    for seed in SEEDS:
                        key=(outer['id'],arm,win['candidate'],seed);dynamic[key]=dict(role_id=outer['id'],arm=arm,seed=seed,recipe=next(v for v in RECIPES if v['id']==win['candidate']))
        flush_reads('P3');progress('P3_selection',completed=len(decisions)//12,total=60)
    require(len(decisions)==720,'Two policies x six methods x 60 roles')
    save(OUT/'selections/candidate-metrics.parquet',pd.DataFrame(rows));immutable(OUT/'selections/decisions.json',decisions)
    immutable(OUT/'selections/outer-fit-jobs.json',dict(static=list(static.values()),dynamic=list(dynamic.values())))
    seal(OUT/'manifests/P3-complete.json',[OUT/'selections/candidate-metrics.parquet',OUT/'selections/decisions.json',OUT/'selections/outer-fit-jobs.json'],policies=720)
    codecheck(hashes)

def outer_model_seal():
    barrier('P3-complete.json');decisions=read(OUT/'selections/decisions.json');files=[];endpoints=[]
    for r in contract()['roles']:
        for seed in SEEDS:
            endpoints.append(dict(role_id=r['id'],pipeline='B0',seed=seed,beta=0.,export_path=None))
            for d in [v for v in decisions if v['role_id']==r['id']]:
                path=None if d['inactive'] else modelroot(r,d['arm'],d['candidate'],SEEDS[0] if d['arm'].startswith('R-') else seed)
                if path is not None:verifyseal(path/'complete.json');files.append(path/'complete.json')
                endpoints.append(dict(role_id=r['id'],pipeline=d['arm']+'-'+d['policy'],seed=seed,beta=d['beta'],export_path=None if path is None else rel(path/'export.pt')))
    require(len(endpoints)==2340,'All outer logical endpoints')
    immutable(OUT/'manifests/outer-endpoints.json',endpoints);files.append(OUT/'manifests/outer-endpoints.json')
    seal(OUT/'manifests/P4-models-complete.json',list(dict.fromkeys(files)),endpoints=2340,H_read=False)

def outer_predict():
    configure('inference');barrier('P4-models-complete.json');hashes=code_seal('P5-predict');out=[]
    eps=read(OUT/'manifests/outer-endpoints.json')
    for r in contract()['roles']:
        query=historical(r,'query');raw=tensor(query[HIST]);cache={}
        with compute('H-post-inference',role_id=r['id']),torch.no_grad():
            lp0=base_logp(raw,base(r));cache[None]=lp0
            for e in [v for v in eps if v['role_id']==r['id']]:
                path=e['export_path']
                if path not in cache:cache[path]=branch_logp(raw,own(ROOT/path,r['id']))
                lp=mixture(lp0,cache[path],e['beta']);require(bool(torch.isfinite(lp).all()),'H nonfinite prediction')
                d=pd.DataFrame(cpu(lp),columns=[f'l{k}' for k in range(6)])
                for k in range(6):d[f'p{k}']=np.exp(d[f'l{k}'])
                d['prediction']=lp.argmax(1).cpu().numpy();d['visit_id']=query.visit_id.to_numpy()
                for k in ['role_id','pipeline','seed','beta']:d[k]=e[k]
                d['target']=r['target'];d['group']=r['group'];d['outer']=r['outer'];out.append(d)
        flush_reads('P5');progress('P5_H_post_predictions',completed=len(out)//39,total=60)
    d=pd.concat(out,ignore_index=True);require(len(d)==56160,'H logical prediction coverage')
    save(OUT/'predictions/post-only.parquet',d);seal(OUT/'manifests/P5-predictions-complete.json',[OUT/'predictions/post-only.parquet'],rows=56160,H_labels_read=False)
    codecheck(hashes)
