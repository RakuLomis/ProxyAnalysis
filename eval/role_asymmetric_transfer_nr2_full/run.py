"""Authorized full NR2 continuation; inherited cumulative activity cap 8h."""
import time
LOAD_START=time.perf_counter()
from common import *
import common as C

def main():
    C.START=LOAD_START
    latest=read(NR2/'analysis/interpretation.json')['parent_cumulative_with_analysis_seconds']
    components=dict(latest_NR2_analysis_cumulative_seconds=latest,conservative_unmetered_post_closeout_charge_seconds=60.,charge_not_a_measurement=True)
    C.PRIOR=latest+60.;components['total_prior_charged_seconds']=C.PRIOR
    lock=writable(OUT/'run.lock');fd=os.open(lock,os.O_CREAT|os.O_EXCL|os.O_WRONLY);os.write(fd,str(os.getpid()).encode());os.close(fd)
    try:
        require(not (OUT/'failure.json').exists() and not (OUT/'completion.json').exists(),'Terminal full NR2 run; no automatic restart')
        configure();write(OUT/'manifests/prior-activity.json',components)
        import register,engineering,train,predict,score,report,verify
        for name,fn in [('R0',register.run),('E0',engineering.run),('R1',train.adopt),('P3',train.fit),('P4',train.seal),
                        ('P5',predict.run),('P6',score.run),('report',report.run),('verify',verify.run)]:fn()
        primary=read(OUT/'comparisons/primary.json');cost=read(OUT/'scores/C-practical-cost.json');byref={x['reference']:x for x in primary['comparisons']}
        write(OUT/'completion.json',dict(program_complete=True,numeric_pass=True,all_roles_complete=True,H_predictions_sealed=True,H_scored=True,
            new_resumed_fits=1296,adopted_scientific=624,historical_aliases=420,total_lineage_optimization_attempts=1993,
            cumulative_active_seconds=spent(),effect_vs_Psmall=byref['P__m010__SYM']['positive'],
            allocation_effect_same_mass=byref['P__m025__SYM']['positive'],pair_increment=byref['G__m025__UPR']['positive'],
            pre_transform_increment=byref['RawPre__m025__UPR']['positive'],rawpost_exposure_control=byref['RawPost__m025__UPR']['positive'],
            C_overall_cost_pass=cost['overall_pass'],C_each_deployment_cost_pass=cost['each_deployment_pass'],
            new_method_selected_after_H=False,old_stops_preserved=True,verification_sha256=sha(OUT/'verification.json')))
        progress('full_NR2_complete',new_models=1296,logical_endpoints=2340)
    except BaseException as exc:
        write(OUT/'failure.json',dict(type=type(exc).__name__,exception=str(exc),traceback=traceback.format_exc(),
            time_unix=time.time(),cumulative_active_seconds=spent(),automatic_retry=False))
        import report
        report.stop_closeout(exc);print(traceback.format_exc(),flush=True)
    finally:
        write(OUT/'cost-final.json',dict(prior_components=components,new_active_seconds=time.perf_counter()-C.START,
            cumulative_active_seconds=spent(),cap_seconds=28800,program_complete=(OUT/'completion.json').exists()))
        if lock.exists() and lock.read_text()==str(os.getpid()):lock.unlink()
    return 0 if (OUT/'completion.json').exists() else 1

if __name__=='__main__':raise SystemExit(main())
