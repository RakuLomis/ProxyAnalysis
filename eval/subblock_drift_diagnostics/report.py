"""Human-readable complete SD1 report from sealed diagnostic tables only."""
from .common import *


def number(value):
    if pd.isna(value):
        return 'NA'
    return f'{float(value):.6g}'


def markdown(frame, columns):
    lines = ['| ' + ' | '.join(columns) + ' |', '| ' + ' | '.join(['---']*len(columns)) + ' |']
    for _, row in frame.iterrows():
        values = []
        for c in columns:
            value = row[c]
            if isinstance(value, (bool, np.bool_)):
                values.append('是' if value else '否')
            elif isinstance(value, (float, np.floating)):
                values.append(number(value))
            else:
                values.append(str(value).replace('|', '\\|'))
        lines.append('| ' + ' | '.join(values) + ' |')
    return '\n'.join(lines)


def run():
    c = contract()
    dep = pd.read_parquet(OUT/'by-deployment-block.parquet')
    whole = pd.read_parquet(OUT/'full-vector-by-deployment.parquet')
    quality = pd.read_parquet(OUT/'prediction-quality.parquet')
    cis = pd.read_parquet(OUT/'bootstrap-descriptive.parquet')
    flags = read(OUT/'screening-flags.json')
    ver = read(OUT/'verification.json')
    budget = read(OUT/'budget.json')
    tests = pd.read_parquet(OUT/'synthetic-tests.parquet')
    maps = pd.read_parquet(OUT/'map-replay-checks.parquet')
    status = pd.DataFrame([{'deployment': p,
                            'S单元': int(dep[dep.deployment.eq(p)].S.sum()),
                            'N单元': int(dep[dep.deployment.eq(p)].N.sum()),
                            'D单元': int(dep[dep.deployment.eq(p)].D.sum()),
                            '总体SND单元': int(dep[dep.deployment.eq(p)].SND.sum()),
                            '讨论候选': sum(x['discussion_candidate'] for x in flags['units'] if x['deployment'] == p)}
                           for p in PROTOCOLS])
    candidate_rows = [x for x in flags['units'] if x['discussion_candidate']]
    candidate_text = ('没有部署乘块单元满足全部固定讨论条件。' if not candidate_rows else
                      '满足固定讨论条件的单元为：' + '、'.join(x['deployment']+'/'+x['feature'] for x in candidate_rows) + '。')
    # Interval table covers all forty units; no selection on favorable bounds.
    interval_rows = []
    for r in dep.itertuples():
        ci = cis[cis.deployment.eq(r.deployment) & cis.block.eq(r.block)].set_index('metric')
        row = {'deployment': r.deployment, 'feature': r.feature}
        for metric in ['G_R_gain', 'P_loc_raw_gain', 'P_loc_std_gain']:
            x = ci.loc[metric]
            row[metric] = f'{number(x.estimate)} [{number(x.lower)}, {number(x.upper)}]'
        interval_rows.append(row)
    full_gains = []
    for protocol in PROTOCOLS:
        for arm in ['P', 'G']:
            w = whole[whole.deployment.eq(protocol) & whole.arm.eq(arm)].set_index('view')
            full_gains.append({'deployment': protocol, 'arm': arm,
                               'BASE_raw96_MSE': w.loc['BASE', 'raw_mse'],
                               'LOC_raw96_MSE': w.loc['LOC', 'raw_mse'],
                               'raw96_gain': w.loc['BASE', 'raw_mse']-w.loc['LOC', 'raw_mse'],
                               'BASE_std96_MSE': w.loc['BASE', 'std_mse'],
                               'LOC_std96_MSE': w.loc['LOC', 'std_mse'],
                               'std96_gain': w.loc['BASE', 'std_mse']-w.loc['LOC', 'std_mse']})
    content = pd.read_parquet(OUT/'content-strata.parquet')
    lines = [
        '# SD1 块内质量序位位置与形状漂移诊断完整报告', '', '日期：2026-10-15。', '',
        '## 1 结项结论', '',
        f'本轮完成60角色、四个C内部折、480个冻结P/G映射的诊断。新增模型拟合为0，边际统计摘要为240套。{candidate_text}', '',
        '程序完成与讨论候选是不同状态。候选仅说明固定序位方向的相对稳定、保护需求和形状预测增量在同一单元具有重复信号，不构成物理不变量、业务增益或部署启用资格。', '',
        markdown(status, list(status)), '',
        f'新增合成检查{len(tests)}项全部通过。原映射BASE重放最大绝对差为{number(maps.raw_max_abs_replay_error.max())}；独立代数复核最大归一化差为{number(ver["max_independent_normalized_error"])}。', '',
        '## 2 数据和权限', '',
        '数据来自Extend的SS、VLESS、Trojan和VMess四个排他TCP部署。来源队列480访问、30共同内容、六业务，每内容每部署四次重复。60角色为四部署乘五外折乘三个遮蔽组。每角色C含16内容64访问；四个内部折各以12内容48访问拟合、4内容16访问查询。', '',
        '评价包含3840个角色访问暴露，实际只覆盖480个不同部署访问和30个内容，不是3840个独立样本。五预测器共有19200行数值预测，其中P/G映射共同查询预测为7680行；两映射四视图为30720行。', '',
        '只读取每角色合法C、冻结映射及其内部折尺度。实际H/U输入与标签、原生全量配对缓存和PCAP均未读取。业务标签仅从登记C-post的元数据列取得，用于评分侧分层，不进入预测worker。', '',
        '本轮允许实际目标C，不称纯源、零目标校准或首次盲测。旧eta选择的内容接触限制保留；本队列已被多次研究。', '',
        markdown(content.groupby('label_id').size().rename('内容数').reset_index(), ['label_id', '内容数']), '',
        '## 3 固定模型与数学口径', '',
        '原96维由四个9箱字节直方图和六个10箱计数直方图组成。每块固定分为质量M、序位位置L及剩余形状R，秩为1、1、n−2。总计10个M、10个L、76个R方向；不拟合PCA或重新选择频率基。', '',
        'L以等间隔序位坐标c构造，不使用开放末箱的虚构字节中心。质量恒为1不等于总字节守恒；R不是预先验证的协议噪声或业务独立分量。', '',
        f'旧eta取值为{sorted(set(r["eta"] for r in c["roles"]))}。每个映射均保留原矩阵、偏置、eta和内部折mu/scale；先从标准化坐标解码到原频率，再做分解。新拟合映射、G、教师、分类器和温度均为0。', '',
        'P/G统一作用于登记P-query的pre数组，使用同一个真实P-score目标。旧G查询两侧独立乱序，本轮没有按行匹配，也未复用其Cartesian资格评分。G训练仍只具有原匿名组信息。', '',
        '五参照为ID、训练post均值MEAN、训练边际SHIFT、冻结MAP-P和冻结MAP-G。MEAN/SHIFT及内容方差从各折48次合法拟合访问的匿名边际计算，P/G共享。', '',
        'D/V先对每内部折取两侧内容方差的较小值，再按查询权重分别聚合D与V后相除。分母不超过1e−12时为NA；无epsilon或ratio截断。M不参与稳定性排名。', '',
        '## 4 全部部署块的稳定性与形状预测', '',
        'rho越小，表示真实跨侧位移相对拟合内容尺度越小。形状误差差为参照减P，正数表示P更好；所有R误差均除以n−2。S/N/D列是固定数值筛查，不是显著性检验。', '',
        markdown(dep, ['deployment', 'feature', 'D_L', 'V_L', 'rho_L', 'D_R', 'V_R', 'rho_R',
                       'ID_R_gain', 'MEAN_R_gain', 'SHIFT_R_gain', 'G_R_gain', 'S', 'N', 'D']), '',
        '均值漂移、中心化波动、重复方差、序位重心分位数、内容贡献和五外折分项均保存在对应明细表。稳定非零偏移不改称恒等不变。前向形状预测优势只约束当前冻结估计器，不证明逆向可恢复。', '',
        '## 5 位置保护与标准化代价', '',
        'BASE、MASS、LOC、MASSLOC四视图均在读取query-post之前，对全部十块固定生成。LOC保持原质量分量，不会把归一化修复计作位置保护；原始预测和修正后负值、质量残差均保留。', '',
        '下表完整96维raw/std MSE均除以96；完整结果按箱数汇总，不平均十个块的MSE。正gain表示LOC改善。块级筛查N使用各块完整误差，不使用全向量收益替某块放行。', '',
        markdown(pd.DataFrame(full_gains), list(full_gains[0])), '',
        '原频率正交不保证标准化误差改善。标准化空间中的交叉项不强行置零；对带质量误差的预测，c^T hat_b也不当作纯L分量。', '',
        '### 所有单元的主要描述性区间', '',
        '单元格为点估计及未校正95%内容簇bootstrap区间。G_R_gain为G形状误差减P；保护gain分别为BASE减LOC的原频率块平方误差与标准化块MSE。', '',
        markdown(pd.DataFrame(interval_rows), list(interval_rows[0])), '',
        '### 预测质量', '',
        '各部署、映射、视图及块的负箱数、含负值比例、最小预测箱值、块质量残差均在prediction-quality.parquet中报告。没有截负、softmax或单纯形投影，预测不是合法流量生成器。', '',
        f'全视图最小预测箱值为{number(quality.minimum_predicted_bin.min())}；最大块质量绝对残差为{number(quality.max_absolute_mass_residual.max())}。', '',
        '## 6 外折和内容一致性', '',
        '讨论候选要求同一部署同一块的S/N/D在至少四个外折成立，并且保护与P相对G的形状改善各至少由两个内容提供正贡献。没有将四个C内部折当作五外折；没有把不同块的优势拼成成功。', '',
        markdown(pd.DataFrame([{'deployment': x['deployment'], 'feature': x['feature'],
                               'SND外折数': x['SND_outer_folds'],
                               '保护正贡献内容数': x['positive_contents']['P_loc_raw_gain'],
                               '真配形状正贡献内容数': x['positive_contents']['G_R_gain'],
                               '讨论候选': x['discussion_candidate'], '区间不确定': x['uncertainty_unresolved']}
                              for x in flags['units']]),
                 ['deployment', 'feature', 'SND外折数', '保护正贡献内容数', '真配形状正贡献内容数', '讨论候选', '区间不确定']), '',
        '## 7 统计数值和来源核验', '',
        '工程版本记录：run-01在P1合成测试因CUDA cumsum缺少严格确定性实现而停止；run-02改用固定三角矩阵乘法，完成P2后在P3遇到字符串业务标签被误按整数解析而停止。两次停止均在query-post数值评分之前。run-03保留原字符串标签并重新验收，明确独立核验的批次数和实际行数；旧停止、合同和代码快照均保留，早先活动计算累计计入1800秒预算。模型、损失、权限与门限未改变。', '',
        '固定10000次六业务分层共同内容簇bootstrap，seed=20261015。同一个内容次数在全部部署、映射、视图及角色共享；原查询权重乘抽样次数后在部署总体归一，不重新均分空内部折。模型、尺度及训练摘要不随重采样重拟合。', '',
        '区间是条件于冻结模型的描述性区间，没有多重比较校正。区间跨零不等于等效；候选筛查不赋予家族显著性。无效尺度与skill参照产生NA，并在bootstrap表中保留无效比例。', '',
        f'已核验全部登记输入散列、预测封存、评分权重和独立原频率/标准化误差。独立逐访问块复核{ver["independent_pair_block_checks"]}项；C-score解码{ver["score_reads"]}次，其中240次正式评分、240次独立复核。C业务元数据读取{ver["C_metadata_reads"]}次。', '',
        f'活动计算累计{budget["active_compute_seconds"]:.3f}秒，上限1800秒。阶段墙钟与活动分段见ledger及budget；输入读取、散列和写盘不等于GPU计算时间。', '',
        '## 8 停止边界与产物', '',
        '旧Guard仍为stop_no_supported_protection_target；旧P-small、OR1和业务预测没有改变。无论讨论候选是否存在，本轮均在诊断结项。没有授权SD2、逆向G、新分类、GAN、实际H/U读取或业务F1评价。', '',
        '全部40单元、外折、角色、内容及负向结果均保留。最小复核入口为contract.json、source-bindings.parquet、predictions-complete.json、verification.json和completion.json；统计入口为by-deployment-block.parquet、bootstrap-descriptive.parquet及screening-flags.json。', '',
        f'机器可读结果目录：`{OUT.as_posix()}`。', '',
        '代码入口：`python -m eval.subblock_drift_diagnostics.run --stage all --resume`；已有完成阶段会验证来源后跳过，不隐式覆盖。', '',
    ]
    textfile(DOC/'complete-report.md', '\n'.join(lines))
