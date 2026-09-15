"""Apply explicit target-level user evidence without rewriting capture telemetry."""
from __future__ import annotations
import argparse
from collections import defaultdict
from pathlib import Path
import pyarrow.parquet as pq
from ..information_validation.data import digest
from ..reproducibility.registry import read_json
from ..reproducibility.preflight import write_json, write_table


def resolve_activity(row, confirmations):
    matches=[c for c in confirmations if (c['batch'],c['url'])==(row['batch'],row['target_url'])]
    if len(matches)>1:raise ValueError('duplicate target confirmation')
    manual=matches[0] if matches else None
    valid=manual['main_content_playback'] if manual else row['video_capture_valid']
    activity=manual['activity'] if manual else row['verified_activity']
    return {**row, 'automated_video_capture_valid':row['video_capture_valid'],
        'effective_video_capture_valid':valid, 'effective_activity':activity,
        'effective_label_id':row['target_domain']+'::'+activity if activity else None,
        'manual_confirmation_applied':manual is not None,
        'manual_page_kind':manual['page_kind'] if manual else None,
        'effective_evidence_source':'user_target_confirmation' if manual else 'capture_summary',
        'evidence_granularity':'target_level_not_per_session_telemetry' if manual else 'session_summary',
        'evidence_disagreement':manual is not None and row['video_capture_valid'] and not valid}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output-root',type=Path,required=True)
    p.add_argument('--confirmations',type=Path,default=Path('configs/activity-confirmations-20260914.json'))
    args=p.parse_args();root=args.output_root;config=read_json(args.confirmations)
    if Path(config['applies_to_run']).resolve()!=root.resolve():raise ValueError('confirmation scope mismatch')
    source=root/'playback-presence-policy/capture-validity.parquet'
    rows=pq.read_table(source).to_pylist()
    observed={(r['batch'],r['target_url']) for r in rows}
    if any((c['batch'],c['url']) not in observed for c in config['confirmations']):
        raise ValueError('confirmed target missing from run')
    revised=[resolve_activity(r,config['confirmations']) for r in rows]
    out=root/'activity-confirmation-v3';out.mkdir(exist_ok=False)
    write_table(out/'activity-labels.parquet',revised)
    grouped=defaultdict(list)
    for r in revised:grouped[(r['batch'],r['target_domain'],r['target_url'])].append(r)
    summaries=[]
    for (batch,domain,url),group in sorted(grouped.items()):
        summaries.append({'batch':batch,'domain':domain,'url':url,'sessions':len(group),
            'automated_video':sum(r['automated_video_capture_valid'] for r in group),
            'effective_video':sum(r['effective_video_capture_valid'] for r in group),
            'manual_confirmations':sum(r['manual_confirmation_applied'] for r in group),
            'effective_activity':group[0]['effective_activity'],'manual_page_kind':group[0]['manual_page_kind']})
    write_json(out/'summary.json',{'policy':config,'policy_sha256':digest(args.confirmations),'source_sha256':digest(source),
        'groups':summaries,'newly_valid':sum(r['effective_video_capture_valid'] and not r['automated_video_capture_valid'] for r in revised),
        'frozen_telemetry_features_models_unchanged':True})
    lines=['# 人工确认后的活动标签','',
        '采用用户对本次具体目标的确认，不以域名或URL外观自动推断播放。机器原始播放标记保持不变；effective字段供后续业务标签使用。',
        '用户证据粒度为目标级，应用于该目标的选定会话；不冒充逐会话播放器遥测。目标时长、原始采集质量及路由scope不变。','',
        '| 批次 | URL | 会话 | 机器证实播放 | 最终视频标签 | 人工页面类型 |','|---|---|---:|---:|---:|---|']
    for r in summaries:
        if r['domain'] in ['bilibili.com','youtube.com','vimeo.com']:
            lines.append(f"| {r['batch']} | {r['url']} | {r['sessions']} | {r['automated_video']} | {r['effective_video']} | {r['manual_page_kind'] or '—'} |")
    lines += ['', 'Bilibili两个资源URL共享bilibili.com::video_playback标签，但保留不同content/activity_id；首页不据此改成视频。',
        'Vimeo首页与固定视频简介页均不进入video_playback标签；保留homepage/video_description元数据，暂不擅自拆成更细业务Y类别。',
        '此前报告中Bilibili/Vimeo缺少自动播放证据的描述属于历史机器审计；当前业务标签以本附录为准。',
        '原有协议分类与变换统计不使用此次业务标签，故不重算已有模型，也未启动新业务Y训练。']
    (out/'README.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print('sessions',len(rows),'newly valid',sum(r['effective_video_capture_valid'] and not r['automated_video_capture_valid'] for r in revised))


if __name__=='__main__':main()
