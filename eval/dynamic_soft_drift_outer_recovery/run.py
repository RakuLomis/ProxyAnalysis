"""Run unit tests, register/prepare, then the isolated source-only pilot."""
import argparse
from common import *

def main():
    ap=argparse.ArgumentParser();ap.add_argument('command',choices=['unit-test','prepare','pilot','report']);a=ap.parse_args()
    import tests
    if a.command=='unit-test':print(tests.run(),flush=True);return
    if a.command=='prepare':
        import recover
        recover.register()
        with stage('prepare'):
            write(OUT/'tests/outer-policy.json',tests.run());write(OUT/'tests/permissions.json',tests.permission_tests())
            require(read(OUT/'recovery-audit.json')['passed'],'Recovery audit failed')
            write(OUT/'ready.json',dict(passed=True,trajectories=36,business_authorized=False,H_U_reads=0,new_fits=0))
            textfile(DOC/'implementation-status.md','# 动态软约束漂移外层优化先导实施状态\n\n独立先导已登记。投影、回溯、质量、权限与安全序列化检查以及原全1起点重放均已通过。范围为f0全部12角色、36条源内轨迹，累计活动计算上限4小时；本轮不授权新的业务分类或H/U读取。\n\n运行结束后生成pilot-results.md和独立verification.json。旧run-02和P-small结果不变。\n')
        progress('ready',trajectories=36,new_source_fits=0,business_authorized=False,controlled_recovery=True)
    elif a.command=='pilot':
        require(read(OUT/'ready.json')['passed'],'Preparation not passed')
        require(not (OUT/'completion.json').exists(),'Pilot already stopped; no automatic retry/resume')
        import pilot
        import report
        import verify
        try:
            with stage('pilot'):pilot.run()
        except BaseException:
            if (OUT/'completion.json').exists():
                with stage('report'):report.build()
            raise
        with stage('report'):report.build()
        with stage('verify'):verify.verify()
    else:
        import report
        import verify
        with stage('report'):report.build()
        with stage('verify'):verify.verify()

if __name__=='__main__':main()
