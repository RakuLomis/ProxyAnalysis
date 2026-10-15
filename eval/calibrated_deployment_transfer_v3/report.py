"""Report unchanged business endpoints and the explicit solver repair history."""
from common import *

def run():
    start('report');require(read(OUT/'verification.json')['passed'],'Verify before final report')
    formatter=load_frozen('report').table
    paths=[('主要方法成绩','scores/equal-weight-summary.parquet'),('三项主要比较','comparisons/primary-contrasts.parquet'),
           ('各目标部署','scores/target-summary.parquet'),('全部十二场景','scores/target-group-summary.parquet'),
           ('完整六类分项','scores/class-results.parquet')]
    sections=['# 辅助业务校准迁移实验修复版结果\n\n日期：2026年10月6日。四部署、六业务、30全局内容、480访问、23566连接对。目标四类提供配对校准，目标另两类训练pre/post均禁止使用；测试仅输入post直方图。',
      '## 优化修复\n\n第一版CT1耗尽500次仍不满足原梯度门；第二版预条件化修复原角色，但另一角色因目标变化小而提前退出。第三版保留可逆曲率坐标和原CE、L2、post缩放、标签权限与内容折，采用原坐标梯度感知停止。五主臂统一使用同一求解器，原门及500/625预算不变。两个旧运行、684个第一版模型和104个第二版主候选全部保留。第三版14700个主模型重新拟合，300个先导计入内层预算；复用680个诊断模型。累计接受的新正式模型15488个，不含失败、合成测试及确定性诊断。',
      '## 判定\n\n'+formatter(pd.DataFrame([read(OUT/'comparisons/decision.json')]))]
    for title,path in paths:sections.append('## '+title+'\n\n'+formatter(pd.read_parquet(OUT/path)))
    sections.append('## 统计口径与边界\n\n五折先汇总完整六类混淆矩阵，再取两未覆盖类F1。三项主要比较为CT4对StrongPost、CT1及CT3，10000次共同业务分层内容bootstrap，家族校正98.3333%区间；条件于固定选定模型，不是完整训练不确定性或外部盲测。2/5个百分点辅助代价是实践筛查，不是统计非劣效。部署混合协议、节点、配置及路径效应。尚未完成独立physical-only访问提取，不把给定双侧离线资格集合推广为在线无索引攻击。')
    DOC.mkdir(parents=True,exist_ok=True)
    p=DOC/'calibrated-transfer-results-v3.md'
    # This Markdown is a generated report, not an edit of frozen source.
    p.write_text('\n\n'.join(sections)+'\n',encoding='utf-8')
    finish('report',report=rel(p))

if __name__=='__main__':run()
