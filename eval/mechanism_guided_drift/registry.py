"""Execute P1 only: historical stack registration, no fitting and no PCAP reads."""
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
import json
import platform
import sys

import pandas as pd

from common import ROOT, RAW, OLD, LATEST, SOURCE, OUT, DOC
from common import read_json, write_json, file_hash, digest, long_path, relative_child, git, safe_hash
from safe_profile import FIELDS, PROTOCOLS, extract_layer, public_schema, normalize_protocol
from mechanisms import make_rules, qualify_rule

EXPECTED = {
    'shadowsocks': ['cipher', 'plugin', 'smux_enabled', 'udp', 'udp_over_tcp'],
    'vless': ['transport', 'tls', 'reality', 'vision', 'flow', 'smux_enabled', 'packet_encoding'],
    'vmess': ['cipher', 'alter_id', 'transport', 'tls', 'reality', 'smux_enabled', 'global_padding', 'authenticated_length'],
    'trojan': ['transport', 'tls', 'reality', 'smux_enabled', 'secondary_shadowsocks'],
    'anytls': ['transport', 'tls', 'idle_session_check_interval_seconds', 'idle_session_timeout_seconds',
               'minimum_idle_sessions', 'disable_reuse', 'padding_scheme_sha256'],
    'hysteria2': ['transport', 'tls', 'obfs', 'port_hopping', 'hop_interval_seconds', 'udp_mtu',
                  'up_mbps', 'down_mbps', 'congestion'],
}


def selected_build(snapshot):
    build = snapshot.get('build', {})
    return {'client_commit': safe_hash(build.get('vcs_revision'), 40),
            'executable_sha256': safe_hash(build.get('executable_sha256')),
            'dependency_lock_sha256': safe_hash(build.get('dependency_lock_sha256')),
            'source_tree_sha256': safe_hash(build.get('source_tree_sha256')),
            'vcs_modified': build.get('vcs_modified') if type(build.get('vcs_modified')) is bool else None,
            'identity_verified_self': build.get('executable_hash_status') == 'verified_self'}


def source_validate():
    original = read_json(SOURCE / 'manifest.json')
    supplement = read_json(OUT / 'source-supplement/manifest.json')
    assert not original['errors'] and original['repository_unchanged']
    sources = original['sources'] + supplement['sources']
    for record in sources:
        assert file_hash(ROOT / record['local_path']) == record['sha256'], 'source_hash_mismatch'
    assert supplement['commit'] == original['captured_build_commit']
    return original, supplement, sources


def snapshot_fields(snapshot):
    evidence = snapshot.get('evidence', {})
    result, rejected = {}, Counter()
    for layer in ['configured', 'effective']:
        result[layer], counts = extract_layer(evidence.get(layer, {}))
        rejected.update(counts)
    for layer in ['negotiated', 'observed']:
        node = evidence.get(layer, {}).get('status', {})
        state = node.get('state')
        result[layer + '_state'] = state if state in {'known', 'unknown', 'not_applicable', 'unsupported'} else 'unknown'
    return result, rejected


def normalize_derived(protocol, fields):
    """Keep raw option snapshots intact; return explicit source-derived annotations."""
    result = []
    if protocol == 'anytls':
        for name in ['idle_session_check_interval_seconds', 'idle_session_timeout_seconds']:
            item = fields.get(name, {})
            if item.get('state') == 'known':
                result.append({'field': 'library_' + name, 'adapter_option_value': item['value'],
                    'source_derived_value': 30 if item['value'] <= 5 else item['value'],
                    'status': 'partial', 'evidence_kind': 'source_derived_constructor_normalization',
                    'runtime_timer_observed': False, 'rule_id': 'anytls-idle-normalization'})
    if protocol == 'vmess' and fields.get('cipher', {}).get('value') == 'auto':
        result.append({'field': 'resolved_security', 'value': None, 'status': 'insufficient',
            'reason_code': 'auto_security_selection_not_recorded', 'rule_id': 'vmess-chunk'})
    return result


