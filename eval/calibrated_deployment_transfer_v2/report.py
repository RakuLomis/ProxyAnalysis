"""Report unchanged business endpoints and the explicit solver repair history."""
from common import *

def run():
    start('report');require(read(OUT/'verification.json')['passed'],'Verify before final report')
    formatter=load_frozen('report').table
    paths=[('主要方法成绩','scores/equal-weight-summary.parquet'),('三项主要比较','comparisons/primary-contrasts.parquet'),
           ('各目标部署','scores/target-summary.parquet'),('全部十二场景','scores/target-group-summary.parquet'),
           ('完整六类分项','scores/class-results.parquet')]
    sections=['# 辅助业务校准迁移实验修复版结果\n\n日期：2026年10月6日。四部署、六业务、30全局内容、480访问、23566连接对。目标四类提供配对校准，目标另两类训练pre/post均禁止使用；测试仅输入post直方图。',
      '## 优化修复\n\n原CT1在500次迭代仍不满足原梯度门。v2采用可逆初始曲率参数预条件化，保持原CE、L2、共享post缩放、标签权限和内容折不变；最终映回原W/b并独立验收。所有五主臂同样处理。旧运行和684个旧新模型不覆盖。新主实验14700次拟合，复用680个诊断模型；原4个主CT0重跑，累计正式新拟合15384次。',
      '## 判定\n\n'+formatter(pd.DataFrame([read(OUT/'comparisons/decision.json')]))]
    for title,path in paths:sections.append('## '+title+'\n\n'+formatter(pd.read_parquet(OUT/path)))
    sections.append('## 统计口径与边界\n\n五折先汇总完整六类混淆矩阵，再取两未覆盖类F1。三项主要比较为CT4对StrongPost、CT1及CT3，10000次共同业务分层内容bootstrap，家族校正98.3333%区间；条件于固定选定模型，不是完整训练不确定性或外部盲测。2/5个百分点辅助代价是实践筛查，不是统计非劣效。部署混合协议、节点、配置及路径效应。尚未完成独立physical-only访问提取，不把给定双侧离线资格集合推广为在线无索引攻击。')
    DOC.mkdir(parents=True,exist_ok=True)
    p=DOC/'calibrated-transfer-results-v2.md'
    # This Markdown is a generated report, not an edit of frozen source.
    p.write_text('\n\n'.join(sections)+'\n',encoding='utf-8')
    finish('report',report=rel(p))

if __name__=='__main__':run()
