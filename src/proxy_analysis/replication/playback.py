"""Re-audit capture validity without overwriting frozen model experiments."""
from __future__ import annotations
import argparse
from collections import Counter
from pathlib import Path
import pyarrow.parquet as pq
from ..information_validation.data import classify_activity, digest
from ..reproducibility.registry import read_json
from ..reproducibility.preflight import write_json, write_table


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output-root',type=Path,required=True)
    args=p.parse_args(); root=args.output_root
    out=root/'playback-presence-policy';out.mkdir(exist_ok=False)
    policy=Path('configs/playback-validity-20260914.json')
    rows=[]
    for batch in ['broad','repeat']:
        for r in pq.read_table(root/batch/'audit/run_registry.parquet').to_pylist():
            if not r['is_final']:continue
            source=Path(r['session_path'])/'analysis/summary.json'
            summary=read_json(source)
            if summary['session_id']!=r['session_id']:raise ValueError('summary identity mismatch')
            status=classify_activity(summary)
            rows.append({**{k:r[k] for k in ['session_id','target_domain','target_url','protocol','repetition','activity_id']},
                         'batch':batch,**status,'evidence_path':str(source),'evidence_sha256':digest(source)})
    write_table(out/'capture-validity.parquet',rows)
    summary=[]
    for batch,domain in sorted({(r['batch'],r['target_domain']) for r in rows}):
        group=[r for r in rows if (r['batch'],r['target_domain'])==(batch,domain)]
        summary.append({'batch':batch,'domain':domain,'sessions':len(group),
                        'valid_main_content_capture':sum(r['video_capture_valid'] for r in group),
                        'duration_goal_met':sum(r['playback_goal_met'] for r in group),
                        'newly_eligible':sum(r['video_capture_valid'] and not r['playback_goal_met'] for r in group)})
    write_json(out/'summary.json',{'policy':read_json(policy),'policy_sha256':digest(policy),'groups':summary,
        'selected_sessions':len(rows),'newly_eligible':sum(r['newly_eligible'] for r in summary),
        'frozen_feature_and_model_outputs_unchanged':True})
    lines=['# 正片出现即有效：视频采集证据重审','',
        '新口径：观察到正片播放即是有效视频采集，不要求达到20/25秒。目标时长是否达到单独保留。',
        '页面加载、播放器存在或仅有广告不自动证明正片播放；未证实不等于证明没有播放。',
        '本次只更新活动有效性审计，不更改原始质量标记、特征、统计cohort或已冻结的模型实验。','',
        '| 批次 | 域名 | 会话 | 正片已证实 | 达到原时长目标 | 新增有效 |','|---|---|---:|---:|---:|---:|']
    for r in summary:
        if r['domain'] in ['youtube.com','bilibili.com','vimeo.com']:
            lines.append(f"| {r['batch']} | {r['domain']} | {r['sessions']} | {r['valid_main_content_capture']} | {r['duration_goal_met']} | {r['newly_eligible']} |")
    (out/'README.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print('audited',len(rows),'newly eligible',sum(r['newly_eligible'] for r in summary))


if __name__=='__main__':main()