def cache_agrees(fields, deployment):
    if not deployment:
        return False
    for layer in ['configured', 'effective']:
        for field, value in fields[layer].items():
            cached = deployment.get('evidence', {}).get(layer, {}).get(field)
            if cached is None:
                continue
            if cached.get('state') != value['state']:
                return False
            if value['state'] == 'known' and cached.get('value') != value['value']:
                return False
    return True


def historical_registry():
    report = ROOT / 'docs/protocol-normalization/targeted-diagnostics-20260923/report.md'
    reference = {'path': report.relative_to(ROOT).as_posix(), 'sha256': file_hash(report),
                 'evidence_kind': 'documented_collector_confirmation', 'confirmation_date': '2026-09-23'}
    values = {
        'shadowsocks': {'plugin': 'none', 'smux_enabled': False, 'udp': True, 'udp_over_tcp': False},
        'vless': {'transport': 'tcp', 'tls': True, 'reality': True, 'vision': True,
                  'flow': 'xtls-rprx-vision', 'smux_enabled': False},
        'hysteria2': {'transport': 'quic', 'obfs': 'none', 'port_hopping': True},
    }
    records = []
    for scope in ['0914-broad', '0914-repeat', '0916']:
        for protocol, fields in values.items():
            records.append({'dataset_scope': scope, 'protocol': protocol, 'status': 'partial',
                'client_commit': None, 'evidence': reference,
                'fields': {key: {'value': value, 'status': 'partial',
                    'reason_code': 'collector_confirmation_not_per_session_snapshot'} for key, value in fields.items()},
                'cipher': {'value': None, 'status': 'insufficient'} if protocol == 'shadowsocks' else None,
                'extend_applicability': False, 'training_use': False})
    return records


def base_files(source_records):
    names = [
        'docs/mihomo-protocol-drift-analysis-20261003.md', 'docs/proxy-drift-model-construction.md',
        'docs/business-protocol-eval-extend/formal-results.md',
        'plan/mihomo-mechanism-guided-drift-three-step-plan-20261003.md',
        'eval/business_protocol_eval/generation.py', 'eval/business_protocol_eval/common.py',
        'eval/hy2_carrier_calibration/window_model.py',
        'outputs/extend-calibration-20260930/run-01/sessions.parquet',
        'outputs/extend-calibration-20260930/run-01/deployment-registry.json',
        'outputs/extend-calibration-20260930/run-01/metadata-hashes.json',
        'outputs/extend-calibration-20260930/run-01/extraction-03/identity-source-evidence/qualification.json',
        'outputs/business-protocol-eval-extend/run-01/cohort.parquet',
        'outputs/business-protocol-eval-extend/run-01/global-folds.parquet',
        'outputs/business-protocol-eval-extend/run-01/contract.json',
        'outputs/business-protocol-eval-extend/run-01/prediction-seal.json',
        'outputs/business-protocol-eval-extend/run-01/predictions.parquet',
        'outputs/business-protocol-eval-extend/run-01/primary-contrasts.parquet',
        'outputs/mihomo-protocol-audit-20261003/manifest.json',
        'outputs/mechanism-guided-drift-20261003/registry/source-supplement/manifest.json',
    ]
    names += [item['local_path'] for item in source_records]
    return {name: file_hash(ROOT / name) for name in sorted(set(names))}


