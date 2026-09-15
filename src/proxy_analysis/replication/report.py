"""Render a run-specific research handoff only after numerical acceptance."""
from __future__ import annotations
import argparse
from collections import Counter
from pathlib import Path
import json
import math
import numpy as np
import pyarrow.parquet as pq
from ..information_validation.data import digest, write_json


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-root',type=Path,required=True)
    args=parser.parse_args(); root=args.output_root
    def read(path): return json.loads((root/path).read_text(encoding='utf-8'))
    def table(path): return pq.read_table(root/path).to_pylist()
    def link(label,path): return f'[{label}]({(root/path).resolve().as_posix()})'
    required=['broad/features-quality.json','repeat/features-quality.json',
        'broad/aligned/aligned-quality-report.json','repeat/aligned/aligned-quality-report.json',
        'broad/statistics/statistical-quality-report.json','broad/formal/independent-validation.json',
        'repeat/audit/independent-validation.json','repeat/audit/repeat_statistics-validation.json',
        'repeat/information-validation/independent-validation.json','repeat/reproduction-validation.json']
    for path in required:
        if read(path)['state']!='passed': raise ValueError(f'acceptance not passed: {path}')
    quality={b:read(f'{b}/features-quality.json') for b in ['broad','repeat']}
    formal=read('broad/formal/formal-evaluation-manifest.json')
    info=table('repeat/information-validation/classification-summary.parquet')
    regress=table('repeat/information-validation/recoverability-summary.parquet')
    a=table('repeat/audit/within_protocol_repeatability.parquet')
    iccs=table('repeat/audit/repeatability_icc.parquet')
    sep=table('repeat/audit/between_protocol_separation.parquet')
    consistency=table('repeat/audit/cross_url_consistency.parquet')
    routes=table('repeat/audit/routing_eligibility.parquet')
    labels=table('repeat/information-validation/label-evidence.parquet')
    comparison=read('comparison/comparison-summary.json')
    primary=lambda r:r['stratum']=='all5' and r['selection']=='observed' and r['cohort']=='page_proxy'
    lines=['# 20260914 最新流量：复现实验阶段总结','',
        '本轮已完成既有分析在最新两批数据上的复现，以及新旧契约/共同有效URL的描述性对照。'
        '不包含业务Y分类、teacher/LUPI或新增捕获。结果为固定部署下的关联，不是剥离节点与配置后的纯协议因果效应。','',
        '## 1. 数据与产物','',
        '| 批次 | selected会话 | 实体记录 | 严格配对记录 | Hy2窗口 | Web会话 |','|---|---:|---:|---:|---:|---:|']
    for batch,q in quality.items():
        c=q['record_counts'];lines.append(f"| {batch} | {q['session_count']} | {c['entity']} | {c['exclusive_pair']} | {c['hysteria2_window']} | {c['web_session']} |")
    lines += ['', 'broad：64个目标URL、50个domain，每部署一次；repeat：18个目标、每部署5次，共270次选定访问。'
        'broad另有2次非选定attempt，仅保留审计，不进入主数据。',
        '全量基础特征包括长度/IAT/方向及其分布、方向性包/字节、burst、FR与归一化FR、转移/熵、累计形状、'
        '配对变换和分布距离、页面连接/并发/共享信息，以及已有TCP与active/idle扩展。原始字段由项目解析，特征不调用Wireshark内置统计。'
        '18个代表指标的专项推断并不等于对全部宽表列逐一检验。',
        'IP、端口、域名及标签身份仅作元数据/分组。SNI解析阶段未在本轮新增；不据此宣称识别CDN出口、供应商或PoP。','',
        '三张表每批各有一套：请求—连接索引、URL关联配对特征、页面会话协议特征。页面保留会话和轮次，不折叠重复访问。','']
    for batch in ['broad','repeat']:
        lines.append(f"- {batch}："+'；'.join(link(label,f'{batch}/aligned/{filename}') for label,filename in [
            ('请求索引','url-connection-index.parquet'),('URL配对','url-aligned-pair-features.parquet'),('页面表','page-aligned-protocol-features.parquet')]))
    lines += ['', '## 2. broad：统计与部署分类','',
        'Q1/Q2/Q3、资源strict/weighted及敏感性均已计算。最终统计验收通过，保留3类解释警告：'
        '已确认的VLESS burst口径敏感、Hy2载体描述范围、CDN不可观测。',
        '用户已确认：VLESS资源级burst_count的strict中位log-ratio为0，weighted为0.1029（约+10.84%）；'
        'strict为主、weighted仅作敏感性，不作跨口径稳健增加声明。零中位数不证明等效，页面Q1不能替代资源Q3。',
        link('统计汇总及原值','broad/statistics/README.md'),'',
        '正式分类保持5折×5次外层、4折内层、按site分组、训练内预处理和调参。下表是25个外层fold的macro-F1均值；'
        '与所有OOF合并计算的pooled F1不同，不将fold视为独立重复实验。','',
        '| 特征集/消融 | 模型 | 特征数 | mean-fold macro-F1 |','|---|---|---:|---:|']
    for r in formal['results']:lines.append(f"| {r['ablation']} | {r['model']} | {r['feature_count']} | {r['macro_f1']['mean']:.4f} |")
    old=json.loads(Path('outputs/experiments/formal/nested-a_core-multinomial_logistic-a_core_all.json').read_text())
    new=read('broad/formal/nested-a_core-multinomial_logistic-a_core_all.json')
    lines += ['',f"同类A-core logistic旧批次为{old['summary']['macro_f1']['mean']:.4f}，新批次为{new['summary']['macro_f1']['mean']:.4f}。"
        '这是两批整体性能的描述性对照，不是相同cohort的重训对照，也不据此声称差异显著或归因为协议变化。',
        link('正式评估清单','broad/formal/formal-evaluation-manifest.json'),'',
        '## 3. repeat：变换可重复性','',
        f"页面代理候选{sum(r['page_context_candidate'] for r in routes)}次、主文档代理候选{sum(r['main_document_proxy_candidate'] for r in routes)}次。"
        '有效URL数按指标、scope、轮次和缺失情况确定；ICC仅使用完整URL×轮次网格，n≥3的方向描述另计。',
        '以下中心为每URL五次（或可用重复）Δ均值的跨URL中位数，再经exp转回比例；不是按包加权的总量比例。','',
        '| 协议 | 指标 | n≥3 URL | 中心变化 | 重复MAD中位数（log尺度） | ICC(A,1) | ICC完整URL |',
        '|---|---|---:|---:|---:|---:|---:|']
    for protocol in ['SHADOWSOCKS','VLESS']:
        for metric in ['packet_count','transport_bytes','burst_count','fr_runs']:
            rows=[r for r in a if primary(r) and r['protocol']==protocol and r['scope']=='exclusive_page' and r['metric']==metric and r['n']>=3]
            i=next(r for r in iccs if primary(r) and r['protocol']==protocol and r['scope']=='exclusive_page' and r['metric']==metric)
            lines.append(f"| {protocol} | {metric} | {len(rows)} | {(math.exp(float(np.median([r['mean'] for r in rows])))-1)*100:+.2f}% | "
                f"{np.median([r['mad_raw'] for r in rows]):.5f} | {i['icc_A1']:.4f} | {i['n_urls']} |")
    lines += ['', '组间分离主分析仅含SS/VLESS，S为同URL协议间均值方差与协议内重复方差之比；不是显著性或因果指标。','',
        '| 指标 | 完整共同URL | S_local | S_global | BH q |','|---|---:|---:|---:|---:|']
    for r in sep:
        if primary(r) and r['row_type']=='summary' and r['metric'] in ['packet_count','fr_runs','length_js']:
            lines.append(f"| {r['metric']} | {r['n_urls']} | {r['S_local_pooled']:.3f} | {r['S_global']:.3f} | {r['q_value']:.6g} |")
    lines += ['', 'SS的packet增加、burst增加且bytes满足等效范围这一联合profile，在14个n≥3 URL中有12个同时成立，去首轮后仍为12/14。'
        '这支持一个候选变换profile，但样本URL有限、每URL仅4/5轮且同轮网络可能相关，仍不能宣称无条件跨站点普遍规律。',
        'Hy2只描述页面关联inner与共享carrier时间窗，不将载体背景流量算作纯页面开销，不自动提升生命周期scope。',
        link('完整A/B/C报告与区间','repeat/audit/transformation-reproducibility-report.md'),'',
        '## 4. 信息论桥接：强分类不等于可逆变换','',
        '此部分仅SS/VLESS两类，14个URL×2部署×5轮=140个主队列会话。14个pre、14个post与17个Δ特征分别输入；'
        'domain只作分组，metadata和missingness另作诊断。LORO留整轮，LOUO留整URL。不是broad三分类的同一任务。','',
        '| 划分 | 输入 | logistic pooled macro-F1 | log-loss(bits) |','|---|---|---:|---:|']
    for r in info:
        if r['setting']=='primary' and r['model']=='logistic' and r['view'] in ['pre','post','delta']:
            lines.append(f"| {r['scheme']} | {r['view']} | {r['macro_f1']:.4f} | {r['log_loss_bits']:.4f} |")
    lines += ['', 'pre自身已能很好地区分部署，提示pre侧工作负载/路径/反馈差异仍是重要混杂；Δ分类强并不证明它是与业务无关的纯协议信息。',
        'post→Δ恢复采用固定ridge，同时保留部署/URL均值、代数和同家族剔除对照。下面仅列跨URL的ridge：','',
        '| Δ目标 | LOUO ridge R² | 剔除同家族后的R² |','|---|---:|---:|']
    for metric in ['packet_count','transport_bytes','burst_count','fr_runs','length_js','iat_js']:
        rows={r['model']:r for r in regress if r['setting']=='primary' and r['scheme']=='LOUO' and r['target_view']=='delta' and r['metric']==metric}
        lines.append(f"| {metric} | {rows['ridge_post']['r2']:.4f} | {rows['ridge_post_drop_family']['r2']:.4f} |")
    lines += ['', 'packet/bytes/burst/FR的主ridge跨URL R²为负，说明该固定模型未实现稳定的跨URL恢复；不能据此证明信息不存在。'
        '同家族剔除后部分改善也不等于完全排除数学耦合。',
        'H(C)−交叉熵和Fano代入量均为经验操作量，不是精确互信息或总体置信下界。'
        '尤其LOUO post的F1较高，但过度自信的错误使log-loss约1.72 bits、H−CE为负，必须同时看概率质量。',
        'Δ含pre和post的共同数学项；本轮未执行完整分布置换耦合实验，也未证明Δ可作为业务学习的可部署teacher。',
        link('信息论完整报告','repeat/information-validation/first-stage-validation-report.md'),'',
        '## 5. 独立验收与新旧对照','',
        '两次独立信息论运行的12张Parquet表逐值、逐行顺序完全一致；训练/测试分组及OOF所属测试集检查通过。'
        '15,136条分类OOF和94,456条回归OOF包含多设置/模型/目标，不是这么多个独立会话。',
        '正式CV的site/session/索引实体隔离和每轮OOF覆盖已独立验收；保留全部逐样本预测及训练测试身份。',
        f"broad目标声明契约对照：{comparison['broad_target_contracts']}。",
        f"repeat目标声明契约对照：{comparison['target_contracts']}。",
        'repeat的bilibili/youtube/vimeo时长改变；旧douban被新rottentomatoes替换。声明配置相同仍不能控制采集日期、网络和实现版本。'
        '共同有效URL结果只作描述对照，两批不合并为额外轮次，分类没有按共同cohort重新训练。',
        link('新旧对照及机器表说明','comparison/comparison-report.md'),'',
        '## 6. 下一确认节点：业务标签与跨内容采样','',
        '| 域名 | 审计会话 | 正式播放通过 | 通过且页面代理候选 | 内容数 |','|---|---:|---:|---:|---:|']
    for domain in ['bilibili.com','youtube.com','vimeo.com']:
        rows=[r for r in labels if r['site_domain']==domain]
        lines.append(f"| {domain} | {len(rows)} | {sum(r['playback_verified'] for r in rows)} | "
            f"{sum(r['playback_verified'] and r['page_proxy_candidate'] for r in rows)} | {len({r['content_id'] for r in rows})} |")
    lines += ['', '标签定义继续为domain × activity。YouTube播放质量已改善，但每平台只有一个主要内容；'
        'Bilibili/Vimeo仍不能把page_load当成验证过的视频播放。当前不足以验证“同domain下跨内容共有业务活动”的泛化。',
        '停止在业务Y/teacher训练前。建议下一步先明确跨内容采样与播放证据门槛，再补齐至少两个可验证活动类别；'
        '不得仅凭Δ分类F1=1就启动语义解耦结论。新增捕获、标签替换或Y模型需要用户确定范围。','',
        '## 7. 复现与边界','',
        '入口：`python -m proxy_analysis.replication.run`，新批次配置`configs/replication-20260914.yaml`。'
        '已有全量数据可从`--stage broad-models`继续；信息论输出目录要求新建，独立重跑使用单独目录。'
        '独立检查见`replication.validate`，新旧对照见`replication.compare`，本报告见`replication.report`。',
        '环境为Pytorch312，未修改原始数据、未安装或升级依赖、未提交推送Git。'
        '代码修复包含真实selected语义、Hy2声明多路径、动态记录数校验、轮次身份和OOF审计。'
        '报告修正了旧批次候选数残留，并分别列ICC完整网格与n≥3分母。','']
    (root/'stage-results-report.md').write_text('\n'.join(lines),encoding='utf-8')
    artifacts={}
    for p in sorted(root.rglob('*')):
        if p.is_file() and p.suffix in ['.parquet','.json','.md'] and 'features' not in p.parts and 'smoke-features' not in p.parts and 'history' not in p.parts:
            if p.name=='stage-artifacts.json':continue
            artifacts[str(p.relative_to(root))]={'bytes':p.stat().st_size,'sha256':digest(p)}
    write_json(root/'stage-artifacts.json',{'acceptance_reports':required,'artifacts':artifacts,
        'scope':'derived tables/reports/current checkpoints; raw captures and per-session base feature shards excluded'})
    print('report and artifact hashes written',len(artifacts))


if __name__=='__main__':main()
