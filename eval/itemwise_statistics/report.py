"""Build full item reports and scope-explicit statistical tables from extraction caches."""
from __future__ import annotations

from collections import Counter
import argparse
from itertools import combinations
import json
import math
import platform
from pathlib import Path
import sys

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

sys.path.insert(0, str(Path(__file__).resolve().parent))
from extract import ROOT, OUT, DOC, VERSION, read, sha, stats
from proxy_analysis.reproducibility.preflight import write_json
from proxy_analysis.config import FeatureConfig

PRIMARY_SCOPES = ['exclusive_page', 'carrier_context_envelope', 'direct_pre_only']
PROTOCOLS = ['SHADOWSOCKS', 'VLESS', 'HYSTERIA2']
SHORT = {'SHADOWSOCKS': 'SS', 'VLESS': 'VLESS', 'HYSTERIA2': 'Hy2'}
KEYS = ['packet_count', 'nonempty_packets', 'transport_bytes', 'ip_bytes',
        'up_transport_bytes', 'down_transport_bytes', 'up_byte_fraction', 'duration_s',
        'entity_count', 'connection_span_concurrency_max', 'burst_count', 'fr_runs',
        'fr_switches', 'fr_runs_per_packet', 'fr_switches_per_possible_transition',
        'direction_entropy', 'transition_entropy', 'length_median', 'length_p95',
        'iat_median_us', 'iat_us_p95', 'offload_suspect_fraction', 'full_retransmission_fraction',
        'rtt_median_ms', 'length_js', 'length_ks', 'length_wasserstein_bytes', 'iat_js',
        'iat_ks', 'iat_wasserstein_log1p_us', 'cumulative_l1']
NAMES = {'packet_count': '包数', 'transport_bytes': '传输层载荷字节', 'ip_bytes': 'IP 字节',
         'burst_count': '方向 burst 数（含空载荷包）', 'fr_runs': 'TCP FR（非空方向段数）',
         'length_median': '非空载荷长度中位数', 'iat_median_us': '连接内 IAT 中位数（µs）',
         'entity_count': '非空观测实体数', 'duration_s': '观测包络时长（s）'}
BASE = ['batch', 'item_id', 'target_index', 'target_domain', 'target_url', 'resource', 'label_id',
        'protocol', 'repetition', 'session_id', 'main_route', 'activity_state', 'run_state']
GROUP = ['batch', 'item_id', 'protocol', 'scope', 'selection', 'view', 'metric']


def save(name, rows):
    df = rows if isinstance(rows, pd.DataFrame) else pd.DataFrame(rows)
    pq.write_table(pa.Table.from_pandas(df, preserve_index=False), OUT / name, compression='zstd')
    return df


def fmt(x):
    if x is None or isinstance(x, float) and not math.isfinite(x):
        return '—'
    return f'{x:.5g}' if isinstance(x, (int, float, np.number)) else str(x).replace('|', '\\|').replace('\n', ' ')


def mdtable(headers, rows):
    return '\n'.join(['| '+' | '.join(headers)+' |', '| '+' | '.join(['---']*len(headers))+' |']+
                     ['| '+' | '.join(fmt(x) for x in row)+' |' for row in rows])+'\n'


def write_md(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip()+'\n', encoding='utf-8')


def transform_kind(name):
    if 'fraction' in name or name.startswith('transition_p_') or 'entropy' in name or 'per_packet' in name or 'per_possible' in name:
        return 'difference'
    return 'log_ratio'


def delta(a, b, kind):
    if a is None or b is None:
        return None, 'undefined_or_missing_side'
    if kind == 'difference':
        return b-a, None
    if a <= 0 or b <= 0:
        return None, 'both_zero' if a == b == 0 else 'pre_zero' if a == 0 else 'post_zero'
    return math.log(b/a), None


def materialize(reg):
    sides, transforms, coverage, captures, sequences, sources = [], [], [], [], [], {}
    scalar_names = set()
    for row in reg:
        if not row['is_final']:
            continue
        cached = read(OUT/'sessions'/(row['session_id']+'.json'))
        assert cached['version'] == VERSION
        sources.update(cached['sources'])
        meta = {k: row.get(k) for k in BASE}
        available = []
        for scope in cached['scopes']:
            common = {**meta, 'scope': scope['scope'], 'selection': scope['selection']}
            if scope['selection'] == 'observed' and scope['pre'] and scope['post']:
                available.append(scope['scope'])
            for side in ('pre', 'post'):
                values = scope[side]
                sides.append({**common, 'side': side, 'available': bool(values), **values,
                              'mapped_logical_connections_per_carrier': scope.get('mapped_logical_connections_per_carrier')})
            names = sorted({k for side in ('pre', 'post') for k, v in scope[side].items()
                            if (v is None or isinstance(v, (float, int))) and k not in {'first_ns', 'last_ns'}})
            scalar_names.update(names)
            for name in names:
                a, b = scope['pre'].get(name), scope['post'].get(name)
                kind = transform_kind(name)
                value, reason = delta(a, b, kind)
                transforms.append({**common, 'metric': name, 'transform': kind, 'pre': a, 'post': b,
                                   'difference': b-a if a is not None and b is not None else None,
                                   'ratio': b/a if a is not None and a > 0 and b is not None else None,
                                   'value': value, 'reason': reason})
            for name, value in scope['distances'].items():
                transforms.append({**common, 'metric': name, 'transform': 'distance', 'pre': None,
                                   'post': None, 'difference': None, 'ratio': None, 'value': value, 'reason': None})
        coverage.append({**meta, 'has_proxy_comparison': bool(available), 'available_proxy_scopes': json.dumps(available),
                         'indexed_pre_count': cached.get('indexed_pre_count'), 'indexed_entity_count': cached.get('indexed_entity_count'),
                         'indexed_route_counts': json.dumps(cached.get('indexed_route_counts', {})),
                         'excluded_pair_count': cached.get('excluded_pair_count'),
                         'proxy_requests': row['proxy_requests'], 'direct_requests': row['direct_requests'],
                         'unresolved_requests': row['unresolved_requests'], 'manual_confirmation': row['manual_confirmation'],
                         'error_count': len(cached['errors']), 'errors': json.dumps(cached['errors']),
                         'interpretation': 'main_target_proxy_context' if row['main_route'] == 'proxy' and available else
                             'auxiliary_or_unresolved_proxy_context' if available else 'no_proxy_pair_observation',
                         'has_direct_pre': any(s['scope'] == 'direct_pre_only' and s['pre'] for s in cached['scopes'])})
        captures.extend({**meta, **c} for c in cached['captures'])
        sequences.extend({**meta, **c} for c in cached['sequences'])
    side = save('visit-side-features.parquet', sides)
    trans = save('visit-transformations.parquet', transforms)
    cov = save('coverage-and-eligibility.parquet', coverage)
    save('capture-audit.parquet', captures)
    save('sequence-prefixes.parquet', sequences)
    write_json(OUT/'source-hashes.json', sources)
    return side, trans, cov, scalar_names


