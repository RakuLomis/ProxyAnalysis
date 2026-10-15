"""Alias accepted P0; freeze unchanged science and retain parent stop."""
from common import *

def run():
    configure();require(not (OUT/'manifests/seal.json').exists(),'Refuse repair registration overwrite')
    parent=read(PARENT/'manifests/experiment-contract.json')
    require(sha(PARENT/'manifests/experiment-contract.json')==read(PARENT/'manifests/seal.json')['sha256'],'Parent contract')
    stop=read(PARENT/'completion.json');require(not stop['passed'] and not stop['H_scored'] and stop['stage']=='P1_cuda_pilot','Preserve parent stop')
    verifyseal(PARENT/'packages/complete.json');require(read(PARENT/'audits/P0-complete.json')['passed'],'P0 reuse gate')
    verifyseal(PARENT/'manifests/engineering-code.json')
    fixed=[PARENT/'completion.json',PARENT/'ledger.json',PARENT/'pilot/closeout.json',
           PARENT/'manifests/experiment-contract.json',PARENT/'manifests/seal.json',PARENT/'packages/complete.json',
           PARENT/'audits/P0-complete.json',PARENT/'audits/unit-tests.json',PARENT/'manifests/engineering-code.json']
    repair=dict(parent=str(PARENT.relative_to(ROOT)),parent_stop_unchanged=True,
                authorization='2026-10-14 user authorized engineering records and batching numeric interface only',
                P0_alias=True,old_terminal_models_imported=False,new_model_capacity=False,
                losses_and_data_permissions_unchanged=True,thresholds_unchanged=True,
                parent_files={rel(p):sha(p) for p in fixed})
    c=dict(parent);c['version']='post-associated-residual-stage-A-v2-engineering';c['repair']=repair
    same=[k for k in parent if k!='version']
    require(all(c[k]==parent[k] for k in same),'Scientific field changed')
    write(OUT/'manifests/experiment-contract.json',c)
    write(OUT/'manifests/seal.json',dict(sha256=sha(OUT/'manifests/experiment-contract.json')))
    write(OUT/'manifests/repair-scope.json',dict(**repair,science_equal_fields=same,passed=True))
    oldled=read(PARENT/'ledger.json')
    write(OUT/'ledger.json',dict(training_wall_seconds=oldled['training_wall_seconds'],inherited_training_wall_seconds=oldled['training_wall_seconds'],
          inherited_engineering_residual_fits=3,engineering_residual_fits=0,engineering_teacher_fits=0,
          teachers=0,residual_fits=0,source_LR_new=0))
    write(OUT/'packages/complete.json',read(PARENT/'packages/complete.json'))
    write(OUT/'audits/P0-complete.json',dict(passed=True,roles=780,reused_from=rel(PARENT/'audits/P0-complete.json'),new_fits=0,H_reads=0,U_reads=0))
    write(OUT/'inventory.json',dict(passed=True,roles=60,source_tasks=720,reused_training_task_packages=780,reused_bases=780,new_fits=0))
    progress('repair_registered',P0_reused=780,science_fields_unchanged=len(same))

if __name__=='__main__':run()
