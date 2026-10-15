"""D26 complete evidence report, contract and model card; no new model choices."""
from common import *

def table(d,digits=6):
    def cell(v):
        if v is None or (isinstance(v,(float,np.floating)) and not np.isfinite(v)): return 'NA'
        if isinstance(v,(float,np.floating)): return f'{v:.{digits}f}'
        return str(v).replace('|','/').replace('\n',' ')
    return '\n'.join(['| '+' | '.join(d.columns)+' |','| '+' | '.join(['---']*len(d.columns))+' |']+
                     ['| '+' | '.join(cell(v) for v in row)+' |' for row in d.itertuples(index=False,name=None)])+'\n'

def frame(p): return pd.read_parquet(OUT/p)
def link(p): return f'[{Path(p).name}]({rel(OUT/p)})'
def emit(name,sections):
    DOC.mkdir(parents=True,exist_ok=True); (DOC/name).write_text('\n\n'.join(sections)+'\n',encoding='utf-8')

def main():
    c=start('report'); audit=read(OUT/'verification.json'); require(audit['pass'],'Verification must pass before report')
    summary=frame('scores/protocol-summary.parquet'); overall=frame('scores/overall-summary.parquet')
    contrasts=frame('comparisons/main-contrasts.parquet'); classes=frame('scores/class-summary.parquet')
    choices=pd.DataFrame(read(OUT/'selection/choices.json')); inner=frame('manifests/inner-optimizer.parquet')
    outer=frame('manifests/outer-optimizer.parquet'); cf=frame('manifests/CF12-optimizer.parquet')
    activity=frame('diagnostics/outer-base-activity.parquet'); comp=frame('states/outer-composition.parquet')
    scores=frame('states/outer-CF-scores.parquet'); masses=frame('states/outer-visit-masses.parquet')
    supported=bool(contrasts.family_positive.all() and contrasts.loc[contrasts.comparison=='DSR4-DSR1','point'].iloc[0]>=.01)
    verdict=('达到三个主比较的家族校正下界>0及对DSR1至少1个百分点的预登记条件。'
             if supported else '未达到完整预登记成功条件。本轮在此收束，不增加温度、保护系数、分组数、特征或模型搜索。')
    selected=choices[choices.arm!='DSR1'].groupby(['arm','alpha']).size().rename('outer_roles').reset_index()
    state=comp.groupby(['protocol','arm','state'],as_index=False).agg(
        OOF_CE=('OOF_CE','mean'),OOF_accuracy=('OOF_accuracy','mean'),mean_true_score=('mean_true_score','mean'),
        zero_support=('mean_zero_support','mean'),low_support=('mean_low_support','mean'),
        effective_contents=('effective_contents','mean'),max_content_fraction=('max_content_fraction','max'))
    act=activity.groupby(['protocol','arm'],as_index=False).agg(
        mean_gap=('drift_gap','mean'),max_gap=('drift_gap','max'),CE_grad=('CE_gradient_norm','mean'),
        L2_grad=('L2_gradient_norm','mean'),state_grad=('drift_gradient_norm','mean'))
    fitstats=[]
    for name,d in [('CF12',cf),('inner_positive',inner),('outer_selected_positive',outer)]:
        fitstats.append({'stage':name,'fits':len(d),'seconds':float(d.seconds.sum()),
                         'max_gradient':float(d.max_gradient.max()) if len(d) else None,
                         'max_iterations':int(d.iterations.max()) if len(d) else 0})
    overlaps=[]; relations=[]; distributions=[]
    for (p,o),d in scores.groupby(['protocol','outer']):
        for a,col in [('DSR2','d_post'),('DSR3','d_group'),('DSR4','d_true')]:
            for label,part in d.groupby('label_id'):
                for target in ['d_post','connections','zero_support','low_support']:
                    corr=part[[col,target]].corr(method='spearman').iloc[0,1] if col!=target else 1.
                    relations.append({'protocol':p,'outer':o,'arm':a,'business':label,'target':target,'spearman':corr})
            for (source,label),part in d.groupby(['source','label_id']):
                distributions.append({'protocol':p,'outer':o,'source':source,'business':label,'arm':a,
                    'count':len(part),'mean':part[col].mean(),'min':part[col].min(),'median':part[col].median(),'max':part[col].max()})
        parts={a:masses[(masses.protocol==p)&(masses.outer==o)&(masses.arm==a)&(masses.state==0)].set_index('visit_id').mass for a in ARMS[2:]}
        for ref in ['DSR2','DSR3']:
            t=parts['DSR4']; z=parts[ref].loc[t.index]
            overlaps.append({'protocol':p,'outer':o,'reference':ref,'same_state_mass':float((1-abs(t-z)).mean()),
                             'shared_low_mass':float(np.minimum(t,z).sum()),'low_mass':float(t.sum())})
    save(pd.DataFrame(overlaps),OUT/'diagnostics/state-overlap.parquet')
    save(pd.DataFrame(relations),OUT/'diagnostics/state-associations.parquet')
    save(pd.DataFrame(distributions),OUT/'diagnostics/CF-source-distributions.parquet')
    finalgrad=outer.groupby(['protocol','arm'],as_index=False).agg(alpha=('alpha','mean'),
        mean_stay=('stay','mean'),mean_logit_rms=('logit_rms','mean'),mean_CE=('CE','mean'),
        mean_gap=('drift_gap','mean'),state_grad=('drift_gradient_norm','mean'),
        protection_grad=('protection_gradient_norm','mean')) if len(outer) else pd.DataFrame(columns=['protocol','arm'])
    complete(OUT/'diagnostics',offline_only=True,no_selection_feedback=True)
    mainrows=['# DSR 漂移状态组风险分类完整实验报告 2026 10 06',
      '## 1 结论\n\n'+verdict+' 这是固定四个已见TCP部署、未见内容任务的结果，不是未见协议或外部数据验证。',
      table(overall),table(contrasts),
      '主终点先在每部署120访问上计算完整六类macro-F1，再对四部署等权；pooled F1仅作附录。区间来自10000次六业务分层内容bootstrap，跨部署/方法共享内容索引，重复随内容移动。普通95%及三个主比较Bonferroni对应98.333333%区间均条件于固定、已选模型，不重训。',
      '## 2 数据与隔离\n\n固定23566对排他TCP连接、480访问、30内容、六业务、每内容四次重复（1、2、4、5）。四部署为SS、VLESS、Trojan、VMess。AnyTLS与Hy2未加入本轮。原W/U/P/E、FR_packet_runs及R_unique_zero_runs组成10项连接观测，按既有箱形成96维post访问直方图。没有新增包扫描、地址、端口、SNI、载荷内容或协议身份数值输入。原FR未替换成记录排序特征。',
      '全局五折按内容划分，所有部署、重复、两侧、连接整体随内容。外层训练/测试24/6内容；内层分类训练/验证18/6内容；内层训练状态的源范围12内容，外层训练状态源范围18内容。登记pair、visit、logical、carrier、epoch代理均不跨全局折；这不等于对所有未知TCP生命周期的普遍证明。',
      'SS为已登记AES-256-GCM无plugin/smux；VLESS为TCP+TLS，非旧REALITY/Vision部署；Trojan为TCP+TLS；VMess为WS+TLS，历史security细节缺口保留。协议机制限定观测解释，不能从核统计反推精确封装开销。',
      '## 3 五臂设计\n\n'+table(pd.DataFrame([
       ['DSR0','原零LR，rho=.001','固定post监督基座'],
       ['DSR1','原KSR1四L2候选，内层选择','公平调参强post参照'],
       ['DSR2','CF post CE类内低/高状态','不用pre的难度控制'],
       ['DSR3','匿名核+内容pre箱边际期望负log概率','拟合与查询都删除精确身份'],
       ['DSR4','共同真配核+同次pre/post负log概率','主候选']
      ],columns=['arm','训练信息','用途'])),
      '共同核不按业务条件化：每连接拟合质量1/(4×该访问连接数)，每内容总质量1，原平滑alpha=beta=1。状态分数先逐连接、十变量权重平均，再按访问等权。字节/包/事件变量权重各1/12，两个方向段变量各1/6。真配分数为bit；DSR2交叉拟合CE为nat，仅各方法内部排序，不跨单位比较绝对强弱。',
      '匿名拟合是同内容两侧加权箱边际的乘积；匿名查询是对内容pre边际取−log2 KG(B|A)的期望，而非−log混合概率。接口不接收pre访问、pair或carrier身份。受信任离线包构建器拥有关联权限；角色白名单与SHA不等于OS安全沙箱。',
      '## 4 模型与目标\n\n六类线性softmax，96维输入，W为6×96、b为6，共582参数。各部署独立模型，使用各角色训练post的mu/scale，常数维度scale=1。Delta从零初始化，最终合并回同容量LR。alpha=0直接返回原基座，逐参数和逐概率精确复现。',
      '每业务按自身状态分数划低/高两组等质量；边界并列使用分数质量拆分，整类同分每访问两组各0.5，不用访问ID破平局。外层每类每状态质量8，内层6。gamma冻结后，R_g为六类等权组CE，(R0+R1)/2=全训练CE。',
      '固定目标 L=(1−alpha)CE+alpha×[logsumexp(R0,R1)−log2]+0.0005||W||²+0.1Rstay；Rstay=mean||P6(logits−base_logits)||²/5。温度1 nat；仅alpha∈{0,.1,.25,.5}按四内层合并96访问六类macro-F1选择，1e−12内平局选最小alpha。DSR1的L2选择完整复现旧规则。凸目标不等于泛化保证；组风险差单独不被声称凸。',
      'CUDA float64全批LBFGS，strong Wolfe，max_iter500，tolerance_grad1e−9、tolerance_change1e−12；工程门为有限、目标不上升、max gradient≤1e−5、未触顶。关闭TF32并严格确定性；无随机训练seed或checkpoint搜索，无CPU拟合/推理回退。',
      '## 5 全部结果\n\n'+table(summary),
      '### 5.1 逐业务结果\n\n每类每部署支持20次访问，保留全部类别。\n\n'+table(classes),
      '### 5.2 预登记主比较\n\n'+table(contrasts),
      '### 5.3 逐部署探索性比较\n\n下列95%区间不属于主检验家族，不据此替代主终点。\n\n'+table(frame('comparisons/protocol-descriptive.parquet')),
      '### 5.4 选择及新增计算\n\n'+table(selected)+'\n\n'+table(choices)+'\n\n'+table(pd.DataFrame(fitstats)),
      '240个内层CF逻辑查询对应40个独立12内容训练集合，按成员和源码封存复用拟合，共400个新核bundle、40个难度LR；另80个18内容源角色复用并重放旧核/模型。逻辑查询仍逐一排除来源内容并审计。候选数匹配不等于总计算匹配：状态学习额外使用两侧和辅助CF拟合。',
      '## 6 状态与目标作用\n\n下表对五个外层训练角色、六业务等权汇总，不是留出分类终点。DSR2与OOF CE的关系由构造决定。DSR3/4的关系仅为描述，不能解读为因果或互信息。\n\n'+table(state),
      '### 6.1 基座目标压力\n\n'+table(act),
      'gap=tau log cosh((R1−R0)/(2tau))，风险接近时为二阶小量。表中state_grad为未乘alpha的gap梯度；protection梯度记录已乘eta。状态非零不等于优化压力强。不能看到压力弱后重新调整温度或CE单位。',
      '### 6.2 选定正alpha模型的变化\n\n零alpha角色不计入此均值，完整日志另存。\n\n'+table(finalgrad),
      '### 6.3 同状态质量重合\n\n'+table(pd.DataFrame(overlaps)),
      'same_state_mass=mean(1−|gamma_true,low−gamma_control,low|)，只是训练分组重合。内容贡献、按CF源的分数分布、业务内分数与连接数/零支持/低支持Spearman另存完整表，不根据这些诊断筛样本或重新定义状态。',
      '## 7 错误翻转与离线状态\n\n'+table(frame('scores/error-flip-summary.parquet')),
      '修复=参照错而DSR4对；新增=参照对而DSR4错。全部逐访问正确类别概率差和逐内容计数保留，不能用净修复数掩盖新增错误。\n\n'+table(frame('scores/content-flips.parquet')),
      '### 7.1 封存后状态附录\n\n'+table(frame('diagnostics/offline-state-scores.parquet')),
      '此附录使用测试pre与Y，仅在分类预测封存后运行。测试分数为四个18内容共同核负log概率平均，再应用各业务冻结训练阈值，所有臂使用同一DSR4状态；不重算测试中位数。训练单核OOF与测试四核平均有观测差异；无完整六类支持的状态F1记NA。这不是攻击者可用查询，不回写模型或选择。',
      '## 8 审计与复现\n\n```json\n'+json.dumps(audit,ensure_ascii=False,indent=2)+'\n```',
      '本轮于2026-10-05登记，2026-10-06按用户确认完成工程修订：L2单项梯度日志显式记录bias零导数，其他项仍严格检查计算图；没有给bias新增正则化。原契约与源码快照保留，修订契约单独封存，原目标与训练主函数AST相同，已有CF产物SHA不变。机器修订契约见 `manifests/experiment-contract-amended-v1.json`，修复测试及快照见 `manifests/engineering-repair-v1/`。',
      '来源契约、每阶段读取台账、选择封存时间、模型/状态/概率逐一重放均保存。分类推理只接收opaque visit_id和96维post；拟合不接收当前验证/测试内容；匿名查询不接收真实pre身份。alpha=0与原基座精确一致。老源码和旧产物SHA保持不变。',
      '复现入口见 `eval/drift_state_group_risk/README.md`。源码/包/旧产物哈希见 `outputs/drift-state-group-risk-20261005/run-01/manifests/experiment-contract.json`；全部候选预测、OOF分数、gamma、边界、混淆矩阵、优化日志与bootstrap索引均在该run目录。',
      '## 9 停止决策与范围\n\n'+verdict+' 本轮不重写旧GE资格，不删除不利业务，不追加模型容量或新权重搜索。已测的对应概率结构与本次分类用途是两件事；若分类未改善，不能据此否定全部测量价值。即使改善，也不证明未知部署、外部DIRECT、在线无索引分段、业务解耦、协议噪声消除或真实配对普遍必要。',
      '## 10 图\n\n'+ '\n\n'.join(f'![{name}](figures/{name}.png)' for name in ['protocol-performance','main-contrasts','alpha-selection','state-OOF-difficulty','baseline-risk-pressure','error-flips','business-F1'])]
    emit('complete-report-20261006.md',mainrows)
    emit('experiment-contract-20261006.md',['# DSR实验契约',
      '本文件为已封存机器契约的可读摘要，不替代原计划或SHA台账。',
      table(pd.DataFrame([['样本','23566连接对/480访问/30内容/6业务/4部署'],['折','全局内容五折；24/18/12内容训练层级'],
          ['输入','post HIST96，582参数，已知部署路由'],['候选','五臂，三个组风险臂alpha仅四点'],
          ['固定项','tau=1，eta=.1，rho=.001，类内两组等质量'],['主比较','DSR4−DSR1/2/3；部署等权完整六类F1'],
          ['统计','10000次内容bootstrap，三个Bonferroni区间，固定模型'],['效应','对DSR1至少.01且三下界>0'],
          ['停止','工程失败需登记修订；完整矩阵完成后收束']],columns=['项目','契约'])),
      '源码/输入/旧来源SHA已在任何新增分组或拟合前封存。40个新CF12集合对应240逻辑角色，复用不允许扩大训练范围。',
      table(choices),'批准计划：`plan/drift-state-group-risk-classification-plan-20261005.md`。机器契约：`outputs/drift-state-group-risk-20261005/run-01/manifests/experiment-contract.json`。'])
    emit('model-card-20261006.md',['# DSR模型卡',
      '用途：固定四个已见TCP代理部署下的六业务未见内容分类。独立部署LR使用96维post直方图，不显式输入协议身份；路由预先知道部署。',
      '训练额外权限：DSR4使用训练范围的pre/post真配用于CF状态；DSR3使用内容匿名边际；DSR2使用CF post和业务标签。Y也用于类均衡。不能称为完全无标签方法。',
      '推理：仅post直方图，经保存训练坐标输入冻结582参数LR；没有pre、Y、gamma、内容查询、核查询或测试缩放。测试状态附录明确不属于模型接口。',
      '结果：\n\n'+table(overall),verdict,
      '限制：回顾性数据、重复研究过的固定队列、bootstrap条件于固定模型；没有外部独立验证。只完成已见部署的内容留出，不声称留协议、跨日期或在线泛化。',
      '实现：Pytorch312 CUDA float64，确定性关闭TF32，LBFGS；训练内容尺度与CF源隔离。全部已保存模型可逐概率重放。'])
    finish('D26',complete=True,full_claim_supported=supported,stop_after_report=True)
    write(OUT/'report-complete.json',{'completed_unix':time.time(),'full_claim_supported':supported,
          'docs_sha256':{rel(p):sha(p) for p in DOC.glob('*.md')},'stop':True})
    print(verdict,flush=True)

if __name__=='__main__': main()
