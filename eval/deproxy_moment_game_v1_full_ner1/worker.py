"""Bounded full-range queues using the exact NER1 solve and Adam policies."""
from common import *
from problems import load,initial_arrays,initial_head,arrays,fit_anchor,headpath
from classifier import basis,independent
from throughput import concurrent
from simplex import project_blocks,valid
from bound_engine import BoundEngine,bind
from models import generate

def modelroot(r,arm,candidate,seed):return OUT/'models'/r['id']/arm/candidate/str(seed)

def audit_head(p,x,y,w,g):
    h=own(p,read(p.with_suffix('.json'))['role_id']);q=read(p.with_suffix('.quality.json'))
    val,gw,gc,_=independent(h['W'],h['c'],x,y,w,g)
    require(q['accepted'] and q['gamma']==g and q['iterations']<2000 and q['evaluations']<10000,'Saved head budget/version')
    require(max(float(gw.abs().max()),float(gc.abs().max()))<=1e-5 and abs(float(val)-q['objective'])/max(1,abs(q['objective']))<=1e-10,'Saved NER1 original-equation replay')
    return h

def export(r,arm,rec,seed,d,st=None):
    p=modelroot(r,arm,rec['id'],seed);head=own(p/'head.pt',r['id'])
    if (p/'complete.json').exists():verifyseal(p/'complete.json');return
    init=initial_head(r,'post' if arm=='E-post' else 'pre',rec['gamma'])
    value=dict(head=head,mu_A=d['mu_A'],scale_A=d['scale_A'],mu_B=d['mu_B'],scale_B=d['scale_B'],
        anchor=None if arm=='E-post' else own(OUT/'anchors'/r['id']/f'{capfor(arm)}.pt',r['id']),
        residual=None if st is None else {k:st[k] for k in ['U1','d1','U2']},initial_head=init,
        adam_head=None if st is None else dict(W=basis()@st['A'],c=basis()@st['c']))
    put(p/'export.pt',value,role_id=r['id'],capability='export',arm=arm,post_only_interface=True)
    from deploy import branch_logp
    with torch.no_grad():
        lp=branch_logp(d['b'],value)
        hat=project_blocks(d['anchor']) if st is None else generate(st,d)[0]
        reference=F.log_softmax(F.linear((hat-d['mu_A'])/d['scale_A'],head['W'],head['c']),1)
        require(torch.allclose(lp,reference,atol=1e-9,rtol=1e-8),'Train-post export replay')
    files=[p/'head.pt',p/'head.quality.json',p/'export.pt']
    if st is not None:files+=[p/'terminal.pt',p/'trace.json']+list((p/'trajectory').glob('*.pt'))
    seal(p/'complete.json',files,role_id=r['id'],arm=arm,numeric_version='NER1',post_only=True)

def initial_problems(rs,cap):
    side='pre' if cap=='G' else 'post'
    for r in rs:
        x,y,w=initial_arrays(r,side)
        for g in GAMMAS:
            p=headpath(r,side,g)
            if p.exists():audit_head(p,x,y,w,g);continue
            s=dict(key=f'{r["id"]}/{side}/{gamma_tag(g)}',role_id=r['id'],arm=side,kind='initial',gamma=g,capability=side)
            yield dict(x=x,y=y,w=w,gamma=g,init=None,spec=s,output_path=p)

def static_problems(rs,cap,scope):
    arm='R-'+cap;selected=read(OUT/'selections/outer-fit-jobs.json')['static'] if scope=='outer' else None
    for r in rs:
        gs=GAMMAS if scope=='inner' else sorted({j['gamma'] for j in selected if j['role_id']==r['id'] and j['arm']==arm})
        if not gs:continue
        d=load(r,arm);x,y,w=arrays(d,project_blocks(d['anchor']))
        for g in gs:
            rec=dict(id=gamma_tag(g),gamma=g,lr=0);p=modelroot(r,arm,rec['id'],SEEDS[0])/'head.pt'
            if p.exists():audit_head(p,x,y,w,g);export(r,arm,rec,SEEDS[0],d);continue
            s=dict(key=f'{r["id"]}/{arm}/{rec["id"]}',role_id=r['id'],arm=arm,kind='static',gamma=g,capability=cap)
            yield dict(x=x,y=y,w=w,gamma=g,init=initial_head(r,'pre',g),spec=s,output_path=p,
                export_args=(r,arm,rec,SEEDS[0],d))

def head_queue(problems,tag):
    batch=[];completed=0
    def flush(batch):
        concurrent(batch,4,OUT/'unused')
        for p in batch:
            if 'export_args' in p:export(*p['export_args'])
        flush_reads(tag);deadline()
    for p in problems:
        batch.append(p)
        if len(batch)==32:
            flush(batch);completed+=len(batch);batch=[];torch.cuda.empty_cache()
            progress(tag,completed_new_heads=completed)
    if batch:flush(batch);completed+=len(batch)
    return completed

def dynamic_jobs(rs,cap,scope):
    if scope=='inner':return [dict(role_id=r['id'],arm=a,recipe=rec,seed=SEEDS[0]) for r in rs for rec in RECIPES for a in DYNAMIC if capfor(a)==cap]
    return [j for j in read(OUT/'selections/outer-fit-jobs.json')['dynamic'] if capfor(j['arm'])==cap]

