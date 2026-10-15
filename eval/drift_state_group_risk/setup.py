"""Trusted cache packer and pre-fit contract seal."""
import platform
import sys
from common import *

def tests():
    logs=[]
    def check(name,ok): require(ok,name); logs.append({'test':name,'pass':True})
    y=tensor(np.repeat(np.arange(6),4),torch.long); score=tensor(np.tile([1,2,2,3],6))
    gamma,bd=partition(score,y)
    check('boundary ties fractional, identity-free',torch.equal(gamma[:4,0],tensor([1,.5,.5,0])))
    tie,_=partition(torch.ones_like(score),y); check('all ties both half',torch.equal(tie,torch.full_like(tie,.5)))
    torch.manual_seed(20261005); x=torch.randn(24,96,device=device(),dtype=torch.float64)/10
    w=torch.randn(6,96,device=device(),dtype=torch.float64)/20; b=torch.zeros(6,device=device(),dtype=torch.float64)
    loss,p=objective(w,b,x,y,gamma,w,b,.25)
    check('state mean equals CE',abs(float((p['R0']+p['R1'])/2-p['CE']))<1e-12)
    check('robust no less than mean',float(p['drift_gap'])>=-1e-12)
    zero,p0=objective(w,b,x,y,gamma,w,b,0.)
    check('base protection zero',float(p0['stay'])==0)
    _,shift=objective(w,b+3,x,y,gamma,w,b,.25)
    check('uniform bias shift protection invariant',float(shift['stay'])<1e-28)
    check('alpha zero original target',abs(float(zero-(F.cross_entropy(x@w.T+b,y)+.0005*w.square().sum())))<1e-12)
    wt=w.clone().requires_grad_(); bt=b.clone().requires_grad_(); v,_=objective(wt,bt,x,y,gamma,w,b,.25)
    grad=torch.autograd.grad(v,wt)[0][0,0]; eps=1e-5; plus=w.clone(); minus=w.clone(); plus[0,0]+=eps; minus[0,0]-=eps
    fd=(objective(plus,b,x,y,gamma,w,b,.25)[0]-objective(minus,b,x,y,gamma,w,b,.25)[0])/(2*eps)
    check('analytic finite difference gradient',abs(float(grad-fd))<1e-8)
    mid=objective(w*.8,b,x,y,gamma,w,b,.5)[0]
    ends=(objective(w*.6,b,x,y,gamma,w,b,.5)[0]+objective(w,b,x,y,gamma,w,b,.5)[0])/2
    check('convex Jensen test',float(mid)<=float(ends)+1e-12)
    illegal=pd.DataFrame({**{h:[0.] for h in HIST},'visit_id':['x'],'pre_W_up':[1]})
    caught=False
    try: validate_query(illegal)
    except RuntimeError: caught=True
    check('pre field rejected at inference',caught)
    from grouping import group_scores
    caught=False
    try: group_scores(pd.DataFrame({'visit_id':['x'],'content_id':['c'],'pre_W_up':[1]}),pd.DataFrame(),[])
    except RuntimeError: caught=True
    check('anonymous query rejects exact pre identity',caught)
    caught=False
    try:
        group_scores(pd.DataFrame({'visit_id':['x'],'content_id':['c'],**{'post_'+f:[1] for f in FEATURES}}),
                     pd.DataFrame({'content_id':['c'],'visit_id':['x'],**{h:[0.] for h in HIST}}),[])
    except RuntimeError: caught=True
    check('anonymous pre marginal rejects visit identity',caught)
    for name,source,query,parent in [('overlap',['a'],['a'],['a']),('wrong cache',['a','c'],['b'],['a','b'])]:
        caught=False
        try: validate_scope(source,query,parent)
        except RuntimeError: caught=True
        check('reject '+name,caught)
    validate_scope(['a'],['b'],['a','b'])
    check('CUDA weighted count deterministic',torch.equal(weighted(tensor([0,1,1],torch.long),tensor([.3,.2,.5]),2),tensor([.3,.7])))
    check('right edge fixed bins',torch.equal(bins([0,1,256,4096],0),tensor([0,1,2,4],torch.long)))
    write(OUT/'manifests/unit-tests.json',logs)

