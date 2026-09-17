"""Independent identity checks, URL-cluster uncertainty and research handoff."""
from collections import defaultdict
from datetime import datetime
import json
import hashlib
from pathlib import Path

import numpy as np
from sklearn.model_selection import GroupKFold

from ..information_validation.experiments import bit_loss
from ..reproducibility.preflight import write_json, write_table
from .prepare import load_config, table, guarded, digest


def audit_map(rows, registry):
    grouped = defaultdict(list)
    for r in rows:
        a, b = registry[r['receiver_session_id']], registry[r['donor_session_id']]
        if (a['target_url'], a['protocol']) != (b['target_url'], b['protocol']):
            raise ValueError('cross-stratum donor')
        if r['target_url'] != a['target_url'] or r['protocol'] != a['protocol']:
            raise ValueError('map metadata mismatch')
        if r['wrong'] and a['session_id'] == b['session_id']: raise ValueError('wrong pair fixed point')
        if not r['wrong'] and a['session_id'] != b['session_id']: raise ValueError('true pair mismatch')
        is_test = r['role'] == 'outer_test'
        if (a['target_url'] == r['outer_fold']) != is_test:
            raise ValueError('outer test leakage')
        grouped[(r['outer_fold'], r['inner_fold'], r['role'])].append(r)
    for (outer, inner, role), group in grouped.items():
        receivers = {r['receiver_session_id'] for r in group}
        if len(receivers) != len(group) or {r['donor_session_id'] for r in group} != receivers:
            raise ValueError('not a within-partition bijection')
        all_train = [r for r in registry.values() if r['target_url'] != outer]
        if role.startswith('inner_'):
            splits = list(GroupKFold(n_splits=3).split(all_train,
                          groups=[r['target_url'] for r in all_train]))
            train_idx, val_idx = splits[inner]
            idx = train_idx if role == 'inner_train' else val_idx
            expected = {all_train[i]['session_id'] for i in idx}
        elif role == 'outer_train': expected = {r['session_id'] for r in all_train}
        else: expected = {r['session_id'] for r in registry.values() if r['target_url'] == outer}
        if receivers != expected: raise ValueError('partition mismatch')
    return len(rows)


def audit_predictions(rows, registry):
    if len(rows) != len(registry) or {r['session_id'] for r in rows} != set(registry):
        raise ValueError('prediction coverage mismatch')
    for r in rows:
        original = registry[r['session_id']]
        if r['fold'] != original['target_url'] or r['truth'] != int(original['protocol']=='VLESS'):
            raise ValueError('prediction fold/truth mismatch')
        if not np.isfinite(r['prob_vless']) or not 0 <= r['prob_vless'] <= 1:
            raise ValueError('invalid probability')


def cluster_interval(values, groups, seed, repetitions=1000):
    units = sorted(set(groups))
    centers = np.asarray([np.mean([v for v,g in zip(values,groups) if g==u]) for u in units])
    rng = np.random.default_rng(seed)
    sampled = centers[rng.integers(0,len(units),size=(repetitions,len(units)))].mean(axis=1)
    return float(centers.mean()), *map(float, np.quantile(sampled,[.025,.975]))


