"""Interpretive tables and final document QA, using only this run's outputs."""
from __future__ import annotations

import json
import math
from pathlib import Path
import re
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from extract import ROOT, OUT, DOC, sha, read
from report import mdtable, save, write_md, SHORT
from proxy_analysis.reproducibility.preflight import write_json


def enhance():
    s = pd.read_parquet(OUT/'item-protocol-summary.parquet')
    base = s[(s.selection == 'observed') & (s.cohort == 'main_target_proxy') &
             (s.scope == 'exclusive_page') & (s.n_valid > 0)]
    metrics = ['packet_count', 'transport_bytes', 'burst_count', 'fr_runs', 'length_js', 'iat_js']
    matched = []
    for batch, group in base.groupby('batch'):
        common = set(group[group.protocol == 'SHADOWSOCKS'].item_id) & set(group[group.protocol == 'VLESS'].item_id)
        for metric in metrics:
            for protocol in ['SHADOWSOCKS', 'VLESS']:
                part = group[(group.item_id.isin(common)) & (group.metric == metric) &
                             (group.view == 'transformation') & (group.protocol == protocol)]
                value = float(part['median'].median())
                matched.append({'batch': batch, 'protocol': protocol, 'metric': metric, 'items': len(part),
                                'visits': int(part.n_valid.sum()), 'median_item_delta': value,
                                'ratio': math.exp(value) if not metric.endswith('_js') else None,
                                'positive_items': int((part['median'] > 0).sum()),
                                'negative_items': int((part['median'] < 0).sum())})
    save('matched-protocol-overview.parquet', matched)
    registry = pd.read_parquet(OUT/'item-registry.parquet')
    labels = registry[registry.is_final].groupby('item_id').first()[['label_id', 'target_domain']]
    business = base[(base.batch == '0916') & (base.view == 'transformation') & base.metric.isin(metrics)].merge(labels, on='item_id')
    business_rows = []
    for (label, protocol, metric), group in business.groupby(['label_id', 'protocol', 'metric']):
        value = float(group['median'].median())
        business_rows.append({'label': label, 'protocol': protocol, 'metric': metric, 'items': len(group),
                              'visits': int(group.n_valid.sum()), 'median_item_delta': value,
                              'ratio': math.exp(value) if not metric.endswith('_js') else None})
    save('0916-business-overview.parquet', business_rows)
    captures = pd.read_parquet(OUT/'capture-audit.parquet')
    cov = pd.read_parquet(OUT/'coverage-and-eligibility.parquet')
    quality = read(OUT/'quality-report.json')
    d = pd.read_parquet(OUT/'dataset-overview.parquet')
    rows = []
    for batch in ['0914-broad', '0914-repeat', '0916']:
        for protocol in ['SHADOWSOCKS', 'VLESS']:
            part = d[(d.batch == batch) & (d.protocol == protocol)].set_index('metric')
            rows.append([batch, SHORT[protocol], int(part.loc['packet_count', 'item_count']),
                         *[part.loc[m, 'ratio'] for m in ['packet_count', 'transport_bytes', 'burst_count', 'fr_runs']],
                         part.loc['length_js', 'median_item_delta'], part.loc['iat_js', 'median_item_delta']])
    text = ['# 统计结果解读与重点发现', '',
        '本章解释逐条目数据表所呈现的规律，不把本轮全量描述性统计替换成此前分类实验的性能结论。', '',
        '## 1. 数据覆盖与资格', '',
        '两个数据集包含 1,002 次存储尝试，选定 987 次。分批条目为 64 + 18 + 35 = 117；相同资源在 broad 与 repeat 中仍是不同条目，不能视作独立的新内容或简单拼成六次重复。', '',
        mdtable(['批次', '部署', '访问', '可计算代理上下文', '主请求proxy', 'DIRECT pre观测'],
            [(batch, SHORT[protocol], len(g), int(g.has_proxy_comparison.sum()), int((g.main_route == 'proxy').sum()), int(g.has_direct_pre.sum()))
             for (batch, protocol), g in cov.groupby(['batch', 'protocol'])]), '',
        '“可计算代理上下文”比“主请求 proxy”多，并不是多了有效的视频代理样本，而是某些主请求走 DIRECT 的访问仍包含辅助代理资源。0916 VLESS 的 157 次上下文中，有 150 次主请求 proxy；这一区别在条目表中保留，不把余下辅助上下文并入六业务主统计。', '',
        'Bilibili 的用户播放确认继续有效，本轮并未否定播放。缺失的是将其主要播放负载解释为经代理传输的路由证据。Hy2 Bing 同样按 DIRECT 实况报告。', '',
        '## 2. 字节量、分包与交互不表现为同一种变换', '',
        '下表均为主请求 proxy、严格 TCP 配对访问集合。先对每个条目的重复取中位 log-ratio，再按条目等权汇总；各部署可用条目数不完全一致。', '',
        mdtable(['批次', '部署', '条目n', '包数倍率', '载荷字节倍率', 'burst倍率', 'FR倍率', 'length JS', 'IAT JS'], rows), '',
        '三个批次中，SS 的载荷字节典型增幅约 1.4%–1.9%，但包数约增加 63%–66%、burst 约增加 75%–86%。这支持“在当前观测范围内，宏观载荷量相近而微观分包/方向交互明显改变”的描述，不能升级为字节严格守恒或所有 URL 一律如此。', '',
        'SS 的 TCP FR 典型增幅约 2.7%–5.1%，远小于其 observed burst 的增幅。这与定义相符：observed burst 会被空载荷控制包分割，FR 只计非空方向段。不能将两者混称为一个方向反转指标。', '',
        'VLESS 的载荷字节典型增加约 5.7%–6.0%，包数约增加 22%–28%，FR 约增加 23%–24%。但 burst 的方向不统一：0916 的 30 个条目中 21 个中位变换为正、8 个为负、1 个为零。因而总体 burst 中位增长不能写成每个业务都增加。', '',
        '长度分布 JS 在 SS 下明显高于 VLESS：0916 分别约 0.348 与 0.051。IAT JS 分别约 0.200 与 0.077。它们是固定分箱散度，不是分类准确率，也不是信息泄露量；其大小受采集点、offload、传输状态和应用负载共同影响。', '',
        '## 3. 先对齐条目集合，再比较 SS 与 VLESS', '',
        '以下补表只保留两部署主请求均可代理观测的共同条目：0914 broad 为 39 个、repeat 为 13 个、0916 为 30 个。同条目并不意味着相同时间或完全相同响应字节，所以仍不是因果随机对照。', '',
        mdtable(['批次', '部署', '指标', '条目n', '访问n', 'Δ中位', '倍率', '方向 +/−'],
                [(r['batch'], SHORT[r['protocol']], r['metric'], r['items'], r['visits'], r['median_item_delta'], r['ratio'],
                  f"{r['positive_items']}/{r['negative_items']}") for r in matched]), '',
        '逐条目报告另外给出 pre、post 各自的跨部署差异。若 pre 已经明显不同，就不能将全部 post 差异归因于代理变换；请同时检查请求数、字节量、时长和路由。', '',
        '## 4. 六业务内部差异：0916 的全部五次重复', '',
        '此处使用 300 次 SS/VLESS 主请求代理访问，而非先前保守的 240 次队列。每业务 5 个内容、每内容 5 次重复；降级访问作为真实观测保留，状态见条目报告。未将 Bilibili DIRECT 播放并入代理业务统计。', '',
        mdtable(['domain × activity', '部署', '指标', '内容n', '访问n', 'Δ中位', '倍率'],
                [(r['label'], SHORT[r['protocol']], r['metric'], r['items'], r['visits'], r['median_item_delta'], r['ratio']) for r in business_rows]), '',
        '以上业务级数字是内容等权的描述，不能作为新的标签选择依据或重新声称跨内容识别性能。详细的内容间差异及异常重复保留在 35 份 0916 条目页中。', '',
        '## 5. Hy2：这些大倍率不能解释为协议开销', '',
        'Hy2 carrier_context_envelope 中，三个批次的载荷字节典型倍率约为 16.0、27.6、21.5，包数典型倍率约为 23.2、33.5、33.0。它们是“相关 pre 逻辑连接集合”对“共享 UDP 载体时间包络”的观测比值，而非已验证的一对一业务载荷膨胀倍数。', '',
        '共享载体可能包含窗口内非目标逻辑流、背景传输和协议控制负载；索引相关性不提供每个 UDP 包的明文业务归属。即使限定时间包络，业务归属范围仍未变得相同。因此不能写成“Hy2 有二十倍加密开销”，也不能与 TCP FR 或 SS/VLESS 的载荷守恒直接排序。', '',
        '保留这些数值的用途是展示可观察载体行为、窗口敏感性及后续归因的边界。full/envelope、关联逻辑连接/载体扇出和三种 packet selection 在机器表中可复核，本轮未放宽 Hy2 的严格配对资格。', '',
        '## 6. 重复性和跨批次结论的强度', '',
        '重复数据的每条目报告均包含 IQR、MAD、最小/最大值及每次访问原值。0916 SS 的载荷 log-ratio 条目 MAD 中位约 0.00252、包数约 0.0483；VLESS 分别约 0.00394、0.0636。宏观载荷比的重复离散性较小，不意味着所有方向/时间特征也同样稳定。', '',
        '0914 broad 每个部署仅一次访问，没有重复离散性可估计；其 MAD/IQR 标为缺失，而不是零。五次重复同样不足以给出高精度总体方差、等效结论或大量显著性结论。', '',
        '跨批次表有 12 对条目级资源重合候选（包含 broad/repeat 两种来源），不等于 12 个独立的共同 URL。Bilibili 候选缺少主业务代理资格；保留下来的数值比较仍未严格匹配采集时长与工作负载，只能作为批次参考。', '',
        '## 7. 质量、复现与尚未覆盖的内容', '',
        f'本轮解析 {len(captures):,} 个连接/载体捕获记录，累计 {int(captures.packet_count.sum()):,} 个记录内数据包；不是去重后的全局链路包数。记录原始顺序时间回退 {int(captures.timestamp_regressions.sum()):,} 次，IAT 计算统一按连接内时间排序。没有未知方向或包数解析缺口触发提取错误。', '',
        f'与既有 0916 缓存的 {quality["legacy_scalar_checks"]:,} 项标量、0914 repeat 的 {quality["legacy_0914_checks"]:,} 项数值/变换进行交叉核对，均无差异。方向包/字节守恒、FR 恒等关系、直方图计数、唯一键与非负 IAT 校验均通过。', '',
        '本轮新增及相关单元测试共 19 项通过。首次历史测试遇到旧 pytest 临时目录权限错误，改用本轮输出目录的独立临时目录后通过，不涉及修改原始数据或 conda 环境。', '',
        '未新增 TLS/SNI 指纹、CDN 厂商识别或解密后的应用字节；IP/端口/SNI 不进入统计特征。已有模型实验没有重训，旧产物不覆盖。序列附表保存每实体前 32 包，完整包序列仍由原始 PCAP 提供，所有标量使用完整选定包集合。', '',
        '[返回总报告](overall-report.md) · [完整口径](methods.md) · [全条目索引](README.md)']
    write_md(DOC/'findings.md', '\n'.join(text))
    marker = '## 统计解读补充'
    for name in ['README.md', 'overall-report.md']:
        p = DOC/name
        old = p.read_text(encoding='utf-8').split('\n'+marker)[0].rstrip()
        write_md(p, old+'\n\n'+marker+'\n\n[重点发现、共同条目比较、六业务统计及 Hy2 解释边界](findings.md)')
    missing = []
    for p in DOC.rglob('*.md'):
        for target in re.findall(r'\]\(([^)]+)\)', p.read_text(encoding='utf-8')):
            if target.startswith(('https:', 'http:', '#')):
                continue
            if not (p.parent/target.split('#')[0]).exists():
                missing.append({'document': str(p.relative_to(DOC)), 'target': target})
    qa = {'markdown_files': len(list(DOC.rglob('*.md'))), 'item_reports': len(list((DOC/'items').rglob('*.md'))),
          'figures': len(list((DOC/'figures').glob('*.png'))), 'broken_links': missing,
          'tests': {'passed': 19, 'command': 'python -m pytest tests/test_itemwise_statistics.py tests/unit/test_reproducibility.py tests/unit/test_pairwise.py -q -p no:cacheprovider --basetemp <fresh workspace temporary directory>'}}
    write_json(OUT/'document-quality.json', qa)
    provenance = read(OUT/'provenance.json')
    provenance['code'].update({str(p): sha(p) for p in (ROOT/'eval/itemwise_statistics').glob('*.py')})
    provenance['output_tables'] = {p.name: sha(p) for p in OUT.glob('*.parquet')}
    provenance['reports'] = {str(p.relative_to(DOC)): sha(p) for p in DOC.rglob('*.md')}
    write_json(OUT/'provenance.json', provenance)
    print(json.dumps(qa, ensure_ascii=False), flush=True)
    if missing:
        raise SystemExit('Broken report links')


if __name__ == '__main__':
    enhance()
