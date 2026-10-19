"""Independent convex solves on dedicated streams; ledger written by coordinator."""
from common import *
from classifier import solve,persist
from problems import spec_cap
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
                progress('convex_head',problem=key,workers=workers,accepted=result['quality']['accepted'],iterations=result['quality']['iterations'])
        require(not failed,'Convex head failed original gate; pending is not fallback')
    require(len(results)==len(problems),'Complete workload only')
    return results
