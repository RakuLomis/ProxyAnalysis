"""JAT1 immutable phase barriers, exact physical-fit aliases and bounded dispatch.

The learner receives training tensors only. Query/labels have distinct readers
which cannot open their registered files until the appropriate global seal.
"""
from common import *
from data import TrainingPool,pilot_roles,canonical_jobs,materialize
from models import initial,loss_one,loss_independent,forward_post
from train import Engine
from telemetry import Sampler
import gc

HIST=[f'h{i:02}_{j:02}' for i,n in enumerate([9]*4+[10]*6) for j in range(n)]
LABELS=['bing.com::search_results_view','developer.mozilla.org::document_view',
        'github.com::repository_view','wikipedia.org::article_view',
        'youtube.com::search_results_view','youtube.com::video_playback']
ARMS=['B0','JC','JP','JG','FR','MX00','MX01','MX10']
_SEAL_CACHE={}

def authorize():
    p=OUT/'manifests/execution-authorization.json'
    if p.exists():return authorized()
    ix=read(OUT/'engineering/qualification-index.json');entry=ix['history'][-1]
    q=ROOT/entry['qualification'];require(read(q)['streams']['passed'],'Latest CUDA stream backend did not qualify')
    require(all(sha(ROOT/p)==h for p,h in entry['code_sha256'].items()),'Requalify current code before execution authorization')
    immutable(p,dict(version='JAT1-execution-01',parent_contract_sha256=sha(OUT/'manifests/contract.json'),
          authorization='User: 32 models + 8 CUDA streams + CUDA Graph; complete P1 then full matrix after engineering/budget gates',
          backend='streams',concurrent_models=32,streams=8,cuda_graph=True,
          training_budget_seconds=86400,forecast_ceiling_seconds=69120,selection_uses_all_720=True,
          pilot_query_allowed=False,pilot_business_gate=False,H_pre_allowed=False,U_training_allowed=False,
          counts=dict(inner_physical=14400,inner_logical=17280,inner_updates=24480000,H_logical_rows=34560),
          numerical_qualification=rel(q),numerical_qualification_sha256=sha(q),
          original_engineering_contract_retained=True))
    immutable(p.with_suffix('.seal.json'),dict(sha256=sha(p)))
    hashes={}
    for src in sorted(CODE.glob('*.py')):
        dst=writable(OUT/'manifests/execution-code'/src.name);require(not dst.exists(),'Code snapshot exists')
        dst.write_bytes(src.read_bytes());hashes[rel(src)]=sha(src)
    immutable(OUT/'manifests/execution-code.json',dict(files=hashes,authorization_sha256=sha(p),plan_sha256=sha(PLAN)))
    write(OUT/'budget.json',dict(cap_seconds=86400,used_seconds=0.,batches=[],fit_count=0,model_updates=0))

def authorized():
    p=OUT/'manifests/execution-authorization.json'
    require(p.exists() and sha(p)==read(p.with_suffix('.seal.json'))['sha256'],'Execution not authorized/sealed')
    require(read(p)['parent_contract_sha256']==sha(OUT/'manifests/contract.json'),'Parent contract changed')

def codecheck():
    authorized()
    for p,h in read(OUT/'manifests/execution-code.json')['files'].items():require(sha(ROOT/p)==h,'Execution code changed: '+p)

def saveframe(p,d):
    p=writable(p);require(not p.exists(),'Refuse table overwrite');d.to_parquet(p,index=False)

def seal(p,files,**meta):
    expanded=[]
    for f in map(Path,files):
        expanded.append(f)
        if f.suffix=='.pt':expanded.append(f.with_suffix('.json'))
    immutable(p,dict(files={rel(f):sha(f) for f in dict.fromkeys(expanded)},**meta))

def verifyseal(p):
    p=Path(p);signature=(p.stat().st_size,p.stat().st_mtime_ns)
    if _SEAL_CACHE.get(str(p),(None,None))[0]==signature:return _SEAL_CACHE[str(p)][1]
    v=read(p)
    for f,h in v['files'].items():require(sha(ROOT/f)==h,'Sealed artifact changed: '+f)
    _SEAL_CACHE[str(p)]=(signature,v)
    return v

