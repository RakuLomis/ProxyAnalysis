"""Independent convex solves on dedicated streams; ledger written by coordinator."""
from common import *
from classifier import solve,persist
from problems import specs,spec_cap,build
from concurrent.futures import ThreadPoolExecutor,wait,FIRST_COMPLETED

def concurrent(problems,workers,path):
    require(workers in [1,4,8] and len(problems)<=32,'Frozen head backend bounds')
    root=torch.cuda.current_stream();ready=torch.cuda.Event();ready.record(root)
    streams=[torch.cuda.Stream() for _ in range(workers)]
    from queue import Queue
    slots=Queue()
    for s in streams:slots.put(s)
    results={};failed=False;queued=list(problems);futures={}
    def one(problem):
        s=slots.get()
        try:
            with torch.cuda.stream(s):
                s.wait_event(ready)
                result=solve(problem['x'],problem['y'],problem['w'],problem['gamma'],problem['init'])
                event=torch.cuda.Event();event.record(s);event.synchronize()
            return problem,result
        finally:slots.put(s)
    with ThreadPoolExecutor(max_workers=workers) as pool:
        while queued or futures:
            while queued and len(futures)<workers and not failed:
                p=queued.pop(0);futures[pool.submit(one,p)]=p['spec']['key']
            if not futures:break
            done,_=wait(futures,return_when=FIRST_COMPLETED)
            for f in done:
                key=futures.pop(f);problem,result=f.result();s=problem['spec']
                persist(problem.get('output_path',path/key/'head.pt'),result,role_id=s['role_id'],capability=s.get('capability',spec_cap(s)),problem_key=key)
                results[key]=result['quality'];failed|=not result['quality']['accepted']
                progress('R3_head',problem=key,workers=workers,accepted=result['quality']['accepted'],iterations=result['quality']['iterations'])
        require(not failed,'Numerical head failure: backend rejected; remaining tasks not run')
    require(len(results)==len(problems),'Complete workload only')
    return results

def synthetic_problems():
    out=[]
    for n in [192,384,352,704]:
        gen=torch.Generator(device='cuda').manual_seed(20261016+n)
        x=torch.randn((n,96),device='cuda',dtype=torch.float64,generator=gen)
        y=torch.arange(n,device='cuda')%6;w=1/(6*torch.bincount(y)[y]).double()
        for g in GAMMAS:
            s=dict(key=f'synthetic-{n}-{g}',role_id='synthetic',arm='post',kind='initial',gamma=g,capability='synthetic')
            out.append(dict(x=x,y=y,w=w,gamma=g,init=None,spec=s))
    return out

def bench(cap,workers,round_,synthetic=False):
    configure('synthetic' if synthetic else cap)
    tag=f'R3-{"synthetic" if synthetic else cap}-r{round_}-C{workers}'
    begin(tag);started=time.perf_counter()
    try:
        for c in ['P','G','E']:require(read(OUT/'tests'/f'R1-{c}-current.json')['passed'],'R1 complete before throughput')
        problems=synthetic_problems() if synthetic else [build(s) for s in specs() if spec_cap(s)==cap]
        prepared=time.perf_counter()-started
        result=concurrent(problems,workers,OUT/'R3'/tag)
        rows=[dict(problem_key=k,**{key:val for key,val in q.items() if key not in ['accepted_points','settings']}) for k,q in result.items()]
        save(OUT/'tests'/f'{tag}.parquet',rows)
        write(OUT/'tests'/f'{tag}.json',dict(passed=True,workers=workers,round=round_,problems=len(rows),
            prepare_seconds=prepared,total_seconds=time.perf_counter()-started,query_read=False),True);codecheck()
    except BaseException as e:failure(tag,e);raise
    finally:end(tag)

def equal_tree(a,b):
    if torch.is_tensor(a):
        require(a.shape==b.shape and (torch.equal(a,b) if not a.is_floating_point() else torch.allclose(a,b,atol=1e-9,rtol=1e-8)),'Concurrent solver tensor/state mismatch')
    elif isinstance(a,dict):
        require(a.keys()==b.keys(),'Concurrent state keys')
        for k in a:equal_tree(a[k],b[k])
    elif isinstance(a,(list,tuple)):
        require(len(a)==len(b),'Concurrent state lengths')
        for x,y in zip(a,b):equal_tree(x,y)
    else:require(a==b,'Concurrent solver exact state')

def choose():
    configure('coordinator');begin('R3-compare');records=[];eligible=[]
    try:
        for workers in [1,4,8]:
            passed=True;times=[];error=None
            try:
                for rnd in [0,1,2]:
                    total=0.
                    for cap in ['G','P','E','synthetic']:
                        tag=f'R3-{cap}-r{rnd}-C{workers}';base=f'R3-{cap}-r{rnd}-C1'
                        meta=read(OUT/'tests'/f'{tag}.json');require(meta['passed'],'Backend workload incomplete')
                        if cap!='synthetic':total+=meta['total_seconds']
                        for path in sorted((OUT/'R3'/tag).glob('*/head.pt')):
                            ref=OUT/'R3'/base/path.parent.name/'head.pt'
                            a=torch.load(path,map_location='cuda',weights_only=True);b=torch.load(ref,map_location='cuda',weights_only=True)
                            equal_tree(a,b)
                            equal_tree(torch.load(path.with_name('head-solver.pt'),map_location='cuda',weights_only=True),torch.load(ref.with_name('head-solver.pt'),map_location='cuda',weights_only=True))
                            qa=read(path.with_suffix('.quality.json'));qb=read(ref.with_suffix('.quality.json'))
                            for k in ['accepted','iterations','evaluations','optimizer_exit']:require(qa[k]==qb[k],'Concurrent exit/counter mismatch')
                    times.append(total)
            except (RuntimeError,FileNotFoundError) as e:passed=False;error=str(e)
            row=dict(workers=workers,qualified=passed,round_seconds=times,median_seconds=float(np.median(times)) if len(times)==3 else None,error=error)
            records.append(row)
            if passed:eligible.append(row)
        require(any(r['workers']==1 for r in eligible),'Serial backend qualification')
        choice=min(eligible,key=lambda r:(r['median_seconds'],r['workers']))
        write(OUT/'tests/backend-choice.json',dict(qualified=True,workers=choice['workers'],backends=records,selection='complete real workload three-round median; tie lower concurrency',query_read=False),True)
        progress('R3_backend_chosen',workers=choice['workers'],median_seconds=choice['median_seconds']);codecheck()
    except BaseException as e:failure('R3-compare',e);raise
    finally:end('R3-compare')

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('phase',choices=['bench','choose']);p.add_argument('--cap',choices=['P','G','E'],default='G')
    p.add_argument('--workers',type=int,choices=[1,4,8],default=1);p.add_argument('--round',type=int,default=0);p.add_argument('--synthetic',action='store_true')
    a=p.parse_args();choose() if a.phase=='choose' else bench(a.cap,a.workers,a.round,a.synthetic)
