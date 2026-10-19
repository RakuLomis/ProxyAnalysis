"""Bounded persistent source-only schedule. Any failure preserves pending work."""
from common import *
import subprocess

def call(script,args=()):
    start=time.time();name=f'{time.time_ns()}-{Path(script).stem}';logs=OUT/'logs';logs.mkdir(parents=True,exist_ok=True)
    with (logs/(name+'.stdout.log')).open('w',encoding='utf-8') as so,(logs/(name+'.stderr.log')).open('w',encoding='utf-8') as se:
        child=subprocess.Popen([sys.executable,'-u',str(CODE/script),*args],cwd=ROOT,stdout=so,stderr=se)
        # Registration creates the budget, so use a launch bound for that first call.
        if script!='register.py':write(OUT/'active-child.json',dict(pid=child.pid,script=script,args=list(args),stdout=rel(logs/(name+'.stdout.log')),stderr=rel(logs/(name+'.stderr.log')),unix=start))
        try:
            remaining=10800-(start-read(OUT/'budget.json')['start_unix']) if (OUT/'budget.json').exists() else 10800
            rc=child.wait(timeout=max(.1,remaining))
        except subprocess.TimeoutExpired:
            child.terminate();child.wait(timeout=30);raise RuntimeError('3h pilot cap watchdog')
    b=read(OUT/'budget.json');b['items'].append(dict(stage=Path(script).stem+(':'+','.join(args) if args else ''),seconds=time.time()-start,returncode=rc))
    b['used_seconds']=time.time()-b['start_unix'];write(OUT/'budget.json',b)
    require(rc==0,'Child stopped: '+script+' '+str(args));deadline()
    if script!='register.py':codecheck()

def forecast():
    # Fixed two roles, six paths and eight heads. No business query has been read.
    b=read(OUT/'budget.json');used=time.time()-b['start_unix'];gen={}
    for cap in ['P','G']:gen[cap]=read(OUT/'workers'/f'generate-{cap}-pilot.json')
    fit=read(OUT/'workers/fit-pilot.json');paths=sum(v['paths'] for v in gen.values());require(paths==6 and fit['heads']==8,'Fixed engineering subset')
    gen_remaining=sum(v['seconds']/v['paths']*(96-4 if k=='P' else 48-2) for k,v in gen.items())
    fit_remaining=fit['seconds']/8*184
    total=used+1.5*(gen_remaining+fit_remaining)+600
    result=dict(used_seconds=used,measured_paths=6,measured_heads=8,generation_remaining_seconds=gen_remaining,
        convex_remaining_seconds=fit_remaining,conservative_total_seconds=total,forecast_gate_seconds=8640,passed=total<=8640,
        overhead_reserve_seconds=600,empirical_not_runtime_bound=True,actual_H_U_reads=0,query_reads=0)
    immutable(OUT/'manifests/P1-forecast.json',result);require(result['passed'],'2.4h conservative source pilot forecast failed')
    files=[OUT/'manifests/math-complete.json',OUT/'manifests/P1-forecast.json']
    seal(OUT/'manifests/P1-complete.json',files,engineering_passed=True,budget_passed=True)
    progress('P1_passed',conservative_hours=total/3600)

def run():
    require(not OUT.exists(),'No implicit restart')
    try:
        call('register.py');call('prepare.py');call('tests.py')
        for cap in ['P','G']:call('worker.py',['generate','--cap',cap,'--which','pilot'])
        call('worker.py',['fit','--which','pilot']);forecast()
        for cap in ['P','G']:call('worker.py',['generate','--cap',cap,'--which','rest'])
        call('worker.py',['fit','--which','rest'])
        for phase in ['seal','predict','diagnose']:call('evaluate.py',[phase])
        call('score.py');call('report.py')
        b=read(OUT/'budget.json');immutable(OUT/'completion.json',dict(program_complete=True,numeric_pass=True,source_only=True,H_scored=False,
            actual_H_U_reads=0,source_query_pre_offline=True,heads=192,paths=144,cumulative_seconds=b['used_seconds'],
            progression_screen=read(OUT/'scores/progression-screen.json')['passed'],full_run_not_started=True))
        seal(OUT/'manifests/complete-seal.json',[OUT/'completion.json',OUT/'manifests/report-complete.json',OUT/'manifests/scores-complete.json'])
        progress('complete',source_only=True,H_scored=False,seconds=b['used_seconds'])
    except BaseException as e:
        if OUT.exists():
            failure('driver',e);immutable(OUT/'stop-record.json',dict(reason=str(e),program_complete=False,pending_is_not_ZERO=True,H_scored=False,
                cumulative_seconds=time.time()-read(OUT/'budget.json')['start_unix'] if (OUT/'budget.json').exists() else 0))
        raise

if __name__=='__main__':run()