def barrier(name):
    p=OUT/'manifests'/name
    require(p.exists(),'Global phase barrier not reached: '+name)
    return verifyseal(p)

def debit(seconds,count,updates,kind,**extra):
    p=OUT/'budget.json';b=read(p)
    b['used_seconds']+=seconds;b['fit_count']+=count;b['model_updates']+=updates
    b['batches'].append(dict(kind=kind,seconds=seconds,count=count,model_updates=updates,**extra));write(p,b)
    require(b['used_seconds']<=b['cap_seconds'],'Global training budget exhausted; unrun roles are NOT fallback')

def remaining():
    b=read(OUT/'budget.json');require(b['used_seconds']<b['cap_seconds'],'Global activity budget exhausted')
    return b['cap_seconds']-b['used_seconds']

def rolelookup():return {r['id']:r for r in contract()['inner_roles']+contract()['roles']}

def recipes(arm):return POST_RECIPES if arm=='JC' else RECIPES

def job(r,arm,recipe,seed=SOURCE_SEED):
    return dict(role=r,arm=arm,recipe=recipe,seed=seed)

def canonical(j):
    if j['arm'] in {'JP','JG'} and j['recipe']['lam']==0:
        c=next(c for c in POST_RECIPES if c['lr']==j['recipe']['lr'] and c['gamma']==j['recipe']['gamma'])
        return job(j['role'],'JC',c,j['seed'])
    return j

def jid(j):return f"{j['role']['id']}/{j['arm']}/{j['recipe']['id']}/s{j['seed']}"

def modelpath(j,mid=False):
    return OUT/('inner-models' if j['role']['inner'] is not None else 'outer-models')/(jid(j)+('.mid.pt' if mid else '.pt'))

def warmjob(j):return canonical(job(j['role'],'JP',j['recipe'],j['seed']))

def target_arm(j):return 'JP' if j['arm'] in {'FR','MX01','MX10'} else j['arm']

def diagnostic(state,d,j,gradients=False):
    s={k:v.detach().clone().requires_grad_(True) for k,v in state.items()}
    loss,parts=loss_one(s,d,j['recipe']);ind,_=loss_independent(s,d,j['recipe'])
    require(torch.allclose(loss,ind,atol=1e-10,rtol=1e-10),'Independent objective replay failed')
    with torch.no_grad():
        z,g=forward_post(d['x'],s);lin=F.linear(d['x'],s['W']);assoc=F.linear(g.double(),s['V'])
        gc_=g.double()-g.double().mean(0);sv=torch.linalg.svdvals(gc_);ev=sv.square();pr=ev/ev.sum().clamp_min(1e-30)
        result=dict(objective=float(loss.detach()),CE=float(parts[0].detach()),MSE=float(parts[1].detach()),L2=float(parts[2].detach()),
            norms={k:float(v.detach().double().norm()) for k,v in s.items()},
            G_variance=cpu(g.double().var(0,unbiased=False)).tolist(),G_effective_rank=float(torch.exp(-(pr*pr.clamp_min(1e-30).log()).sum())),
            direct_logit_rms=float(lin.square().mean().sqrt()),associated_logit_rms=float(assoc.square().mean().sqrt()),
            bias_rms=float(s['c'].square().mean().sqrt()))
    if gradients:
        vec=[]
        for term in [parts[0],j['recipe']['lam']*parts[1],parts[2]]:
            if not term.requires_grad:gs=[torch.zeros_like(s[k]) for k in GKEYS]
            else:
                gs=torch.autograd.grad(term,[s[k] for k in GKEYS],retain_graph=True,allow_unused=True)
                gs=[torch.zeros_like(s[k]) if g is None else g for k,g in zip(GKEYS,gs)]
            vec.append(torch.cat([g.double().flatten() for g in gs]))
        result['G_gradient_norms']=[float(v.norm()) for v in vec]
        result['G_gradient_cosines']=[float((a@b)/(a.norm()*b.norm()).clamp_min(1e-30)) for a,b in [(vec[0],vec[1]),(vec[0],vec[2]),(vec[1],vec[2])]]
    return result