def main():
    cfg = load_config('configs/paired-information-0914.yaml'); root = Path(cfg['output_root'])
    destination = root/'report'; destination.mkdir(exist_ok=False)
    cohort = table(root/'cohort.parquet'); registry = {r['session_id']: r for r in cohort}
    manifest = json.loads((root/'source-manifest.json').read_text())
    for path, expected in manifest['sources'].items():
        if digest(Path(path)) != expected: raise ValueError('source changed')
    for row in cohort:
        guarded(Path(row['session_path'])/'analysis/summary.json', cfg['raw_root'])
    replay = json.loads((root/'true-pair-replay-audit.json').read_text())
    if len(replay)!=len(cohort) or not all(r['passed'] for r in replay): raise ValueError('replay incomplete')
    wrong_dirs = sorted(root.glob('wrong-[0-9][0-9][0-9]'))
    if len(wrong_dirs) != cfg['permutations']: raise ValueError('wrong repetitions incomplete')
    all_dirs = [root/'views', root/'families', *wrong_dirs]
    maps_checked, predictions_checked = 0, 0
    for directory in all_dirs:
        for file in directory.glob('*-pair-map.parquet'):
            maps_checked += audit_map(table(file), registry)
        for file in directory.glob('*-oof.parquet'):
            rows = table(file); audit_predictions(rows, registry); predictions_checked += len(rows)
    for file in (root/'calibration').glob('*-oof.parquet'):
        if 'training-oof' in file.name:
            for row in table(file):
                if row['target_url'] == row['outer_test_url']: raise ValueError('calibration leakage')
        else: audit_predictions(table(file), registry)
    results = []
    for view in ['delta_scalar', 'delta_distribution']:
        true_rows = sorted(table(root/'views'/f'{view}-oof.parquet'), key=lambda r:r['session_id'])
        true_loss = bit_loss([r['truth'] for r in true_rows], [r['prob_vless'] for r in true_rows])
        wrong_losses, seed_summaries, fingerprints = [], [], set()
        for directory in wrong_dirs:
            rows = sorted(table(directory/f'{view}-oof.parquet'), key=lambda r:r['session_id'])
            wrong_losses.append(bit_loss([r['truth'] for r in rows],[r['prob_vless'] for r in rows]))
            seed_summaries.append(next(r for r in table(directory/'summary.parquet') if r['view']==view))
            pairs = table(directory/f'{view}-pair-map.parquet')
            identity = sorted((r['outer_fold'], r['inner_fold'], r['role'],
                               r['receiver_session_id'], r['donor_session_id']) for r in pairs)
            fingerprints.add(hashlib.sha256(json.dumps(identity).encode()).hexdigest())
        wrong_losses = np.asarray(wrong_losses)
        group = [r['target_url'] for r in true_rows]
        mean, lower, upper = cluster_interval(wrong_losses.mean(axis=0)-true_loss, group,
                                             cfg['seed'], cfg['bootstrap_repetitions'])
        results.append({'view': view, 'seeds': len(wrong_dirs), 'true_log_loss_bits': float(true_loss.mean()),
            'wrong_mean_log_loss_bits': float(wrong_losses.mean()),
            'true_pair_loss_advantage': mean, 'url_cluster_ci_low': lower, 'url_cluster_ci_high': upper,
            'wrong_mean_f1': float(np.mean([r['macro_f1'] for r in seed_summaries])),
            'wrong_f1_seed_p025': float(np.quantile([r['macro_f1'] for r in seed_summaries], .025)),
            'wrong_f1_seed_p975': float(np.quantile([r['macro_f1'] for r in seed_summaries], .975)),
            'unique_full_mapping_configurations': len(fingerprints),
            'ci_scope': 'URL cluster, seed-averaged losses, fixed fitted OOF models; not full training uncertainty'})
    write_table(destination/'pairing-value.parquet', results)
    coverage = table(root/'activity-content-coverage.parquet'); union = defaultdict(set)
    for r in coverage:
        if r['label']: union[r['label']].update(r['urls'])
    write_json(destination/'business-feasibility.json', {
        'distinct_urls_upper_bound_not_independent_content': {k:len(v) for k,v in union.items()},
        'video_gate': 'insufficient_contents_for_train_validation_test',
        'bilibili_video_urls': len(union.get('bilibili.com::video_playback',[])),
        'youtube_video_urls': len(union.get('youtube.com::video_playback',[])),
        'all_other_business_tasks': 'require_semantic_workload_and_content_review',
        'teacher_started': False})
    side = {r['session_id']:r for r in table(root/'side-summaries.parquet') if r['selection']=='observed'}
    paired = defaultdict(dict)
    for row in cohort: paired[(row['target_url'],row['repetition'])][row['protocol']] = row
    quality = []
    for (url, repetition), protocols in paired.items():
        ss, vl = protocols['SHADOWSOCKS'], protocols['VLESS']
        values = {}
        for name in ('packet_count','transport_bytes','iat_median_us','length_median','entity_count'):
            values['ss_pre_'+name] = side[ss['session_id']]['pre'][name]
            values['vless_pre_'+name] = side[vl['session_id']]['pre'][name]
        quality.append({'target_url':url, 'repetition':repetition, **values,
            'visit_start_gap_seconds': abs((datetime.fromisoformat(ss['started_at'])-
                                            datetime.fromisoformat(vl['started_at'])).total_seconds()),
            'ss_quality':ss['quality_json'], 'vless_quality':vl['quality_json'],
            'ss_profile':ss['profile_fingerprint'], 'vless_profile':vl['profile_fingerprint']})
    write_table(destination/'pre-quality-pairs.parquet', quality)
    views = table(root/'views/summary.parquet'); families = table(root/'families/summary.parquet')
    calibration = table(root/'calibration/summary.parquet'); recovery = table(root/'recovery/summary.parquet')
    lines = ['# 0914-only 配对信息阶段结果', '',
        '仅0914，主队列14 URL×SS/VLESS×5轮=140会话；Hy2不进入exclusive-page机制模型。',
        '464存储尝试、462选定会话用于来源/标签登记，不是464个训练样本。', '',
        '## 1. 数值回放与验证', '',
        f'140会话×3种selection×18指标={sum(r["comparisons"] for r in replay)}条真实比较全部回放一致。',
        f'检查{maps_checked}条donor映射、{predictions_checked}条分类OOF；均不是独立样本数。',
        '旧批次未参与；原始数据和旧结果未覆盖。', '',
        '## 2. 四视图（未校准）', '', '| 视图 | F1 | log-loss bits |', '|---|---:|---:|']
    for r in views: lines.append(f'| {r["view"]} | {r["macro_f1"]:.4f} | {r["log_loss_bits"]:.6f} |')
    lines += ['', '标量档14/14/28/14维；分布档联合输入包含双侧归一化直方图与曲线，Δ17包含三个距离。',
        '本轮内层GroupKFold以规范URL分组，旧实现以activity_id哈希分组；组排序会改变内层分配与所选C。',
        '所以新pre/post数值不必等于旧模型；旧OOF另在baseline-recheck.parquet原样复核，不能把两次差异当数据变化。',
        '分布联合输入也达到高辨识力，不能只凭Δ优于单侧就断言Δ独有优势。', '',
        '## 3. 真/错配（均未校准，100次错配）', '',
        '| 视图 | 真配对loss | 错配平均loss | 真配对loss优势[URL区间] | 错配平均F1 |',
        '|---|---:|---:|---|---:|']
    for r in results:
        lines.append(f'| {r["view"]} | {r["true_log_loss_bits"]:.4f} | {r["wrong_mean_log_loss_bits"]:.4f} | '
                     f'{r["true_pair_loss_advantage"]:.4f} [{r["url_cluster_ci_low"]:.4f}, {r["url_cluster_ci_high"]:.4f}] | {r["wrong_mean_f1"]:.4f} |')
    lines += ['', '优势定义为错配loss减真实loss。区间为先平均100次错配损失、再按URL成组bootstrap的条件性区间；不包含完整训练不确定性。',
        '同URL/部署跨重复错配，LOUO内外层分别构造；LORO测试层单例不做错配。不把错配胜负频率当p值。', '',
        '## 4. pre家族', '', '| 家族 | F1 | log-loss bits |', '|---|---:|---:|']
    for r in families:
        lines.append(f'| {r["view"]} | {r["macro_f1"]:.4f} | {r["log_loss_bits"]:.4f} |')
    lines += ['', 'IAT单量辨识较强，但不能据此归因于拥塞机制。pre-quality-pairs提供同URL/轮次的工作量、时间间隔及质量比较。', '',
        '## 5. 训练侧嵌套温度校准', '', '| 视图 | F1 | 校准后log-loss bits |', '|---|---:|---:|']
    for r in calibration: lines.append(f'| {r["view"]} | {r["macro_f1"]:.4f} | {r["log_loss_bits"]:.6f} |')
    lines += ['', '每外层训练集再按URL生成嵌套调参的组外概率拟合温度；测试标签不参与。校准可能恶化，全部结果保留。', '',
        '## 6. 恢复性', '', '| 目标 | 模型 | R² | MAE |', '|---|---|---:|---:|']
    for r in recovery:
        lines.append(f'| {r["target"]} | {r["model"]} | {r["r2"]:.4f} | {r["mae"]:.5f} |')
    lines += ['', 'ridge_drop_family仅剔除spec名义家族，与旧实现额外剔除强相关派生量的规则不同，不能冒充原drop对照复现。',
        'known_deployment_mean是已知真实部署的oracle诊断。负R²不证明信息不存在；恢复失败不否定一切配对学习。', '',
        '## 7. 业务及结论边界', '',
        '0914两组去重后Bilibili播放2个URL、YouTube播放1个URL，Vimeo不是播放；不足以做所提播放业务的训练/验证/测试内容隔离。',
        '其他page_load标签需业务语义和内容独立性审核，不自动当搜索或阅读。未启动业务teacher、未补采。',
        '当前证据针对部署C而非业务Y；预测损失增益不是精确条件互信息。保留offline-index-assisted post边界。',
        '未检验未来日期、纯协议因果或跨批次泛化。', '',
        '## 8. 后续尚未完成的扩展', '',
        '去首轮/其他selection的模型敏感性、真训练→错测试扰动、所有辅助代数恢复基线、活动契约逐项语义复核尚未全部执行。',
        '本报告是主队列LOUO阶段成果，不宣称整个原子计划及全部敏感性已完成。']
    (destination/'report.md').write_text('\n'.join(lines)+'\n', encoding='utf-8')
    write_json(destination/'independent-validation.json', {'passed':True, 'primary_sessions':len(cohort),
        'replay_rows':sum(r['comparisons'] for r in replay), 'pair_mapping_rows_checked':maps_checked,
        'classification_prediction_rows_checked':predictions_checked, 'wrong_runs':len(wrong_dirs),
        'scope':'structural lineage, partition membership, OOF coverage; not independent model refitting',
        'old_data_used':False})
    print(json.dumps(results), flush=True)


if __name__ == '__main__': main()