def summarize(trans):
    # Work at the visit level. No pooling of packets or pair records across visits.
    registry = pq.read_table(OUT/'item-registry.parquet').to_pylist()
    denominators = Counter((r['item_id'], r['protocol'], cohort)
                           for r in registry if r['is_final']
                           for cohort in ('all_indexed_contexts', 'main_target_proxy')
                           if cohort == 'all_indexed_contexts' or r['main_route'] == 'proxy')
    frames = []
    for view, col in [('pre', 'pre'), ('post', 'post'), ('transformation', 'value')]:
        use = trans if view == 'transformation' else trans[trans['transform'] != 'distance']
        f = use[[c for c in GROUP if c != 'view']+['session_id', 'main_route', col]].copy()
        f = f.rename(columns={col: 'number'})
        f['view'] = view
        frames.append(f)
    long = pd.concat(frames, ignore_index=True)
    summaries = []
    for cohort in ('all_indexed_contexts', 'main_target_proxy'):
        frame = long if cohort == 'all_indexed_contexts' else long[long.main_route == 'proxy']
        for key, group in frame.groupby(GROUP, sort=False):
            x = group.number.dropna().to_numpy(float)
            summary = stats(x)
            if len(x) < 2:
                summary['std'] = summary['iqr'] = summary['mad'] = None
            total = denominators[(key[1], key[2], cohort)]
            summaries.append({**dict(zip(GROUP, key)), 'cohort': cohort, 'n_selected': total,
                              'n_valid': len(x), 'n_missing': total-len(x), **summary,
                              'visits_json': json.dumps(group.session_id.tolist()),
                              'values_json': json.dumps([None if pd.isna(v) else float(v) for v in group.number])})
    return save('item-protocol-summary.parquet', summaries)


def compare_protocols(summary):
    s = summary[(summary.selection == 'observed') & summary.scope.isin(PRIMARY_SCOPES)
                & (summary.cohort == 'all_indexed_contexts') & (summary.n_valid > 0)]
    rows = []
    for key, group in s.groupby(['batch', 'item_id', 'view', 'metric'], sort=False):
        for (_, a), (_, b) in combinations(list(group.iterrows()), 2):
            if a.protocol == b.protocol:
                continue
            # Direct observations must not masquerade as one side of a proxy pair.
            if (a.scope == 'direct_pre_only') != (b.scope == 'direct_pre_only'):
                continue
            rows.append({**dict(zip(['batch', 'item_id', 'view', 'metric'], key)),
                         'protocol_a': a.protocol, 'protocol_b': b.protocol, 'scope_a': a.scope, 'scope_b': b.scope,
                         'comparison_type': 'same_scope_unpaired_visits' if a.scope == b.scope else 'heterogeneous_scope_descriptive_only',
                         'n_a': a.n_valid, 'n_b': b.n_valid, 'median_a': a['median'], 'median_b': b['median'],
                         'median_b_minus_a': b['median']-a['median'],
                         'ratio_of_medians_b_over_a': b['median']/a['median'] if a['median'] > 0 and b['median'] >= 0 else None})
    return save('cross-protocol-comparison.parquet', rows)


def cross_dataset(reg, summary):
    items = pd.DataFrame([r for r in reg if r['is_final']]).groupby('item_id', sort=False).first().reset_index()
    candidates, rows = [], []
    s = summary[(summary.selection == 'observed') & summary.scope.isin(PRIMARY_SCOPES)
                & (summary.cohort == 'main_target_proxy') & (summary.n_valid > 0)]
    for _, a in items[items.batch != '0916'].iterrows():
        for _, b in items[(items.batch == '0916') & (items.resource == a.resource)].iterrows():
            # Same observed activity kind + manual semantic suffix: video != page browsing.
            sem_a = 'video' if a.label_id.endswith('::video_playback') else a.activity_kind
            sem_b = 'video' if b.label_id.endswith('::video_playback') else b.activity_kind
            compatible = sem_a == sem_b
            candidates.append({'item_a': a.item_id, 'batch_a': a.batch, 'item_b': b.item_id,
                               'resource': a.resource, 'activity_a': a.label_id, 'activity_b': b.label_id,
                               'activity_compatible': compatible, 'comparability': 'same_resource_activity_descriptive_only' if compatible else 'activity_mismatch',
                               'workload_equivalence': 'not_established_no_cross_batch_pairing'})
            if not compatible:
                continue
            left = s[s.item_id == a.item_id]
            right = s[s.item_id == b.item_id]
            merged = left.merge(right, on=['protocol', 'scope', 'view', 'metric'], suffixes=('_a', '_b'))
            for _, m in merged.iterrows():
                rows.append({'batch_a': a.batch, 'item_a': a.item_id, 'item_b': b.item_id, 'resource': a.resource,
                             **{k: m[k] for k in ('protocol', 'scope', 'view', 'metric')},
                             'n_a': m.n_valid_a, 'n_b': m.n_valid_b, 'median_a': m['median_a'], 'median_b': m['median_b'],
                             'median_b_minus_a': m['median_b']-m['median_a'],
                             'interpretation': 'descriptive_batch_difference_workload_not_matched'})
    save('cross-dataset-candidates.parquet', candidates)
    save('cross-dataset-comparison.parquet', rows)
    return candidates, rows


