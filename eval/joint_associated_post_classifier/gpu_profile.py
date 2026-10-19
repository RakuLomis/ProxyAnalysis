"""Bounded source-training CUDA probes only. Never shadow the stdlib profile module."""
from common import *
from data import TrainingPool,pilot_roles
from train import Engine
from telemetry import Sampler

def one_case(pool,backend,n,graph,sampler):
    rs=pilot_roles();jobs=[]
    for i in range(n):
        lam=[0.,.1,1.][i%3]
        # Independent engineering copies, never counted as new visits or official models.
        jobs.append(dict(role=rs[i%len(rs)],arm='JC' if lam==0 else ('JP' if i%2 else 'JG'),
             recipe=dict(lam=lam,lr=.001,gamma=.001),seed=SOURCE_SEED+i))
    data=[pool.get(j['role'],j['arm'],j['recipe']['lam']) for j in jobs]
    torch.cuda.empty_cache();torch.cuda.reset_peak_memory_stats()
    name=f'{backend}-'+('graph' if graph else 'eager')+f'-n{n}'
    sampler.label(name+'-setup');setup=time.perf_counter()
    en=Engine(data,jobs,backend)
    if graph:en.capture()
    torch.cuda.synchronize();setup_seconds=time.perf_counter()-setup
    en.advance(10);torch.cuda.synchronize()
    sampler.label(name);start=time.perf_counter();start_event=torch.cuda.Event(enable_timing=True);end_event=torch.cuda.Event(enable_timing=True)
    start_event.record();updates=0
    # Bounded: at most 1000 probe updates/model, no checkpoints promoted to science.
    while updates<1000:
        en.advance(25);updates+=25;torch.cuda.synchronize()
        if time.perf_counter()-start>=6.:break
    end_event.record();torch.cuda.synchronize();elapsed=time.perf_counter()-start
    health=not bool(en.net.bad.any())
    value=dict(name=name,backend=backend,cuda_graph=graph,models=n,updates_per_model=updates,
         model_updates=n*updates,seconds=elapsed,cuda_event_seconds=start_event.elapsed_time(end_event)/1000,
         model_updates_per_second=n*updates/elapsed,setup_seconds=setup_seconds,healthy=health,
         peak_allocated_MiB=torch.cuda.max_memory_allocated()/1048576,peak_reserved_MiB=torch.cuda.max_memory_reserved()/1048576,
         allocated_after_MiB=torch.cuda.memory_allocated()/1048576,probe_only=True,scientific_models_created=0)
    sampler.label(name+'-cleanup');time.sleep(.1)
    value['telemetry']=sampler.summary(name)
    del en,data,jobs;torch.cuda.empty_cache()
    progress('P1_GPU_case',**{k:value[k] for k in ['name','seconds','model_updates_per_second','peak_allocated_MiB']})
    return value

def profile(tag,qualification_tag=None):
    with engineering(tag) as root:
        if qualification_tag is None:
            qualification_tag=read(OUT/'engineering/qualification-index.json')['latest_tag']
        qual=read(OUT/'engineering'/qualification_tag/'registered-qualification.json')
        for p,h in qual['code_sha256'].items():require(sha(ROOT/p)==h,'Code changed since numerical qualification')
        pool=TrainingPool();sampler=Sampler(root/'nvidia-smi-samples.json').start();cases=[]
        try:
            # An actual idle/background window, not a single utilization screenshot.
            time.sleep(7);baseline=sampler.summary('baseline')
            cases.append(one_case(pool,'independent',8,False,sampler))
            for n in [8,32,64]:cases.append(one_case(pool,'independent',n,True,sampler))
            if qual['backends'].get('streams',{}).get('passed'):
                for n in [8,32,64,128]:cases.append(one_case(pool,'streams',n,True,sampler))
            if qual['backends']['tensorized']['passed']:
                for n in [16,64,256,1024]:
                    free,total=torch.cuda.mem_get_info()
                    if free<2*1024**3:break
                    cases.append(one_case(pool,'tensorized',n,True,sampler))
                    # Avoid allocation-only 'utilization': the next size needs a measured throughput rationale.
                    if n>=256 and len(cases)>=2 and cases[-1]['model_updates_per_second']<.95*cases[-2]['model_updates_per_second']:break
            else:progress('P1_GPU_tensorized_skipped',reason='prefix gate failed; preserving original tolerance')
        finally:sampler.stop()
        good=[r for r in cases if r['healthy']]
        require(good,'No healthy CUDA probe')
        fastest=max(good,key=lambda v:v['model_updates_per_second'])
        choice=dict(backend=fastest['backend'],cuda_graph=fastest['cuda_graph'],batch_size=fastest['models'],
                    throughput=fastest['model_updates_per_second'],source='engineering compute only; no validation scores',
                    formal_ready=False,remaining='complete numerical/checkpoint prefix gates at selected occupancy, then run fixed P1 pilot; review GPU report before full matrix')
        immutable(root/'summary.json',dict(baseline=baseline,cases=cases,recommendation=choice,
              actual_H_reads=0,actual_U_reads=0,query_reads=0,formal_training_started=False,
              global_utilization_is_not_process_SM_occupancy=True,profile_source_roles=12))
        entry=dict(path=rel(root/'summary.json'),recommendation=choice)
        immutable(root/'profile-index-entry.json',entry)
        index=OUT/'engineering/profile-index.json';history=read(index)['history'] if index.exists() else []
        write(index,dict(history=history+[entry],latest_tag=tag))
        progress('P1_GPU_observation_complete',recommendation=choice)