def checkpoint_one(cp,i):return dict(state=cp['parameters'][i],adam=cp['adam'][i],steps=cp['steps'])

def load_start(j):
    if j['arm'] in {'FR','MX01','MX10'}:return own(modelpath(warmjob(j),True))
    return None

def fit_batch(js,pool,steps=2000,warm_only=False,kind='inner'):
    require(0<len(js)<=32,'Fixed concurrency limit');remaining();codecheck()
    ds=[pool.get(j['role'],target_arm(j),j['recipe']['lam']) for j in js]
    branches=js[0]['arm'] in {'FR','MX01','MX10'}
    require(all((j['arm'] in {'FR','MX01','MX10'})==branches for j in js),'Mixed branch bucket')
    starts=[load_start(j) for j in js] if branches else None
    sg=js[0]['arm']!='MX10';ug=not branches or not sg;uh=not branches or sg
    start=time.perf_counter()
    e=Engine(ds,js,'streams',states=None if starts is None else [s['state'] for s in starts],
             adam=None if starts is None else [s['adam'] for s in starts],update_G=ug,update_head=uh)
    initial_states=e.snapshot_all();initial_step=e.steps;traces=[[] for j in js]
    for i,(s,d,j) in enumerate(zip(initial_states,ds,js)):
        traces[i].append(dict(step=initial_step,**diagnostic(s,d,j,True)))
    e.capture();last=initial_step+steps
    stops=sorted(set([n for n in [1,10,100,500,1000,1500,2000] if initial_step<n<=last]+[last]))
    mids=None
    for n in stops:
        e.advance(n-e.steps);snap=e.snapshot_all()
        for i,(s,d,j) in enumerate(zip(snap,ds,js)):
            record=diagnostic(s,d,j,n in [1000,2000]);record.update(step=n,preclip_gradient_norm=float(e.norms[i]),
                clipped_updates=int(e.clip_count[i]),parameter_motion={k:float((s[k]-initial_states[i][k]).double().norm()) for k in KEYS})
            traces[i].append(record)
        if n==1000:mids=e.checkpoint()
        require(time.perf_counter()-start<remaining(),'Global training budget exhausted in active batch')
    end=e.checkpoint();torch.cuda.synchronize();elapsed=time.perf_counter()-start
    if branches:
        frozen=HKEYS if ug else GKEYS
        for i,s in enumerate(starts):
            for k in frozen:
                require(torch.equal(s['state'][k],end['parameters'][i][k]),'Frozen parameter changed')
                require(all(torch.equal(v,end['adam'][i][k][name]) for name,v in s['adam'][k].items()),'Frozen Adam changed')
    debit(elapsed,len(js),len(js)*steps,kind,ids=[jid(j) for j in js],concurrent=len(js),update_G=ug,update_head=uh)
    for i,j in enumerate(js):
        meta=dict(role_id=j['role']['id'],job=jid(j),recipe=j['recipe'],seed=j['seed'],seconds_batch=elapsed,
                  backend='streams',cuda_graph=True,steps=end['steps'],update_G=ug,update_head=uh)
        if mids is not None and not modelpath(j,True).exists():put(modelpath(j,True),checkpoint_one(mids,i),**dict(meta,steps=1000))
        if not warm_only:put(modelpath(j),checkpoint_one(end,i),**meta)
        tracepath=OUT/'training-traces'/(jid(j)+('.warm.json' if warm_only else '.json'))
        immutable(tracepath,dict(**meta,trace=traces[i],clipped_updates=int(e.clip_count[i]),
            CUDA_peak_allocated_MiB=torch.cuda.max_memory_allocated()/1048576))
    del e,end,mids,initial_states;gc.collect()
    progress(kind+'_batch',physical_total=read(OUT/'budget.json')['fit_count'],active_seconds=read(OUT/'budget.json')['used_seconds'],
             last_batch_seconds=elapsed,last_batch_models=len(js))

