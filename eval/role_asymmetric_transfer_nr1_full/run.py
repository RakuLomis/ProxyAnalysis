"""Authorized full RA1 continuation with an unchanged cumulative 8h cap."""
import time
_LOAD_START=time.perf_counter()
from common import *
import common as C

def main():
    C.START=_LOAD_START
    old=read(OLD/'cost-ledger.json')['active_seconds'];nr=read(NR/'cost-ledger.json')['activity_seconds']
    oldanalysis=read(ROOT/'outputs/role-asymmetric-transfer-v1-20261017/closeout-20261018/stop-analysis.json')['analysis_seconds']
    nranalysis=read(NR/'analysis/summary.json')['additional_readonly_analysis_seconds']
    components=dict(original_run_seconds=old,NR1_seconds=nr,recorded_old_analysis_seconds=oldanalysis,recorded_NR1_analysis_seconds=nranalysis,
                    conservative_unmetered_prior_overhead_charge_seconds=60.,charge_not_a_fabricated_measurement=True)
    C.PRIOR=old+nr+oldanalysis+nranalysis+60.;components['total_prior_charged_seconds']=C.PRIOR
    lock=writable(OUT/'run.lock');fd=os.open(lock,os.O_CREAT|os.O_EXCL|os.O_WRONLY);os.write(fd,str(os.getpid()).encode());os.close(fd)
    try:
        require(not (OUT/'failure.json').exists() and not (OUT/'completion.json').exists(),'Terminal run; no automatic restart')
        configure();write(OUT/'manifests/prior-activity.json',components)
        import register,train,predict,score,report,verify
        steps=[('R0',register.run),('R1',train.adopt),('P3',train.fit),('P4',train.seal),('P5',predict.run),('P6',score.run),('report',report.run),('verify',verify.run)]
        for name,fn in steps:fn()
        primary=read(OUT/'comparisons/primary.json');cost=read(OUT/'scores/C-practical-cost.json')
        byref={v['reference']:v for v in primary['comparisons']}
        complete=dict(program_complete=True,numeric_pass=True,all_roles_complete=True,H_predictions_sealed=True,H_scored=True,new_resumed_fits=1754,
            adopted_scientific=166,historical_aliases=420,total_physical_lineage_attempts=1954,cumulative_active_seconds=spent(),
            effect_vs_Psmall=byref['P__m010__SYM']['positive'],allocation_effect_same_mass=byref['P__m025__SYM']['positive'],pair_increment=byref['G__m025__UPR']['positive'],
            pre_transform_increment=byref['RawPre__m025__UPR']['positive'],rawpost_exposure_control=byref['RawPost__m025__UPR']['positive'],
            C_overall_cost_pass=cost['overall_pass'],C_each_deployment_cost_pass=cost['each_deployment_pass'],new_method_selected_after_H=False,
            original_stop_preserved=True,verification_sha256=sha(OUT/'verification.json'))
        write(OUT/'completion.json',complete);progress('full_nr1_complete',new_models=1754,logical_endpoints=2340)
    except BaseException as exc:
        write(OUT/'failure.json',dict(type=type(exc).__name__,exception=str(exc),traceback=traceback.format_exc(),time_unix=time.time(),cumulative_active_seconds=spent(),automatic_retry=False))
        import report
        report.stop_closeout(exc)
        raise
    finally:
        write(OUT/'cost-final.json',dict(prior_components=components,new_active_seconds=time.perf_counter()-C.START,cumulative_active_seconds=spent(),cap_seconds=28800))
        if lock.exists() and lock.read_text()==str(os.getpid()):lock.unlink()

if __name__=='__main__':main()
