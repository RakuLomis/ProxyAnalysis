"""P/G isolated generation; fit-only process owns the original classification slots."""
from common import *
from model import load,residual,diagnostic
from engine import Engine
import argparse

def selected(which):
    if which=='all':return roles()
    if which=='pilot':return [r for r in roles() if r['inner']==1 and (r['target'],r['group']) in [('shadowsocks','G0'),('vmess','G2')]]
    return [r for r in roles() if not (r['inner']==1 and (r['target'],r['group']) in [('shadowsocks','G0'),('vmess','G2')])]

def generate(cap,which):
    configure(cap);barrier('P0-complete.json');codecheck();rs=selected(which);jobs=[]
    barrier('math-complete.json' if which=='pilot' else 'P1-complete.json')
    for r in rs:
        for arm in (['DA-G'] if cap=='G' else ['DA-P','Full-P']):jobs.append((r,arm))
    started=time.perf_counter();done=0
    # Keep decision-space and 96-space graph shapes separate.
    for arm in ARMS:
        todo=[j for j in jobs if j[1]==arm]
        for begin in range(0,len(todo),32):
            deadline();batch=todo[begin:begin+32];ds=[load(r,a) for r,a in batch]
            en=Engine(ds,batch);en.capture();logs=[[] for _ in batch];start=time.perf_counter()
            for stop in [0,1,100,500,1000,2000]:
                deadline();en.advance(stop-en.steps);ck=en.snapshot()
                for i,((r,a),d) in enumerate(zip(batch,ds)):
                    root=modelroot(r,a);name='terminal.pt' if stop==2000 else f'trajectory/step-{stop:04}.pt'
                    put(root/name,dict(parameters=ck['parameters'][i],gradients=ck['gradients'][i],adam=ck['adam'][i],steps=stop,clips=ck['clips'][i]),role_id=r['id'],capability='model')
                    log=diagnostic(en.states[i],d);log['step']=stop;log['clip_count']=int(ck['clips'][i]);logs[i].append(log)
                flush('generator');progress('generator',capability=cap,arm=arm,batch=len(batch),step=stop,completed=done,total=len(jobs))
            for i,((r,a),d) in enumerate(zip(batch,ds)):
                root=modelroot(r,a);put(root/'export.pt',dict(parameters=ck['parameters'][i]),role_id=r['id'],capability='model')
                immutable(root/'trace.json',dict(steps=logs[i],rank=d['Q'].shape[1],single_lr=True,arm=a))
                seal(root/'complete.json',[root/'terminal.pt',root/'export.pt',root/'trace.json'],steps=2000,role_id=r['id'],arm=a)
            immutable(OUT/'batches'/f'{cap}-{time.time_ns()}.json',dict(models=len(batch),arm=arm,seconds=time.perf_counter()-start,steps=2000,which=which))
            done+=len(batch);del en,ds,ck;torch.cuda.empty_cache()
    immutable(OUT/'workers'/f'generate-{cap}-{which}.json',dict(paths=done,seconds=time.perf_counter()-started,passed=True))

def fit(which):
    from classifier import solve
    from concurrent.futures import ThreadPoolExecutor
    configure('fit');barrier('P0-complete.json');codecheck();rs=selected(which);work=[]
    if which!='pilot':barrier('P1-complete.json')
    for r in rs:
        p=OUT/'packages'/r['id'];slot=own(p/'classification.pt',r['id']);shared=own(p/'shared.pt',r['id'])
        for arm in ['B0-R']+ARMS:
            x=slot['x'].clone()
            if arm!='B0-R':
                verifyseal(modelroot(r,arm)/'complete.json');s=own(modelroot(r,arm)/'export.pt',r['id'])['parameters']
                with torch.no_grad():x[288:432]=shared['mapped']+residual(s,shared['sx'])
            require(torch.equal(x[:288],slot['x'][:288]) and torch.equal(x[432:],slot['x'][432:]),'Only mapped slot changes')
            work.append((r,arm,x,slot['y'],slot['mass']))
    started=time.perf_counter();root=torch.cuda.current_stream();ready=torch.cuda.Event();ready.record(root)
    def one(job):
        r,arm,x,y,w=job;st=torch.cuda.Stream()
        with torch.cuda.stream(st):
            st.wait_event(ready);result=solve(x,y,w,.0005*(1+r['t']),None);torch.cuda.current_stream().synchronize()
        path=OUT/'classifiers'/r['id']/(arm+'.pt');persist(path,result,role_id=r['id'],arm=arm)
        require(result['quality']['accepted'],'Final convex head failed: '+r['id']+'/'+arm)
        return dict(role_id=r['id'],arm=arm,seconds=result['quality']['seconds'],accepted=True)
    with ThreadPoolExecutor(max_workers=4) as pool:
        for start in range(0,len(work),4):
            for i,record in enumerate(pool.map(one,work[start:start+4])):
                progress('convex_heads',completed=start+i+1,total=len(work),which=which,**record)
    flush('fit');immutable(OUT/'workers'/f'fit-{which}.json',dict(heads=len(work),seconds=time.perf_counter()-started,passed=True))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('phase',choices=['generate','fit']);p.add_argument('--cap',choices=['P','G']);p.add_argument('--which',choices=['pilot','rest','all'],required=True);a=p.parse_args()
    try:generate(a.cap,a.which) if a.phase=='generate' else fit(a.which)
    except BaseException as e:failure('worker',e);raise
