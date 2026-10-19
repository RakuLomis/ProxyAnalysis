"""One process per capability. Never deserialize another arm's training package."""
from common import *
from data import load,fit_initial,fit_anchor,headpath,anchorpath
from classifier import fit,basis,within_budget
from simplex import project_blocks

def modelroot(r,arm,candidate,seed):return OUT/'models'/r['id']/arm/candidate/str(seed)

def export(r,arm,path,head,d,state=None):
    if (path/'export.pt').exists():return
    value=dict(head=head,mu_A=d['mu_A'],scale_A=d['scale_A'],mu_B=d['mu_B'],scale_B=d['scale_B'],
        anchor=None if arm=='E-post' else own(anchorpath(r,capfor(arm)),r['id']),
        residual=None if state is None else {k:state[k] for k in ['U1','d1','U2']})
    put(path/'export.pt',value,role_id=r['id'],capability='export',arm=arm,post_only_interface=True)
    seal(path/'complete.json',[path/'head.pt',path/'head.quality.json',path/'export.pt']+([path/'terminal.pt',path/'trace.json']+list((path/'trajectory').glob('*.pt')) if state is not None else []),role_id=r['id'],arm=arm)

def static(r,arm,gamma):
    p=modelroot(r,arm,gamma_tag(gamma),SEEDS[0])/'head.pt'
    d=load(r,arm)
    hat=project_blocks(d['anchor']);x=torch.cat([(hat-d['mu_A'])/d['scale_A'],d['real_x']])
    y=torch.cat([d['y'],d['y_pre']]);w=torch.cat([d['w'],d['w_pre']])/2
    init=own(headpath(r,'pre',gamma),r['id'])
    head=fit(x,y,w,gamma,p,dict(role_id=r['id'],arm=arm,capability=capfor(arm),candidate=gamma_tag(gamma),seed=SEEDS[0],kind='static-refit'),init=init)
    export(r,arm,p.parent,head,d);return head

def pilot_jobs(cap):
    rs=pilot_roles();fixed=[r for r in rs if (r['target'],r['group']) in [('shadowsocks','G0'),('vmess','G2')]]
    jobs=[]
    for r in rs:
        for rec in RECIPES if r in fixed else RECIPES[:1]:
            for arm in DYNAMIC:
                if capfor(arm)==cap:jobs.append(dict(role_id=r['id'],arm=arm,recipe=rec,seed=SEEDS[0]))
    return jobs

