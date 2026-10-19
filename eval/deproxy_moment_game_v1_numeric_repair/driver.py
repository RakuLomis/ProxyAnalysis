"""Only the approved repair pilot; never imports historical full runner."""
from common import *
import subprocess

def command(args):
    b=read(OUT/'budget.json');used=b['repair_seconds'];started=time.perf_counter()
    require(used<14400 and b['used_seconds']<86400,'Activity budget before child')
    tag=f'{time.time_ns()}-{Path(args[0]).stem}';path=OUT/'logs'/f'{tag}.log';path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('w',encoding='utf-8') as log:
        proc=subprocess.run([sys.executable,str(CODE/args[0]),*args[1:]],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
    duration=time.perf_counter()-started
    b=read(OUT/'budget.json');inside=b['repair_seconds']-used;uncovered=max(0.,duration-inside)
    b['repair_seconds']+=uncovered;b['used_seconds']=b['parent_seconds']+b['repair_seconds']
    b['items'].append(dict(stage='coordinator-subprocess-overhead',command=args,seconds=uncovered,wall_seconds=duration,child_accounted_seconds=inside,returncode=proc.returncode))
    write(OUT/'budget.json',b)
    progress('NER1_child_finished',command=args,returncode=proc.returncode,wall_seconds=duration,repair_seconds=b['repair_seconds'])
    require(b['repair_seconds']<=14400 and b['used_seconds']<=86400,'Activity budget after child')
    return proc.returncode

def main():
    configure('coordinator')
    require(all(read(OUT/'tests'/f'R1-{cap}-current.json')['passed'] for cap in ['P','G','E']),'R1 serial verification')
    codecheck()
    # Pre-driver shell invocations did not have a whole-process wall recorder.
    # Reserve their entire elapsed uncovered interval as an explicit conservative
    # safety charge (includes development idle time, NOT claimed compute time).
    b=read(OUT/'budget.json')
    if not any(i['stage']=='pre-driver-conservative-wall-reserve' for i in b['items']):
        elapsed=max(0.,time.time()-(OUT/'registration.json').stat().st_mtime)
        reserve=max(0.,elapsed-b['repair_seconds']);b['repair_seconds']+=reserve;b['used_seconds']=b['parent_seconds']+b['repair_seconds']
        b['items'].append(dict(stage='pre-driver-conservative-wall-reserve',seconds=reserve,not_measured_compute=True,reason='upper bound on uncaptured pre-driver activity; includes idle/development'))
        write(OUT/'budget.json',b)
    estimate=1800. # Bounded engineering projection, not a qualified full forecast.
    require(b['repair_seconds']+estimate<14400,'Pilot projection exceeds remaining repair cap')
    write(OUT/'tests/R1-closeout.json',dict(passed=True,heads=25,remaining_pilot_projection_seconds=estimate,
        remaining_pilot_projection_not_full_forecast=True,full_experiment_enabled=False),True)
    steps=[['replay.py','synthetic']]+[['replay.py','legacy','--cap',c] for c in ['P','G','E']]
    rejected=set()
    try:
        for args in steps:require(command(args)==0,'Repair replay stopped; no automatic retry')
        for rnd,order in enumerate([[1,4,8],[4,8,1],[8,1,4]]):
            for workers in order:
                if workers in rejected:continue
                for cap in ['G','P','E','synthetic']:
                    args=['throughput.py','bench','--workers',str(workers),'--round',str(rnd)]
                    args+=['--synthetic'] if cap=='synthetic' else ['--cap',cap]
                    rc=command(args)
                    if rc:
                        # Only this explicit local numerical status permits rejecting
                        # a backend. Integrity/permission/source errors stop everything.
                        log=sorted((OUT/'logs').glob('*-throughput.log'),key=lambda p:p.stat().st_mtime)[-1].read_text(encoding='utf-8')
                        require(workers!=1 and 'Numerical head failure: backend rejected' in log,'Head benchmark stopped; no safe local rejection')
                        rejected.add(workers);break
        require(command(['throughput.py','choose'])==0,'No verified head backend')
        for phase,caps in [('initial',['G','E']),('static',['P','G']),('dynamic',['P','G','E']),('export',['P','G','E'])]:
            for cap in caps:require(command(['integrated.py',phase,'--cap',cap])==0,'Unified fixed P1 stopped')
        require(command(['closeout.py'])==0,'Closeout stopped')
    except BaseException as e:
        failure('repair-driver',e)
        command(['closeout.py','--partial'])
        raise

if __name__=='__main__':main()