def main():
    configure(); require(not (OUT/'manifests/experiment-contract.json').exists(),'Registration exists; no overwrite')
    old=read(OLD/'manifests/experiment-contract.json'); baseline={}
    for p,h in {**old['source_sha256'],**old['packages_sha256']}.items():
        require(sha(ROOT/p)==h,'Frozen source/package differs'); baseline[p]=h
    for p in [PLAN,OLD/'selection/choices.json',OLD/'selection/complete.json',
              Q/'features/paired-flow-features.parquet',Q/'cohorts/folds.parquet',OLD/'verification.json']:
        baseline[rel(p)]=sha(p)
    df=pd.read_parquet(Q/'features/paired-flow-features.parquet'); folds=pd.read_parquet(Q/'cohorts/folds.parquet')
    require(len(df)==23566 and df.session_id.nunique()==480 and df.content_id.nunique()==30 and df.pair_id.is_unique,'Cohort')
    for field in ['pair_id','session_id','logical_id','carrier_id','registered_epoch_proxy']:
        require(df.groupby(field).fold.nunique().max()==1,'Registered entity crosses global folds')
    df['visit_id']=df.session_id.map(visitid); pool=[]
    for proto in PROTOCOLS:
        r={'outer':0,'inner':None,'protocol':proto}; src=oldfolder('packages',r)
        tr=pd.read_parquet(src/'fit-post-hist.parquet'); tr['visit_id']=tr.session_id.map(visitid)
        labels=pd.read_parquet(src/'score-labels.parquet'); query=pd.read_parquet(src/'query-post-hist.parquet')
        te=query.merge(labels,on='visit_id',validate='one_to_one'); pp=pd.concat([tr,te],ignore_index=True)
        pp=pp[['visit_id','content_id','label_id',*HIST]]; pp['protocol']=proto
        require(len(pp)==120 and pp.visit_id.is_unique,'Histogram pool'); pool.append(pp)
    hist=pd.concat(pool,ignore_index=True); packages={}; roles=old['roles']; sources={}; queries=[]; audit=[]
    def store(frame,path): save(frame,path); packages[rel(path)]=sha(path)
    def flow_subset(proto,contents): return df[(df.protocol==proto)&df.content_id.isin(contents)].copy().sort_values('pair_id')
    for r in roles:
        tr=set(r['train_contents']); va=set(r['validation_contents']); root=mainfolder('packages',r)
        require(not tr&va and not tr&set(r.get('outer_test_contents',[])),'Main role leakage')
        h=hist[(hist.protocol==r['protocol'])&hist.content_id.isin(tr)].drop(columns='protocol').sort_values('visit_id')
        v=hist[(hist.protocol==r['protocol'])&hist.content_id.isin(va)].sort_values('visit_id')
        store(h,root/'train-post.parquet'); store(v[['visit_id',*HIST]],root/'query-post.parquet')
        score=v[['visit_id','content_id','label_id','protocol']].copy(); score['fold']=r['inner'] if r['inner'] is not None else r['outer']
        store(score,root/'score-labels.parquet')
        if r['inner'] is None:
            raw=flow_subset(r['protocol'],va)
            store(raw[['visit_id','content_id','label_id',*['pre_'+f for f in FEATURES],*['post_'+f for f in FEATURES]]],root/'test-paired.parquet')
        for name in ['zero']+['KSR1-t'+format(t,'g') for t in [.25,1,4]]:
            p=oldfolder('models',r)/(name+'.pt')
            if p.exists():
                require(read(p.parent/'complete.json')['sha256'][p.name]==sha(p),'Old LR seal'); baseline[rel(p)]=sha(p)
        remaining=sorted(folds[folds.content_id.isin(tr)].fold.unique().tolist())
        require(len(remaining)==(4 if r['inner'] is None else 3),'Parent training folds')
        for held in remaining:
            querycontents=sorted(folds[folds.fold==held].content_id.tolist()); traincontents=sorted(tr-set(querycontents))
            if r['inner'] is None:
                sourceid=f"cf18/f{r['outer']}/{r['protocol']}/i{held}"
                oldr=next(x for x in roles if x['outer']==r['outer'] and x['protocol']==r['protocol'] and x['inner']==held)
                source={'id':sourceid,'kind':'old18','protocol':r['protocol'],'train_contents':traincontents,'old_role':oldr}
                require(set(oldr['train_contents'])==set(traincontents),'Old CF member mismatch')
                for f in FEATURES:
                    p=oldfolder('kernels',oldr)/(f+'.pt'); require(read(p.parent/'complete.json')['sha256'][p.name]==sha(p),'Old kernel seal'); baseline[rel(p)]=sha(p)
            else:
                trainfolds=sorted(set(remaining)-{held}); sourceid=f"cf12/{r['protocol']}/s{''.join(map(str,trainfolds))}"
                source={'id':sourceid,'kind':'new12','protocol':r['protocol'],'train_contents':traincontents}
            if sourceid in sources: require(sources[sourceid]['train_contents']==traincontents,'Wrong cache scope')
            else: sources[sourceid]=source
            q={'id':rolekey(r)+f'/g{held}','parent':r,'source':sourceid,'held':int(held),'query_contents':querycontents}
            validate_scope(traincontents,querycontents,tr)
            queries.append(q); qr=queryfolder('packages',q); raw=flow_subset(r['protocol'],querycontents)
            store(raw[['visit_id','content_id',*['pre_'+f for f in FEATURES],*['post_'+f for f in FEATURES]]],qr/'query-paired.parquet')
            store(raw[['visit_id','content_id',*['post_'+f for f in FEATURES]]].sample(frac=1,random_state=72),qr/'query-group-post.parquet')
            # Only aggregated content bins are exposed to anonymous queries.
            vals=[]
            for content,part in raw.groupby('content_id'):
                record={'content_id':content}
                for j,f in enumerate(FEATURES):
                    mass=tensor(part.content_visit_flow_mass); z=weighted(bins(part['pre_'+f],j),mass,size(j)); z=z/z.sum()
                    record.update({f'h{j:02d}_{b:02d}':float(z[b]) for b in range(size(j))})
                vals.append(record)
            store(pd.DataFrame(vals),qr/'query-group-pre.parquet')
            hh=hist[(hist.protocol==r['protocol'])&hist.content_id.isin(querycontents)].sort_values('visit_id')
            store(hh[['visit_id',*HIST]],qr/'query-post.parquet'); store(hh[['visit_id','content_id','label_id']],qr/'query-labels.parquet')
            audit.append({'query':q['id'],'source':sourceid,'source_contents':len(traincontents),'query_contents':6,
                          'query_visits':len(hh),'member_overlap':0})
    require(len(roles)==100 and len(queries)==320 and sum(s['kind']=='new12' for s in sources.values())==40,'Role/cache counts')
    for source in sources.values():
        if source['kind']!='new12': continue
        raw=flow_subset(source['protocol'],source['train_contents']); src=sourcefolder('packages',source)
        paired=raw[['pair_id','visit_id','content_id',*['pre_'+f for f in FEATURES],*['post_'+f for f in FEATURES]]].copy()
        paired['fit_mass']=raw.content_visit_flow_mass.to_numpy(); store(paired,src/'fit-paired.parquet')
        for side in ['pre','post']:
            group=paired[['content_id','fit_mass',*[side+'_'+f for f in FEATURES]]].sample(frac=1,random_state=91 if side=='pre' else 92)
            store(group,src/('group-'+side+'.parquet'))
        hh=hist[(hist.protocol==source['protocol'])&hist.content_id.isin(source['train_contents'])].drop(columns='protocol').sort_values('visit_id')
        require(len(hh)==48 and abs(paired.fit_mass.sum()-12)<1e-10,'CF12 size/mass')
        store(hh,src/'train-post.parquet')
    tests()
    files=list(Path(__file__).parent.glob('*.py'))+[Path(__file__).parent/'README.md']
    write(OUT/'manifests/experiment-contract.json',{'registered_unix':time.time(),'roles':roles,'sources':list(sources.values()),'queries':queries,
      'source_sha256':{rel(p):sha(p) for p in files},'packages_sha256':packages,'baseline_sha256':baseline,
      'alpha':ALPHAS,'tau':TAU,'eta':ETA,'rho':.001,'features':FEATURES,'weights':WEIGHTS,'labels':LABELS,
      'main_family':3,'main_comparisons':['DSR4-DSR1','DSR4-DSR2','DSR4-DSR3'],'practical_gain_vs_DSR1':.01,
      'bootstrap':{'samples':10000,'seed':20261005,'shared_by_content':True,'fixed_models':True},
      'fit_quality_max_gradient':1e-5,'permission_whitelist_not_OS_sandbox':True,
      'CF12_dedup':'40 unique training memberships for 240 logical queries; no query-based fit choices',
      'new_classifier_fit_budget_upper':1020,'stop_after_report':True})
    write(OUT/'manifests/role-audit.json',audit)
    write(OUT/'manifests/environment.json',{'python':sys.version,'executable':sys.executable,'torch':torch.__version__,
      'cuda':torch.version.cuda,'gpu':torch.cuda.get_device_name(0),'dtype':'float64','deterministic':True,
      'TF32':False,'arrow_before_torch':True,'platform':platform.platform()})
    finish('D00-D09',roles=100,CF_logical_roles=320,unique_CF12_sources=40,pairs=len(df),visits=480)

if __name__=='__main__': main()
