"""Seal stopped NER1 artifacts after all writers have finished; no training."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent/'deproxy_moment_game_v1_numeric_repair'))
from common import *

def main():
    started=time.perf_counter();codecheck()
    pointer=read(OUT/'completion-current.json');state=ROOT/pointer['path']
    require(sha(state)==pointer['sha256'],'Final state pointer')
    c=read(state);require(c['integrated_pilot_verified'] and not c['full_experiment_enabled'],'Stopped verified pilot')
    require(not c['full_scope_budget_feasible'],'Current registered budget decision retained')
    report=ROOT/'docs/deproxy-moment-game-v1-20261016/numeric-repair-pilot.md'
    files={rel(p):sha(p) for p in OUT.rglob('*') if p.is_file() and p.name not in ['artifact-seal.json','budget.json','progress.json'] and not p.name.endswith('.tmp')}
    sources={rel(p):sha(p) for p in CODE.glob('*.py')}
    for name in ['deproxy_moment_game_v1_numeric_repair_audit.py','deproxy_moment_game_v1_numeric_repair_forecast.py','deproxy_moment_game_v1_numeric_repair_observer.py','deproxy_moment_game_v1_numeric_repair_finalize.py']:
        p=ROOT/'eval'/name;sources[rel(p)]=sha(p)
    b=read(OUT/'budget.json');elapsed=time.perf_counter()-started
    b['repair_seconds']+=elapsed;b['used_seconds']=b['parent_seconds']+b['repair_seconds']
    b['items'].append(dict(stage='final-artifact-hashing',seconds=elapsed));write(OUT/'budget.json',b)
    files[rel(OUT/'budget.json')]=sha(OUT/'budget.json')
    write(OUT/'artifact-seal.json',dict(files=files,source_files=sources,report={rel(report):sha(report)},
        status=c['status'],query_read=False,H_scored=False,full_experiment_enabled=False,
        budget_seconds=b['used_seconds'],hashing_seconds=elapsed,progress_json_is_volatile=True),True)
    print('NER1 stopped artifacts sealed',len(files),flush=True)

if __name__=='__main__':main()