def dispatch(js,pool,kind='inner',steps=2000,warm_only=False):
    unique={jid(j):j for j in js};pending=[]
    for j in unique.values():
        p=modelpath(j,warm_only)
        if p.exists():
            require(read(p.with_suffix('.json'))['job']==jid(j),'Existing checkpoint identity mismatch');own(p)
        else:pending.append(j)
    # Stable job order, numerical buckets only; all batches use independent model arithmetic.
    buckets={}
    for j in pending:
        key=(j['recipe']['lr'],j['arm'] in {'FR','MX01'},j['arm']=='MX10',j['role']['inner'] is None)
        buckets.setdefault(key,[]).append(j)
    for jobs in buckets.values():
        for left in range(0,len(jobs),32):fit_batch(jobs[left:left+32],pool,steps,warm_only,kind)

def inner_endpoints(rs):
    return [dict(role_id=r['id'],arm=arm,recipe=c['id'],seed=SOURCE_SEED,path=rel(modelpath(canonical(job(r,arm,c)))))
            for r in rs for arm in ['JC','JP','JG','FR'] for c in recipes(arm)]

def pilot(pool):
    p=OUT/'manifests/P1-complete.json'
    if p.exists():return verifyseal(p)
    rs=pilot_roles();require(len(rs)==12,'Fixed pilot size')
    before=read(OUT/'budget.json')['used_seconds'];sampler=Sampler(OUT/'engineering/fixed-P1/gpu.json').start();sampler.label('P1-training')
    try:
        dispatch(canonical_jobs(rs),pool,'P1-full')
        dispatch([job(r,'FR',c) for r in rs for c in RECIPES],pool,'P1-FR',steps=1000)
        # Registered 928-row engineering timing is legal training-only and reusable
        # as the corresponding outer candidate if selected. It opens no query.
        ro=contract()['roles'][0]
        from teacher import fit_teachers
        teacher_start=time.perf_counter();fit_teachers([ro]);teacher_seconds=time.perf_counter()-teacher_start
        probe=job(ro,'JP',RECIPES[2]);dispatch([probe],pool,'P1-928-shape')
    finally:sampler.stop()
    b=read(OUT/'budget.json');full=[v for v in b['batches'] if v['kind']=='P1-full'];fr=[v for v in b['batches'] if v['kind']=='P1-FR']
    require(sum(v['count'] for v in full)==168 and sum(v['count'] for v in fr)==72,'Pilot physical counts')
    # Include capture, health checks, all diagnostic backwards, not hot-loop-only rates.
    full_rate=sum(v['seconds'] for v in full)/sum(v['model_updates'] for v in full)
    fr_rate=sum(v['seconds'] for v in fr)/sum(v['model_updates'] for v in fr)
    outer_rate=max(full_rate,next(v['seconds']/v['model_updates'] for v in b['batches'] if v['kind']=='P1-928-shape'))
    # Conservative: 720 terminal paths + 180 warm paths + both matrix continuations.
    estimate=720*14*2000*full_rate+720*6*1000*fr_rate+(720*2000+180*1000+360*1000)*outer_rate+60*teacher_seconds
    require(estimate<=69120,'Forecast exceeds 19.2h gate; request engineering decision, do not shrink matrix')
    eps=inner_endpoints(rs);files=[ROOT/e['path'] for e in eps]
    report=dict(passed=True,source_roles=12,physical_source_fits=240,source_updates=408000,
        training_seconds=b['used_seconds']-before,forecast_training_seconds=estimate,forecast_hours=estimate/3600,
        forecast_ceiling_seconds=69120,activity_cap_seconds=86400,query_reads=0,H_reads=0,U_training_reads=0,
        full_seconds_per_model_update=full_rate,FR_seconds_per_model_update=fr_rate,outer_conservative_rate=outer_rate,
        telemetry=sampler.summary('P1-training'),business_gate=False,backend='streams',models=32,streams=8,cuda_graph=True)
    immutable(OUT/'engineering/fixed-P1/report.json',report);seal(p,files+[OUT/'engineering/fixed-P1/report.json'],**report)
    progress('P1_passed',forecast_hours=estimate/3600,full_matrix_authorized=True)
    return report