def methods(names):
    feature_dictionary = {
        'schema_version': 1, 'extractor_version': VERSION, 'feature_config_sha256': sha(ROOT/'configs/feature-defaults.yaml'),
        'histogram_edges': dict(FeatureConfig.load(ROOT/'configs/feature-defaults.yaml').values['histograms']),
        'scalar_features': {name: {'transform': transform_kind(name), 'label': NAMES.get(name, name)} for name in sorted(names)},
        'direction': '+1 indexed initiator -> responder; -1 reverse. Not inferred from first captured packet.',
        'length': 'transport payload bytes; nonempty lengths only; may include offload/coalescing artifacts, not wire MTU claims',
        'iat': 'microseconds, timestamp+ordinal sorted within original entity; never across independent connections',
        'FR': 'TCP nonempty direction runs summed over connections; runs=nonempty connections+switches',
        'fr_normalization': 'runs/nonempty_packets and switches/(nonempty_packets-nonempty_entities); undefined denominator => null',
        'burst': 'direction runs of selected packets, including control-only TCP packets for observed selection',
        'distance': {'JS': 'base-2 divergence on frozen histogram bins, explicit tails', 'KS': 'exact empirical CDF maximum, p-values not reported',
                     'Wasserstein_length': 'empirical samples, bytes', 'Wasserstein_IAT': 'empirical log1p(microseconds)', 'curve': '101-point normalized time and normalized cumulative payload'},
        'repeat_dispersion': 'np quantile linear, unscaled MAD, population STD; n<2 => dispersion null',
        'zero_policy': 'strict natural log(post/pre) only both >0; no epsilon; bounded feature post-pre',
        'tcp': 'project TCP sequence/ACK state estimator; full retransmission exclusion does not remove partial retransmission bytes; raw window NOT scaled advertised receive window',
        'rtt': 'capture-local ACK matching estimator (including handshake if available); not guaranteed Internet RTT; no inference when samples absent',
        'idle': 'sum/count of within-entity gaps > threshold; active span sum <= threshold. Across-entity sums not wall-clock page active time.',
        'multiplexing': 'mapped logical connections / indexed physical carriers in context; not decrypted QUIC streams or instantaneous multiplexing',
        'sequences': 'first 32 packets/entity, not full stored packet sequence; all observed packets used for scalar features',
        'unavailable': ['TLS handshake/SNI fingerprint not newly extracted', 'CDN provider attribution', 'application throughput or decrypted content', 'strict Hy2 logical pre/post mapping'],
    }
    write_json(OUT/'feature-dictionary.json', feature_dictionary)
    lines = ['# 统计口径与使用边界', '',
        '本报告是固定采集的描述性统计，不训练分类器，不开展新的特征筛选或显著性搜索。所有指标由项目自己的数据包/状态实现计算，未调用 Wireshark 内置统计。', '',
        '## 样本与观察范围', '',
        '- 全量 registry 含 1,002 次存储尝试；仅 987 次选定访问参与统计。0914 broad、0914 repeat、0916 三个批次分别报告。',
        '- 同一条目按批次、目标索引、规范化资源标识；活动证据逐访问保留，不把异常访问改成新条目。查询参数保留，仅删除既有 Bing 重定向跟踪参数。',
        '- exclusive_page：已有索引中排他、外侧实体未复用的 TCP→TCP 配对集合。不是网页所有流量，更不是每个应用资源都已解密归属。',
        '- carrier_context_envelope：Hy2 相关逻辑连接的 pre 包络内截取共享 UDP 载体；full 是载体全范围敏感性。可能含共享背景流量，不能当作一对一逻辑流。',
        '- direct_pre_only：有明确 DIRECT 路由的 pre 观测；不制造 post，不赋予代理变换。主文档 DIRECT 而存在辅助代理连接时，辅助连接仍展示但不纳入主请求代理汇总。',
        '- 主请求 proxy 仅说明主请求路由，不保证页面所有资源均走代理。三种部署路由/传输范围差异是实测条件的一部分。', '',
        '## 定义', '',
        '- 方向由索引的发起端定义。长度用传输层载荷和 IP 总长；大于 MTU 的观测包保留并标记 offload 嫌疑，不等价于线上物理分包。',
        '- IAT 在原连接内按时间戳＋序号排序后计算，单位 µs。原始时间回退计数保留；不跨连接拼接 IAT、FR 或 transition。',
        '- 原 TCP FR=非空方向段数；总 FR=非空实体数＋总 switches。分别给出 runs/N 和 switches/(N−非空实体数)。Hy2 中相似方向段统计单独命名 analog，不称原 TCP FR。',
        '- observed burst 包括纯 ACK 等空载荷包，因而不等于 FR。另给 nonempty 与 exclude_full_retransmission 敏感性，后者不等价于完整去重传字节。',
        '- 分布距离：JS 是固定分箱的 base-2 散度（非平方根距离）；KS 是原始样本经验 CDF 最大差；Wasserstein 长度用 bytes、IAT 用 log1p(µs)。不解释依赖包样本的 KS p 值。',
        '- 累积曲线各侧独立归一化时间/字节，101 点；其接近不代表绝对延迟或字节量接近。直方图和曲线保存在侧特征表。',
        '- RTT 为现有 TCP ACK 匹配估计，不保证端到端网络 RTT；窗口为 raw 字段未应用缩放；无样本不补零。active/idle 是连接内 gap 阈值汇总，不是网页真实墙钟活跃时长。',
        '- 并发是已观测连接生命周期包络的最大重叠（端点相等时闭区间处理），不是浏览器 HTTP 请求并发。载体扇出是索引映射比例，不是 QUIC 内部瞬时并发。', '',
        '## 汇总规则', '',
        '- 每次访问先算 pre/post 与严格 ln(post/pre)，再对重复汇总。零值保留，log-ratio 无定义时记录原因，不添加 epsilon。比例/概率/熵使用 post−pre。',
        '- 重复报告中位数、min/max、Q25/Q75、IQR、未缩放 MAD；单次 broad 不提供重复离散性。4/5 次重复主要作描述，不估计高精度区间。',
        '- 总览先取各条目重复中位数，再按条目等权取中位数。增长率 exp(中位 log-ratio)−1 不等于先混合所有包或字节求比。',
        '- 跨协议相同 repetition 编号不是同时观测的因果配对；比较各自访问分布。SS/VLESS 同口径比较与 Hy2 异质范围比较明确区分。',
        '- 跨批次仅列确切资源和兼容活动候选；采集时长、路由、实际内容交付未严格匹配，因此只作批次参考，不声称时间不变性或纯协议因果效应。',
        '- SNI/域名/IP 是元数据，不用于这些统计主指标；SNI 不能单独确认 CDN 厂商。本轮不新增 TLS 指纹或 CDN 归因。', '',
        '## 固定分箱边界', '',
        '分布图横轴是分箱序号；序号 0 为 underflow，末序号为 overflow，其间按以下边界划分。', '',
        chr(96)*3+'json', json.dumps(feature_dictionary['histogram_edges'], ensure_ascii=False, indent=2), chr(96)*3, '',
        '## 特征索引', '', mdtable(['字段', '变换'], [(n, transform_kind(n)) for n in sorted(names)])]
    write_md(DOC/'methods.md', '\n'.join(lines))


