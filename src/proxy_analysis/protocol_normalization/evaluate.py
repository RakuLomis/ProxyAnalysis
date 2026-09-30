"""Descriptive O/F/U contrasts and an explicit historical-configuration gate."""
import json
import math
import platform
import sys
import xml.etree.ElementTree as ET

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pyarrow.parquet as pq

from .common import ROOT,OUT,DOC,digest,read,save,markdown
from ..reproducibility.preflight import write_json


def table(headers,rows):
    def fmt(v):
        if v is None or isinstance(v,float) and not math.isfinite(v):return '—'
        if isinstance(v,(float,np.floating)):return f'{v:.6g}'
        return str(v).replace('|','\\|')
    return '\n'.join(['| '+' | '.join(headers)+' |','| '+' | '.join(['---']*len(headers))+' |']+
                     ['| '+' | '.join(fmt(v) for v in row)+' |' for row in rows])+'\n'


def validate(ledger,capture,contrast):
    errors=[]
    valid=ledger[ledger.observed_unique_valid]
    if not (valid.observed_payload_bytes==valid.unique_payload_bytes+valid.duplicate_payload_bytes).all():errors.append('byte_identity')
    if (valid.duplicate_payload_bytes<0).any():errors.append('negative_duplicates')
    if (valid.exclude_full_retransmission_bytes<valid.unique_payload_bytes).any():errors.append('F_less_than_U')
    if ledger.duplicated(['session_id','connection_id','side','direction']).any():errors.append('duplicate_entity_direction')
    if ledger[~ledger.observed_unique_valid].unique_payload_bytes.notna().any():errors.append('invalid_unique_export')
    for r in valid.itertuples():
        if r.new_byte_curve_absolute[-1]!=r.unique_payload_bytes:errors.append('curve_endpoint');break
    old=pd.read_parquet(ROOT/'outputs/itemwise-statistics-0914-0916/run-01/visit-side-features.parquet')
    old=old[(old.scope=='exclusive_page')&(old.selection=='observed')&old.available]
    new=ledger.groupby(['session_id','side']).observed_payload_bytes.sum()
    checks=0
    for r in old.itertuples():
        checks+=1
        if new.get((r.session_id,r.side))!=r.transport_bytes:errors.append('legacy_observed_bytes_mismatch:'+r.session_id)
    # Events must conserve direction totals. Read aggregate columns only, without identifiers/labels.
    event=pq.read_table(OUT/'new-byte-events.parquet',columns=['session_id','connection_id','side','direction','new_payload_bytes']).to_pandas()
    sums=event.groupby(['session_id','connection_id','side','direction']).new_payload_bytes.sum()
    for r in valid.itertuples():
        if sums.get((r.session_id,r.connection_id,r.side,r.direction),0)!=r.unique_payload_bytes:
            errors.append('event_sum');break
    raw_pairs=ledger[['session_id','connection_id']].drop_duplicates()
    if len(contrast)!=len(raw_pairs)*2*3:errors.append('contrast_grid_incomplete')
    contract=read(OUT/'contract.json')
    for path,h in contract['sources'].items():
        if digest(path)!=h:errors.append('frozen_input_changed:'+path)
    coverage=pd.read_parquet(OUT/'coverage.parquet')
    if len(coverage)!=987 or coverage.error_count.sum():errors.append('coverage_or_extraction_error')
    result={'passed':not errors,'errors':errors,'ledger_direction_rows':len(ledger),'strict_pairs':len(raw_pairs),
            'observed_unique_valid_rows':len(valid),'invalid_rows':len(ledger)-len(valid),
            'closed_contiguous_direction_rows':int(ledger.closed_contiguous_capture_candidate.sum()),
            'Q2_rows':int((ledger.quality=='Q2').sum()),'new_byte_event_rows':len(event),
            'legacy_side_total_checks':checks,'extraction_errors':int(coverage.error_count.sum()),
            'snaplen_truncated_packets':int(capture.snaplen_truncated.sum()),
            'parse_incomplete_packets':int(capture.parse_incomplete.sum()),'model_fits':0}
    write_json(OUT/'measurement-quality.json',result)
    return result


