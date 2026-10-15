"""One registered workflow; no automatic retry, H only after complete seals."""
import argparse
from common import *

def prepare():
    import register,tests,scales,compatibility,eligibility
    register.run()
    with stage('prepare'):
        write(OUT/'tests/outer-policy.json',tests.run());write(OUT/'tests/permissions.json',tests.permission_tests());write(OUT/'tests/qualified-policy.json',tests.strategy_tests())
        compatibility.run();scales.prepare();eligibility.reuse_pilot()
        write(OUT/'ready.json',dict(passed=True,remaining_trajectories=144,reused_f0=36,H_U_reads=0,new_source_fits=0,new_final_fits=0,global_budget_hours=20,C_overall_max_cost=.01,C_deployment_max_cost=.02))
        textfile(DOC/'implementation-status.md','# 资格启用与固定回退实施状态\n\n用户确认的原资格、固定回退、累计20小时优化预算及C业务代价门已冻结。120个回退模型的928行槽位、原目标及梯度重放和420参照完整性核验通过；f0保留12启用、24回退。其余144条源内轨迹就绪，所有180决定和600模型端点封存前不读取H。\n')
    progress('ready',remaining=144,CUDA=True,H_U_reads=0,new_fits=0)

def execute():
    import trajectory,eligibility,endpoints,predict,score,verify,report
    require(read(OUT/'ready.json')['passed'],'Preparation incomplete');require(not (OUT/'completion.json').exists(),'Stopped run cannot automatically restart')
    seconds={};began=time.perf_counter();phase='optimization';clock_started=False
    try:
        with stage('optimization'):
            start_clock();clock_started=True;resource_gate()
            for r in contract()['roles']:
                if r['outer']==0:continue
                for arm in ARMS:
                    resource_gate();root=OUT/'trajectories'/r['id']/arm;require(not (root/'result.json').exists(),'Fresh registered run only')
                    trajectory.fit_role(r,arm);eligibility.publish(r,arm,root)
                    count=len(list((OUT/'decisions').rglob('*.json')));progress('strategy_terminal',role=r['id'],arm=arm,decisions=count,expected=180,ledger=read(OUT/'ledger.json'))
            eligibility.seal_all();stop_clock();clock_started=False
        seconds[phase]=time.perf_counter()-began
        for phase,fn in [('models',endpoints.run),('predict',predict.run)]:
            began=time.perf_counter()
            with stage(phase):fn()
            seconds[phase]=time.perf_counter()-began
        phase='score';began=time.perf_counter();score.run();seconds[phase]=time.perf_counter()-began
        phase='verify';began=time.perf_counter()
        # Verification publishes a seal only AFTER its own stage marker is final.
        with stage('preverify'):pass
        vh=verify.run();seconds[phase]=time.perf_counter()-began
        write(OUT/'completion.json',dict(status='qualified_policy_complete',passed=True,formal_complete=True,H_scored=True,verification_sha256=vh,phase_seconds=seconds,ledger=read(OUT/'ledger.json'),automatic_extension=False))
        report_path=report.build();write(OUT/'report-seal.json',dict(passed=True,path=rel(report_path),sha256=sha(report_path),verification_sha256=vh));progress('complete',verification_sha256=vh)
    except BaseException as exc:
        if clock_started:stop_clock()
        status='paused_global_resource' if isinstance(exc,BudgetStop) else 'stop_integrity_or_numeric'
        write(OUT/'completion.json',dict(status=status,passed=False,formal_complete=False,H_scored=(OUT/'scores/pooled.parquet').exists(),reason=str(exc),stage=phase,phase_seconds=seconds,ledger=read(OUT/'ledger.json'),automatic_retry=False))
        report.build();raise

def main():
    ap=argparse.ArgumentParser();ap.add_argument('command',choices=['unit-test','prepare','execute']);cmd=ap.parse_args().command
    if cmd=='unit-test':
        import tests
        print(tests.run());print(tests.strategy_tests())
    elif cmd=='prepare':prepare()
    else:execute()

if __name__=='__main__':main()