def dynamic(jobs):
    from engine import Engine
    from models import generate
    cached={};pending=[]
    for j in jobs:
        r=lookup(j['role_id']);p=modelroot(r,j['arm'],j['recipe']['id'],j['seed'])
        if (p/'complete.json').exists():
            verifyseal(p/'complete.json')
            require(within_budget(read(p/'head.quality.json')),'Saved head hit original cumulative budget; not reusable')
            require(read(p/'trace.json').get('uniform_lr_bucket') is True,'Previous mixed-lr bucket requires separately registered compatibility replay, not silent reuse')
            continue
        require(not (p/'terminal.pt').exists(),'Incomplete saved trajectory requires explicit engineering recovery, not silent retraining')
        pending.append(j)
    from itertools import groupby
    buckets=[]
    for lr,group in groupby(sorted(pending,key=lambda j:j['recipe']['lr']),key=lambda j:j['recipe']['lr']):
        group=list(group);buckets.extend(group[i:i+32] for i in range(0,len(group),32))
    offset=0
    for batch in buckets:
        ds=[];heads=[]
        for j in batch:
            key=(j['role_id'],j['arm'])
            if key not in cached:cached[key]=load(lookup(j['role_id']),j['arm'])
            ds.append(cached[key]);r=lookup(j['role_id']);side='post' if j['arm']=='E-post' else 'pre'
            heads.append(own(headpath(r,side,j['recipe']['gamma']),r['id']))
        remaining();t=time.perf_counter();engine=Engine(ds,batch,heads,streams=True);engine.capture();traces=[[] for _ in batch]
        snapshots={}
        try:
            for stop in [0,1,100,500,1000,2000]:
                require(time.perf_counter()-t<remaining(),'Global budget exhausted during Adam')
                if stop:engine.advance(stop-engine.steps)
                logs=engine.diagnostics()
                for i,log in enumerate(logs):traces[i].append(log)
                snapshots[stop]=engine.checkpoint()
                progress('P1_dynamic',completed_paths=offset,total_paths=len(pending),models=len(batch),step=stop)
            torch.cuda.synchronize();duration=time.perf_counter()-t
        finally:
            torch.cuda.synchronize();debit('dynamic-Adam',time.perf_counter()-t,paths=len(batch),formal_updates=len(batch)*engine.steps,steps_per_path=engine.steps,
                capability=capfor(batch[0]['arm']),batch_jobs=batch,graph=True,streams=8)
        for i,(j,d) in enumerate(zip(batch,ds)):
            r=lookup(j['role_id']);p=modelroot(r,j['arm'],j['recipe']['id'],j['seed']);terminal=snapshots[2000]['parameters'][i]
            put(p/'terminal.pt',dict(parameters=terminal,adam=snapshots[2000]['adam'][i],steps=2000),role_id=r['id'],capability=capfor(j['arm']),arm=j['arm'],recipe=j['recipe'],seed=j['seed'])
            for stop,ck in snapshots.items():
                if stop==2000:continue
                put(p/'trajectory'/f'step-{stop:04}.pt',dict(parameters=ck['parameters'][i],adam=ck['adam'][i],steps=stop),role_id=r['id'],capability=capfor(j['arm']))
            immutable(p/'trace.json',dict(steps=traces[i],batch_seconds=duration,batch_models=len(batch),steps_not_a_stationarity_certificate=True,
                uniform_lr_bucket=True,bucket_lr=j['recipe']['lr']))
            with torch.no_grad():hat,res=generate(terminal,d);xh=(hat-d['mu_A'])/d['scale_A']
            x=torch.cat([xh,d['real_x']]);y=torch.cat([d['y'],d['y_pre']]);w=torch.cat([d['w'],d['w_pre']])/2
            q=basis();init=dict(W=q@terminal['A'],c=q@terminal['c'])
            head=fit(x,y,w,j['recipe']['gamma'],p/'head.pt',dict(role_id=r['id'],arm=j['arm'],capability=capfor(j['arm']),candidate=j['recipe']['id'],seed=j['seed'],kind='terminal-generator-convex-refit'),init=init)
            export(r,j['arm'],p,head,d,terminal)
        offset+=len(batch);del engine,snapshots;torch.cuda.empty_cache()

def run(cap,phase,pilot=True):
    configure(cap);barrier('P0-complete.json');rs=pilot_roles() if pilot else roles()
    tag=f'{phase}-{cap}-'+str(time.time_ns());hashes=code_seal(tag)
    try:
        if phase=='dynamic':
            require(pilot,'Full scheduling requires P1 acceptance');dynamic(pilot_jobs(cap))
        for i,r in enumerate(rs if phase!='dynamic' else []):
            if phase=='initial':
                side='post' if cap=='E' else 'pre'
                require(cap in ['G','E'],'Initial capability')
                for g in GAMMAS:fit_initial(r,side,g)
            elif phase=='anchor':
                require(cap in ['P','G'],'Anchor capability');fit_anchor(r,cap)
            elif phase=='static':
                require(cap in ['P','G'],'Static capability')
                for g in GAMMAS:static(r,'R-'+cap,g)
            else:raise RuntimeError('Unknown worker phase')
            flush_reads(tag);progress('P1_'+phase,capability=cap,completed=i+1,total=len(rs))
        codecheck(hashes)
        immutable(OUT/'workers'/(tag+'.json'),dict(passed=True,phase=phase,capability=cap,roles=[r['id'] for r in rs]))
    except BaseException as e:failure(tag,e);raise

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--cap',choices=['P','G','E'],required=True);p.add_argument('--phase',choices=['initial','anchor','static','dynamic'],required=True)
    p.add_argument('--all',action='store_true');a=p.parse_args();run(a.cap,a.phase,not a.all)