def dynamic(jobs,tag):
    pending=[];reused=0
    for j in jobs:
        r=lookup(j['role_id']);p=modelroot(r,j['arm'],j['recipe']['id'],j['seed'])
        if (p/'complete.json').exists():verifyseal(p/'complete.json');reused+=1;continue
        if (p/'head.pt').exists():
            # Only imported sealed pilot endpoints may be completed without a fit.
            require(read(p/'head.json').get('imported_from_pilot',False),'Unsealed existing head; explicit recovery required')
            d=load(r,j['arm']);st=own(p/'terminal.pt',r['id'])['parameters']
            with torch.no_grad():hat,_=generate(st,d)
            x,y,w=arrays(d,hat);audit_head(p/'head.pt',x,y,w,j['recipe']['gamma'])
            export(r,j['arm'],j['recipe'],j['seed'],d,st);reused+=1;continue
        require(not (p/'terminal.pt').exists(),'Incomplete path: no automatic continuation or retraining')
        pending.append(j)
    completed=0
    for lr in [.0003,.001]:
        ordered=sorted([j for j in pending if j['recipe']['lr']==lr],key=lambda j:(j['role_id'],j['arm'],j['recipe']['id'],j['seed']))
        for start in range(0,len(ordered),32):
            deadline();batch=ordered[start:start+32];ds=[];hs=[];cache={};tick=time.perf_counter()
            for j in batch:
                key=(j['role_id'],j['arm']);r=lookup(j['role_id'])
                if key not in cache:cache[key]=load(r,j['arm'])
                d,h=bind(cache[key],j,initial_head(r,'post' if j['arm']=='E-post' else 'pre',j['recipe']['gamma']))
                ds.append(d);hs.append(h)
            engine=BoundEngine(ds,batch,hs,True);engine.capture();traces=[[] for _ in batch]
            for stop in [0,1,100,500,1000,2000]:
                deadline();engine.advance(stop-engine.steps);ck=engine.checkpoint();logs=engine.diagnostics()
                for i,j in enumerate(batch):
                    p=modelroot(lookup(j['role_id']),j['arm'],j['recipe']['id'],j['seed'])
                    path=p/'terminal.pt' if stop==2000 else p/'trajectory'/f'step-{stop:04}.pt'
                    put(path,dict(parameters=ck['parameters'][i],adam=ck['adam'][i],gradients=ck['gradients'][i],steps=stop,clips=ck['clips'][i]),
                        role_id=j['role_id'],capability=capfor(j['arm']))
                    traces[i].append(logs[i])
                progress(tag,lr=lr,batch_models=len(batch),step=stop,completed_new_paths=completed,reused_paths=reused,total_paths=len(jobs))
                flush_reads(tag)
            adam_seconds=time.perf_counter()-tick;q=basis();problems=[]
            for i,(j,d) in enumerate(zip(batch,ds)):
                r=lookup(j['role_id']);p=modelroot(r,j['arm'],j['recipe']['id'],j['seed']);st=ck['parameters'][i]
                write(p/'trace.json',dict(steps=traces[i],uniform_lr_bucket=True,bucket_lr=lr,bucket_models=len(batch),numeric_version='NER1'))
                with torch.no_grad():hat,_=generate(st,d);valid(hat)
                x,y,w=arrays(d,hat);s=dict(key=f'{r["id"]}/{j["arm"]}/{j["recipe"]["id"]}/{j["seed"]}',role_id=r['id'],arm=j['arm'],kind='refit',gamma=j['recipe']['gamma'],capability=capfor(j['arm']))
                problems.append(dict(x=x,y=y,w=w,gamma=s['gamma'],init=dict(W=q@st['A'],c=q@st['c']),spec=s,output_path=p/'head.pt',
                    export_args=(r,j['arm'],j['recipe'],j['seed'],d,st)))
            del engine;head_queue(problems,tag);completed+=len(batch)
            immutable(OUT/'batches'/f'{tag}-{time.time_ns()}.json',dict(jobs=batch,adam_and_diagnostic_seconds=adam_seconds,
                total_batch_seconds=time.perf_counter()-tick,paths=len(batch),steps=2000,lr=lr,streams=min(8,len(batch))))
            del ck,ds,hs,cache,problems;torch.cuda.empty_cache()
    return completed,reused

def run(cap,phase,scope):
    configure(cap);barrier('P1-complete.json');rs=contract()['inner_roles'] if scope=='inner' else contract()['roles']
    if scope=='outer':barrier('P3-complete.json')
    tag=f'{scope}-{phase}-{cap}';begin(tag);hashes=code_seal(tag)
    try:
        if phase=='initial':require(cap in ['G','E'],'Initial cap');n=head_queue(initial_problems(rs,cap),tag)
        elif phase=='anchor':
            require(cap in ['P','G'],'Anchor cap');n=0
            for r in rs:deadline();fit_anchor(r,cap);n+=1;flush_reads(tag)
        elif phase=='static':require(cap in ['P','G'],'Static cap');n=head_queue(static_problems(rs,cap,scope),tag)
        elif phase=='dynamic':n=dynamic(dynamic_jobs(rs,cap,scope),tag)[0]
        else:raise RuntimeError('Unknown phase')
        codecheck(hashes);immutable(OUT/'workers'/f'{tag}.json',dict(passed=True,scope=scope,phase=phase,capability=cap,new_completed=n))
    except BaseException as e:failure(tag,e);raise
    finally:end(tag)

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--cap',choices=['P','G','E'],required=True);p.add_argument('--phase',choices=['initial','anchor','static','dynamic'],required=True);p.add_argument('--scope',choices=['inner','outer'],required=True)
    a=p.parse_args();run(a.cap,a.phase,a.scope)
