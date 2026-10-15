"""Read sealed results, report all methods and retain the extraction boundary."""
from common import *

def table(d):
    d = d.copy()
    for k in d:
        if pd.api.types.is_float_dtype(d[k]): d[k] = d[k].map(lambda x: f'{x:.6f}')
    return '| '+' | '.join(d.columns)+' |\n| '+' | '.join(['---']*len(d.columns))+' |\n'+''.join(
        '| '+' | '.join(str(x) for x in row)+' |\n' for row in d.itertuples(index=False, name=None))

def emit(name, s):
    DOC.mkdir(parents=True, exist_ok=True); (DOC/name).write_text(s+'\n', encoding='utf-8')

def diagnostics_report():
    start('diagnostic_report'); d = pd.read_parquet(OUT/'diagnostics/classification-summary.parquet')
    k = pd.read_parquet(OUT/'diagnostics/kernel-feature-summary.parquet')
    sections = ['# 当前96维表示的部署迁移定位\n\n四部署、30全局内容、480访问、23566连接对。五折先汇总，再计算完整六类指标。pre和核评价仅属于离线诊断，不参与目标适配或选参。']
    for kind in ['post', 'pre', 'postmix']:
        sections.append('## '+kind+' 分类结果\n\n'+table(d[d.kind.eq(kind)]))
    composites = []
    for (source, target), part in k.groupby(['source', 'target']):
        part = part.set_index('feature').loc[FEATURES]
        composites.append({'source': source, 'target': target,
            'conditional_loss_bits': float(np.dot(part.loss_bits, FEATURE_WEIGHTS)),
            'marginal_loss_bits': float(np.dot(part.marginal_bits, FEATURE_WEIGHTS)),
            'weighted_zero_support_fraction': float(np.dot(part.zero_support_fraction, FEATURE_WEIGHTS))})
    sections.append('## 源核迁移\n\n访问内连接、内容内重复和内容之间依次等权。十项复合权重保持原定义。\n\n'+table(pd.DataFrame(composites)))
    sections.append('## 边界\n\n部署包含协议、节点、配置和路径差异。没有据迁移矩阵挑选源部署或修改后续业务组；不把pre当作不变语义。旧六维窗口E2结果保留，不由本矩阵替代。')
    emit('migration-diagnostics.md', '\n\n'.join(sections)); finish('diagnostic_report', report='migration-diagnostics.md')

def observation_inventory():
    c = start('observation_inventory'); parent = ROOT/'outputs/extend-calibration-20260930/run-01/extraction-03/sessions'
    require(sha(OUT/'manifests/cohort-visits.parquet') == c['cohort_visits_sha256'], 'Observation cohort seal')
    visits = pd.read_parquet(OUT/'manifests/cohort-visits.parquet')
    # Schema and file presence only; do not read raw captures or derive a new oracle cut.
    records = []
    for rowmeta in visits.itertuples(index=False):
        sid = parent/rowmeta.session_id
        row = {'session_directory': sid.name, 'protocol': rowmeta.protocol, 'directory_exists': sid.is_dir()}
        for filename in ['post-W-events.parquet', 'T-newbyte-events.parquet', 'T-direction-ledger.parquet', 'T-pairs.json']:
            p = sid/filename; row[filename] = p.exists()
            if p.exists() and p.suffix == '.parquet': row[filename+'_schema'] = pyarrow.parquet.read_schema(p).names
        records.append(row)
    decision = {'cache_directories': len(records), 'raw_captures_read': 0,
        'external_attacker_observable_window_verified': False, 'full_unpaired_post_cache_verified': False,
        'current_window_rule': 'max(tun_ready,physical_ready) to browser_quiescent; NetLog clock mapping',
        'stage3_status': 'needs_external_window_and_physical_cache_contract',
        'test_input_reextracted': False, 'physical_only_classification_claimed': False}
    write(OUT/'observation/inventory.json', {'decision': decision, 'schemas': records})
    emit('post-observation-boundary.md', '# 单侧观测资格边界\n\n'+
         '现有窗口规则依赖ready、browser_quiescent与NetLog时钟映射。尚未确认这些边界能由攻击者独立取得。post-W缓存和按logical_id组织的T缓存不能自动证明全部physical连接及其新字节都可单侧恢复。\n\n'+
         '本次仅盘点缓存文件与schema，没有读取PCAP，没有构造新的physical-only测试输入，没有重训或改变主模型。CT42–CT46尚未通过；需要确认外部窗口来源，再登记完整post连接重建和有限PCAP读取范围。前两阶段仍只支持给定访问及双侧离线资格集合的结果。')
    finish('observation_inventory', **decision)