def plot_item(item_id, rows, batch):
    usable = rows[(rows.selection == 'observed') & rows.scope.isin(PRIMARY_SCOPES) & (rows.scope != 'direct_pre_only')]
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.1), layout='constrained')
    for ax, names, title in [(axes[0], ['packet_count', 'transport_bytes', 'burst_count'], 'Visit-level log(post/pre)'),
                             (axes[1], ['length_js', 'iat_js', 'cumulative_l1'], 'Distribution / shape divergence')]:
        for j, protocol in enumerate(PROTOCOLS):
            for k, metric in enumerate(names):
                values = usable[(usable.protocol == protocol) & (usable.metric == metric)].value.dropna().to_numpy()
                if len(values):
                    x = k+(j-1)*.23
                    ax.scatter(x+np.linspace(-.045, .045, len(values)), values, s=12, color=f'C{j}', alpha=.7, label=SHORT[protocol] if k == 0 else None)
                    ax.plot([x-.07, x+.07], [np.median(values)]*2, color=f'C{j}', lw=2)
        ax.set_xticks(range(3), [n.replace('_count', '').replace('_bytes', '') for n in names], fontsize=9)
        ax.set_title(title, fontsize=10)
        ax.axhline(0, color='gray', lw=.6)
        ax.grid(axis='y', alpha=.2)
    if axes[0].get_legend_handles_labels()[0]:
        axes[0].legend(fontsize=8)
    else:
        axes[0].text(.5, .5, 'No eligible proxy pair; see coverage / DIRECT table',
                     ha='center', transform=axes[0].transAxes, fontsize=8)
    fig.suptitle(f'{batch} / {item_id}   Hy2: carrier envelope, not TCP pair', fontsize=9)
    p = DOC/'figures'/f'{item_id}.png'
    p.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(p, dpi=130)
    plt.close(fig)


def plot_shapes(item_id, side):
    selected = side[(side.item_id == item_id) & (side.selection == 'observed') &
                    side.scope.isin(['exclusive_page', 'carrier_context_envelope']) & side.available]
    fig, axes = plt.subplots(1, 3, figsize=(12, 3.2), layout='constrained')
    for j, protocol in enumerate(PROTOCOLS):
        for which in ('pre', 'post'):
            group = selected[(selected.protocol == protocol) & (selected.side == which)]
            for ax, field, title in zip(axes, ['length_hist', 'iat_hist', 'curve'],
                                        ['Payload length distribution', 'Within-entity IAT distribution', 'Normalized cumulative payload']):
                vectors = []
                for values in group[field]:
                    if isinstance(values, (list, np.ndarray)) and len(values):
                        x = np.asarray(values, dtype=float)
                        if field != 'curve':
                            if x.sum() == 0:
                                continue
                            x = x/x.sum()
                        vectors.append(x)
                if vectors:
                    mean = np.mean(vectors, axis=0)
                    x = np.linspace(0, 1, len(mean)) if field == 'curve' else np.arange(len(mean))
                    ax.plot(x, mean, color=f'C{j}', ls='-' if which == 'pre' else '--',
                            lw=1.25, label=f'{SHORT[protocol]} {which}')
                ax.set_title(title, fontsize=10)
                ax.set_xlabel('Normalized time' if field == 'curve' else 'Frozen bin index (tails included)', fontsize=8)
                ax.grid(alpha=.2)
    handles, labels = axes[0].get_legend_handles_labels()
    if handles:
        fig.legend(handles, labels, loc='outside lower center', ncol=6, fontsize=8)
    fig.suptitle('Equal-visit mean normalized distributions; Hy2 carrier scope is heterogeneous', fontsize=9)
    fig.savefig(DOC/'figures'/f'{item_id}-shapes.png', dpi=130)
    plt.close(fig)