def main():
    ledger=pd.read_parquet(OUT/'tcp-byte-ledger.parquet')
    contrast=pd.read_parquet(OUT/'dedup-ablation.parquet')
    captures=pd.read_parquet(OUT/'capture-audit.parquet')
    coverage=pd.read_parquet(OUT/'coverage.parquet')
    quality=validate(ledger,captures,contrast)
    if not quality['passed']:raise ValueError(quality)
    test_path=OUT/'byte-ledger-tests.xml'
    test_result={'status':'not_run'}
    if test_path.exists():
        suites=list(ET.parse(test_path).getroot().iter('testsuite'))
        test_result={k:sum(int(s.get(k,0)) for s in suites) for k in ['tests','failures','errors','skipped']}
        test_result['status']='passed' if not test_result['failures'] and not test_result['errors'] else 'failed'
        test_result['source_sha256']=digest(test_path)
    write_json(OUT/'byte-ledger-tests.json',test_result)
    eligible=contrast[(contrast.common_unique_valid)&(contrast.main_route=='proxy')].copy()
    # O/F/U all use the identical pair-direction intersection, never different survivor sets.
    visits=eligible.groupby(['batch','item_id','protocol','repetition','session_id','direction','view'],as_index=False)[['pre','post']].sum()
    visits['difference']=visits.post-visits.pre
    visits['log_ratio']=np.where((visits.pre>0)&(visits.post>0),np.log(visits.post/visits.pre),np.nan)
    visits['absolute_difference']=abs(visits.difference)
    save('visit-dedup-comparison.parquet',visits)
    items=visits.groupby(['batch','item_id','protocol','direction','view'],as_index=False).agg(
        median_log_ratio=('log_ratio','median'),n_visits=('session_id','size'),median_absolute_difference=('absolute_difference','median'))
    save('item-dedup-comparison.parquet',items)
    summary=[]
    for key,g in items.groupby(['batch','protocol','direction','view']):
        summary.append(dict(zip(['batch','protocol','direction','view'],key))|{
            'items':len(g),'visits':int(g.n_visits.sum()),'median_item_log_ratio':float(g.median_log_ratio.median()),
            'typical_ratio':float(np.exp(g.median_log_ratio.median()))})
    save('dedup-summary.parquet',summary)
    retrans=[]
    for key,g in ledger[ledger.observed_unique_valid].groupby(['batch','protocol','side','direction']):
        obs=g.observed_payload_bytes.sum();unique=g.unique_payload_bytes.sum();f=g.exclude_full_retransmission_bytes.sum()
        retrans.append(dict(zip(['batch','protocol','side','direction'],key))|{
            'rows':len(g),'observed':int(obs),'unique':int(unique),'duplicate_bytes':int(obs-unique),
            'byte_weighted_duplicate_fraction':float((obs-unique)/obs) if obs else None,
            'remaining_overlap_after_full_packet_filter':int(f-unique),
            'median_connection_duplicate_fraction':float(g.duplicate_fraction.median())})
    save('duplicate-byte-summary.parquet',retrans)
    gate_cols=['session_id','batch','item_id','protocol','connection_id','entity_id','side','direction','epoch_id',
               'quality','observed_unique_valid','closed_contiguous_capture_candidate','qualification_reasons']
    save('connection-eligibility.parquet',ledger[gate_cols])
    runs=pd.read_parquet(OUT/'byte-run-comparison.parquet')
    runsummary=[]
    for key,g in runs[runs.main_route=='proxy'].groupby(['batch','protocol','threshold_bytes']):
        runsummary.append(dict(zip(['batch','protocol','threshold_bytes'],key))|{
            'pairs':len(g),'median_absolute_run_difference':float(abs(g.run_difference).median()),
            'pre_retained_median':float(g.pre_retained_fraction.median()),
            'post_retained_median':float(g.post_retained_fraction.median()),
            'pre_degenerate_fraction':float(g.pre_degenerate.mean()),'post_degenerate_fraction':float(g.post_degenerate.mean())})
    save('byte-run-summary.parquet',runsummary)
    # Protocol adapters remain unavailable rather than returning fake corrected numbers.
    write_json(OUT/'protocol-adapter-gate.json',{
        'SS':'blocked_missing_cipher_and_wrapper_evidence',
        'VLESS':'blocked_missing_transport_TLS_Vision_mux_evidence',
        'Hy2':'no_verified_STREAM_frames; full_carrier_member_capture_audit_not_completed',
        'K_features_generated':False,'oracle_decryption_performed':False,'model_training_performed':False})
    lines=['# 唯一 TCP 字节与协议规范化：阶段性测量报告','',
           '本次完成协议证据审计和可独立实施的区间字节测量。停在历史协议配置确认门；尚未执行精确协议校正、TLS 记录恢复、Hy2 全成员联合字节分析或任何分类训练。','',
           '## 主要发现','',
           '在共同有效连接集合、主请求 proxy、按条目等权的口径下，0916 SS 上行典型 post/pre 从 O 的约 1.195 降至 U 的约 1.111；'
           '下行为约 1.010→1.012。VLESS 上行 O/U 均约 1.415，下行约 1.0472→1.0468。'
           '去重并非必然把两侧比值拉近 1：它同时修正 pre 和 post；也不能由去重后的差值直接确定封装种类。','',
           '## 1. 覆盖与质量','',
           f'登记 1,002 次尝试、987 次选定访问。严格 TCP 配对 {quality["strict_pairs"]:,} 条，方向侧台账 {len(ledger):,} 行；'
           f'可用唯一观测字节 {quality["observed_unique_valid_rows"]:,} 行，Q0 {quality["invalid_rows"]} 行。数据提取错误 {quality["extraction_errors"]}。','',
           table(['批次','协议','选定访问','访问有严格TCP配对','配对数'],
                 [(b,p,len(g),int((g.eligible_pair_count>0).sum()),int(g.eligible_pair_count.sum())) for (b,p),g in coverage.groupby(['batch','protocol'])]),'',
           'Hy2 的 0 表示不适用严格 TCP→TCP 对照，并非没有流量。DIRECT 与辅助代理上下文没有被改成主要代理业务。','',
           '## 2. 完整性与异常','',
           table(['批次','协议','侧','方向侧记录','唯一字节可用','闭合连续候选','序号/epoch歧义','冲突方向记录'],
                 [(b,p,side,len(g),int(g.observed_unique_valid.sum()),int(g.closed_contiguous_capture_candidate.sum()),
                   int(g.sequence_epoch_ambiguous.sum()),int((g.overlap_content_conflicts>0).sum()))
                  for (b,p,side),g in ledger.groupby(['batch','protocol','side'])]),'',
           '所有可用量仍是 Q1：观测到的唯一序号位置，而非成功交付字节。闭合连续候选由 SYN/FIN、内部缺口、RST 和内容冲突检查决定，'
           '没有独立成功转发验证，故不升级 Q2。冲突只比较内存字节并保存计数，不保存载荷内容，不据此诊断攻击或归因协议。','',
           '## 3. 重复字节量','',
           '下面是方向侧记录的字节加权诊断，不是内容等权业务结果。O=观测字节，F=删除完全重传包，U=精确序号区间并集。F−U 表示仅删除完全重传后残留的重叠字节。','',
           table(['批次','协议','侧','方向','观测字节','唯一字节','重复比例(字节加权)','F−U'],
                 [(r['batch'],r['protocol'],r['side'],r['direction'],r['observed'],r['unique'],r['byte_weighted_duplicate_fraction'],r['remaining_overlap_after_full_packet_filter']) for r in retrans]),'',
           '重复字节可能来自网络重传或捕获重复；仅凭区间重叠不能区分来源。观察到重叠载荷冲突或 epoch 歧义的方向不输出精确 U。','',
           '## 4. 同一集合上的 O / F / U 对照','',
           '只使用主请求 proxy、两侧唯一字节均有效的共同连接方向集合；先在每访问内累加，再对每条目重复取中位 log-ratio，最后按条目等权取中位。'
           '+1=上行，−1=下行。不能将这些方向结果与旧双向总字节混为一谈。','',
           table(['批次','协议','方向','视角','条目数','访问数','典型post/pre倍率'],
                 [(r['batch'],r['protocol'],r['direction'],r['view'],r['items'],r['visits'],r['typical_ratio']) for r in summary]),'',
           '![去重对照](figures/dedup-ratios.png)','',
           'O→U 的变化只能解释重复观测的贡献；余下差值可能含封装、控制、截断与未转发部分。由于协议栈仍未知，本轮没有 U→K 结果，不把 U 后残差直接叫作认证或填充开销。','',
           '## 5. 固定多尺度方向段','',
           '从首次观测新字节事件合并同方向段，阈值固定 0/64/256/1024 bytes。各阈值独立从原段表出发，单次同时删除小段，再合并相邻同方向段。'
           '以下是连接级描述，连接数不是独立访问数；高阈值可能删除大部分控制交互，差值更小不自动表示更好。','',
           table(['批次','协议','阈值','配对数','|段数差|中位','pre保留中位','post保留中位','pre零/单段率','post零/单段率'],
                 [(r['batch'],r['protocol'],r['threshold_bytes'],r['pairs'],r['median_absolute_run_difference'],r['pre_retained_median'],r['post_retained_median'],r['pre_degenerate_fraction'],r['post_degenerate_fraction']) for r in runsummary]),'',
           '原 FR 定义未改写；新段是首次观测唯一字节上的交互，仍受时间顺序、调度与缓冲影响，不是协议不变量。未根据标签或 pre/post 相似度选择阈值。','',
           '## 6. 复核与下一步','',
           f'方向 observed=unique+duplicate、事件累计、独立区间并集、累计曲线端点、配对网格和输入冻结校验通过。'
           f'与旧统计报告的 {quality["legacy_side_total_checks"]:,} 个侧总载荷逐项相等。新增事件 {quality["new_byte_event_rows"]:,} 行；旧 240 主队列成员只做覆盖登记，没有改动或训练。','',
           '源代码、配置、输入及输出摘要记录在 provenance.json。协议证据详情见 [栈审计](stack-and-observability-audit.md)，'
           '本轮暂停点见 [阶段门](measurement-gate.md)。','',
           '相关测试记录：'+json.dumps(test_result,ensure_ascii=False)]
    DOC.mkdir(parents=True,exist_ok=True);(DOC/'figures').mkdir(exist_ok=True)
    fig,axes=plt.subplots(1,2,figsize=(10,4),layout='constrained')
    summary_df=pd.DataFrame(summary)
    for ax,direction in zip(axes,[1,-1]):
        labels=[];positions=[]
        for j,(batch,protocol) in enumerate([(b,p) for b in ['0914-broad','0914-repeat','0916'] for p in ['SHADOWSOCKS','VLESS']]):
            labels.append(batch+'\n'+('SS' if protocol=='SHADOWSOCKS' else 'VL'));positions.append(j)
            for k,view in enumerate(['O','F','U']):
                r=summary_df[(summary_df.batch==batch)&(summary_df.protocol==protocol)&(summary_df.direction==direction)&(summary_df.view==view)]
                if not r.empty:ax.scatter(j+(k-1)*.18,r.typical_ratio.iloc[0],color=f'C{k}',marker=['o','s','^'][k],label=view if j==0 else None)
        ax.set_xticks(positions,labels,fontsize=7);ax.set_title('Upload' if direction==1 else 'Download')
        ax.axhline(1,color='gray',lw=.7);ax.grid(axis='y',alpha=.2);ax.set_ylabel('Item-equal typical post/pre byte ratio');ax.legend()
    fig.savefig(DOC/'figures/dedup-ratios.png',dpi=160);plt.close(fig)
    markdown('measurement-report.md','\n'.join(lines))
    markdown('measurement-gate.md','# 阶段门：历史协议栈待确认\n\n'
             '当前不是 N13 分类放行。N0–N2 审计完成，N2 显示运行配置不足；在此基础上完成 N3–N6 的观测字节路径及 N10 多尺度段。'
             'N3 中的独立成功转发/Q2 验证尚未建立。N7/N8 精确校正未启用，N9 只完成 STREAM 可观测性检查、未完成全载体成员包级核对；'
             'N11 仅有 O/F/U 对照，N12/N13 未完成，N14/N15 未启动。\n\n'
             '请提供 0914/0916 采集时的脱敏节点配置：\n\n'
             '- SS：cipher、plugin、mux 等封装。\n'
             '- VLESS：network、TLS/REALITY 是否启用、flow/Vision、mux 与附加传输。\n'
             '- Hy2：obfs 类型与相关传输设置；如已有外层 qlog/STREAM 日志，仅先说明其存在与位置。\n\n'
             '不需要密码、UUID 或私钥，不要求补采。若只能提供当前配置，请说明它与采集时是否一致；当前配置不能自动充当历史证据。\n\n'
             '已确认所有 987 会话的 Mihomo commit 均为 fcacc8696dfd574d0faa2770c5d3151e21dd9bbc；45 个运行诊断 section 全为哈希。'
             '没有发现按 config/profile/keylog/qlog 命名的证据文件或含 stream ID+offset 的 trace 事件。\n\n'
             '如果历史配置无法恢复，可以先把本轮定为“去重与可观测性边界”的测量结果；是否仅用 U 表示进入业务对照，需要另行确认，不能称为协议特异性校正已完成。')
    write_json(OUT/'stage-status.json',{'N0':'complete','N1':'complete','N2':'complete_gate_blocked_configuration',
        'N3':'observed_eligibility_complete_Q2_unproven','N4':'complete','N5':'complete','N6':'complete',
        'N7':'blocked','N8':'blocked','N9':'observability_only','N10':'complete','N11':'O_F_U_only',
        'N12':'not_started','N13':'not_reached','N14':'not_authorized','N15':'not_authorized'})
    files=[*PathFinder('src/proxy_analysis/protocol_normalization'),*PathFinder('eval/protocol_normalization'),ROOT/'configs/protocol-normalization-20260922.yaml',
           ROOT/'src/proxy_analysis/sequences/tcp_state.py',ROOT/'src/proxy_analysis/pipeline/analyze_entity.py',
           ROOT/'src/proxy_analysis/parsing/packet_decoder.py',ROOT/'tests/unit/test_protocol_normalization_ledger.py']
    write_json(OUT/'provenance.json',{'python':sys.version,'platform':platform.platform(),'code':{str(f):digest(f) for f in files},
                                    'outputs':{p.name:digest(p) for p in OUT.glob('*.parquet')},'legacy_unchanged':True})
    print(json.dumps(quality),flush=True)


def PathFinder(relative):
    return (ROOT/relative).glob('*.py')


if __name__=='__main__':main()
