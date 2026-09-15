"""Human-readable A/B/C results with exportable scientific figures."""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
from datetime import date

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pyarrow.parquet as pq

from .preflight import write_json


def fmt(x):
    return 'NA' if x is None else f'{x:.4g}'


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output_root',type=Path)
    args=parser.parse_args()
    root=args.output_root
    def table(name): return pq.read_table(root/(name+'.parquet')).to_pylist()
    a=table('within_protocol_repeatability')
    b=table('between_protocol_separation')
    c=table('cross_url_consistency')
    iccs=table('repeatability_icc')
    features=table('repeat_feature_long')
    pairs=table('exclusive_pair_feature_long')
    extraction=json.loads((root/'repeat-extraction-status.json').read_text(encoding='utf-8'))
    registry=table('run_registry')
    selected=[r for r in registry if r['is_final']]
    selected_ids={r['session_id'] for r in selected}
    routes=[r for r in table('routing_eligibility') if r['session_id'] in selected_ids]
    versions=Counter(r['traffictracer_commit'] for r in selected)
    metrics=list(dict.fromkeys(r['metric'] for r in features))
    def primary(r,stratum='all5'):
        return r['stratum']==stratum and r['selection']=='observed' and r['cohort']=='page_proxy'
    def scope_for(p): return 'carrier_context_envelope' if p=='HYSTERIA2' else 'exclusive_page'
    protocols=['SHADOWSOCKS','VLESS','HYSTERIA2']
    lines=['# Transformation reproducibility：五次重复数据结果', '',
           f'日期：{date.today().isoformat()}。SS/VLESS严格配对主分析，Hy2仅carrier-context描述。', '',
           '## 产物与样本', '',
           f'- 提取attempt：{len(extraction)}；成功：{sum(r["state"]=="complete" for r in extraction)}。',
           f'- 特征长表：{len(features):,}行；exclusive连接级特征长表：{len(pairs):,}行。',
           f'- 登记选定访问{len(selected)}次、非选定尝试{len(registry)-len(selected)}次；推断只使用选定会话。',
           '- 正式计算口径包含18个代表量、observed/nonempty/exclude_full_retransmission三种包选择。',
           f'- 页面代理候选{sum(r["page_context_candidate"] for r in routes)}会话；更严格的最终主文档走代理候选{sum(r["main_document_proxy_candidate"] for r in routes)}会话。各指标的有效URL数仍由缺失值、配对和重复完整性决定。',
           '- SS/VLESS只纳入TCP一对一inner/outer；复用outer的连接剔除并在会话JSON记录。',
           '- Hy2使用页面关联inner到carrier的页面时间窗；完整捕获carrier窗仅作敏感性。未推断纯协议开销。', '',
           '## 特征定义与统计方式', '',
           '计数和字节按实体相加；IAT、burst、FR不跨连接建立伪转移。FR主字段为每TCP stream的runs求和，switch另列。'
           '方向概率合并连接内转移计数；累计曲线按去重实体包的时间合并、两侧分别归一化到[0,1]后比较。',
           '主要Δ为ln(post/pre)，0操作数记NA；另保留加1伪计数的对照列。JS为base-2 divergence，固定桶含underflow/overflow。'
           'bounded量用post-pre；距离量不做方向↑/↓判定。',
           '表A的中心变化为URL级重复均值的跨URL中位数；MAD为各URL重复MAD的中位数，只汇总n>=3的URL。'
           'ICC使用完整URL×轮次矩阵，absolute agreement / single measurement，URL bootstrap 5000次；退化结果NA，负估计保留。',
           '表B仅比较SS/VLESS。B为同URL的协议均值间样本方差，W为同URL协议内重复方差均值。'
           'S=mean_URL(B)/(mean_URL(W)+epsilon)，并列全局协议平均差对应的S。CI为URL成组bootstrap，'
           'p采用URL级配对均值差的精确符号翻转，依赖URL误差对称性假设，不是实际调度随机化检验；18个代表量在各分层内做BH。',
           '表C：增加/减少需95% t区间超过实用阈值；stable需90%区间完全落在等效界内（TOST式区间规则）。'
           '比例边界[0.9,1.1]，bounded差阈值0.05。n<3不分类。因重复次数少、同轮网络相关可能存在，方向标签仅描述性，'
           '不是经过跨URL多重校正的逐网站确认结论。', '',
           '## A. Within-protocol repeatability', '']
    for stratum in ('all5','rounds2to5'):
        lines += [f'### {stratum}', '', '| 协议 | 指标 | n≥3 URL | 中心Δ | 重复MAD中位数 | ICC完整URL数 | ICC(A,1) | ICC 95% CI |',
                  '|---|---|---:|---:|---:|---:|---:|---|']
        for p in protocols:
            for metric in metrics:
                group=[r for r in a if primary(r,stratum) and r['scope']==scope_for(p)
                       and r['protocol']==p and r['metric']==metric and r['n']>=3]
                if not group: continue
                ir=next((r for r in iccs if primary(r,stratum) and r['scope']==scope_for(p)
                         and r['protocol']==p and r['metric']==metric),{})
                lines.append(f"| {p} | {metric} | {len(group)} | {fmt(float(np.median([r['mean'] for r in group])))} | "
                             f"{fmt(float(np.median([r['mad_raw'] for r in group])))} | {ir.get('n_urls', 0)} | {fmt(ir.get('icc_A1'))} | "
                             f"[{fmt(ir.get('ci95_low'))}, {fmt(ir.get('ci95_high'))}] |")
    direction=table('url_direction_classification')
    summary_lines=['## 本轮主要发现', '']
    for p in ('SHADOWSOCKS','VLESS'):
        changes={}
        for m in ('packet_count','transport_bytes','burst_count','fr_runs'):
            group=[r for r in a if primary(r) and r['protocol']==p and r['metric']==m
                   and r['scope']=='exclusive_page' and r['n']>=3]
            changes[m]=(np.exp(np.median([r['mean'] for r in group]))-1)*100
        summary_lines.append(f"- {p}：URL级中心变化对应 packet {changes['packet_count']:+.1f}%，"
                             f"transport bytes {changes['transport_bytes']:+.1f}%，burst {changes['burst_count']:+.1f}%，"
                             f"FR-runs {changes['fr_runs']:+.1f}%。这些是URL等权的中心概括，不代表每个URL都有相同变化。")
    for stratum in ('all5','rounds2to5'):
        sets=[]
        for metric,label in (('packet_count','increase'),('transport_bytes','practically_stable'),('burst_count','increase')):
            sets.append({r['target_domain'] for r in direction if primary(r,stratum)
                         and r['protocol']=='SHADOWSOCKS' and r['scope']=='exclusive_page'
                         and r['metric']==metric and r['classification']==label})
        common=set.intersection(*sets)
        eligible={r['target_domain'] for r in direction if primary(r,stratum)
                  and r['protocol']=='SHADOWSOCKS' and r['metric']=='packet_count' and r['n']>=3}
        summary_lines.append(f"- SS联合profile（packet增加、burst增加、bytes等效）在{stratum}的"
                             f"{len(eligible)}个n≥3 URL中，有{len(common)}个同时成立：{', '.join(sorted(common))}。")
    for stratum in ('all5','rounds2to5'):
        significant=[r['metric'] for r in b if primary(r,stratum) and r['row_type']=='summary'
                     and r.get('q_value') is not None and r['q_value']<.05]
        summary_lines.append(f"- {stratum}：SS/VLESS组间BH q<0.05的指标：{', '.join(significant) or '无'}。效应量和CI见B表。")
    summary_lines.extend(['- 联合profile仅按上方实际URL计数解释，不默认沿用旧数据支持结论。',
                          '- Hy2分子含共享载体背景与控制流量，不能解释为纯页面膨胀系数。', ''])
    location=lines.index('## A. Within-protocol repeatability')
    lines[location:location]=summary_lines
    lines += ['', 'ICC的完整URL数在repeatability_icc.parquet中，可能少于表中n≥3 URL数。'
              'ICC高不意味着绝对MAD低；近常量但稳定的变换可能得到低/未定义ICC。', '',
              '## B. Between-protocol separation（仅SS/VLESS）', '']
    for stratum in ('all5','rounds2to5'):
        lines += [f'### {stratum}', '', '| 指标 | 完整配对URL | B | W | S local | S global | VLESS−SS | 95% CI | q |',
                  '|---|---:|---:|---:|---:|---:|---:|---|---:|']
        for r in b:
            if not primary(r,stratum) or r['row_type']!='summary':continue
            lines.append(f"| {r['metric']} | {r['n_urls']} | {fmt(r['between_variance'])} | {fmt(r['within_variance'])} | "
                         f"{fmt(r['S_local_pooled'])} | {fmt(r['S_global'])} | {fmt(r['difference_VLESS_minus_SS'])} | "
                         f"[{fmt(r['ci95_low'])}, {fmt(r['ci95_high'])}] | {fmt(r['q_value'])} |")
    lines += ['', 'S不是显著性或因果指标。S local远高于S global可能反映协议排序随URL变化。'
              'W接近0时不能仅凭S的大数值排名，原表保留near_zero_W。SS/VLESS的entity_count比例等于1由一对一配对筛选构造，'
              '不能当作独立发现的协议保持性质。', '',
              '## C. Cross-URL consistency', '']
    for stratum in ('all5','rounds2to5'):
        lines += [f'### {stratum}', '', '| 协议 | 指标 | 观测URL / n≥3 | ↑ | ≈ | ↓ | 不确定 | 距离高于阈值 | 距离低于阈值 |',
                  '|---|---|---:|---:|---:|---:|---:|---:|---:|']
        for r in c:
            if not primary(r,stratum) or r['scope']!=scope_for(r['protocol']):continue
            lines.append(f"| {r['protocol']} | {r['metric']} | {r['n_urls_observed']} / {r['n_urls_n_ge_3']} | "
                         f"{r['increase']} | {r['practically_stable']} | {r['decrease']} | {r['uncertain']} | "
                         f"{r['distance_above_threshold']} | {r['distance_within_threshold']} |")
    lines += ['', '## 已完成的敏感性', '',
              '- 全五轮 vs 第2–5轮：去首轮敏感性，不自动等同于版本对照。',
              '- observed vs 非空包 vs 排除full retransmission；部分重传仍保留。',
              '- 页面代理候选 vs 主文档代理 vs 五个低变动目标 vs 排除重试单元 vs 三协议完整候选集。',
              '- Hy2页面时间窗 vs carrier完整捕获窗。',
              '- SS/VLESS逐一删除URL、逐一删除整轮；epsilon ×0.1/×10。', '',
              '历史attempt只在存在且已提取时保留；不将缺少同等预检的历史会话直接加入主推断；no_retry是保留选定首次尝试的敏感性，'
              '不冒充首attempt替换分析。carrier完整成员机制分析仍因生命周期证据不足不开展。', '',
              '## 限制与后续', '',
              '当前是小样本探索性重复性结果。各协议单节点/单部署，不支持剥离节点、路径和配置的纯协议因果解释。'
              'ICC与逐URL t区间受4/5轮估计精度限制；协议检验受少量URL及共同轮次网络状态影响。',
              f'Manifest记录commit计数：{dict(versions)}。仅依实际版本记录解释，不假定旧批次的版本分界仍存在。',
              'SS的“宏观workload保持+微观packetization重建”需要bytes等效和packet/burst增加共同成立，不能只靠平均值趋势命名。'
              '请结合下方逐URL图和C表中的uncertain/例外，而不是只引用一个中位数。', '',
              '另已生成pre_workload_adjustment.parquet：以配对Δ差为响应、pre字节量和实体数的协议间log-ratio为协变量，'
              '含URL与轮次固定效应的探索性OLS；仅报告满秩时的等pre工作量差异，不作因果解释和显著性推断。实体数不是并发量。'
              '下一步建议优先解释稳定且跨URL一致的代表量，并扩展实际并发调整；'
              'RTT、active/idle、握手等B类和Wasserstein/KS扩展未纳入本次18个代表量的主检验。', '',
              '## 文件索引', '',
              '- repeat_feature_long.parquet：session级pre/post/Δ与scope、版本、包选择、NA原因。',
              '- exclusive_pair_feature_long.parquet：SS/VLESS连接级配对原值和Δ。',
              '- sequence_prefixes.parquet：方向、signed length、IAT前32包序列。',
              '- within_protocol_repeatability.parquet / repeatability_icc.parquet：A表及ICC。',
              '- between_protocol_separation.parquet：B表，row_type区分URL和summary。',
              '- cross_url_consistency.parquet / url_direction_classification.parquet：C表和URL明细。',
              '- reproducibility_sensitivity.parquet：删除URL/轮次和epsilon检查。',
              '- feature-contract.json / statistics-summary.json：配置指纹与统计设定。', '',
              '## 图形', '']
    figures=root/'figures'
    figures.mkdir(exist_ok=True)
    colors={'SHADOWSOCKS':'#1976a3','VLESS':'#d56831','HYSTERIA2':'#588844'}
    fig,axes=plt.subplots(2,2,figsize=(13,8))
    for ax,metric in zip(axes.flat,('packet_count','transport_bytes','burst_count','fr_runs')):
        for i,p in enumerate(protocols):
            group=[r for r in a if primary(r) and r['protocol']==p and r['scope']==scope_for(p)
                   and r['metric']==metric and r['n']>=3]
            for j,r in enumerate(group):
                x=i+(j-(len(group)-1)/2)*.025
                ax.scatter([x]*len(r['values']),r['values'],s=8,alpha=.25,color=colors[p])
                ax.scatter(x,r['median'],s=20,marker='D',color=colors[p])
        ax.axhline(0,color='gray',lw=.8)
        ax.axhspan(np.log(.9),np.log(1.1),color='gray',alpha=.12)
        ax.set_xticks(range(3),['SS','VLESS','Hy2 context'])
        ax.set_title(metric+' | all5, n>=3 per URL')
        ax.set_ylabel('log(post/pre)')
        if metric=='fr_runs':
            ax.text(2,.2,'Not applicable\n(UDP carrier)',ha='center',color='gray',fontsize=9)
    fig.suptitle('Repeat-level deltas and URL medians; Hy2 is descriptive context only')
    fig.tight_layout()
    fig.savefig(figures/'repeat_deltas.png',dpi=180)
    plt.close(fig)
    fig,axes=plt.subplots(1,2,figsize=(15,8))
    for ax,stratum in zip(axes,('all5','rounds2to5')):
        group=[r for r in b if primary(r,stratum) and r['row_type']=='summary']
        positions=np.arange(len(group))
        ax.barh(positions-.18,[r['within_variance']+1e-9 for r in group],height=.35,label='Within W',color='#1976a3')
        ax.barh(positions+.18,[r['between_variance']+1e-9 for r in group],height=.35,label='Between B',color='#d56831')
        ax.set_yticks(positions,[r['metric'] for r in group],fontsize=8)
        ax.set_xscale('log')
        ax.set_xlabel('Variance (+1e-9 for display)')
        ax.legend()
        ax.set_title('SS vs VLESS | '+stratum)
    fig.tight_layout()
    fig.savefig(figures/'between_within_variance.png',dpi=180)
    plt.close(fig)
    lines+=['![重复点与URL中位数](figures/repeat_deltas.png)', '',
            '![协议间与重复内方差](figures/between_within_variance.png)', '']
    (root/'transformation-reproducibility-report.md').write_text('\n'.join(lines),encoding='utf-8')
    write_json(root/'result-artifacts.json',{'feature_rows':len(features),'pair_rows':len(pairs),
        'sequence_rows':pq.read_metadata(root/'sequence_prefixes.parquet').num_rows,
        'extraction_errors':sum(r['state']!='complete' for r in extraction),
        'representative_metrics':len(metrics),'report':'transformation-reproducibility-report.md'})
    print('Report and two figures written')


if __name__=='__main__':main()