def render_items(reg, trans, summary, cov, cross, side):
    df = pd.DataFrame([r for r in reg if r['is_final']])
    links = []
    for item_id, visits in df.groupby('item_id', sort=False):
        first = visits.iloc[0]
        batch = first.batch
        t = trans[(trans.item_id == item_id) & (trans.selection == 'observed') & trans.scope.isin(PRIMARY_SCOPES)]
        s = summary[(summary.item_id == item_id) & (summary.selection == 'observed') & summary.scope.isin(PRIMARY_SCOPES)
                    & (summary.cohort == 'all_indexed_contexts')]
        c = cov[cov.item_id == item_id]
        name = f'{int(first.target_index):03d}-{item_id}.md'
        relative = f'items/{batch}/{name}'
        links.append({'batch': batch, 'item_id': item_id, 'target_index': int(first.target_index), 'domain': first.target_domain,
                      'url': first.target_url, 'labels': ' / '.join(sorted(visits.label_id.unique())), 'report': relative})
        lines = [f'# {batch} · 条目 {int(first.target_index):03d} · {first.target_domain}', '',
                 f'目标：{first.target_url}', '', f'活动标签：{" / ".join(sorted(visits.label_id.unique()))}。选定访问 {len(visits)} 次。', '',
                 '[返回总索引](../../README.md) · [统计口径](../../methods.md)', '',
                 '## 覆盖与资格（每次访问均保留）', '',
                 mdtable(['部署', '重复', '主请求路由', '活动状态', '代理比较', 'DIRECT pre', '请求 proxy/direct/unresolved', '错误'],
                         [(SHORT[r.protocol], r.repetition, r.main_route, r.activity_state, r.has_proxy_comparison,
                           r.has_direct_pre, f'{r.proxy_requests}/{r.direct_requests}/{r.unresolved_requests}', r.errors)
                          for r in c.sort_values(['protocol', 'repetition']).itertuples()]), '',
                 '主请求非 proxy 的统计仅解释为已索引的辅助代理连接或 DIRECT 观测，不代表目标业务经代理传输。播放确认与配对资格是两道不同的门。', '',
                 f'![逐访问变换](../../figures/{item_id}.png)', '',
                 '图中散点为单次访问，短线为重复中位数；Hy2 是共享载体包络，不能与 TCP 配对作等范围因果对比。', '',
                 f'![长度IAT与累积形态](../../figures/{item_id}-shapes.png)', '',
                 '形态图先逐访问归一化，再对访问等权平均；实线 pre，虚线 post。分箱序号及边界见 methods，不将分箱索引误解为长度或时间。', '',
                 '## 每次访问的关键观测', '']
        for protocol in PROTOCOLS:
            pt = t[t.protocol == protocol]
            lines += [f'### {SHORT[protocol]}', '']
            for scope in pt.scope.unique():
                part = pt[pt.scope == scope]
                lines += [f'范围：`{scope}`。每格 pre → post；空值为不可观测/不适用。', '',
                          mdtable(['重复', '包数', '载荷字节', 'burst', 'TCP FR', 'IAT中位µs', 'length JS', 'IAT JS'],
                            [(rep, *[visit_cell(part, rep, metric) for metric in ['packet_count', 'transport_bytes', 'burst_count', 'fr_runs', 'iat_median_us', 'length_js', 'iat_js']])
                             for rep in sorted(visits[visits.protocol == protocol].repetition.unique())]), '']
            lines += ['完整标量统计：中位数 [min,max]；Δ 为重复内逐访问变换的中位数，MAD 未缩放。n 为可用变换数；DIRECT-only 的 nΔ=0 不代表 pre 不可用。', '']
            ps = s[s.protocol == protocol]
            display = []
            for (scope, metric), g in ps.groupby(['scope', 'metric'], sort=True):
                views = {r.view: r for r in g.itertuples()}
                a, b, d = [views.get(k) for k in ('pre', 'post', 'transformation')]
                span = lambda x: '—' if x is None or x.n_valid == 0 else f'{fmt(x.median)} [{fmt(x.min)}, {fmt(x.max)}]'
                display.append([scope, metric, span(a), span(b), fmt(d.median) if d else '—',
                                fmt(d.iqr) if d else '—', fmt(d.mad) if d else '—', d.n_valid if d else 0])
            lines += [mdtable(['scope', '特征', 'pre', 'post', 'Δ', 'IQRΔ', 'MADΔ', 'nΔ'], display), '']
        cp = cross[(cross.item_id == item_id) & cross.metric.isin(KEYS)]
        lines += ['## 不同部署对比', '',
                  '以下是各部署自身重复中位数的差异，不按重复编号强行配对。跨 TCP/Hy2 的行标记异质观测范围。', '',
                  mdtable(['视角', '特征', '部署A', '部署B', 'A中位', 'B中位', 'B−A', '比较口径'],
                          [(r.view, r.metric, SHORT[r.protocol_a], SHORT[r.protocol_b], r.median_a, r.median_b,
                            r.median_b_minus_a, r.comparison_type) for r in cp.itertuples()]), '',
                  '## 可复核的访问标识', '',
                  mdtable(['部署', '重复', 'session_id'], [(SHORT[r.protocol], r.repetition, r.session_id) for r in visits.itertuples()]), '',
                  '全量三种 packet selection、Hy2 full 范围、Q25/Q75、直方图与曲线见机器可读产物；本页只显示 observed 主范围。']
        write_md(DOC/relative, '\n'.join(lines))
        plot_item(item_id, trans[trans.item_id == item_id], batch)
        plot_shapes(item_id, side)
    return links


