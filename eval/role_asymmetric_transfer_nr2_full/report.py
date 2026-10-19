"""NR2 resumed results and honest terminal closeout; old results remain read-only."""
from common import *
from weight_schedule import PRIMARY,REFERENCES

def md(df):
    cols=list(df);lines=['| '+' | '.join(cols)+' |','| '+' | '.join(['---']*len(cols))+' |']
    for row in df.itertuples(index=False,name=None):lines.append('| '+' | '.join(str(v) for v in row)+' |')
    return '\n'.join(lines)

def run():
    with stage('report'):
        c=contract();primary=read(OUT/'comparisons/primary.json');cost=read(OUT/'scores/C-practical-cost.json');point=pd.read_parquet(OUT/'scores/pooled.parquet').set_index('policy_id')
        show=point.loc[[PRIMARY,*REFERENCES],['F1_U','F1_C','F1_all','CE_U','Brier_U','worst_target_F1_U']].reset_index()
        for k in list(show)[1:]:show[k]=show[k].map(lambda x:f'{x:.6f}')
        comp=pd.DataFrame([dict(reference=x['reference'],delta_F1_U_pp=f"{100*x['delta_F1_U']:+.4f}",CI_family_pp=f"[{100*x['CI_family'][0]:+.4f},{100*x['CI_family'][1]:+.4f}]",delta_CE_U=f"{x['delta_CE_U']:+.6f}",delta_Brier_U=f"{x['delta_Brier_U']:+.6f}") for x in primary['comparisons']])
        new=pd.read_parquet(OUT/'manifests/new-endpoints.parquet')
        lines=['# RA1完整NR2恢复实验报告','', '日期：2026-10-18。旧run-01、Full NR1两次科学停止及NR1/NR2先导、早期工程停止均保持不变。','',
          '## 1. 科学问题与固定方案','',
          '主候选P-U50：rho_C=0、rho_U=.5。保持96维访问直方图、既有P/G全仿射和CORAL、源真实post/目标C-post质量、分类t和JA2来源共同eta。唯一科学干预仍是辅助视图按业务角色的固定权重分配。四来源×三剂量×三分配，加S和P/G-full，共39政策；没有按H挑赢家。',
          '', '## 2. 数据和训练资源','',
          '四TCP部署SS/VLESS/Trojan/VMess；六业务、30全局内容，每内容每部署四重复，共480不同访问。五折×四目标×三遮蔽=60角色。每角色三源288次+目标C64次=352真实训练访问，H为24次访问；视图、角色、seed或逻辑行不当作独立样本。全局内容、重复、两侧和内部flow整体分折。',
          '', '每类CE总质量1/6，源主槽/辅助槽/目标C-post各1/3；C与U辅助各1/6。P/G/RawPre/RawPost按各自标签/排序分配rho，不恢复匿名源pre/post身份。没有目标U训练数值、H-pre或PCAP读取。推理只读取post96及冻结mu/scale和W/b，不接收C/U身份。',
          '', '## 3. NR2数值政策与复用证明','',
          '统一新拟合从零，原Cholesky/原梯度感知LBFGS最多1024更新，未达原门再用最多32次原目标解析Hessian Newton。581维保留完整W，仅冻结共同bias。有限阻尼只求方向、不加入损失；数值函数体直接复用NR2先导。CUDA float64，无AMP/TF32/CPU求解回退。目标sum mass*CE+.0005*(1+t)||W||²不变，bias不惩罚。原坐标梯度<=1e-5、目标/梯度重放<1e-10、严格总更新<4000及20000评价额度不变。',
          '', 'NR2固定先导52例全部通过，4例各一次Newton，两失败点从零1024+1合格，前缀/重复精确。恢复优先采用NR2的52个从零唯一端点，与原1024交叠32，合计624科学+420历史=1044复用。其源日志、policy SHA、源额度保留，旧32文件不删除；快照诊断和重复不采纳。补拟合1296后形成2340逻辑端点。旧不同后端不声称走过NR2轨迹。',
          '', '## 4. 封存与评价','',
          '全部模型封存后才读取H-post；56160条逻辑预测全部封存后才读取H标签。各政策在部署×遮蔽内先合并五折120访问，构造完整6×6矩阵，再取U/C类F1及部署×遮蔽等权。F1_U包含全部六类假阳性，不是只取真实U行的二分类。',
          '', '## 5. 主要结果','',md(show),'', '## 6. 六项主比较','',md(comp),'',
          'Delta均为候选减参照：F1正向有利，CE/Brier负向有利。共享内容簇bootstrap为10000次、seed20261017、业务分层每类5内容同步重抽；六项家族Bonferroni边际覆盖99.1666667%，普通95%并存。没有把本轮与历史家族混装。',
          '', '## 7. C实践代价与概率','',f"主候选相对P-small总体Delta F1_C={100*cost['delta_F1_C']:+.4f}pp，总体1pp实践筛查={cost['overall_pass']}，各部署2pp筛查={cost['each_deployment_pass']}。",'',
          md(pd.DataFrame([dict(deployment=k,delta_F1_C_pp=f'{100*v:+.4f}') for k,v in cost['per_deployment'].items()])),
          '', 'C门不用于H后回退，不是统计非劣效证明。CE/Brier及共同正确/共同错误/修复/新错分解完整保留，不能用分类点估计隐去概率代价。',
          '', '## 8. 全39政策、错误与混淆','',
          'scores包含全部政策总体、部署、遮蔽、业务精度/召回/预测类别频率、30内容和完整混淆矩阵；comparisons/descriptive.json含同剂量UPR-SYM/CPR和预定比例曲线对比，均为解释性结果，不升级次要最高点。error-transitions与probability-contributions给出六主对照的逐访问修复/新错、C/U流向和可加和CE/Brier贡献。',
          '', '## 9. 计算成本','',
          f"本恢复新拟合1296；旧/先导复用1044。新solver-seconds合计{new.seconds.sum():.3f}，中位{new.seconds.median():.3f}，最大{new.seconds.max():.3f}。新增Newton触发{int((new.newton_updates>0).sum())}，接受Newton更新合计{int(new.newton_updates.sum())}；保守谱系优化尝试697+1296=1993，未超过2348保护。累计活动在报告前约{spent():.3f}秒，最终活动/预算见completion.json和cost-ledger.json。",
          '', '原8小时从未重置；prior-activity.json继承NR2分析的最新父累计2048.441729秒（不重复累加已含原运行），另保守计费60秒未独立计量的后续只读结项启动/检查，明确非实测替代。所有新失败成本计入。本轮不以GPU显存占满作为验收，不改变动态独立线搜索以追求利用率。',
          '', '## 10. 结论层级与边界','',
          '是否增强已有方法由对P-small决定，是否角色分配有用由同质量SYM25决定；G/RawPre/RawPost分别界定精确管线、入口额外资源及源post曝光竞争解释。各项分别裁决，不用胜P-full替代胜P-small，不要求全部六项通过才承认某项有限结果。',
          '', '这是历史同批固定方案内部评价，H已反复研究；条件区间不是外部盲测或跨节点/跨日期保证。未验证AnyTLS/Hy2、本轮无新采集、单flow分类或无索引在线分段。没有把先导数值通过等同于业务效力。',
          '', '机器复核、模型和预测封存、源码/来源哈希及完整预算为终态组成；只有verification和completion均完整才算实现完成。','']
        textfile(DOC/'complete-report.md','\n'.join(lines))

def stop_closeout(exc):
    attempts=list((OUT/'attempts').rglob('*.json'));ends=list((OUT/'new-endpoints').rglob('*.json'))
    pending=[]
    if (OUT/'manifests/seal.json').exists():
        done={(read(p)['role_id'],read(p)['policy_id']) for p in ends}
        pending=[x for x in contract()['pending'] if (x['role_id'],x['policy_id']) not in done]
    write(OUT/'pending-on-stop.json',pending)
    textfile(DOC/'execution-stop.md','\n'.join(['# RA1-NR2完整恢复停止记录','',f"停止原因：{type(exc).__name__}: {exc}",'',
        f'新尝试{len(attempts)}，新接受{len(ends)}，累计活动约{spent():.3f}秒。旧停止不改写，无自动重试或基座回退。',
        '', '本文件不披露不完整矩阵的局部赢家。完整状态、异常和pending以新运行根failure.json及pending-on-stop.json为准。']))
    write(OUT/'run-closeout.json',dict(program_complete=False,new_attempts=len(attempts),new_accepted=len(ends),pending=len(pending),cumulative_active_seconds=spent(),auto_retry=False))