def final_report():
    start('final_report'); d = pd.read_parquet(OUT/'scores/equal-weight-summary.parquet')
    target = pd.read_parquet(OUT/'scores/target-summary.parquet'); detail = pd.read_parquet(OUT/'scores/target-group-summary.parquet')
    contrasts = pd.read_parquet(OUT/'comparisons/primary-contrasts.parquet'); decision = read(OUT/'comparisons/decision.json')
    classes = pd.read_parquet(OUT/'scores/class-results.parquet'); choices = pd.DataFrame(read(OUT/'selection/choices.json'))
    sections = ['# 辅助业务校准与跨部署业务迁移实验结果\n\n日期：2026-10-06。四TCP部署、六业务、30个内容、480次访问、23566对连接。仅目标四类辅助业务提供pre/post；目标另两类训练区pre/post均禁止拟合、缩放与选参。六类业务知识来自其他三部署。',
        '## 预定判断\n\n'+table(pd.DataFrame([decision])),
        '## 完整方法与主要成绩\n\n'+table(d),
        '## 三项主要比较\n\n从完整六类混淆矩阵取两未覆盖类F1。98.3333%区间为三项家族校正；10000次共同业务分层内容bootstrap条件于固定选定模型，不是外部验证或完整训练不确定性。\n\n'+table(contrasts),
        '## 部署分项\n\n'+table(target), '## 十二个部署与业务组合\n\n'+table(detail),
        '## 逐类结果\n\n'+table(classes),
        '## 源内选择\n\n'+table(choices),
        '## 权限和方法\n\nCT0充分post联合监督；CT1额外原样源pre；CT2固定正则1的辅助槽CORAL；CT3同内容边际组核；CT4真实连接核；StrongPost仅在源内伪目标中选择CT0/CT2；CT5完整目标post为额外资源参照。各臂源主、辅助、目标C损失质量各1/3，六类各1/6；共有真实post拟合缩放，合成槽不改变缩放。没有向主模型传入目标U pre，没有把概率模板固定成分类权重。',
        '## 局限和停止\n\n目标部署已经得到辅助校准，不是无目标域泛化；30内容曾反复分析，不是外部盲测；已登记实体无跨折冲突不等于完整TCP出生重建。2/5个百分点辅助代价阈值只是实践筛查，不构成统计非劣效。所有结果保留，不根据失败扩大模型、改掩码或搜索新损失。单侧观测CT42–CT46需独立窗口与完整physical缓存资格，未完成时不声称现场post-only提取成立。']
    emit('calibrated-transfer-results.md', '\n\n'.join(sections))
    emit('complete-report-20261006.md', '\n\n'.join(sections[:6])+ '\n\n完整12格、逐类和选择台账见 calibrated-transfer-results.md；当前表示定位见 migration-diagnostics.md；应用提取边界见 post-observation-boundary.md。')
    emit('experiment-contract-summary.md', '# 校准迁移实验契约\n\n'+
        '外层60场景，内层720伪角色，300个C-only核包。主实验14400内层加300外层LR，第一阶段680新LR，共15380次正式新拟合。CUDA float64，独立LBFGS最多500迭代，四点L2。实际目标任何数据不进入内层选参。预测全部封存后才读取外层标签和离线测试pre。\n\n'+
        '角色白名单不是操作系统沙箱。原始数据、旧模型、目标全量资源参照与主臂权限分开；主臂禁止目标U。配置、源码和角色hash见manifests/experiment-contract.json。')
    emit('model-card.md', '# 校准部署业务分类器模型卡\n\n'+
        '输入为目标post的96维流级直方图；六类domain × activity标签；没有IP、端口、SNI、域名文本、内容ID、绝对时间、质量标志或协议ID数值特征。部署已知用于选定校准模型，不是未知协议识别。LR无隐藏层。训练利用源业务标签和目标辅助校准关联，输出六类概率。\n\n'+
        '适用范围是本批次四TCP部署、未见内容、辅助校准条件下的离线合格访问集合。当前不支持AnyTLS/Hy2同粒度、未知节点配置、异批次外部验证或无索引在线分段。')
    finish('final_report', reports=5, registered_success=decision['registered_attack_increment_and_practical_screen_pass'])

if __name__ == '__main__':
    import sys
    {'diagnostics': diagnostics_report, 'observation': observation_inventory, 'final': final_report}[sys.argv[1]]()