def visit_cell(part, rep, metric):
    rows = part[(part.repetition == rep) & (part.metric == metric)]
    if rows.empty:
        return '—'
    r = rows.iloc[0]
    return fmt(r.value) if r['transform'] == 'distance' else f'{fmt(r.pre)} → {fmt(r.post)}'


def render_batches(links, summary, coverage):
    overall = []
    for batch in ('0914-broad', '0914-repeat', '0916'):
        c = coverage[coverage.batch == batch]
        s = summary[(summary.batch == batch) & (summary.selection == 'observed') & summary.scope.isin(PRIMARY_SCOPES)
                    & (summary.scope != 'direct_pre_only') & (summary.cohort == 'main_target_proxy') & (summary.view == 'transformation')]
        rows = []
        for (protocol, scope, metric), g in s[s.metric.isin(KEYS)].groupby(['protocol', 'scope', 'metric']):
            g = g[g.n_valid > 0]
            if g.empty:
                continue
            median = float(g['median'].median())
            ratio = math.exp(median) if transform_kind(metric) == 'log_ratio' and metric not in ['length_js', 'length_ks', 'length_wasserstein_bytes', 'iat_js', 'iat_ks', 'iat_wasserstein_log1p_us', 'cumulative_l1'] else None
            row = dict(batch=batch, protocol=protocol, scope=scope, metric=metric, item_count=len(g), visits=int(g.n_valid.sum()),
                       median_item_delta=median, ratio=ratio, median_item_mad=float(g.mad.median()) if g.mad.notna().any() else None,
                       positive_items=int((g['median'] > 0).sum()), negative_items=int((g['median'] < 0).sum()))
            overall.append(row)
            rows.append([SHORT[protocol], scope, metric, len(g), int(g.n_valid.sum()), median, ratio, row['median_item_mad'], f"{row['positive_items']}/{row['negative_items']}"])
        li = sorted([x for x in links if x['batch'] == batch], key=lambda x: x['target_index'])
        text = [f'# {batch}：全部条目统计', '',
                f'本批次 {len(li)} 个条目，{len(c)} 次选定访问。主请求 proxy 汇总仅使用明确路由的可比较观测；所有未进入汇总的条目仍可在下方查看。', '',
                '## 路由与特征覆盖', '',
                mdtable(['部署', '选定访问', '主请求proxy', '主请求direct', '可计算代理上下文', 'DIRECT pre', '提取错误'],
                        [(SHORT[p], len(g), int((g.main_route == 'proxy').sum()), int((g.main_route == 'direct').sum()),
                          int(g.has_proxy_comparison.sum()), int(g.has_direct_pre.sum()), int(g.error_count.sum())) for p, g in c.groupby('protocol')]), '',
                '## 按条目等权汇总的变换', '',
                'Δ：每条目内先取重复变换中位数，再对条目取中位数。ratio=exp(Δ) 仅用于正尺度指标。MAD 在单次 broad 不定义；+/− 是条目变换方向数，零单独保留在明细中。', '',
                mdtable(['部署', 'scope', '特征', '条目n', '访问n', 'Δ中位', '典型倍率', '条目MAD中位', '+/−'], rows), '',
                f'![关键变换](figures/{batch}-overview.png)', '',
                '## 全部条目索引', '',
                mdtable(['序号', '域名', '业务标签', '目标URL', '详细报告'],
                        [(x['target_index'], x['domain'], x['labels'], x['url'], f"[打开]({x['report']})") for x in li])]
        write_md(DOC/f'dataset-{batch}.md', '\n'.join(text))
        fig, ax = plt.subplots(figsize=(8, 3.8), layout='constrained')
        for j, p in enumerate(PROTOCOLS):
            for k, m in enumerate(['packet_count', 'transport_bytes', 'burst_count', 'fr_runs']):
                values = s[(s.protocol == p) & (s.metric == m)]['median'].dropna().to_numpy()
                if len(values):
                    pos = k+(j-1)*.23
                    ax.scatter(pos+np.linspace(-.07, .07, len(values)), values, s=9, alpha=.5, color=f'C{j}', label=SHORT[p] if k == 0 else None)
                    ax.plot([pos-.09, pos+.09], [np.median(values)]*2, color=f'C{j}', lw=2)
        ax.axhline(0, color='gray', lw=.7)
        ax.set_xticks(range(4), ['Packets', 'Payload bytes', 'Bursts', 'TCP FR'])
        ax.set_ylabel('Median visit log(post/pre), per item')
        ax.set_title(f'{batch}: main-target proxy; Hy2 carrier scope separate')
        ax.legend()
        fig.savefig(DOC/'figures'/f'{batch}-overview.png', dpi=160)
        plt.close(fig)
    save('dataset-overview.parquet', overall)
    return overall