def report(profiles, audit, historical):
    DOC.mkdir(parents=True, exist_ok=True)
    texts = {
        'shadowsocks': 'AES-256-GCM；无 plugin/smux；UDP enabled；UOT false',
        'vless': 'TCP＋TLS；REALITY false；Vision false；flow none；XUDP；smux false',
        'vmess': 'WS＋TLS；cipher auto；global padding false；authenticated length false；smux false',
        'trojan': 'TCP＋TLS；REALITY false；附加 SS false；smux false',
        'anytls': 'TLS carrier；idle 选项0/0；min idle0；内部默认规范化30s',
        'hysteria2': 'QUIC＋Salamander；hopping false；UDP MTU option1197',
    }
    table = ['| 协议 | 选中会话证据 | 主分类成员 | 配置结论 |', '|---|---:|---:|---|']
    for item in sorted(profiles, key=lambda v: v['protocol']):
        table.append(f"| {item['protocol']} | {item['selected_sessions']} | {item['main_cohort_sessions']} | {texts[item['protocol']]} |")
    body = '\n'.join(table)
    missing = ', '.join(f"{k} {v}" for k, v in audit['missing_selected_by_protocol'].items()) or '无'
    coverage = (f"已登记 Extend 选中会话 {audit['selected_sessions']} 次，全部有可读协议栈证据。"
                if not audit['selected_missing_semantics'] else
                f"已登记选中会话 {audit['selected_sessions']} 次，{audit['selected_with_semantics']} 次有证据，缺失分布为 {missing}。")
    document = f'''# 六协议配置证据与第一阶段结果

日期：2026-10-04。本报告完成三步计划的第一步，不包含机制回归、生成采样或业务分类训练。核心结论是：Extend 已保存逐会话协议栈快照，不能把旧三协议队列的配置套用到它。字段确认指客户端适配器选项层，非完整协商或远端内部状态确认。

## 配置发现与历史口径修正

{body}

上表来源为选中会话的 `raw/proxy-semantics.json`，与已有部署缓存逐字段核对。SS 的 cipher 在 Extend 不是未知；VLESS 也不是历史 REALITY/Vision 部署；Hy2 则启用了 Salamander 而没有开启端口跳跃。上述差异是跨数据队列的部署变化，不是同一部署内互相冲突的证据。

源码收集报告中对旧 SS cipher、旧 VLESS Vision 与旧 Hy2 hopping 的讨论依然适用于相应历史队列；不能用于 Extend 的机制规则选择。旧报告没有发现名为 sanitized 配置的文件，并不代表不存在原生逐会话栈记录。

## 覆盖与一致性

{coverage} 此外清点到 {audit['all_semantics_files']} 个协议栈文件，另外{audit['unselected_semantics_files']}个未选中文件只列索引，不补进旧主队列。

最新五部署 W 主队列 {audit['main_cohort_sessions']} 次访问全部获得原始记录核验，每部署120次；成员、折与旧分类结果未改变。选中会话与主队列是不同范围，不能把前者数量写成模型训练量。全文件计数也不代表同等数量的独立选中访问。

本轮核对了 start/end 白名单字段、协议、客户端构建、会话身份和既有部署缓存。工程审计{'通过' if audit['engineering_passed'] else '未通过'}。{audit['selected_without_cached_deployment']}个非主队列会话没有旧部署缓存，但有本次核验的原始栈记录；保留为原始来源登记，不冒称旧缓存核对通过。详细统计及逐会话缺失/冲突见本地注册表。未知也有登记，不因缺少字段而删会话。

首次工程运行把源码协议名ss与实验台账shadowsocks误判为不一致，也把两条没有旧缓存的非主会话误判为缓存冲突。已用明确名称映射及“缓存不可用”状态修复，并增加名称映射测试；没有改数据、访问资格或阶段门。修复记录见本目录engineering-repair.md。

## effective 字段的可解释边界

固定采集提交的 `adapter/semantics.go` 从配置映射及解析后的 option 构造 configured/effective 字段；`component/proxysemantics/contract.go` 明确将 negotiated/observed 层初始化为 unknown。记录来自采集进程，但不等于每个连接已经附上协商或内部 write 证据。

AnyTLS 的 effective idle0是 option 数值；下游 `session.NewClient` 会将小于等于5秒的值规范化为30秒。本轮保留原值，另写 source-derived 30秒，不能称连接定时器实测。VMess 的 auto 尚未记录最终安全算法，alterId 也未进入此版本栈 schema；不能给出精确 AEAD 请求开销。AnyTLS 动态 padding scheme、Hy2 协商拥塞/运行带宽与远端服务端版本仍不确定。

全部 profile 整体仍标为部分确认，因为客户端 option 确认不等于网络全过程参数完整。未保存实际地址长度、内部 chunk/write 数量、每次 TLS/WS record 数量或 QUIC 明文，不能发布精确访问 K。

## 源码规则资格

- SS 可注册 AES-256-GCM 的32字节 salt与每块34字节局部规则；实际块数未观测，不能用包数替代。
- Extend VLESS 注册 TCP/TLS 与请求封装；Vision padding 分支明确不适用，下一步不做 Vision 阶段切点诊断。
- VMess 必须包含 WS/TLS 外层；global padding/authenticated length 分支不启用，auto及alterId缺口保留。
- Trojan 注册一次性请求头与外层 TLS，目标地址不进入主模型。
- AnyTLS 注册帧、物理 session复用与初始 scheme范围；动态更新和载体阶段尚需现有日志资格检查。
- Hy2 注册 QUIC共享载体与Salamander每外层datagram的8字节salt；不再套用旧“无混淆＋跳跃”描述，且不解除现有分类资格限制。

每条规则在 `mechanism-contract.json` 绑定固定源码文件、行号、哈希、调用单位和配置前提。局部规则精确不等于捕获总开销精确。人工输入验证属于下一阶段，未在本轮提前执行。

## 输出与复现

Python入口为 [registry.py](../../eval/mechanism_guided_drift/registry.py)，脱敏测试为 [test_safe_profile.py](../../eval/mechanism_guided_drift/test_safe_profile.py)。先运行固定补充源码收集，再运行注册与测试：

```powershell
conda run -n Pytorch312 python eval/mechanism_guided_drift/collect_instrumentation.py
conda run -n Pytorch312 python -m unittest discover -s eval/mechanism_guided_drift -p "test_*.py"
conda run -n Pytorch312 python eval/mechanism_guided_drift/registry.py
```

本地结果在 `outputs/mechanism-guided-drift-20261003/registry/`：baseline-manifest、evidence-inventory、profile_schema、implementation-registry、protocol-profile-registry、session-profile-ledger、mechanism-contract、registry-audit。原始配置/endpoint/凭据未复制，原始PCAP未打开；旧输入哈希复核通过，未修改冻结实验。

## 第一确认节点

建议接受上述 Extend 队列专属配置表进入 P2，并修正诊断范围：SS重点验证经典AEAD负载关系；VLESS改为非Vision TCP/TLS；VMess明确WS/TLS及未解析安全模式；AnyTLS区分option与库状态；Hy2按Salamander共享载体只做测量诊断。缺失参数保持未知，不补默认运行状态、不加入分类器身份特征。

本轮在G1停下。确认后才能执行机制诊断；新中心候选和CUDA正式训练仍须等待G2。
'''
    (DOC / 'stage-1-registry-report.md').write_text(document, encoding='utf-8')
    gap_rows = ['# 配置缺口与适用范围', '', '日期：2026-10-04。未知字段不代表禁用，源码默认不代表实际协商。', '']
    for item in profiles:
        gap_rows += ['## ' + item['protocol'], '',
                    '主队列已登记 option；整体为部分确认。缺失字段：' + ', '.join(item['missing_required_fields']) + '。', '',
                    '运行层未知：negotiated/observed、内部计数与远端具体版本。', '']
    gap_rows += ['## 历史队列', '', '0914/0916依据2026-09-23采集者追溯确认单列；SS cipher仍未知。旧配置不得传播至Extend。',
                 '', '本轮未访问秘密原始节点对象，不要求提供endpoint或凭据。']
    (DOC / 'configuration-gaps.md').write_text('\n'.join(gap_rows) + '\n', encoding='utf-8')


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    original, supplement, sources = source_validate()
    before = base_files(sources)
    sessions = pd.read_parquet(OLD / 'sessions.parquet')
    cohort = pd.read_parquet(LATEST / 'cohort.parquet')
    assert sessions.session_id.is_unique and cohort.session_id.is_unique
    assert len(cohort) == 600 and set(cohort.protocol) == PROTOCOLS - {'hysteria2'}
    assert set(cohort.session_id) <= set(sessions.session_id)
    main_ids = set(cohort.session_id)
    cached = {row['deployment_id']: row for row in read_json(OLD / 'deployment-registry.json')}
    profiles, ledger, field_rows, inventory = {}, [], [], []
    counts, missing, conflict, rejected = Counter(), Counter(), Counter(), Counter()
    raw_root = long_path(RAW)
    all_semantics = sorted(raw_root.rglob('proxy-semantics.json'))
    all_hashes = {}
    for filename in all_semantics:
        relative = filename.relative_to(raw_root).as_posix()
        h = file_hash(filename)
        all_hashes[relative] = h
        inventory.append({'path': 'Datasets/extend/' + relative, 'kind': 'capture_protocol_snapshot',
            'sha256': h, 'bytes': filename.stat().st_size})
    for dataset in sorted(raw_root.iterdir()):
        if not dataset.is_dir():
            continue
        for pipeline in sorted(dataset.iterdir()):
            if not pipeline.is_dir() or '__pipeline-' not in pipeline.name:
                continue
            files = [pipeline / 'pipeline-manifest.json'] + sorted(pipeline.glob('candidate-*-runtime-diagnostic.json'))
            for filename in files:
                if filename.is_file():
                    inventory.append({'path': 'Datasets/extend/' + filename.relative_to(raw_root).as_posix(),
                        'kind': 'pipeline_or_runtime_metadata_inventory_only', 'sha256': file_hash(filename),
                        'bytes': filename.stat().st_size, 'proxy_definition_body_exported': False})
    for row in sessions.sort_values('session_id').itertuples(index=False):
        counts[row.protocol] += 1
        manifest_path = relative_child(RAW, row.manifest_relative)
        sem_path = manifest_path.parent / 'raw/proxy-semantics.json'
        member = {'session_id': row.session_id, 'dataset_id': row.dataset, 'dataset_role': row.dataset_role,
            'protocol': row.protocol, 'main_cohort': row.session_id in main_ids, 'profile_id': None}
        if not sem_path.is_file():
            missing[row.protocol] += 1
            member.update({'status': 'insufficient', 'reason_code': 'capture_protocol_snapshot_missing'})
            ledger.append(member)
            continue
        document = read_json(sem_path)
        manifest = read_json(manifest_path)
        assert manifest['session_id'] == row.session_id
        inventory.append({'path': 'Datasets/extend/' + str(row.manifest_relative).replace('\\', '/'),
                          'kind': 'selected_session_manifest', 'sha256': file_hash(manifest_path),
                          'bytes': manifest_path.stat().st_size})
        start = document.get('start', {})
        end = document.get('end', {})
        fields, reject = snapshot_fields(start)
        end_fields, end_reject = snapshot_fields(end)
        rejected.update(reject)
        rejected.update(end_reject)
        build = selected_build(start)
        issues = []
        if normalize_protocol(start.get('protocol')) != row.protocol or normalize_protocol(end.get('protocol')) != row.protocol:
            issues.append('protocol_mismatch')
        if fields != end_fields or build != selected_build(end):
            issues.append('snapshot_changed')
        deployment = cached.get(row.deployment_id)
        if deployment is not None and not cache_agrees(fields, deployment):
            issues.append('cached_deployment_mismatch')
        if build['client_commit'] != original['captured_build_commit'] or not build['identity_verified_self']:
            issues.append('captured_build_not_verified')
        for reason in issues:
            conflict[reason] += 1
        key = digest({'protocol': row.protocol, 'fields': fields, 'build': build})
        if key not in profiles:
            profiles[key] = {'profile_id': key, 'protocol': row.protocol, 'fields': fields,
                'build': build, 'status': 'partial', 'status_reason': 'adapter_options_not_connection_negotiation',
                'datasets': [], 'selected_sessions': 0, 'main_cohort_sessions': 0, 'evidence': [],
                'missing_required_fields': [f for f in EXPECTED[row.protocol] if f not in fields['effective']],
                'derived_annotations': normalize_derived(row.protocol, fields['effective']),
                'legacy_deployment_ids': []}
        profile = profiles[key]
        profile['selected_sessions'] += 1
        profile['main_cohort_sessions'] += int(member['main_cohort'])
        if row.dataset not in profile['datasets']:
            profile['datasets'].append(row.dataset)
        if safe_hash(row.deployment_id) and row.deployment_id not in profile['legacy_deployment_ids']:
            profile['legacy_deployment_ids'].append(row.deployment_id)
        relative = sem_path.relative_to(raw_root).as_posix()
        evidence_ref = {'path': 'Datasets/extend/' + relative, 'sha256': all_hashes[relative],
            'session_id': row.session_id, 'evidence_kind': 'capture_adapter_option_snapshot',
            'scope': row.dataset, 'schema_version': start.get('schema_version'),
            'coverage': 'partial', 'start_end_equal': not issues,
            'collected_at': document.get('started_at') if isinstance(document.get('started_at'), str) and
                __import__('re').fullmatch(r'[0-9T:.Z+\-]+', document.get('started_at')) else None}
        profile['evidence'].append(evidence_ref)
        member.update({'profile_id': key, 'status': 'conflicting' if issues else 'partial',
                       'issue_codes': issues, 'evidence_sha256': all_hashes[relative],
                       'cached_deployment_evidence': 'verified' if deployment is not None and not issues else
                           'unavailable' if deployment is None else 'conflicting'})
        ledger.append(member)
    rules = make_rules()
    values = sorted(profiles.values(), key=lambda x: (x['protocol'], x['profile_id']))
    # This report has dataset-specific findings; fail rather than publish those findings for changed data.
    assert len(values) == 6 and {p['protocol'] for p in values} == PROTOCOLS
    facts = {'shadowsocks': {'cipher': 'aes-256-gcm', 'plugin': 'none', 'smux_enabled': False, 'udp_over_tcp': False},
             'vless': {'transport': 'tcp', 'tls': True, 'reality': False, 'vision': False, 'flow': 'none'},
             'vmess': {'cipher': 'auto', 'transport': 'ws', 'tls': True, 'global_padding': False, 'authenticated_length': False},
             'trojan': {'transport': 'tcp', 'tls': True, 'reality': False, 'secondary_shadowsocks': False},
             'anytls': {'transport': 'tls', 'idle_session_check_interval_seconds': 0, 'idle_session_timeout_seconds': 0},
             'hysteria2': {'transport': 'quic', 'obfs': 'salamander', 'port_hopping': False, 'udp_mtu': 1197}}
    for item in values:
        for field, value in facts[item['protocol']].items():
            assert item['fields']['effective'][field]['state'] == 'known'
            assert item['fields']['effective'][field]['value'] == value, 'changed_dataset_profile_requires_new_report'
    for item in values:
        item['rule_qualification'] = [{**{'rule_id': rule['rule_id']},
            **qualify_rule(rule, item['fields']['effective'])} for rule in rules if rule['protocol'] == item['protocol']]
        for layer in ['configured', 'effective']:
            for field, node in sorted(item['fields'][layer].items()):
                field_rows.append({'profile_id': item['profile_id'], 'protocol': item['protocol'],
                    'dataset_ids': sorted(item['datasets']), 'client_commit': item['build']['client_commit'],
                    'field_name': field, 'layer': layer, **node,
                    'evidence_kind': 'capture_adapter_option_snapshot',
                    'evidence_references': [r['sha256'] for r in item['evidence']]})
    main_ledger = [r for r in ledger if r['main_cohort']]
    assert len(main_ledger) == 600
    before_after = {key: file_hash(ROOT / key) == value for key, value in before.items()}
    raw_unchanged = all(file_hash(ROOT / record['path']) == record['sha256'] for record in inventory)
    passed = (not conflict and rejected['invalid_typed_values'] == 0 and
              all(before_after.values()) and raw_unchanged and
              all(row['profile_id'] and row['status'] != 'conflicting' for row in main_ledger))
    audit = {'stage': 'P1', 'execution_date': '2026-10-04', 'engineering_passed': passed,
        'selected_sessions': len(sessions), 'selected_counts_by_protocol': dict(counts),
        'selected_with_semantics': sum(item['selected_sessions'] for item in values),
        'selected_missing_semantics': sum(missing.values()), 'missing_selected_by_protocol': dict(missing),
        'selected_without_cached_deployment': sum(row.get('cached_deployment_evidence') == 'unavailable' for row in ledger),
        'main_cached_deployment_evidence_complete': all(row.get('cached_deployment_evidence') == 'verified' for row in main_ledger),
        'main_cohort_sessions': len(main_ledger), 'main_counts_by_protocol': dict(Counter(r['protocol'] for r in main_ledger)),
        'main_semantics_coverage_complete': all(row['profile_id'] for row in main_ledger),
        'all_semantics_files': len(all_semantics), 'profile_count': len(values),
        'unselected_semantics_files': len(all_semantics) - sum(item['selected_sessions'] for item in values),
        'source_files_hash_verified': len(sources), 'conflicts': dict(conflict),
        'sanitization_rejections': dict(rejected), 'frozen_inputs_unchanged': all(before_after.values()),
        'raw_semantics_unchanged': raw_unchanged, 'capture_payload_files_opened': 0,
        'classification_performed': False, 'regression_performed': False, 'generator_sampling_performed': False,
        'G1_accepted': False, 'next_stage_authorized': False}
    history = historical_registry()
    write_json(OUT / 'baseline-manifest.json', {'git_commit_after_sync': git('rev-parse', 'HEAD'),
        'date': '2026-10-04', 'sha256': before, 'verification': before_after,
        'old_results_modified': False, 'plan_is_local_only': True})
    write_json(OUT / 'evidence-inventory.json', {'records': inventory, 'capture_payload_reads': False,
        'unselected_semantics_not_added_to_cohort': True})
    write_json(OUT / 'profile_schema.json', public_schema())
    write_json(OUT / 'protocol-profile-registry.json', {'profiles': values, 'historical_scopes': history})
    write_json(OUT / 'protocol-field-registry.json', field_rows)
    write_json(OUT / 'session-profile-ledger.json', ledger)
    write_json(OUT / 'implementation-registry.json', {'current_meta_commit': original['meta_commit'],
        'captured_client_commit': original['captured_build_commit'], 'dependencies': original['dependencies'],
        'profile_builds': [{'profile_id': p['profile_id'], 'protocol': p['protocol'], **p['build']} for p in values],
        'remote_server_commit': None, 'historical_builds_not_imputed': True,
        'instrumentation_source_manifest_sha256': file_hash(OUT / 'source-supplement/manifest.json')})
    write_json(OUT / 'mechanism-contract.json', {'rules': rules,
        'distinctions': ['source_constant', 'adapter_option', 'source_derived_library_parameter',
                         'negotiated_state', 'observed_internal_count', 'capture_proxy', 'training_estimate'],
        'classification_identity_input_allowed': False})
    import torch
    write_json(OUT / 'environment.json', {'python': platform.python_version(), 'executable': sys.executable,
        'torch': torch.__version__, 'cuda_available': torch.cuda.is_available(),
        'cuda_version': torch.version.cuda,
        'gpu': torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
        'stage_1_device': 'cpu_metadata_only', 'future_training_requires_cuda': True})
    write_json(OUT / 'registry-audit.json', audit)
    report(values, audit, history)
    print(json.dumps(audit, ensure_ascii=False, indent=2))
    if not passed:
        raise SystemExit('P1 qualification failed; inspect sanitized audit')


if __name__ == '__main__':
    main()
