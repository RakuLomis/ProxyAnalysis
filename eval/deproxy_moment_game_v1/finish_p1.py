"""Close fixed P1, then promote only if every engineering and budget gate passes."""
from common import *
import subprocess

def call(name):
    result=subprocess.run([sys.executable,str(CODE/name)],cwd=ROOT)
    require(result.returncode==0,'Post-P1 engineering stop; no automatic retry: '+name)

def run():
    barrier('P1-numeric-complete.json');require(read(OUT/'manifests/P0-nested-fold-audit.json')['passed'],'Nested fold audit')
    require(read(OUT/'tests/P1-selection-math.json')['passed'],'Selection rules')
    for name in ['activity_audit.py','provenance.py','inference_check.py','cost.py']:call(name)
    forecast=read(OUT/'manifests/P1-cost-forecast.json')
    files=[OUT/'manifests/P0-nested-fold-audit.json',OUT/'tests/P1-selection-math.json',OUT/'tests/P1-activity-audit.json',OUT/'tests/P1-provenance-audit.json',OUT/'tests/P1-inference.json',OUT/'manifests/P1-cost-forecast.json']
    seal(OUT/'manifests/P1-closeout.json',files,engineering_passed=True,budget_passed=forecast['passed'],H_scored=False,source_query_scored=False)
    if forecast['passed']:call('run.py')
    else:
        immutable(OUT/'completion.json',dict(status='stop_budget_forecast_requires_user',P0_passed=True,P1_engineering_passed=True,
            P1_budget_passed=False,formal_complete=False,formal_remaining_scope_started=False,H_scored=False,
            source_query_scored=False,conservative_forecast_hours=forecast['conservative_total_hours']))

if __name__=='__main__':
    try:run()
    except BaseException as e:failure('P1-closeout',e);raise