def validate(side, trans, cov, reg):
    errors = []
    if len(cov) != 987 or cov.session_id.nunique() != 987:
        errors.append('registry coverage mismatch')
    if cov.error_count.sum():
        errors.append('extraction errors present')
    good = side[side.available]
    for label, ok in [('packet_direction_conservation', np.all(good.packet_count == good.up_packets+good.down_packets)),
                      ('byte_direction_conservation', np.all(good.transport_bytes == good.up_transport_bytes+good.down_transport_bytes)),
                      ('no_negative_iat', bool((good.iat_us_min.dropna() >= 0).all()))]:
        if not ok:
            errors.append(label)
    fr = good[good.fr_runs.notna()]
    if not np.all(fr.fr_runs == fr.fr_switches+fr.nonempty_entity_count):
        errors.append('FR algebra violation')
    hist_errors = 0
    for r in good.itertuples():
        if sum(r.length_hist) != r.nonempty_packets or sum(r.iat_hist) != r.iat_count:
            hist_errors += 1
    if hist_errors:
        errors.append('histogram mass mismatch')
    numeric = trans.select_dtypes(include='number').to_numpy()
    if np.isinf(numeric).any():
        errors.append('infinite scalar')
    if trans.duplicated(['session_id', 'scope', 'selection', 'metric']).any():
        errors.append('duplicate transform key')
    # Independent replay against previously saved business summaries, not newly generated caches.
    old = pq.read_table(ROOT/'outputs/content-generalization-20260916/business-01/side-summaries.parquet').to_pylist()
    new = {(r['session_id'], r['selection'], r['side']): r for r in side[side.scope == 'exclusive_page'].to_dict('records')}
    comparisons, mismatches = 0, []
    for r in old:
        for which in ('pre', 'post'):
            current = new[(r['session_id'], r['selection'], which)]
            for k, value in r[which].items():
                if isinstance(value, (int, float)):
                    comparisons += 1
                    if not np.isclose(value, current.get(k), rtol=1e-10, atol=1e-10):
                        mismatches.append((r['session_id'], which, k))
    if mismatches:
        errors.append('legacy business feature mismatch')
    old14 = pq.read_table(ROOT/'outputs/replication-20260914/run-01/repeat/audit/repeat_feature_long.parquet').to_pylist()
    lookup = {(r['session_id'], r['scope'], r['selection'], r['metric']): r
              for r in trans[trans.batch == '0914-repeat'].to_dict('records')}
    checks14, mismatch14 = 0, []
    for r in old14:
        current = lookup.get((r['session_id'], r['scope'], r['selection'], r['metric']))
        if current is None:
            continue
        for key in ('pre', 'post'):
            if r[key] is not None:
                checks14 += 1
                if current[key] is None or not np.isclose(r[key], current[key], rtol=1e-10, atol=1e-10):
                    mismatch14.append((r['session_id'], r['metric'], key))
        if r['delta'] is not None:
            checks14 += 1
            if current['value'] is None or not np.isclose(r['delta'], current['value'], rtol=1e-10, atol=1e-10):
                mismatch14.append((r['session_id'], r['metric'], 'delta'))
    if mismatch14:
        errors.append('legacy 0914 repeat mismatch')
    result = {'passed': not errors, 'errors': errors, 'selected_visits': len(cov), 'attempts': len(reg),
              'items': cov.item_id.nunique(), 'side_rows': len(side), 'transformation_rows': len(trans),
              'legacy_scalar_checks': comparisons, 'legacy_mismatches': mismatches[:20], 'histogram_errors': hist_errors,
              'legacy_0914_checks': checks14, 'legacy_0914_mismatches': mismatch14[:20],
              'checks': ['direction conservation', 'FR algebra', 'histogram mass', 'nonnegative IAT', 'finite values', 'unique keys', 'legacy replay']}
    write_json(OUT/'quality-report.json', result)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--render-only', action='store_true', help='Reuse this run existing verified tables; regenerate reports/figures.')
    args = parser.parse_args()
    DOC.mkdir(parents=True, exist_ok=True)
    reg = pq.read_table(OUT/'item-registry.parquet').to_pylist()
    if args.render_only:
        side = pd.read_parquet(OUT/'visit-side-features.parquet')
        trans = pd.read_parquet(OUT/'visit-transformations.parquet')
        cov = pd.read_parquet(OUT/'coverage-and-eligibility.parquet')
        names = set(trans.loc[trans['transform'] != 'distance', 'metric'])
    else:
        side, trans, cov, names = materialize(reg)
    print('materialized', len(side), len(trans), flush=True)
    quality = validate(side, trans, cov, reg)
    print('validation', quality, flush=True)
    if args.render_only:
        summary = pd.read_parquet(OUT/'item-protocol-summary.parquet')
        den = Counter((r['item_id'], r['protocol'], cohort)
                      for r in reg if r['is_final']
                      for cohort in ('all_indexed_contexts', 'main_target_proxy')
                      if cohort == 'all_indexed_contexts' or r['main_route'] == 'proxy')
        summary['n_selected'] = [den[(a, b, c)] for a, b, c in zip(summary.item_id, summary.protocol, summary.cohort)]
        summary['n_missing'] = summary.n_selected-summary.n_valid
        save('item-protocol-summary.parquet', summary)
    else:
        summary = summarize(trans)
    print('summarized', len(summary), flush=True)
    cross = compare_protocols(summary)
    candidates, batch_rows = cross_dataset(reg, summary)
    methods(names)
    links = render_items(reg, trans, summary, cov, cross, side)
    overview = render_batches(links, summary, cov)
    save('report-index.parquet', links)
    write_md(DOC/'cross-dataset-comparison.md', '\n'.join(['# 跨批次比较：仅作参考', '',
        '精确资源重合不代表实际 workload、采集时长、部署路由相同；不将两批次拼接为新增重复。下面保留相同资源候选及活动标签差异。数值明细见 cross-dataset-comparison.parquet，未作跨批次显著性或可重复性推断。', '',
        mdtable(['0914子集', '目标资源', '0914活动', '0916活动', '活动兼容', '比较资格'],
                [(r['batch_a'], r['resource'], r['activity_a'], r['activity_b'], r['activity_compatible'], r['comparability']) for r in candidates]), '',
        f'生成 {len(batch_rows)} 条分特征、侧别、部署与范围的描述性对比。标签命名的细化（如 page_load → document_view）仅在原始 activity_kind 一致且目标确切相同时允许进入描述性候选；绝不据此断言任务负载完全相同。']))
    overview_lines = ['# 0914 / 0916 逐条目统计总报告', '',
        f'本轮从原始连接捕获重新计算，覆盖 {quality["selected_visits"]} 次选定访问、{quality["items"]} 个分批条目；全量登记 {quality["attempts"]} 次存储尝试。提取错误 {int(cov.error_count.sum())}。', '',
        '## 先看范围，再看变化', '',
        '本报告区分网页/访问上下文中的严格 TCP 配对、Hy2 共享载体、DIRECT-only 观测。主请求路由、播放有效性与配对可用性独立保留。没有把直连 Bilibili 视频或 Hy2 的 UDP 方向段重新解释为 TCP 代理变换。', '',
        '## 关键统计', '',
        '以下仅汇总主请求明确 proxy 的条目；每条目等权。表中倍率是 exp(条目中位 ln(post/pre) 的中位数)。长度/IAT/曲线距离与绝对流量规模另见批次和逐条目报告。', '',
        mdtable(['批次', '部署', '范围', '指标', '条目数', '访问数', '典型倍率', 'Δ中位', '重复MAD中位'],
                [(r['batch'], SHORT[r['protocol']], r['scope'], r['metric'], r['item_count'], r['visits'], r['ratio'], r['median_item_delta'], r['median_item_mad'])
                 for r in overview if r['metric'] in ['packet_count', 'transport_bytes', 'burst_count', 'fr_runs', 'length_js', 'iat_js']]), '',
        '## 如何理解与此前结果的关系', '',
        '本轮不是训练集、验证集或测试集上的新模型结果，而是全部条目清单的流量描述。此前 0916 的 240 访问主队列与 299/300 候选只占本轮的一部分；样本范围不同导致总中位数不同，不构成旧实验被推翻。', '',
        'SS/VLESS 的严格 TCP 上下文可以同口径比较；与 Hy2 的三方比较只能称部署条件下的观测差异。包数、burst、FR 的不同变化不矛盾：burst 含空载荷包，FR 只看非空方向交替；字节守恒也不意味着分包或时间结构守恒。', '',
        '重复间 MAD/IQR 反映当前少量访问的离散程度，不证明总体稳定性。大包、重传、RTT、路由和实际页面加载变化均可能影响统计，不能归因于代理协议本身。', '',
        '## 数据与质量', '',
        f'侧特征表 {len(side):,} 行；变换明细 {len(trans):,} 行。旧 0916 业务缓存数值交叉核对 {quality["legacy_scalar_checks"]:,} 项，差异 {len(quality["legacy_mismatches"])}。质量状态：{quality["passed"]}。', '',
        '详细字段定义、缺失与零值政策见 [methods](methods.md)。可用性见 coverage-and-eligibility.parquet；原始来源摘要见 source-hashes.json；每次访问缓存可增量重用。', '',
        '## 分报告', '',
        '- [0914 broad：64 个条目](dataset-0914-broad.md)',
        '- [0914 repeat：18 个条目](dataset-0914-repeat.md)',
        '- [0916：35 个条目](dataset-0916.md)',
        '- [跨批次参考](cross-dataset-comparison.md)',
        '- [全条目入口](README.md)']
    write_md(DOC/'overall-report.md', '\n'.join(overview_lines))
    write_md(DOC/'README.md', '\n'.join(['# 两数据集逐条目统计报告索引', '',
        '[总报告](overall-report.md) · [计算口径](methods.md) · [0914 broad](dataset-0914-broad.md) · [0914 repeat](dataset-0914-repeat.md) · [0916](dataset-0916.md) · [跨批次](cross-dataset-comparison.md)', '',
        '机器可读产物：`outputs/itemwise-statistics-0914-0916/run-01/`。三个 packet selection 与载体 full 敏感性全部保留，Markdown 展示 observed 主范围。', '',
        mdtable(['批次', '条目', '域名', '标签', '报告'], [(x['batch'], x['target_index'], x['domain'], x['labels'], f"[详细]({x['report']})") for x in links]), '',
        '复现命令（仓库根目录，Pytorch312）：', '', '```powershell',
        'D:/Tools/Anaconda/envs/Pytorch312/python.exe eval/itemwise_statistics/extract.py --workers 4',
        'D:/Tools/Anaconda/envs/Pytorch312/python.exe eval/itemwise_statistics/report.py', '```']))
    code = [*Path(ROOT/'eval/itemwise_statistics').glob('*.py'), *Path(ROOT/'src/proxy_analysis').rglob('*.py'), ROOT/'configs/feature-defaults.yaml']
    write_json(OUT/'provenance.json', {'python': sys.version, 'platform': platform.platform(),
                                    'code': {str(p): sha(p) for p in code}, 'registries': read(OUT/'registry-provenance.json'),
                                    'output_tables': {p.name: sha(p) for p in OUT.glob('*.parquet')}})
    from supplement import enhance
    enhance()
    print('Reports written:', DOC, 'quality:', quality['passed'], flush=True)
    if not quality['passed']:
        raise SystemExit('Quality gate failed; inspect quality-report.json')


if __name__ == '__main__':
    main()
