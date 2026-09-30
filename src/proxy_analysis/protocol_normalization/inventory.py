"""N0-N2: structural evidence audit; values exported by a narrow allowlist only."""
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
import gzip
import json
import os
from pathlib import Path
import re

import pandas as pd

from .common import ROOT, OUT, DOC, digest, read, save, markdown
from ..reproducibility.preflight import write_json

BATCHES = {
    '0914-broad': 'Datasets/TrafficTracer-Datasets-20260914/sites-64url-repetition-1',
    '0914-repeat': 'Datasets/TrafficTracer-Datasets-20260914/sites-detailed-18url-repetition-5',
    '0916': 'Datasets/TrafficTracer-content-generalization-20260916',
}
FIELDS = {'cipher', 'network', 'tls', 'flow', 'obfs', 'plugin', 'mux', 'smux', 'encryption'}


def structure(value, prefix=''):
    """Keys, not arbitrary scalar contents. Prevent snapshot secrets in outputs."""
    found = []
    if isinstance(value, dict):
        for key, child in value.items():
            path = prefix+'/'+key
            if key in FIELDS:
                # Evidence may concern an unselected node: never promote it automatically.
                scalar = child if isinstance(child, (bool, int)) or child in (None, '') else None
                found.append({'field': key, 'path': path, 'value_type': type(child).__name__,
                              'empty': child is None or child == '', 'safe_value': scalar})
            if isinstance(child, (dict, list)):
                found.extend(structure(child, path))
    elif isinstance(value, list):
        for child in value:
            found.extend(structure(child, prefix+'/*'))
    return found


def audit_one(row):
    p = Path(row['session_path'])
    sources, hints, versions = {}, [], {}
    for rel in ['manifest.json', 'raw/capture-context.json', 'raw/trace-input/capture-context.json',
                'raw/proxy-info.json', 'raw/trace-input/snapshot.json']:
        f = p/rel
        if not f.exists():
            continue
        d = read(f)
        sources[str(f)] = digest(f)
        hints.extend({'source': rel, **x} for x in structure(d))
        if rel == 'manifest.json':
            versions = d.get('component_versions', {})
    types, fields, stages = Counter(), Counter(), Counter()
    frame_candidates = 0
    # Both the bounded trace and retained journal are checked. Counts are evidence scans,
    # not independent network event totals and may overlap.
    for rel in ['raw/mihomo-trace.jsonl', 'raw/trace-input/trace.jsonl.gz']:
        f = p/rel
        if not f.exists():
            continue
        sources[str(f)] = digest(f)
        opener = gzip.open if f.suffix == '.gz' else open
        with opener(f, 'rt', encoding='utf-8') as stream:
            for line in stream:
                if not line.strip():
                    continue
                e = json.loads(line)
                typ = str(e.get('type', 'unknown'))
                types[typ] += 1
                fields.update(e.keys())
                if 'stage' in e:
                    stages[typ] += 1
                if any(k in e for k in ('stream_id', 'streamId', 'quic_stream_id')) and any(k in e for k in ('offset', 'stream_offset')):
                    frame_candidates += 1
    v = versions.get('mihomo', {})
    result = {k: row[k] for k in ['session_id', 'batch', 'item_id', 'protocol', 'repetition', 'profile_fingerprint']}
    result.update(mihomo_version=v.get('version'), mihomo_commit=v.get('commit'),
                  traffictracer_commit=versions.get('traffictracer', {}).get('commit'),
                  known_stack='protocol_label_only', adapter_status='unavailable_pending_historical_stack',
                  stack_fields_json=json.dumps(hints, ensure_ascii=False), trace_types_json=json.dumps(types),
                  trace_fields_json=json.dumps(fields), stage_event_types_json=json.dumps(stages),
                  stream_frame_candidate_events=frame_candidates)
    return result, sources


