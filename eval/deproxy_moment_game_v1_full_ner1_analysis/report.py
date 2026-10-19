"""Read sealed NER1 results and produce a separate, reproducible closeout report.

No training module is imported. No capture, training tensor, H-pre, or forbidden
U-training value is decoded. The completed run and its original report stay intact.
"""
from pathlib import Path
from datetime import datetime, timezone, timedelta
import hashlib
import json
import collections
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
RUN = ROOT / 'outputs/deproxy-moment-game-v1-20261016/full-ner1-01'
DOC = ROOT / 'docs/deproxy-moment-game-v1-20261016'
DEST = DOC / 'full-NER1-complete-results-analysis-20261017.md'
LABELS = ['bing.com::search_results_view', 'developer.mozilla.org::document_view',
          'github.com::repository_view', 'wikipedia.org::article_view',
          'youtube.com::search_results_view', 'youtube.com::video_playback']
NAMES = ['Bing搜索', 'MDN文档', 'GitHub仓库', 'Wikipedia文章', 'YouTube搜索', 'YouTube播放']
MASKS = {'G0': [2, 4], 'G1': [0, 3], 'G2': [1, 5]}
TZ = timezone(timedelta(hours=8))
READ_HASHES = {}


def read(path):
    path = Path(path)
    blob = path.read_bytes()
    READ_HASHES[str(path.relative_to(ROOT)).replace('\\', '/')] = hashlib.sha256(blob).hexdigest()
    return json.loads(blob.decode('utf-8-sig'))


def table(name):
    path = RUN / 'scores' / (name + '.parquet')
    READ_HASHES[str(path.relative_to(ROOT)).replace('\\', '/')] = hashlib.sha256(path.read_bytes()).hexdigest()
    return pd.read_parquet(path)


def fmt(x):
    if isinstance(x, (float, np.floating)):
        if not np.isfinite(x):
            return '未定义'
        return f'{x:.6f}'
    return str(x).replace('|', '\\|').replace('\n', ' ')


def md(frame):
    return '\n'.join(['| ' + ' | '.join(map(str, frame.columns)) + ' |',
                      '| ' + ' | '.join(['---'] * len(frame.columns)) + ' |'] +
                     ['| ' + ' | '.join(fmt(x) for x in r) + ' |' for r in frame.itertuples(index=False, name=None)])


def link(path, label=None):
    p = ROOT / path
    return f'[{label or path}](<{p.as_posix()}>)'


def cm_metrics(part):
    y = part.label_id.map(dict(zip(LABELS, range(6)))).to_numpy(int)
    z = part.prediction.to_numpy(int)
    cm = np.bincount(y * 6 + z, minlength=36).reshape(6, 6)
    den = cm.sum(0) + cm.sum(1)
    f = np.divide(2 * np.diag(cm), den, out=np.zeros(6), where=den > 0)
    u = MASKS[part.group.iloc[0]]
    return f[u].mean(), f.mean()


