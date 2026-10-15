"""Sequential authorized continuation; fail closed and never resume failed solver states."""
from common import *
import subprocess

def run():
    require(read(OUT/'pilot/promotion.json')['passed'],'Fixed numerical pilot not passed')
    require(not (OUT/'completion.json').exists(),'Experiment already complete')
    # Learning code remains sealed in its original append-only extension.
    sources={rel(p):sha(p) for p in [Path(__file__),Path(__file__).with_name('score.py'),
                                    Path(__file__).with_name('full_report.py')]}
    write(OUT/'manifests/continuation-code.json',{'sha256':sources,'science_changed':False,
        'remaining_classifiers':1536,'launch_authority':'user approved complete finite implementation plan',
        'target_U_or_H_tuning_allowed':False})
    stages=[('formal.py',['remaining']),('score.py',[]),('full_report.py',[])]
    for script,args in stages:
        progress('continuation_dispatch',script=script)
        subprocess.run([sys.executable,str(Path(__file__).with_name(script)),*args],cwd=ROOT,check=True)

if __name__=='__main__':run()