def main(workers=4):
    reg_path = ROOT/'outputs/itemwise-statistics-0914-0916/run-01/item-registry.parquet'
    reg = pd.read_parquet(reg_path)
    assert len(reg) == 1002 and int(reg.is_final.sum()) == 987
    assert reg.session_id.nunique() == 1002
    config_path = ROOT/'configs/protocol-normalization-20260922.yaml'
    immutable = [reg_path, config_path, ROOT/'plan/protocol-structured-normalization-atomic-plan-20260922.md',
                 ROOT/'docs/0916-source-classifier-cross-side-transfer-results.md',
                 ROOT/'docs/0916-source-calibration-cross-deployment-results.md',
                 ROOT/'docs/0916-A-H-mechanism-evidence-synthesis.md']
    contract = {'version': 1, 'selected': 987, 'attempts': 1002, 'byte_thresholds': [0,64,256,1024],
                'training_allowed': False, 'sources': {str(p): digest(p) for p in immutable}}
    if (OUT/'contract.json').exists() and read(OUT/'contract.json') != contract:
        raise ValueError('Frozen input contract differs; create a new run.')
    write_json(OUT/'contract.json', contract)
    save('registry.parquet', reg)
    sources, batch_rows, filenames = {}, [], []
    for batch, rel in BATCHES.items():
        root = ROOT/rel
        for f in root.glob('*.json'):
            sources[str(f)] = digest(f)
            d = read(f)
            if 'runtime-diagnostic' in f.name:
                for name, value in d.get('sections', {}).items():
                    batch_rows.append({'batch': batch, 'file': f.name, 'section': name,
                        'hash_only': isinstance(value, str) and bool(re.fullmatch('[0-9a-f]{64}', value)),
                        'stored_value_length': len(value) if isinstance(value, str) else None})
        for folder, _, files in os.walk(root):
            for name in files:
                if re.search(r'(keylog|qlog|\.keys$|profile|config.*\.ya?ml$)', name, re.I):
                    filenames.append({'batch': batch, 'path': str(Path(folder)/name), 'status': 'name_candidate_not_content_verified'})
    rows = []
    with ProcessPoolExecutor(max_workers=workers) as pool:
        for i, (r, evidence) in enumerate(pool.map(audit_one, reg[reg.is_final].to_dict('records'), chunksize=4), 1):
            rows.append(r)
            sources.update(evidence)
            if i % 50 == 0 or i == 987:
                print(f'inventory {i}/987', flush=True)
    save('stack-inventory.parquet', rows)
    save('runtime-diagnostic-inventory.parquet', batch_rows)
    write_json(OUT/'named-evidence-candidates.json', filenames)
    write_json(OUT/'inventory-source-hashes.json', sources)
    obs = []
    for protocol in ['SHADOWSOCKS', 'VLESS', 'HYSTERIA2']:
        for feature, level, state in [('unique_tcp_bytes', 'P', 'available_for_indexed_tcp'),
                                      ('exact_protocol_overhead_correction', 'K', 'unavailable_stack_unknown'),
                                      ('exact_encryption_record_or_stream_targets', 'T', 'no_verified_evidence')]:
            obs.append({'protocol': protocol, 'feature': feature, 'permission': level, 'state': state})
    save('observability-matrix.parquet', obs)
    summary = {'sessions': len(rows), 'mihomo_commits': dict(Counter(r['mihomo_commit'] for r in rows)),
               'runtime_sections': len(batch_rows), 'hash_only_sections': sum(r['hash_only'] for r in batch_rows),
               'named_candidates': filenames, 'stream_candidate_events': sum(r['stream_frame_candidate_events'] for r in rows)}
    write_json(OUT/'stack-summary.json', summary)
    markdown('stack-and-observability-audit.md', '# N0–N2 协议栈与可观测性审计\n\n'
             f'已扫描 {len(rows)} 次选定会话的 manifest、上下文、proxy-info、trace 与保留的 trace journal。运行诊断共有 {len(batch_rows)} 个 section，'
             f'其中 {sum(r["hash_only"] for r in batch_rows)} 个仅为哈希。\n\n'
             'Mihomo 构建身份：'+json.dumps(summary['mihomo_commits'])+'。精确 commit 能标识构建，但不能恢复 cipher/Vision/mux/obfs 的运行配置。\n\n'
             f'按命名搜索的配置/密钥/qlog 候选数：{len(filenames)}；含 stream ID 与 offset 的 trace 候选事件：{summary["stream_candidate_events"]}。'
             '这是已扫描产物的可观测性结论，不声称环境中从未存在相关资料。UDP 收发事件的 seq/len 不是 SS 分块或 QUIC STREAM 字段。\n\n'
             '当前只确认协议标签，精确 SS/VLESS 封装适配器暂停。空 network 不推断基础 TCP；不扣固定百分比或 34 字节/包。'
             '继续可独立验证的区间字节去重与字节方向段。\n\n'
             '需要补充：采集时每个实际节点的脱敏 cipher/network/TLS/REALITY/flow/Vision/mux/obfs/plugin 配置，或可核对哈希的历史快照。'
             '不需要密码、UUID、私钥，也不要求重新采集。')
    print(json.dumps(summary), flush=True)


if __name__ == '__main__':
    main()