def inner(pool):
    p=OUT/'manifests/inner-models-complete.json'
    if p.exists():return verifyseal(p)
    barrier('P1-complete.json');rs=contract()['inner_roles']
    dispatch(canonical_jobs(rs),pool)
    dispatch([job(r,'FR',c) for r in rs for c in RECIPES],pool,'inner-FR',steps=1000)
    eps=inner_endpoints(rs);require(len(eps)==17280,'Inner logical endpoint count')
    immutable(OUT/'manifests/inner-endpoints.json',eps)
    seal(p,[ROOT/e['path'] for e in eps]+[OUT/'manifests/inner-endpoints.json'],logical=17280,physical=14400,passed=True)

def package(r,kind,outer=False):
    if kind=='query':barrier('outer-models-complete.json' if outer else 'inner-models-complete.json')
    else:barrier('H-predictions-complete.json' if outer else 'inner-predictions-complete.json')
    require(kind in {'query','labels'},'Unsupported evaluation asset')
    p=PREP/'packages'/r['id']/(kind+'.parquet');info=contract()['files'][rel(p)]
    require(info['kind']==kind and info['role_id']==r['id'] and sha(p)==info['sha256'],'Evaluation role/hash mismatch')
    READS.append(dict(path=rel(p),role_id=r['id'],kind=kind,phase='H' if outer else 'inner',sha256=info['sha256']))
    d=pd.read_parquet(p)
    require(len(d)==24 and d.visit_id.is_unique,'Query count/identity')
    if kind=='query':require(list(d)==['visit_id']+HIST,'Post-only numerical query schema')
    else:
        require(set(d)=={'visit_id','content_id','label_id','protocol'},'Labels schema')
        require(set(d.content_id)==set(r['validation_contents']),'Query contents differ from role')
        require(set(d.protocol)=={r['calibration']},'Query deployment differs from pseudo/actual target')
    return d

def predict(outer=False):
    name='H' if outer else 'inner';p=OUT/'manifests'/(name+'-predictions-complete.json')
    if p.exists():return verifyseal(p)
    barrier('outer-models-complete.json' if outer else 'inner-models-complete.json')
    eps=read(OUT/'manifests'/('outer-endpoints.json' if outer else 'inner-endpoints.json'));result=[]
    for r in contract()['roles' if outer else 'inner_roles']:
        q=package(r,'query',outer);b=asset(PARENT/'base-models'/r['id']/'P-small.pt',r['id'],'base');x=(tensor(q[HIST])-b['mu'])/b['scale']
        endpoints=[e for e in eps if e['role_id']==r['id']]
        if not outer:endpoints=endpoints+[dict(role_id=r['id'],arm='B0',recipe='base',seed=SOURCE_SEED,path=None)]
        cache={}
        for e in endpoints:
            path=e['path']
            if path not in cache:
                with torch.no_grad():
                    if path is None:z=F.linear(x,b['weight'],b['bias']);no_g=z
                    else:
                        state=own(ROOT/path)['state'];z,_=forward_post(x,state);no_g=F.linear(x,state['W'],state['c'])
                    lp=F.log_softmax(z,1);require(torch.isfinite(lp).all(),'Nonfinite post-only inference');cache[path]=(cpu(lp),cpu(no_g.argmax(1)))
            lp,no_g_pred=cache[path];d=pd.DataFrame(np.exp(lp),columns=[f'p{i}' for i in range(6)])
            for i in range(6):d[f'l{i}']=lp[:,i]
            d['prediction']=lp.argmax(1);d['prediction_without_VG']=no_g_pred;d['visit_id']=q.visit_id.to_numpy()
            for k in ['role_id','arm','recipe','seed']:d[k]=e[k]
            d['target']=r['target'];d['query_deployment']=r['calibration'];d['group']=r['group'];d['outer']=r['outer'];result.append(d)
    d=pd.concat(result,ignore_index=True);expected=34560 if outer else 432000
    require(len(d)==expected,'Logical prediction count');dst=OUT/(name+'-predictions')/'visits.parquet';saveframe(dst,d)
    seal(p,[dst],rows=expected,post_only=True,labels_read=False,H_pre_reads=0)
    progress(name+'_predictions_sealed',rows=expected)

