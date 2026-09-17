"""Capture-execution diagnostics and a sensitivity addendum; no causal claims."""
from collections import Counter, defaultdict
from datetime import datetime
import json
from pathlib import Path

import numpy as np

from ..reproducibility.preflight import write_json, write_table
from .prepare import load_config, table, digest, guarded


def distribution(values):
    a=np.asarray([v for v in values if v is not None and np.isfinite(v)],dtype=float)
    return {'n':len(a),'median':float(np.median(a)) if len(a) else None,
            'q25':float(np.quantile(a,.25)) if len(a) else None,
            'q75':float(np.quantile(a,.75)) if len(a) else None}


def main():
    cfg=load_config('configs/paired-information-0914.yaml'); root=Path(cfg['output_root'])
    out=root/'execution-diagnostics'; out.mkdir(exist_ok=False)
    members=table(root/'registry.parquet'); labels={r['session_id']:r for r in table(root/'labels.parquet')}
    exclusions={r['session_id']:r for r in table(root/'exclusions.parquet')}
    sides={r['session_id']:r for r in table(root/'side-summaries.parquet') if r['selection']=='observed'}
    sources={}; targets={}
    for batch,dirname in [('broad','sites-64url-repetition-1'),('repeat','sites-detailed-18url-repetition-5')]:
        path=guarded(Path(cfg['raw_root'])/dirname/'pipeline-manifest.json',cfg['raw_root'])
        sources[str(path)]=digest(path)
        value=json.loads(path.read_text(encoding='utf-8'))
        for t in value['targets']: targets[(batch,t['index'])]=t
    records=[]
    for r in members:
        if not r['is_final']: continue
        path=guarded(Path(r['session_path'])/'analysis/summary.json',cfg['raw_root'])
        sources[str(path)]=digest(path); summary=json.loads(path.read_text(encoding='utf-8'))
        if summary['session_id']!=r['session_id']: raise ValueError('summary identity')
        target=targets[(r['batch'],r['target_index'])]
        if target['url']!=r['target_url']: raise ValueError('target identity')
        activity=summary.get('activity_outcome') or {}; nav=summary.get('navigation_outcome') or {}
        label=labels[r['session_id']]; side=sides.get(r['session_id'])
        duration=(datetime.fromisoformat(r['completed_at'])-datetime.fromisoformat(r['started_at'])).total_seconds()
        record={k:r[k] for k in ['session_id','batch','target_url','target_domain','protocol','repetition',
                                  'candidate_position','run_ordinal','cache_mode','profile_fingerprint',
                                  'traffictracer_version','traffictracer_commit','started_at']}
        record.update(configured_duration_seconds=target.get('duration_seconds'),
            configured_wait_load_timeout=target.get('wait_load_timeout'),page_type=target.get('page_type'),
            run_elapsed_seconds=duration, activity_state=activity.get('state'),activity_kind=activity.get('kind'),
            navigation_state=nav.get('state'),navigation_final_status=nav.get('final_status'),
            effective_label_id=label['effective_label_id'], evidence_granularity=label['evidence_granularity'],
            primary_content_seconds=label['primary_content_seconds'],playback_goal_met=label['playback_goal_met'],
            included_primary=exclusions.get(r['session_id'],{}).get('included',False),
            primary_exclusion_reasons=exclusions.get(r['session_id'],{}).get('reasons',['broad_not_repeat_primary']))
        for name in ['coverage','packet_coverage','resource_health','network_outcome','quality']:
            record[name+'_json']=json.dumps(summary.get(name),ensure_ascii=False)
        for name in ['pre','post']:
            stats=side[name] if side else None
            record[name+'_observed_span_seconds']=((stats['last_ns']-stats['first_ns'])/1e9) if stats else None
            record[name+'_entity_count']=stats['entity_count'] if stats else None
        records.append(record)
    write_table(out/'session-execution.parquet',records)
    paired=defaultdict(dict)
    for r in records:
        if r['included_primary']: paired[(r['target_url'],r['repetition'])][r['protocol']]=r
    pairs=[]
    for (url,repetition),p in paired.items():
        a,b=p['SHADOWSOCKS'],p['VLESS']
        pairs.append({'target_url':url,'repetition':repetition,
            'start_gap_seconds':abs((datetime.fromisoformat(a['started_at'])-datetime.fromisoformat(b['started_at'])).total_seconds()),
            'configured_duration_equal':a['configured_duration_seconds']==b['configured_duration_seconds'],
            'activity_state_equal':a['activity_state']==b['activity_state'],
            'navigation_state_equal':a['navigation_state']==b['navigation_state'],
            'cache_mode_equal':a['cache_mode']==b['cache_mode'],
            'profile_fingerprint_equal':a['profile_fingerprint']==b['profile_fingerprint'],
            'pre_span_difference_vless_minus_ss':b['pre_observed_span_seconds']-a['pre_observed_span_seconds'],
            'run_elapsed_difference_vless_minus_ss':b['run_elapsed_seconds']-a['run_elapsed_seconds']})
    write_table(out/'execution-pairs.parquet',pairs)
    summary={'selected_sessions':len(records),'primary_pairs':len(pairs),
             'start_gap_seconds':distribution([r['start_gap_seconds'] for r in pairs]),
             'pre_span_difference_vless_minus_ss':distribution([r['pre_span_difference_vless_minus_ss'] for r in pairs]),
             'paired_equal_counts':{k:sum(r[k] for r in pairs) for k in ['configured_duration_equal',
                 'activity_state_equal','navigation_state_equal','cache_mode_equal','profile_fingerprint_equal']},
             'versions':dict(Counter(r['traffictracer_version'] for r in records)),
             'cache_modes':dict(Counter(r['cache_mode'] for r in records)),
             'warning':'run_elapsed is session lifecycle time, not packet capture duration; spans cover selected exclusive entities only'}
    write_json(out/'summary.json',summary); write_json(out/'sources.json',sources)
    sensitivity=root/'sensitivity-01'
    checks=json.loads((sensitivity/'validation.json').read_text())
    advantages=table(sensitivity/'pairing-sensitivity.parquet')
    scores=table(sensitivity/'summary.parquet'); recovery=table(sensitivity/'recovery-controls-summary.parquet')
    lines=['# 0914-only：敏感性与执行因素补充报告','',
        '本轮仍只使用0914，主队列固定14 URL；去首轮为112会话，其余两种包选择仍140会话，不重新按结果选URL。','',
        f'完成{checks["jobs"]}组LOUO任务、检查{checks["pair_map_rows_checked"]}条donor映射；每个敏感性口径20次错配，双向扰动各20次。',
        '这些是主实验100次错配之外的补充。区间是URL级条件性bootstrap，不包括全部训练不确定性。','',
        '## 1. 配对优势并非所有口径都同样明确','',
        '| 口径 | 表示 | 真配对loss | 错配平均loss | 优势[95%区间] |','|---|---|---:|---:|---|']
    for r in advantages:
        lines.append(f'| {r["variant"]} | {r["view"]} | {r["true_loss"]:.4f} | {r["wrong_mean_loss"]:.4f} | '
                     f'{r["advantage"]:.4f} [{r["ci_low"]:.4f}, {r["ci_high"]:.4f}] |')
    lines += ['', 'Δ14在三个补充口径下区间均为正；Δ17在去首轮、排除完整重传时仍为正，但nonempty区间跨零。',
        '应收紧为：配对优势在主要口径及部分敏感性中得到支持，不能宣称所有包选择口径下均已稳健证实。',
        'nonempty不仅删除空包，也改变IAT和部分交互统计的测量对象，不能将差异单独归因于ACK机制。','',
        '## 2. 双向配对扰动','', '| 表示 | 训练配对 | 测试配对 | 平均F1 | 平均loss |', '|---|---|---|---:|---:|']
    groups=defaultdict(list)
    for r in scores:
        if r['variant']=='primary_perturbation': groups[(r['view'],r['train_wrong'],r['test_wrong'])].append(r)
    for (view,tr,te),group in sorted(groups.items()):
        lines.append(f'| {view} | {"错" if tr else "真"} | {"错" if te else "真"} | '
                     f'{np.mean([r["macro_f1"] for r in group]):.4f} | {np.mean([r["log_loss_bits"] for r in group]):.4f} |')
    lines += ['', '训练数据及内层调参遵循训练配对方式，只在外层测试切换配对。此表描述分布扰动，不替代真→真与错→错的主比较。','',
        '## 3. 原强相关剔除和代数对照','',
        f'强相关剔除直接复用原dropped_columns规则；{checks["legacy_strong_drop_predictions_reproduced"]}条预测与0914既有LOUO结果通过数值核对。',
        '这不同于上一阶段仅删除名义家族的ridge_drop_family。','',
        '| 目标 | 模型 | R² | MAE |','|---|---|---:|---:|']
    for r in recovery: lines.append(f'| {r["target"]} | {r["model"]} | {r["r2"]:.4f} | {r["mae"]:.4f} |')
    lines += ['', 'algebra_global仅用测试post及训练侧log(pre)均值；known_deployment版本使用真实部署，是oracle而非未知部署模型。',
        '这些对照用于检查共享代数项的解释力，不产生信息论不可逆证明。','',
        '## 4. 配置一致与执行差异','',
        f'选定会话共{len(records)}，采集版本分布：{summary["versions"]}；缓存模式：{summary["cache_modes"]}。',
        f'主队列70对同URL同轮次的配置时长相同：{summary["paired_equal_counts"]["configured_duration_equal"]}/70。',
        f'同轮访问起点间隔中位数为{summary["start_gap_seconds"]["median"]:.2f}秒；四分位范围 '
        f'[{summary["start_gap_seconds"]["q25"]:.2f}, {summary["start_gap_seconds"]["q75"]:.2f}]秒。',
        '因此同轮编号不能等同同步网络条件。profile指纹差异只能先记录，未解释其生成机制，不能单凭指纹不同断言采集契约不同。',
        'run_elapsed是会话生命周期耗时，不称捕获窗口；pre/post span只覆盖当前选择的exclusive实体，不能代表全部业务。','',
        '## 5. 播放标签与配对可用性分开','',
        'Bilibili资源按用户确认保留有效播放标签。但主队列排除原因涉及route_or_quality、no_usable_exclusive_side及incomplete_grid，不是仅因为没有机器播放证据。',
        'VLESS某些会话自身可用，也会因对应SS会话不可用而被完整配对网格排除。未改写业务标签，也未补采。','',
        '## 6. 当前结论与后续','',
        '保留：当前部署存在入口差异和可识别变换；精确配对相对错配能改善部分表示的预测损失。',
        '收紧：分布Δ的配对优势有包选择依赖；强分类不等于可恢复，更不等于业务蒸馏收益。',
        '后续仍可做有条件的业务内容语义审核及执行因素分层，但不能从这些描述性表确定网络反馈的因果来源。',
        '尚未把本轮全部分析重跑成独立训练复现，也未建立在线未知边界业务模型。']
    (out/'report.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(json.dumps(summary),flush=True)


if __name__=='__main__': main()