def main():
    completion = read(RUN / 'completion.json')
    assert all(completion[k] for k in ['program_complete', 'numeric_pass', 'all_required_roles_completed', 'H_scored'])
    assert not (RUN / 'stop-record.json').exists()
    # Verify the final evidence chains, without rehashing all training tensors.
    verified = {}
    for name in ['complete-seal', 'P6-complete', 'P5-scores-complete', 'report-complete', 'P3-complete']:
        seal = read(RUN / 'manifests' / (name + '.json'))
        for path, expected in seal['files'].items():
            actual = hashlib.sha256((ROOT / path).read_bytes()).hexdigest()
            assert actual == expected, path
            verified[path] = actual
    code = read(RUN / 'manifests/code-seal.json')
    # The code seal schema is retained for provenance; original P6 audited it.
    contract = read(RUN / 'manifests/contract.json')
    budget = read(RUN / 'budget.json')
    start = read(RUN / 'driver-start.json')
    finish = read(RUN / 'progress.json')
    audit = read(RUN / 'tests/P6-independent-verification.json')
    nested = read(RUN / 'manifests/P0-nested-fold-audit.json')
    primary = read(RUN / 'comparisons/primary.json')
    screen = read(RUN / 'comparisons/practical-screen.json')
    decisions = pd.DataFrame(read(RUN / 'selections/decisions.json'))
    jobs = read(RUN / 'selections/outer-fit-jobs.json')
    outer_manifest = read(RUN / 'manifests/P4-models-complete.json')
    inner_manifest = read(RUN / 'manifests/P2-models-complete.json')
    endpoints = read(RUN / 'manifests/outer-endpoints.json')
    pooled, targets, seeds = table('pooled'), table('targets'), table('seed-summary')
    pred, flips = table('row-costs'), table('error-flip-costs')
    classes, stages = table('classes'), table('selected-PURE-stage-summary')
    contents = table('content-costs')
    candidate = pd.read_parquet(RUN / 'selections/candidate-metrics.parquet')
    base = pooled.set_index('pipeline').loc['B0']
    chosen = pooled.set_index('pipeline').loc['F-P-FUSE']
    assert len(pred) == 56160 and pred.visit_id.nunique() == 480 and pred.content_id.nunique() == 30
    assert len(pred.drop_duplicates(['pipeline', 'role_id', 'visit_id', 'seed'])) == len(pred)
    # Independent confusion-matrix reconstruction of every scored scenario.
    replay = []
    for key, d in pred.groupby(['pipeline', 'target', 'group', 'seed']):
        fu, fa = cm_metrics(d)
        replay.append(dict(pipeline=key[0], target=key[1], group=key[2], seed=key[3], F1_U=fu, F1_all=fa))
    r = pd.DataFrame(replay).groupby('pipeline')[['F1_U', 'F1_all']].mean()
    assert np.max(np.abs(r - pooled.set_index('pipeline')[['F1_U', 'F1_all']])) < 1e-12
    replay_error = float(np.max(np.abs(r - pooled.set_index('pipeline')[['F1_U', 'F1_all']]).to_numpy()))

    # Fixed artifacts, no new fit: head acceptance and outer learning trajectories.
    quality_rows = []
    for part in [inner_manifest, outer_manifest]:
        for path in part['files']:
            if not path.endswith('/complete.json') or '/models/' not in path:
                continue
            qpath = (ROOT / path).parent / 'head.quality.json'
            q = read(qpath)
            tokens = Path(path).parts
            arm = tokens[-4]
            quality_rows.append(dict(scope='outer' if '/outer/' in path else 'inner', arm=arm,
                accepted=q['accepted'], iterations=q['iterations'], evaluations=q['evaluations'],
                gradient=q['original_gradient_max'], objective_error=q['independent_objective_error'],
                gradient_error=q['independent_gradient_error']))
    quality = pd.DataFrame(quality_rows)
    assert quality.accepted.all()
    assert (quality.iterations < 2000).all() and (quality.evaluations < 10000).all()
    traces = []
    for path in outer_manifest['files']:
        if not path.endswith('/complete.json') or '/models/' not in path:
            continue
        tr = (ROOT / path).parent / 'trace.json'
        if not tr.exists():
            continue
        t = read(tr)['steps']
        a, b = t[0], t[-1]
        tokens = Path(path).parts
        arm = tokens[-4]
        traces.append(dict(arm=arm, J0=a['objective'], Jend=b['objective'],
            decrease=b['objective'] <= a['objective'], raw0=a['raw_target_error'], rawend=b['raw_target_error'],
            std0=a['generated_std_error'], stdend=b['generated_std_error'],
            task0=a['parts'][2], taskend=b['parts'][2], recend=b['parts'][3],
            fidend=b['parts'][4]+b['parts'][5], gapend=b['parts'][6]+b['parts'][7],
            regend=b['parts'][9], clips=b['clip_count'], rank=b['generated_rank'],
            cosine_task_rec=b['gradient_cosines'][0][1],
            cosine_task_fid=b['gradient_cosines'][0][2],
            cosine_task_gap=b['gradient_cosines'][0][3]))
    tr = pd.DataFrame(traces)

    lines = []
    def add(text=''): lines.append(text)
    def section(title, text=''):
        add('\n## ' + title + '\n')
        if text: add(text + '\n')
    def tbl(d): add(md(d) + '\n')

    add('# DP-GAN1-M v1 / Full NER1 完整实验分析报告\n')
    add('日期：2026-10-17。范围：完整720个源内任务、60个外层角色及全部H评价；不是仅对工程先导作总结。')
    section('1. 结项结论',
        '**程序完整完成、数值验收通过，但主候选没有增强原P-small。** '
        'F-P-FUSE的F1_U为0.779655，P-small为0.796931，下降1.727686个百分点；'
        '五项家族校正使用的99%边际区间为[-2.900469,-0.724761]个百分点，整体方向明确不利。\n\n'
        '**同时保留一项有限的正结果：**F-P-FUSE相对F-G-FUSE增加2.438787个百分点，'
        '99%区间[0.881500,4.594983]个百分点。它支持当前逆锚点与恢复目标组合中精确对应管线优于匿名组控制，'
        '不支持整体方法优于P-small，也不能单独归因于矩项。\n\n'
        '相对E-post、N-P和R-P的三项主区间跨零。C总体F1下降1.234149个百分点，超过既定1个百分点代价范围；'
        '各部署C下降均未超过2个百分点。U的CE与Brier均较P-small恶化。')
    tbl(pd.DataFrame([
        ['执行完整性', str(completion['program_complete']), '全部角色、预测、评分与复核已完成'],
        ['数值完整性', str(completion['numeric_pass']), '不是数值中断导致的无业务结论'],
        ['整体效力', '不支持改进，主区间全负', 'F-P-FUSE弱于P-small'],
        ['精确对应管线相对组控制', '有家族校正正增量', '仅限当前方法族及队列'],
        ['矩组合独立增量', '未建立', 'F-P−N-P区间跨零'],
        ['C实践代价', '总体未通过，四部署分别通过', '不是统计非劣效证明'],
    ], columns=['维度', '结论', '解释']))
    section('2. 完成状态、版本与旧停止记录')
    end = datetime.fromtimestamp(finish['unix'], TZ)
    begun = datetime.fromtimestamp(start['unix'], TZ)
    add(f'主调度启动：{begun:%Y-%m-%d %H:%M:%S}；最终完成：{end:%Y-%m-%d %H:%M:%S}（北京时间）。'
        f'主调度墙钟{(finish["unix"]-start["unix"])/3600:.3f}小时。当前运行没有stop-record.json；'
        'active-child/active-stage只是最后阶段的留存信息，不能据其存在误认为仍在训练。')
    add(f'累计活动{budget["used_seconds"]/3600:.6f}小时，包括继承成本{budget["inherited_seconds"]/3600:.6f}小时；'
        f'本版本新增{budget["new_seconds"]/3600:.6f}小时。40小时保护尚余{40-budget["used_seconds"]/3600:.3f}小时，'
        '本次没有触发预算退出。32小时是启动时的保守预计门，不是要求必须运行到32小时。')
    add('本轮为独立full-ner1-01；run-01及numeric-repair-01原停止/先导记录保持原样。'
        '原24小时/19.2小时政策经用户明确修订为40小时/32小时；未据H调模型、损失、候选或数值门。'
        '完成标记与效果标记分开，不能把numeric_pass当作方法成功。')
    section('3. 数据、粒度与观测权限')
    add('沿用Datasets/extend衍生的连接级配对特征及固定业务队列；没有新增抓包或重扫PCAP。'
        '当前完整实验只含SS、VLESS、Trojan、VMess四个已登记TCP部署，不代表六协议统一评价。'
        'AnyTLS、Hy2未纳入本轮合同，不能把本次结论扩展到共享carrier。')
    tbl(pd.DataFrame([
        ['全局内容', 30, '六业务，每业务五个内容'],
        ['不同访问', 480, '30内容×4部署×4重复'],
        ['外层角色', 60, '5折×4目标部署×3业务遮蔽'],
        ['源内任务', 720, '每外层12个伪目标任务'],
        ['外层训练访问/角色', 352, '三源288＋目标C64'],
        ['目标U训练禁用访问/角色', 32, '目标部署两个业务的训练pre和post均不使用'],
        ['H访问/角色', 24, '六个留出内容，每内容四重复，只有post进入推理'],
        ['源内训练访问/任务', 192, '两源144＋伪目标C48'],
        ['源内query访问/任务', 24, '仅来自外层训练内容的合法内层留出'],
        ['主逻辑端点', 2340, '60角色×3seed×13管线'],
        ['主逻辑预测行', 56160, '重复路由与seed，不是56160个独立访问'],
    ], columns=['对象', '数量', '口径']))
    tbl(pd.DataFrame([['G0', 'GitHub仓库、YouTube搜索'], ['G1', 'Bing搜索、Wikipedia文章'],
                      ['G2', 'MDN文档、YouTube播放']], columns=['U遮蔽组', '两个目标业务']))
    add('六类标签为domain×activity，完整名称：' + '；'.join(LABELS) + '。')
    add('同内容在所有部署、全部重复、两侧和内部flow全局分折；外层训练24内容与H的六内容不交叉，'
        '内层18训练＋六query均属于外层24训练内容。源内伪目标不是实际外层目标，不能把role_target当成query部署。'
        '本轮重新核对现有嵌套折审计与最终指标；没有新扫描PCAP证明所有物理连接的跨访问归属。'
        '该实验继承既有父访问/连接登记，不使用随机flow或SNI子集切分。')
    section('4. 实际输入：96维访问直方图，不是原始流量序列')
    features = ['W_up', 'W_down', 'U_up', 'U_down', 'P_up', 'P_down', 'E_up', 'E_down', 'FR_packet_runs', 'R_unique_zero_runs']
    tbl(pd.DataFrame([[i, f, 9 if i < 4 else 10] for i, f in enumerate(features)], columns=['块编号', '连接级统计', '箱数']))
    add('各访问对登记连接统计进行计数再除连接数，得到十个归一化块，共96维。'
        'W为正TCP负载包的观测payload字节（含重复/重传，不含链路/IP/TCP头部字节），U为唯一新TCP字节；'
        'P/E为对应正负载包/正新字节事件计数；'
        'FR_packet_runs与R_unique_zero_runs为各自已登记方向段口径，不混称一个FR。'
        '字节箱边界[1,256,1024,4096,16384,65536,262144,1048576]；'
        '计数箱边界[1,2,3,4,8,16,32,64,128]。本轮不输入IP、端口、SNI、域名字符串、标签或访问键。')
    add('标签与内容键仅用于训练监督、成员审计和离线评分。路由预先选择角色专用模型，'
        '并不等于未知协议下的共享单模型在线识别。未验证自然流量分段和真实DIRECT→代理泛化。')
    section('5. 可信raw训练包与P/G/E隔离')
    add('P0按角色训练访问白名单，从既有整数连接特征重建raw pre/post直方图，保存分子/分母并重放历史post和匿名pre边际。'
        '不是从标准化教师特征逆算raw。训练质量分源U、源C、目标C三组各1/3，总质量1、各类1/6。'
        '外层三组96/192/64访问分别每行1/288、1/576、1/192；内层48/96/48分别1/144、1/288、1/144。')
    tbl(pd.DataFrame([
        ['P', '合法训练raw a/b精确对应、标签、质量、条件单元', '任何query/H、实际目标U训练值'],
        ['G', '独立排列pre/post边际、匿名组中心、真实边际矩', '逐访问pre/post共同身份或P包'],
        ['E-post', 'post、标签、质量、原post尺度', 'pre、pre尺度、pre矩、配对索引'],
        ['H推理', 'post96和冻结导出', 'pre、标签、内容/访问/重复键'],
    ], columns=['能力', '允许输入', '禁止输入']))
    add('pre尺度从合法训练pre等权拟合，低方差维scale=1；post尺度精确继承B0，不利用测试post重新标准化。'
        '真实训练质量w与尺度等权估计是两套定义。P/G/E分别运行于独立能力进程。')
    section('6. 模型与完整损失')
    add('该标识含GAN，但实现**不是完整GAN**：没有可训练判别器、随机噪声或极小极大更新。'
        '准确名称是“配对锚定逆向摘要校准＋有限条件矩＋概率融合”。')
    add('每块冻结逆Ridge G0：输入z_B=S_B(b)，目标raw pre a（P）或匿名组pre中心（G），α=1，截距无正则。'
        '十块共1020个估计参数。动态残差为r(z)=U2 ReLU(U1 z+d1)，96→8→96，无输出bias，共1544参数；'
        'U1随机、d1=0、U2=0，初始输出等于锚点投影。')
    add('\\[\\widehat a=\\Pi_{\\mathcal H}(G_0(b)+r(S_B(b))),\\qquad '
        'h_A(\\widehat a)=W_A S_A(\\widehat a)+c_A.\\]')
    add('Π_H为逐块欧氏单纯形投影，不是softmax或截断归一化；只保证块内非负且和1，'
        '不保证合法协议会话、整数直方图、跨块一致性或业务保持。')
    add('\\[J=\\tfrac12 CE_w(h_A(\\widehat a),y)+\\tfrac12 CE_w(h_A(a),y)'
        '+L_{rec}+L_{fid}+L_{gap}+0.1L_{dev}'
        '+\\gamma(\\|U_1\\|^2+\\|U_2\\|^2+\\|W_A\\|^2).\\]')
    add('rec为raw平方误差/10；dev为未投影残差平方/10。fid使用部署×业务的一阶与原始二阶矩，'
        '尺度分别1/10、1/100；gap只约束C业务生成误差的目标—源域差，不强迫真实pre域差为零。'
        '固定有限核为k(a,c)=aᵀc/10+(aᵀc)²/100，不能据前两阶矩宣称完整分布匹配。')
    tbl(pd.DataFrame([
        ['B0', '原P-small', '全程冻结，无新分支'],
        ['R-P', '真配逆Ridge＋凸头', '无动态残差/矩'],
        ['R-G', '组中心逆Ridge＋凸头', '无逐访问对应'],
        ['N-P', '真配动态恢复', '删除fid/gap，其余与F-P相同'],
        ['F-P', '真配动态恢复＋fid/gap', '主方法分支'],
        ['F-G', '组中心恢复＋真实边际fid/gap', '匿名组控制，矩不是中心外积'],
        ['E-post', 'post→post残差＋任务与dev', '无任何pre监督，无逆锚点'],
    ], columns=['臂', '定义', '用途']))
    add('动态部分名义可训练2126参数（Q对比坐标自由参数2029）；逆向方法另有1020个冻结估计锚点参数。'
        'E-post的可训练部分同量级，但不含逆锚点，不能声称总估计复杂度完全相等。')
    section('7. 训练、读出、融合和选择')
    tbl(pd.DataFrame([
        ['数值', 'Pytorch312 / Python3.12.8 / torch2.5.1 / CUDA12.4；模型全CUDA float64，禁AMP/TF32'],
        ['动态训练', 'Adam2000步；β=(0.9,0.999)，ε=1e-8，独立clip范数5'],
        ['六候选', 'lr∈{0.0003,0.001} × γ∈{0.0001,0.001,0.01}'],
        ['seed', '源内20261014；外层20261014/15/16，不做seed集成'],
        ['真实侧头', 'pre或post上的带权CE＋γ||W||²，bias不惩罚'],
        ['最终读出', '生成器冻结；生成侧和真实侧各0.5w，统一凸头refit；动态从Adam头初始化'],
        ['凸头验收', '原坐标梯度≤1e-5；独立目标/梯度误差≤1e-10；迭代<2000、评价<10000'],
        ['吞吐后端', '最多32独立模型、8 CUDA streams、CUDA Graph；凸头4并发；单lr分桶'],
        ['PURE', '分支单独推理，β=1；独立选择自己的候选'],
        ['FUSE', '(1−β)p_B0+βp_branch；β∈{0,0.25,0.5,0.75,1}，不是logit相加'],
        ['选择', '源内先最大F1_U，再最小CE_U；1e-12内tie依次低β(FUSE)、高γ、低lr、候选号'],
    ], columns=['配置', '固定规则']))
    add('全部源内模型封存后才读取query-post；全部query预测封存后才读标签；'
        'PURE/FUSE所选配置取并集进行外层训练。全部外层模型封存后才H-post预测，全部H预测封存后才评分。'
        'β=0是合法源内选择得到的精确B0别名，不是数值失败或H不利后的回退。')
    section('8. 源内选择：只能用于开发流程，不是完整H成绩')
    source = decisions.groupby(['arm', 'policy'])[['F1_U', 'CE_U', 'beta']].mean().reset_index()
    tbl(source.rename(columns={'beta': '平均β'}))
    baser = candidate[candidate.beta == 0].groupby('role_id')[['F1_U', 'CE_U']].first()
    add(f'同一源内评估上的B0角色均值：F1_U={baser.F1_U.mean():.6f}、CE_U={baser.CE_U.mean():.6f}。'
        '本节是同一源内query上选完候选后的成绩，存在选择乐观性，不能与外层H直接作同分布泛化差值。'
        '也没有以源内必须优于B0作为完整外层放行条件。')
    freq = decisions[decisions.policy == 'FUSE'].groupby(['arm', 'beta']).size().unstack(fill_value=0).reset_index()
    tbl(freq.rename(columns={x: f'β={x:g}' for x in freq.columns if isinstance(x, float)}))
    add('F-P的60角色中35个选择β=0、24个β=0.25、1个β=0.5；仅25个启用非零分支。'
        '平均β=0.108333。没有角色为F-P选择β≥0.75。不能把β0行任意挑出的候选号解读为其正则或lr偏好。')
    active = decisions[(decisions.arm == 'F-P') & (decisions.policy == 'FUSE') & ~decisions.inactive]
    tbl(active.groupby(['candidate', 'gamma', 'lr', 'beta']).size().reset_index(name='启用角色数'))
    section('9. 完整H：全部13条管线')
    tbl(pooled[['pipeline', 'F1_U', 'F1_C', 'F1_all', 'CE_U', 'Brier_U', 'worst_deployment_F1_U']])
    add('F1为0–1，差值“百分点”=100×差值。CE越低越好；Brier为六类概率平方误差之和，范围0–2。'
        '每部署×遮蔽×seed先合并五外折完整六类混淆矩阵，再取两U类宏F1并等权汇总。'
        '不是U二分类，不平均单折F1，也不把4320条单管线逻辑行当独立样本。')
    add(f'F-P-FUSE相对B0：ΔF1_U={(chosen.F1_U-base.F1_U)*100:.6f}个百分点；'
        f'ΔF1_all={(chosen.F1_all-base.F1_all)*100:.6f}个百分点；'
        f'ΔCE_U={chosen.CE_U-base.CE_U:.6f}；ΔBrier_U={chosen.Brier_U-base.Brier_U:.6f}。'
        '描述性地，所有六条FUSE候选的合并F1_U都低于B0，不能因此作未登记的六方法多重显著性结论。')
    tbl(pooled[pooled.pipeline.isin(['B0','F-P-FUSE','F-G-FUSE','N-P-FUSE','E-post-FUSE','R-P-FUSE'])][
        ['pipeline','CE','CE_U','CE_C','Brier','Brier_U','Brier_C']])
    add('概率质量需区分C/U：F-P在U的CE/Brier恶化，但C的CE从0.530316降到0.502636、'
        'Brier从0.235578降到0.231147。因C占四类，总体CE可能略有改善，不能用其遮盖U的损害；'
        '反过来，也不能将U恶化概括为所有概率指标都恶化。C的概率改善与C宏F1下降可以同时成立。')
    section('10. 五项预定主比较')
    compare = []
    for q in primary['comparisons']:
        compare.append([q['reference'], 100*q['delta_F1_U'],
                        '['+', '.join(f'{100*x:.6f}' for x in q['CI95'])+']',
                        '['+', '.join(f'{100*x:.6f}' for x in q['CI99'])+']',
                        q['positive_family_increment']])
    tbl(pd.DataFrame(compare, columns=['F-P-FUSE相对', 'ΔF1_U(百分点)', '95%区间(百分点)', '99%区间(百分点)', '家族正增量']))
    add('10000次按六业务分层的全局内容簇bootstrap，seed20261016；同内容权重共享于所有方法、部署、遮蔽、重复和seed。'
        '五比较以Bonferroni边际99%区间（0.005/0.995分位点）控制家族；不是seed均值t检验。'
        '本分析沿用已封存区间，不重抽样或改变检验家族。')
    add('F-P−F-G的差异同时包含精确锚点和逐访问rec目标的组合差异，不能分离二者；'
        'F-P−N-P才是fid/gap组合增量对照，本轮未获支持。'
        '相对R-P点估计微正但区间跨零，不支持动态残差稳定优于静态校准。'
        '所有FUSE臂共享同一个已含既有关联训练用途的P-small基座；'
        'F-P−F-G并不是整套系统“完全使用精确关联”与“完全不用精确关联”的比较。')
    section('11. 分部署与遮蔽组：不能只报总体')
    keep = ['B0', 'F-P-FUSE', 'F-G-FUSE', 'N-P-FUSE', 'E-post-FUSE', 'R-P-FUSE']
    tbl(targets[targets.pipeline.isin(keep)][['pipeline', 'target', 'F1_U', 'F1_C', 'CE_U', 'Brier_U']])
    wide = targets.pivot(index='target', columns='pipeline', values='F1_U')
    dep = pd.DataFrame({'部署': wide.index, 'F-P−B0(pp)':100*(wide['F-P-FUSE']-wide['B0']),
                        'F-P−F-G(pp)':100*(wide['F-P-FUSE']-wide['F-G-FUSE'])}).reset_index(drop=True)
    tbl(dep)
    add('主候选在四部署U-F1均低于B0。相对F-G的总体正差主要由SS贡献；'
        'Trojan与VMess的F-P点估计反而略低于F-G。因此不能写“精确对应在每个协议都更好”。'
        '这些部署分项是描述性结果，没有新增逐部署显著性家族。')
    scenarios = table('scenarios')
    sg = scenarios[scenarios.pipeline.isin(keep)].groupby(['pipeline', 'group'])[['F1_U','CE_U','Brier_U']].mean().reset_index()
    tbl(sg)
    section('12. C业务实践代价')
    tbl(pd.DataFrame(screen['deployments']))
    add(f'C总体ΔF1_C={100*screen["overall_delta_F1_C"]:.6f}个百分点，'
        f'总体1个百分点门通过={screen["overall_passed"]}。各部署2个百分点门均通过；'
        f'总体与部署联合筛查={screen["passed"]}。**失败的是总体门，不是四部署分别超限。**'
        '原机器报告“逐部署合并筛查”字段使用联合passed，容易误读，本报告按原JSON展开澄清，不改原文件。'
        '该门是实践筛查，不是证明统计非劣；未据H触发回退或重新选择β。')
    section('13. 业务分项与seed')
    cl = classes[classes.pipeline.isin(keep)].groupby(['label','pipeline']).F1.mean().unstack()
    cl.index = [NAMES[LABELS.index(x)] for x in cl.index]
    tbl(cl.reset_index(names='业务（全部遮蔽上下文）'))
    add('上表平均该业务在所有遮蔽上下文的逐类F1，含其作为C和U的情况；下表只取其作为U的唯一遮蔽组。'
        '两者不可混写为同一个“该业务F1”。')
    cu = classes[classes.pipeline.isin(keep)].copy()
    cu = cu[[LABELS.index(y) in MASKS[g] for y,g in zip(cu.label,cu.group)]]
    cu = cu.groupby(['label','pipeline']).F1.mean().unstack()
    cu.index = [NAMES[LABELS.index(x)] for x in cu.index]
    tbl(cu.reset_index(names='业务（仅U）'))
    tbl(seeds[seeds.pipeline.isin(keep)][['pipeline','seed','F1_U','F1_C','CE_U','Brier_U']])
    add('三个F-P-FUSE seed均低于对应B0，均高于F-G-FUSE。seed不是三个新增数据集；'
        'B0与静态R模型的三seed是相同模型的逻辑别名，不能据其零seed方差宣称算法稳健。')
    add('\n### 13.1 全部30个内容的U分项（描述性）\n')
    content_rows = []
    for content, part in contents[contents.scope.eq('U') & contents.pipeline.isin(['B0','F-P-FUSE','F-G-FUSE'])].groupby('content_id'):
        vals = part.groupby('pipeline')[['accuracy','CE','Brier']].mean()
        uflips = flips[flips.scope.eq('U') & flips.reference.eq('B0') & flips.content_id.eq(content)]
        content_rows.append(dict(内容=content, B0准确率=vals.loc['B0','accuracy'],
            F_P准确率=vals.loc['F-P-FUSE','accuracy'],
            准确率差pp=100*(vals.loc['F-P-FUSE','accuracy']-vals.loc['B0','accuracy']),
            相对组准确率差pp=100*(vals.loc['F-P-FUSE','accuracy']-vals.loc['F-G-FUSE','accuracy']),
            CE差=vals.loc['F-P-FUSE','CE']-vals.loc['B0','CE'],
            修复逻辑行=int(uflips.flip.eq('repaired').sum()),新增错误逻辑行=int(uflips.flip.eq('introduced').sum())))
    cr = pd.DataFrame(content_rows).sort_values(['准确率差pp','内容'])
    tbl(cr)
    add('各内容仅取其作为U的遮蔽上下文，再对部署、重复和seed等权。'
        '逐内容准确率不是逐内容宏F1，不能将表中准确率差平均后宣称是主ΔF1_U；'
        '内容分项用于定位错误，不选择性删除内容、不新增显著性或以seed扩充样本。')
    section('14. 错误翻转与概率代价')
    ff = flips.groupby(['reference','scope','flip']).agg(n=('correct','size'),
        mean_delta_CE=('delta_CE','mean'), mean_delta_Brier=('delta_Brier','mean'),
        confidence=('confidence','mean'), reference_confidence=('confidence_reference','mean')).reset_index()
    ff['CE贡献'] = ff['mean_delta_CE'] * ff['n'] / ff.groupby(['reference','scope'])['n'].transform('sum')
    tbl(ff[['reference','scope','flip','n','mean_delta_CE','CE贡献','mean_delta_Brier']])
    add('每个参照的U有1440、C有2880条逻辑行（部署/遮蔽/seed重复），不是独立访问计数。'
        '相对B0，U仅修复4条、新增43条；C修复15条、新增35条。'
        '相对F-G，U修复48条、新增12条，但C修复22条、新增46条。'
        '它解释了“真配优于组控制”与“总体仍不如B0”可以同时成立。')
    conf = pred[pred.pipeline.isin(['B0','F-P-FUSE','F-G-FUSE'])].groupby(['pipeline','scope']).apply(
        lambda d: pd.Series(dict(accuracy=d.correct.mean(),wrong_confidence=d.loc[~d.correct,'confidence'].mean(),
                                 wrong_ge_09=int(((~d.correct)&(d.confidence>=.9)).sum()),
                                 CE=d.CE_i.mean(),Brier=d.Brier_i.mean())), include_groups=False).reset_index()
    tbl(conf)
    add('不能仅凭CE/Brier恶化就说“所有错误更自信”：两者同时取决于错误数量、真类概率与正确样本概率。'
        '相对B0，U共同正确行平均ΔCE=+0.043021，主候选平均最大概率反而由0.871915降到0.838511，'
        '说明正确预测的概率被稀释也有贡献；新增错误与共同错误同样增加CE。'
        '本轮没有拟合温度、截断置信度或用H选校准规则。')
    section('15. PURE分支与读出阶段诊断')
    st = stages.groupby(['pipeline','classifier_stage'])[['F1_U','CE_U','Brier_U']].mean().reset_index()
    tbl(st)
    add('这些头在**同一所选终态生成器**上比较初始化头、Adam终态头、最终refit头；'
        '不是初始生成器与终态生成器的因果比较，也不是额外可选checkpoint。'
        'F-P-PURE最终F1_U=0.572836、CE_U=3.664619，单独逆向分支远弱于B0。'
        '其初始化头CE=2.252195，Adam后3.647744，refit后3.664619；'
        'refit相对Adam变化小，不能把主要弱点只归因于最后凸头refit。'
        '初始化头虽概率损害较小，也未接近B0，不能事后改主方法以规避当前结论。')
    section('16. 实际训练轨迹：只在训练范围解释')
    trajectory = tr.groupby('arm').agg(paths=('arm','size'),
        objective_decrease_rate=('decrease','mean'),J0=('J0','mean'),Jend=('Jend','mean'),
        task0=('task0','mean'),taskend=('taskend','mean'),raw0=('raw0','mean'),rawend=('rawend','mean'),
        recend=('recend','mean'),fidend=('fidend','mean'),gapend=('gapend','mean'),
        regend=('regend','mean'),clips_max=('clips','max')).reset_index()
    tbl(trajectory)
    tbl(tr.groupby('arm')[['std0','stdend','cosine_task_rec','cosine_task_fid','cosine_task_gap']].mean().reset_index())
    dispersion = tr.groupby('arm').agg(stdend_median=('stdend','median'),
        stdend_Q90=('stdend',lambda x:x.quantile(.9)),stdend_max=('stdend','max'),
        rawend_median=('rawend','median'),rank_median=('rank','median')).reset_index()
    tbl(dispersion)
    add('这组训练记录揭示一个具体取舍：F-P训练总目标均值0.600227→0.115933、任务项0.466409→0.047799，'
        'raw恢复误差0.130669→0.099374，但std误差均值67.045986→820.385070。'
        '因此“raw误差下降”不能替代“入口分类坐标保持”；两种度量中坐标权重不同，'
        'raw平方误差与按训练pre尺度转换后的平方误差可以反向变化。'
        '低方差坐标放大是符合该定义的候选解释，但本分析没有逐坐标分解，不能指定某个箱为已证实原因。'
        '终态任务/恢复/矩项梯度余弦多为负，描述了目标间局部取舍；它不证明改权重便会改善H。'
        '训练任务大幅下降而H未改善，更支持本训练分布目标与真实目标U外推之间存在缺口，'
        '而非继续将本轮结果归为“LR没求解完”。')
    add('仅汇总外层927条实际选择并拟合的动态路径（PURE/FUSE配置并集），不是全候选均值，也不是独立统计检验。'
        'raw_target_error为sum w||error||²，rec=raw_error/10；std误差与raw误差单位不同。'
        'F-G raw误差目标为组中心，P为真实逐访问pre；E为真实post，三者不可直接按数值排名恢复能力。'
        'F-G没有真实逐访问std误差，该列空值不代表零。梯度余弦只作终态目标取舍描述，不是冲突的因果证据。'
        '本轮没有读取H-pre，因此没有H恢复MSE，也不能用训练恢复下降替代H分类收益。'
        '非凸2000步是固定日程，未声称其达到全局最优或驻点；凸头通过则有明确原坐标质量门。')
    section('17. 数值与工程验收：不是“未训练完成”的负结果')
    qg = quality.groupby(['scope','arm']).agg(heads=('accepted','size'),accepted=('accepted','sum'),
        max_iterations=('iterations','max'),max_evaluations=('evaluations','max'),
        max_original_gradient=('gradient','max'),max_objective_error=('objective_error','max'),
        max_gradient_error=('gradient_error','max')).reset_index()
    # Scientific notation retains the numerical precision rather than displaying zero.
    for k in ['max_original_gradient','max_objective_error','max_gradient_error']:
        qg[k] = qg[k].map(lambda x:f'{x:.8e}')
    tbl(qg)
    add('上表独立读取全部主管线分支的head质量记录（含合法复用），不包括真实侧初始化头与工程额外参照。'
        '所有这些静态/动态最终头均通过，严格未触及2000迭代或10000函数评价上限。'
        '本次分析另外从预测重建全部scenario混淆矩阵，合并F1最大差'
        f'{replay_error:.3e}；复核{len(verified)}份最终证据链文件hash一致。'
        '这不是重训，也没有声称重新运行所有P1梯度夹具。')
    add(f'原P6记录：post推理重放最大差={audit["post_logp_max_error"]}；'
        f'独立指标误差={audit["independent_metric_error"]}；历史hash复核{audit["historical_hashes_verified"]}项；'
        f'query-pre读={audit["query_pre_reads"]}、实际目标U训练读={audit["target_U_training_reads"]}、'
        f'PCAP读={audit["PCAP_reads"]}。嵌套内容审计passed={nested["passed"]}。')
    section('18. 实际计算量与分项时间')
    nd = len(jobs['dynamic']); ns = len(jobs['static'])
    head_total = 4680 + 4320 + 17280 + ns + nd
    tbl(pd.DataFrame([
        ['合法先导复用动态路径',88,'包含在源内17280之内，不新增样本'],
        ['完整源内静态端点',4320,'两静态臂×720×3γ'],
        ['完整源内动态路径',17280,'四动态臂×720×6候选'],
        ['外层动态路径',nd,'上限1440，实际按PURE/FUSE选择并集'],
        ['外层静态拟合',ns,'上限240，不按seed虚构重复拟合'],
        ['动态路径合计',17280+nd,'含88先导复用'],
        ['正式科学凸头总量',head_total,'含4680真实侧初始化及上述静态/动态refit；不含工程重放/失败'],
        ['主管线最终头本次记录审计',len(quality),'源内21600＋实际外层分支'],
        ['逻辑端点',len(endpoints),'不等于新拟合分类器数'],
    ],columns=['对象','实际数量','说明']))
    times = collections.defaultdict(float)
    for it in budget['items']:
        times[it['stage']] += it['seconds']/3600
    tbl(pd.DataFrame([[k,v] for k,v in times.items()],columns=['预算阶段','小时']))
    add('累计18.074小时低于启动保守预计约30.257小时；外层实际配置并集较最坏上限小，'
        '并且实际吞吐与γ/样本形状相关。模型秒或4个凸头worker秒不能与账本墙钟直接相加。'
        '没有全程GPU利用率采样序列，不能从零散nvidia-smi宣称平均占用或纯CUDA计算时间。')
    section('19. 本轮究竟支持什么、不能支持什么')
    tbl(pd.DataFrame([
        ['支持', '当前真配逆锚点/恢复组合比匿名组组合更好', '五项主比较之一99%区间为正，主要由SS贡献'],
        ['支持', '当前完整F-P-FUSE整体不如P-small', '主区间为负，四部署U点估计均低'],
        ['支持', '晚期融合明显减轻纯分支损害', '描述性FUSE/PURE表；二者分别选择，不是同一模型单因素因果实验'],
        ['不支持', '有限矩组合带来独立业务增益', 'F-P−N-P区间跨零'],
        ['不支持', '动态分支稳定优于静态真配逆Ridge', 'F-P−R-P区间跨零'],
        ['不支持', '引入完整GAN后效果仍负', '本轮根本没有判别器或对抗训练'],
        ['不支持', '所有配对学习或所有漂移信息都无效', '只裁决当前表示、映射、目标、队列与训练政策'],
        ['不支持', '真实pre恢复成功/失败已在H验证', '没有H-pre读取，只有训练恢复诊断'],
        ['不支持', '新部署/跨日期/外部直连可泛化', '完整但同批历史内部评价，数据多次开发'],
    ], columns=['层级','命题','证据或边界']))
    add('建议本轮按“实现完整、主增强目标未成立、精确对照保留局部正证据”结项。'
        '**保留P-small作为当前强参照，不部署F-P替换它；冻结本轮五比较及全部负向结果。**'
        '这不是自动授权增加训练、搜索β/γ、重选部署或增加GAN。若继续，应另立有限问题和合同，'
        '而不是在H引导下挑选初始化头、启用角色或有利部署改写本轮主结论。')
    section('20. 追溯与复现')
    for name, path in [
        ('原子实施计划','plan/DP-GAN1-M-v1-local-implementation-plan-20261016.md'),
        ('预算与权限授权','docs/deproxy-moment-game-v1-20261016/full-NER1-authorization.md'),
        ('NER1工程先导报告','docs/deproxy-moment-game-v1-20261016/numeric-repair-pilot.md'),
        ('完整调度实现','eval/deproxy_moment_game_v1_full_ner1/driver.py'),
        ('损失定义','eval/deproxy_moment_game_v1_full_ner1/models.py'),
        ('最终凸头求解','eval/deproxy_moment_game_v1_full_ner1/classifier.py'),
        ('机器原始报告','outputs/deproxy-moment-game-v1-20261016/full-ner1-01/reports/complete-report.md'),
        ('主比较','outputs/deproxy-moment-game-v1-20261016/full-ner1-01/comparisons/primary.json'),
        ('C筛查','outputs/deproxy-moment-game-v1-20261016/full-ner1-01/comparisons/practical-screen.json'),
        ('最终复核','outputs/deproxy-moment-game-v1-20261016/full-ner1-01/tests/P6-independent-verification.json'),
        ('本报告生成代码','eval/deproxy_moment_game_v1_full_ner1_analysis/report.py'),
    ]: add('- ' + link(path, name))
    add('\n复现本报告只读分析，不启动训练：\n\n```powershell\n'
        '& D:/Tools/Anaconda/envs/Pytorch312/python.exe eval/deproxy_moment_game_v1_full_ner1_analysis/report.py\n```')
    add('本报告新增于docs，不覆盖已封存原报告或训练输出。附带analysis-evidence-20261017.json记录读取hash、'
        '本次指标重建误差和证据链复核范围；不冒称另一次完整P6数值重放。')
    DOC.mkdir(parents=True, exist_ok=True)
    DEST.write_text('\n\n'.join(lines)+'\n', encoding='utf-8')
    # Compact audit: retain direct result bindings and a digest of all inspected
    # training-side metadata hashes, rather than duplicating megabytes of paths.
    train_hashes = {k:v for k,v in READ_HASHES.items() if '/models/' in k}
    result_hashes = {k:v for k,v in READ_HASHES.items() if k not in train_hashes}
    evidence = dict(read_only_training_run=True, no_fit=True, no_H_pre=True, metric_replay_max_error=replay_error,
        checked_final_chain_hashes=len(verified), checked_final_heads=len(quality), outer_traces=len(tr),
        main_prediction_rows=len(pred), unique_visits=pred.visit_id.nunique(), unique_contents=pred.content_id.nunique(),
        inspected_training_metadata_count=len(train_hashes),
        inspected_training_metadata_hash_manifest_sha256=hashlib.sha256(json.dumps(train_hashes,sort_keys=True).encode()).hexdigest(),
        result_read_hashes=result_hashes, report_sha256=hashlib.sha256(DEST.read_bytes()).hexdigest())
    (DOC/'analysis-evidence-20261017.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in evidence.items() if k!='result_read_hashes'},ensure_ascii=False,indent=2))
    print(DEST)


if __name__ == '__main__':
    main()
