"""Generate full evidence tables and static Python figures after frozen scoring."""
from common import *


def table(f):
    return f.to_markdown(index=False, floatfmt='.6f')


def main():
    cli(__doc__).parse_args(); authorize()
    assert read(OUT/'independent-verification.json')['passed']
    assert read(OUT/'diagnosis-complete.json')['passed']
    a = pd.read_parquet(OUT/'aggregate-metrics.parquet')
    contrasts = pd.read_parquet(OUT/'primary-contrasts.parquet')
    pp = pd.read_parquet(OUT/'per-protocol-seed-metrics.parquet')
    pc = pd.read_parquet(OUT/'per-class-metrics.parquet')
    error = pd.read_parquet(OUT/'error-transitions.parquet')
    ret = pd.read_parquet(OUT/'retrieval.parquet'); ret['top1'] = ret['rank'].eq(1)
    retagg = ret.groupby(['arm', 'mode'])[['top1', 'rank', 'gap']].mean().reset_index()
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    figures = OUT/'figures'; figures.mkdir(exist_ok=True)
    final = a[a.stage.eq('finetune')].set_index('arm').loc[ARMS].reset_index()
    fig, axes = plt.subplots(1, 2, figsize=(12, 4), layout='constrained')
    axes[0].bar(final.arm, final.F1); axes[0].set_ylim(0, 1); axes[0].set_ylabel('Protocol-equal macro-F1')
    prim = contrasts[contrasts.primary].reset_index(drop=True)
    axes[1].errorbar(prim.delta, np.arange(len(prim)),
                    xerr=np.array([prim.delta-prim.adjusted_low, prim.adjusted_high-prim.delta]), fmt='o')
    axes[1].axvline(0, color='black', linewidth=.8); axes[1].set_yticks(np.arange(len(prim)), prim.contrast)
    axes[1].set_xlabel('F1 difference; five-comparison adjusted intervals')
    fig.savefig(figures/'final-comparisons.png', dpi=180); plt.close(fig)
    probes = a[a.stage.eq('probe')]
    fig, ax = plt.subplots(figsize=(9, 4), layout='constrained')
    pos = np.arange(len(SOURCES))
    for i, hk in enumerate(['linear', 'mlp']):
        f = probes[probes['head'].eq(hk)].set_index('arm').loc[SOURCES]
        ax.bar(pos+(i-.5)*.35, f.F1, .35, label=hk)
    ax.set_xticks(pos, SOURCES); ax.set_ylim(0, 1); ax.set_ylabel('Frozen probe macro-F1'); ax.legend()
    fig.savefig(figures/'frozen-probes.png', dpi=180); plt.close(fig)
    passed = prim.adjusted_low.gt(0)
    finaltext = '五项主比较均建立正向校正区间。' if passed.all() else f'五项主比较中 {int(passed.sum())} 项建立正向校正区间，不能宣称完整假设全部通过。'
    scopes = ('仅已见五部署 E1、600访问、30内容、六业务、四重复、全局内容五折。'
              'W含重复传输，P为正载荷事件，R为窗口全局方向段，不是旧FR。'
              'Hy2、E2、外部日期、独立配置及在线无索引识别均未执行。')
    sections = [
        '# Extend 机制条件化配对表示学习正式结果',
        '日期：2026-10-04。本报告区分固定候选的实测结果、解释性诊断与未验证外推。'+finaltext,
        '## 数据模型与权限', scopes+' 正式推理只有post六量。所有训练/编码/推理使用CUDA，无TF32/AMP。'
        'B4/B5/B6使用旧P3的18内容拟合、6内容查询decoded中心，不用真实query漂移；B6全流程匿名组。'
        ' E为6→64→32，P为32→32→16，A为无偏置6→32；最终E+32→32→6共3782参数。'
        '各SSL1000步，微调/探针1000步，B0L监督2000步；三seed固定，不早停、不选择测试checkpoint。',
        '## 完整实验臂', 'B0同架构监督；B0L同总更新监督；B1充分post SSL；B2两侧侧内SSL；'
        'B3无条件真配；B4通用中心条件；B5机制中心条件主方法；B6匿名组条件。'
        '所有SSL每步四编码槽；B1四post，B2两post两pre，B3至B6三post一pre。'
        '因此编码槽数相同不意味着各侧曝光完全相同。组级16组合不是16独立访问。',
        '## 最终业务表现', table(final.drop(columns=['stage', 'head'])),
        '## 五项主要比较与解释比较', table(contrasts),
        '10,000次按业务分层内容簇bootstrap，部署/seed/方法共享成员。五项主家族分位0.005/0.995；'
        '次要比较为普通95%。区间条件于固定模型，跨零不是等效。',
        '## 冻结表示的业务可读性', table(probes),
        'R0是未训练随机E，不是已接受标签的B0。线性和MLP各自使用相同读出预算，诊断不替代最终主终点。',
        '## 逐部署成绩', table(pp.groupby(['stage', 'arm', 'head', 'protocol'])[['F1', 'accuracy', 'CE_bits', 'Brier']].mean().reset_index()),
        '## 逐业务成绩', table(pc.groupby(['stage', 'arm', 'head', 'class'])[['precision', 'recall', 'F1']].mean().reset_index()),
        '## 逐seed原始部署成绩', table(pp),
        '## 错误修复与新增错误', table(error.groupby('reference')[['repaired', 'new_error']].sum().reset_index()),
        '计数包含三seed，不能将1800次预测当成1800独立访问。内容和业务详细台账见error-transitions.parquet。',
        '## 配对检索与条件敏感性', table(retagg),
        '此处单独使用test pre作封存后离线诊断，不是业务推理权限。候选仅同部署，屏蔽同内容其他重复。'
        '三种中心各25个source-only全训练范围回归，共75拟合，不用测试内容拟合。'
        'center_direct与神经检索尺度/目标不同，均不是业务互信息或协议机制识别证据。',
        '## CUDA算量与工程审计', table(pd.DataFrame([
            {'stage': stage, 'fold': fold, 'tasks': read(OUT/stage/f'f{fold}'/'complete.json')['tasks'],
             'seconds': read(OUT/stage/f'f{fold}'/'complete.json')['seconds']}
            for stage in ['ssl', 'probe', 'finetune'] for fold in range(5)])),
        '90个SSL、210个冻结读出、120个最终分类器。每折独立批处理，权重不共享。'
        '39600条OOF来自600独立访问，全部重载CUDA预测回放。旧封存输入/源码哈希保持。'
        '物理身份资格沿用P2/P3注册，五例未见SYN和历史预检曝光限制继续披露；不是普遍无泄漏数学证明。',
        '## 结项与未验证范围', '本轮固定停止，不自动扩大网络、改变lambda或mask、删除业务、补采或启动E2。'
        '若只优于group而不优于普通SSL，不能写成普遍配对收益；若不优于B4，新增机制中心用途尚未建立。'
        '六维升维不恢复丢失的顺序。本数据已反复研究，不是外部盲测。',
        '## 图与复现', '![Final comparisons](../../outputs/mechanism-conditioned-ssl-extend/run-01/figures/final-comparisons.png)\n\n'
        '![Frozen probes](../../outputs/mechanism-conditioned-ssl-extend/run-01/figures/frozen-probes.png)\n\n'
        '实现为eval/mechanism_conditioned_ssl；契约见experiment-contract.md。'
        '执行prepare→engineering→run各stage→diagnose→score→verify→report；E2需另行确认。']
    doc = ROOT/'docs/mechanism-conditioned-ssl-extend'; doc.mkdir(parents=True, exist_ok=True)
    (doc/'formal-results.md').write_text('\n\n'.join(sections)+'\n', encoding='utf-8')
    (doc/'model-card.md').write_text('# 机制条件化 post 编码器模型卡\n\n'
        '仅Extend已见五部署、完整六业务、登记访问窗口六量。post-only推理，训练允许额外pre与配对条件；'
        '不输入协议身份、IP/port/SNI或pre辅助量。6→64→32编码器加32→32→6业务头，3782参数。'
        '未验证Hy2、未见协议/配置/日期、DIRECT或在线无索引窗口。数据反复研究，区间条件于固定模型。\n', encoding='utf-8')
    write(OUT/'stopping-decision.json', {'frozen': True, 'primary_positive': int(passed.sum()),
          'primary_total': 5, 'E2_started': False, 'automatic_hyperparameter_search': False})
    write(OUT/'report-manifest.json', {'complete': True, 'result_sha256': sha(doc/'formal-results.md'),
                                      'prediction_sha256': sha(OUT/'oof.parquet')})
    print('Report saved:', doc/'formal-results.md', flush=True)


if __name__ == '__main__': main()
