"""Read-only historical evidence audit. Never bypass a failed qualification gate."""
from pathlib import Path
import collections
import hashlib
import itertools
import json
import sys
import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'src'))
from proxy_analysis.indexing.carrier_paths import bounded_events

OUT = ROOT / 'outputs/hy2-carrier-calibration-0916/run-02'
DOC = ROOT / 'docs/hy2-carrier-calibration-0916'
AUDIT = ROOT / 'outputs/content-generalization-20260916/audit-01'
CONFIG = ROOT / 'configs/hy2-carrier-calibration-0916.yaml'

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))

def write(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding='utf-8')

def save(name, rows):
    frame = pd.DataFrame(rows)
    frame.to_parquet(OUT / (name + '.parquet'), index=False)
    return frame

def path_key(p):
    fields = ('network', 'src_ip', 'src_port', 'dst_ip', 'dst_port')
    if any(p.get(k) is None for k in fields):
        return None
    # Endpoints are hashed for audit joins, never model inputs.
    return hashlib.sha256(json.dumps([p[k] for k in fields]).encode()).hexdigest()

def carrier_evidence(cid, connections, flows, events, global_opens):
    indexed = {c.get('mihomo_connection_id') for c in connections
               if c.get('carrier_binding', {}).get('carrier_id') == cid} - {None}
    flow_ids = {c['conn_id'] for c in flows
                if c.get('carrier_binding', {}).get('carrier_id') == cid}
    related = [e for e in events if e.get('carrier_id') == cid or e.get('outer_conn_id') == cid]
    bindings = {e.get('logical_conn_id', e.get('conn_id')) for e in related
                if e.get('type') == 'logical_carrier_bind'} - {None}
    starts = {e.get('conn_id') for e in events if e.get('type') in ('tcp_connect', 'udp_connect')}
    opens = [e for e in related if e.get('type') == 'carrier_open']
    return dict(indexed_members=len(indexed), flow_index_members=len(flow_ids),
                trace_members=len(bindings), members_absent_request_index=len(bindings-indexed),
                members_absent_flow_index=len(bindings-flow_ids),
                indexed_not_bound=len(indexed-bindings), member_starts_missing=len(bindings-starts),
                local_open_count=len(opens), global_open_count=len(global_opens.get(cid, set())))

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    cfg = yaml.safe_load(CONFIG.read_text(encoding='utf-8'))
    frozen_paths = [CONFIG, Path(__file__), ROOT/'plan/hy2-carrier-feasible-calibration-plan-20260928.md',
                    AUDIT/'run-registry.parquet', AUDIT/'session-eligibility.parquet',
                    AUDIT/'routing/session-routing.parquet',
                    ROOT/'outputs/feasible-summary-calibration-0916/run-01/roles.parquet',
                    ROOT/'outputs/feasible-summary-calibration-0916/run-01/completion.json']
    contract = {'stage': 'HFC0-HFC3', 'files': {str(p):sha(p) for p in frozen_paths},
                'models_trained':0, 'raw_data_modified':False}
    existing = OUT/'contract.json'
    if existing.exists() and read(existing) != contract:
        raise RuntimeError('Contract changed; do not overwrite an existing audit run')
    write(existing, contract)
    registry = pd.read_parquet(AUDIT/'run-registry.parquet')
    eligible = pd.read_parquet(AUDIT/'session-eligibility.parquet')
    routing = pd.read_parquet(AUDIT/'routing/session-routing.parquet')
    candidates = eligible[(eligible.protocol==cfg['protocol']) & eligible.label_id.isin(cfg['labels'])
                          & eligible.repetition.isin(cfg['repetitions'])].copy()
    candidates = candidates.merge(registry[registry.is_selected][['session_id','session_path']],
                                  on='session_id', validate='one_to_one')
    candidates = candidates.merge(routing[['session_id','exact_target_proxy','exact_target_direct']],
                                  on='session_id', validate='one_to_one')
    # Reuse the existing canonical content key, including youtube_video: IDs.
    old_roles = pd.read_parquet(frozen_paths[-2])
    held = old_roles[old_roles.role=='H'][['content_id','fold']].drop_duplicates()
    assert not held.content_id.duplicated().any()
    foldmap = dict(zip(held.content_id, held.fold))
    candidates['fold'] = candidates.content_id.map(foldmap)
    candidates['audit_content_id'] = candidates.content_id
    assert len(candidates)==100 and candidates.content_id.nunique()==25
    assert candidates.fold.notna().all()
    assert candidates.groupby('content_id').repetition.nunique().eq(4).all()
    assert candidates.groupby(['label_id','fold']).size().eq(4).all()
    save('candidate-visits', candidates)

    # All attempts, including non-Hy2/background traces, can contain a carrier open.
    global_opens = collections.defaultdict(set)
    global_uses = collections.defaultdict(set)
    trace_sources = []; cache = {}
    candidate_ids = set(candidates.session_id)
    for i, row in enumerate(registry.itertuples()):
        p = Path(row.session_path)
        trace = p/'raw/mihomo-trace.jsonl'
        summary_path = p/'analysis/summary.json'
        events = [json.loads(line) for line in trace.read_text(encoding='utf-8').splitlines() if line.strip()]
        events = bounded_events(events, read(summary_path))
        for e in events:
            cid = e.get('carrier_id') or e.get('outer_conn_id')
            if cid:
                global_uses[cid].add(row.session_id)
                if e.get('type')=='carrier_open':
                    global_opens[cid].add((row.session_id, e.get('event_seq'), e.get('ts')))
        trace_sources.append({'session_id':row.session_id,'trace_hash':sha(trace),
                              'summary_hash':sha(summary_path),'bounded_events':len(events)})
        if row.session_id in candidate_ids:
            cache[row.session_id] = events
        if (i+1)%100==0: print('bounded historical traces',i+1,flush=True)
    save('historical-trace-sources', trace_sources)
    carriers=[]; windows=[]; membership=[]; sources=[]; qualification=[]
    for row in candidates.itertuples():
        p=Path(row.session_path); events=cache[row.session_id]
        names=['manifest.json','raw/capture-context.json','analysis/connection-index-v2.json',
               'analysis/flow-index.json','analysis/pcap-index-v1.json']
        data={name:read(p/name) for name in names}
        sources.extend({'session_id':row.session_id,'relative_path':name,'sha256':sha(p/name)} for name in names)
        con=data[names[2]]['items']; flows=data[names[3]]['items']; pcaps=data[names[4]]['connections']
        proxy=[c for c in con if c.get('egress',{}).get('outcome')=='proxy']
        ids={c.get('carrier_binding',{}).get('carrier_id') for c in proxy}-{None}
        reasons=[]
        if not row.exact_target_proxy or row.exact_target_direct: reasons.append('target_route_not_exclusively_proxy')
        if not row.automated_label_valid: reasons.append('activity_evidence_not_valid')
        if not ids: reasons.append('no_carrier')
        if any(not c.get('carrier_binding',{}).get('carrier_id') for c in proxy): reasons.append('proxy_member_without_carrier')
        for cid in sorted(ids):
            e=carrier_evidence(cid,con,flows,events,global_opens)
            members=[c for c in proxy if c.get('carrier_binding',{}).get('carrier_id')==cid]
            known_paths={path_key(path) for c in members for path in c.get('carrier_binding',{}).get('physical_paths',[])}-{None}
            trace_paths={path_key(path) for x in events if x.get('carrier_id')==cid for path in x.get('carrier_paths',[])}-{None}
            pre_missing=0; post_paths=set()
            for c in members:
                matches=[x for x in pcaps if x['connection_id']==c['connection_id']]
                for x in matches:
                    pre=x.get('pre_proxy',{}); post=x.get('post_proxy',{})
                    ok=pre.get('status')=='success' and bool(pre.get('packet_count')) and (p/pre.get('path','__missing__')).is_file()
                    pre_missing+=not ok
                    if post.get('status')=='success': post_paths.add(post['path'])
                if not matches: pre_missing+=1
                membership.append({'session_id':row.session_id,'carrier_id':cid,
                                   'connection_id':c['connection_id'],'mihomo_connection_id':c.get('mihomo_connection_id')})
            e.update(session_id=row.session_id,content_id=row.content_id,fold=int(row.fold),carrier_id=cid,
                     other_attempts_referencing=len(global_uses[cid]-{row.session_id}),
                     indexed_paths=len(known_paths), trace_paths=len(trace_paths),
                     trace_paths_missing_index=len(trace_paths-known_paths),
                     pre_members_missing_packets=pre_missing, post_capture_files=len(post_paths),
                     post_files_exist=bool(post_paths) and all((p/x).is_file() for x in post_paths))
            carriers.append(e)
            if not e['local_open_count']: reasons.append('carrier_start_precedes_or_missing_from_visit_trace')
            if not e['global_open_count']: reasons.append('carrier_open_absent_all_attempts')
            if e['members_absent_request_index']: reasons.append('carrier_members_missing_request_index')
            if e['members_absent_flow_index']: reasons.append('carrier_members_missing_flow_index')
            if e['member_starts_missing']: reasons.append('member_start_evidence_missing')
            if e['indexed_not_bound']: reasons.append('indexed_members_not_bound')
            if e['other_attempts_referencing']: reasons.append('carrier_referenced_other_attempt')
            if e['trace_paths_missing_index']: reasons.append('carrier_path_coverage_incomplete')
            if pre_missing or not e['post_files_exist']: reasons.append('indexed_capture_missing')
        ctx=data[names[1]]; coverage=ctx.get('packet_coverage',{}); manifest=data[names[0]]
        # Preserve external session boundaries, but do not equate them with exact
        # capture-ready/capture-stop UTC timestamps without an independent bridge.
        windows.append({'session_id':row.session_id,'session_start_utc':manifest.get('started_at'),
                        'session_end_utc':manifest.get('completed_at'),'clock':coverage.get('clock'),
                        'ready_physical':coverage.get('ready',{}).get('physical'),
                        'ready_tun':coverage.get('ready',{}).get('tun'),
                        'stop_physical':coverage.get('stopped',{}).get('physical'),
                        'stop_tun':coverage.get('stopped',{}).get('tun'),
                        'pre_envelope_used':False,'exact_capture_clock_bridge_verified':False,
                        'window_status':'external_session_window_available_capture_intersection_unverified'})
        qualification.append({'session_id':row.session_id,'label_id':row.label_id,'content_id':row.content_id,
                              'repetition':row.repetition,'fold':int(row.fold),
                              'target_proxy':bool(row.exact_target_proxy),'activity_valid':bool(row.automated_label_valid),
                              'qualified':not reasons,'reasons':json.dumps(sorted(set(reasons)))})
    cf=save('carrier-registry',carriers); save('membership',membership); save('window-audit',windows)
    save('source-hashes',sources); q=save('session-qualification',qualification)
    counts=collections.Counter(reason for s in q.reasons for reason in json.loads(s))
    gate={'status':'blocked' if counts else 'requires_window_validation','candidates':len(candidates),
          'contents':candidates.content_id.nunique(),'labels':candidates.label_id.nunique(),
          'metadata_qualified':int(q.qualified.sum()),'carrier_rows':len(cf),
          'carrier_ids':cf.carrier_id.nunique(),'reason_counts':dict(counts),
          'historical_attempts_scanned':len(registry),'training_authorized_by_gate':False,
          'models_trained':0,'raw_pcaps_scanned':0,'window_gate':'not_passed',
          'old_fsc_completion_unchanged':sha(frozen_paths[-1])==contract['files'][str(frozen_paths[-1])]}
    write(OUT/'qualification-gate.json',gate)
    DOC.mkdir(parents=True,exist_ok=True)
    lines=['# Hy2 HFC0–HFC3 资格审核', '', '状态：尚未进入特征生成或训练；原始数据与旧FSC实验未修改。', '',
           f'固定候选：{len(candidates)}访问、25内容、五类，重复1/2/4/5；原内容五折映射核对通过。', '',
           f'扫描全部{len(registry)}个历史尝试的有界trace；主索引carrier {cf.carrier_id.nunique()}个。', '',
           '## 资格缺口', '', '| 原因 | 涉及访问 |','|---|---:|']
    lines.extend(f'| {k} | {v} |' for k,v in counts.items())
    lines+=['','## 解释边界','','carrier UUID没有重复不等于完整生命周期隔离已经证明。创建事件缺失不能自动判定存在泄漏，也不能自动判定不存在历史成员。',
            '请求索引只覆盖请求关联成员；trace绑定成员更广时，旧pre集合不能代表完整carrier输入。须先检查raw TUN是否可补全，不能把剩余carrier字节分摊给已有成员。',
            'manifest保存独立UTC会话边界，capture ready/stop保存单调时钟。二者不能直接相减；本审核未使用pre首尾或包相似度推算窗口。',
            '成员close不作为硬门：本任务是窗口观测，不要求全部连接在窗口内正常结束。', '',
            '## 产物','','可复用脚本：`eval/hy2_carrier_calibration/prepare.py`；配置：`configs/hy2-carrier-calibration-0916.yaml`。',
            '机器台账：`outputs/hy2-carrier-calibration-0916/run-02/`下contract、候选、carrier、成员、时间窗、来源hash、逐访问资格及qualification-gate。run-01仅为内容键工程检查失败的初始contract，保留不覆盖，未产生模型。',
            '本阶段尚无分类性能，缺口不代表配对增广无效。']
    (DOC/'measurement-audit.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(json.dumps(gate,ensure_ascii=True),flush=True)

if __name__=='__main__': main()