def outer(pool):
    p=OUT/'manifests/outer-models-complete.json'
    if p.exists():return verifyseal(p)
    barrier('selections-complete.json');sels=read(OUT/'selections/selected.json');rs=contract()['roles']
    from teacher import fit_teachers
    for left in range(0,60,32):fit_teachers(rs[left:left+32])
    # One selected recipe per role/arm, shared across outer seeds.
    mains=[];frs=[];mxs=[]
    for r in rs:
        for seed in SEEDS:
            for arm in ['JC','JP','JG']:
                c=next(c for c in recipes(arm) if c['id']==sels[r['id']][arm]);mains.append(canonical(job(r,arm,c,seed)))
            c=next(c for c in RECIPES if c['id']==sels[r['id']]['FR']);frs.append(job(r,'FR',c,seed))
            c=next(c for c in RECIPES if c['id']==sels[r['id']]['JP'])
            mxs.extend([job(r,a,c,seed) for a in ['MX01','MX10']])
    dispatch(mains,pool,'outer-main')
    missing=[warmjob(j) for j in frs if not modelpath(warmjob(j),True).exists()]
    dispatch(missing,pool,'outer-FR-warm',steps=1000,warm_only=True)
    dispatch(frs,pool,'outer-FR',steps=1000)
    # Exact aliases avoid a second identical head-only fit.
    mx_alias={};pending=[]
    for j in mxs:
        f=job(j['role'],'FR',j['recipe'],j['seed'])
        if j['arm']=='MX01' and modelpath(f).exists():mx_alias[jid(j)]=modelpath(f)
        else:pending.append(j)
    dispatch(pending,pool,'outer-matrix',steps=1000)
    eps=[]
    for r in rs:
        for seed in SEEDS:
            eps.append(dict(role_id=r['id'],arm='B0',recipe='base',seed=seed,path=None))
            for arm in ['JC','JP','JG','FR','MX00','MX01','MX10']:
                c=next(c for c in recipes('JP' if arm.startswith('MX') else arm) if c['id']==sels[r['id']]['JP' if arm.startswith('MX') else arm])
                j=job(r,'JP' if arm=='MX00' else arm,c,seed)
                path=modelpath(canonical(j),True) if arm=='MX00' else mx_alias.get(jid(j),modelpath(canonical(j)))
                require(path.exists(),'Outer endpoint not executed')
                eps.append(dict(role_id=r['id'],arm=arm,recipe=c['id'],seed=seed,path=rel(path)))
    require(len(eps)==1440,'Outer logical endpoint count');immutable(OUT/'manifests/outer-endpoints.json',eps)
    files=[ROOT/e['path'] for e in eps if e['path']]+[OUT/'manifests/outer-endpoints.json']
    seal(p,files,passed=True,endpoints=1440,H_reads=0)
    progress('outer_models_sealed',logical_endpoints=1440)

def run(stage='all'):
    configure();authorize();codecheck();READS.clear();pool=TrainingPool();started=time.perf_counter()
    try:
        pilot(pool)
        if stage=='pilot':return
        inner(pool);predict(False)
        from evaluate import select,score
        select();outer(pool);predict(True);score()
        from verify import closeout
        closeout()
    except BaseException as exc:
        p=OUT/'audits'/('stop-'+str(time.time_ns())+'.json')
        immutable(p,dict(error=repr(exc),traceback=traceback.format_exc(),no_auto_retry=True))
        progress('execution_stopped',reason=str(exc));raise
    finally:
        immutable(OUT/'permissions'/('execution-reads-'+str(time.time_ns())+'.json'),dict(reads=READS,
            seconds=time.perf_counter()-started,H_pre_reads=0,U_training_reads=0,PCAP_reads=0,source='phase-gated pure packages'))
