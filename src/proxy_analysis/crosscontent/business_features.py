"""Frozen 0916 business cohort, packet audit and project-owned feature extraction."""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
from urllib.parse import parse_qsl, urlsplit

import yaml

from ..config import FeatureConfig
from ..indexing.pairs import build_exclusive_pairs
from ..pipeline.analyze_entity import analyze_entity_capture
from ..reproducibility.extract import describe
from ..reproducibility.preflight import write_json, write_table
from ..paired_information.prepare import canonical, digest, guarded, table
from ..paired_information.reference_retrain import SCALAR_NAMES


def load_config(path='configs/content-generalization-20260916-business.yaml'):
    cfg = yaml.safe_load(Path(path).read_text(encoding='utf-8'))
    if canonical(cfg['raw_root']) != canonical('Datasets/TrafficTracer-content-generalization-20260916'):
        raise ValueError('Only the approved 0916 dataset is supported')
    return cfg


def resource_identity(url):
    value = urlsplit(url)
    query = parse_qsl(value.query, keep_blank_values=True)
    # Observed Bing redirect bookkeeping, not search content. No other keys dropped.
    if value.hostname == 'www.bing.com' and value.path == '/search':
        query = [(k, v) for k, v in query if k not in {'rdr', 'rdrig'}]
    return (value.scheme, value.hostname, value.path, tuple(sorted(query)), value.fragment)


def accepted_pairs(row, cfg):
    path = Path(row['session_path'])
    guarded(path/'analysis/connection-index-v2.json', cfg['raw_root'])
    pairs = build_exclusive_pairs(path, row['protocol'])
    counts = Counter((p.post.entity_id, str(p.post.capture_path)) for p in pairs)
    return [p for p in pairs if counts[(p.post.entity_id, str(p.post.capture_path))] == 1
            and p.pre.transport_protocol == p.post.transport_protocol == 'tcp']


def freeze(cfg, config_path):
    audit, out = Path(cfg['audit_root']), Path(cfg['output_root'])
    registry = table(audit/'run-registry.parquet')
    labels = table(audit/'activity-confirmation-20260917/effective-session-eligibility.parquet')
    routes = {r['session_id']: r for r in table(audit/'routing/session-routing.parquet')}
    lookup = {r['session_id']: r for r in registry if r['is_final']}
    rows, source_paths = [], {Path(config_path), Path(cfg['feature_config']), Path(cfg['metric_spec'])}
    source_paths.update(Path('src/proxy_analysis').rglob('*.py'))
    source_paths.update([audit/'run-registry.parquet', audit/'activity-confirmation-20260917/effective-session-eligibility.parquet',
                         audit/'routing/session-routing.parquet', Path(cfg['raw_root'])/'pipeline-manifest.json',
                         Path('configs/activity-confirmations-20260916.json')])
    aliases, capture_files = [], []
    for label in labels:
        if label['label_id'] not in cfg['labels'] or label['protocol'] not in cfg['protocols']:
            continue
        row = {**lookup[label['session_id']], **label}
        route = routes[row['session_id']]
        if not route['exact_target_proxy'] or route['exact_target_direct']:
            raise ValueError('Primary business main target not exclusively proxied')
        same = resource_identity(row['target_url']) == resource_identity(row['final_url'])
        aliases.append({'session_id':row['session_id'], 'target_url':row['target_url'],
                        'final_url':row['final_url'], 'same_resource':same})
        if not same:
            raise ValueError(f'Content redirect requires review: {row["session_id"]}')
        row['primary_candidate'] = row['effective_label_valid'] and row['repetition'] in cfg['primary_rounds']
        rows.append(row)
        path=Path(row['session_path'])
        for name in ('summary.json','connection-index-v2.json','pcap-index-v1.json'):
            source_paths.add(guarded(path/'analysis'/name,cfg['raw_root']))
        for pair in accepted_pairs(row,cfg):
            for desc in (pair.pre,pair.post):
                cap=guarded(desc.capture_path,cfg['raw_root'])
                source_paths.add(cap)
                endpoints=sorted([(desc.initiator.ip,desc.initiator.port),(desc.responder.ip,desc.responder.port)])
                capture_files.append({'session_id':row['session_id'],'content_id':row['content_id'],
                    'side':desc.capture_side,'entity_id':desc.entity_id,'path':str(cap),
                    'canonical_path':str(canonical(cap)),'tuple_key':json.dumps(endpoints)})
    if len(rows)!=300 or sum(r['primary_candidate'] for r in rows)!=240:
        raise ValueError('Expected 300 candidates and 240 primary members')
    sources={str(p):digest(p) for p in sorted(source_paths)}
    for r in capture_files: r['sha256']=sources[r['path']]
    duplicates=[]
    for key in ('canonical_path','sha256'):
        groups=defaultdict(list)
        for r in capture_files: groups[r[key]].append(r)
        for value,members in groups.items():
            if len({r['session_id'] for r in members})>1:
                duplicates.append({'key':key,'value':value,'sessions':sorted({r['session_id'] for r in members})})
    out.mkdir(parents=True,exist_ok=False)
    write_json(out/'contract.json',{'config':cfg,'sources':sources,'model_features':list(SCALAR_NAMES),
        'observation_level':cfg['observation_level'],'pending_gate':'packet_extraction_and_tuple_reuse_audit'})
    write_table(out/'candidates.parquet',rows)
    write_table(out/'effective-labels.parquet',labels)
    write_table(out/'capture-files.parquet',capture_files)
    write_json(out/'content-alias-review.json',aliases)
    write_json(out/'duplicate-captures.json',duplicates)
    write_json(out/'attempt-selection-audit.json',{'stored_attempts':len(registry),'selected':len(lookup),
        'prior_attempts_excluded':len(registry)-len(lookup),'selected_business_candidates':len(rows)})
    write_json(out/'feature-dictionary.json',{'model_allowlist':list(SCALAR_NAMES),
        'metric_definitions':yaml.safe_load(Path(cfg['metric_spec']).read_text(encoding='utf-8')),
        'imputation':'training_only','sequence_boundary':'original_entity_then_aggregate',
        'excluded_inputs':['IP_address','MAC','port','SNI','domain','absolute_timestamp','captured_bytes','session_id']})
    mdn=[r for r in rows if not r['effective_label_valid']]
    write_json(out/'mdn-recovered-session-review.json',{'sessions':mdn,
        'decision':'retain_degraded_record_not_in_primary; 300-session_sensitivity_requires_confirmation'})
    if duplicates: raise ValueError('Cross-session duplicate capture requires review')
    print(json.dumps({'candidates':len(rows),'primary':240,'captures':len(capture_files),'sources':len(sources)}),flush=True)


def verify(cfg):
    contract=json.loads((Path(cfg['output_root'])/'contract.json').read_text(encoding='utf-8'))
    if contract['config']!=cfg: raise ValueError('Config changed')
    for path, expected in contract['sources'].items():
        if digest(Path(path))!=expected: raise ValueError(f'Frozen source changed: {path}')
    return contract


def extract(cfg):
    verify(cfg)
    out=Path(cfg['output_root']); cache=out/'sessions'; cache.mkdir(exist_ok=True)
    config=FeatureConfig.load(Path(cfg['feature_config']))
    rows=table(out/'candidates.parquet'); summaries=[]; statuses=[]; audits=[]
    for index,row in enumerate(rows):
        dest=cache/(row['session_id']+'.json')
        if dest.exists():
            result=json.loads(dest.read_text(encoding='utf-8'))
        else:
            result={'session_id':row['session_id'],'summaries':[],'captures':[],'errors':[]}
            try:
                groups={'pre':[],'post':[]}
                pairs=accepted_pairs(row,cfg)
                if not pairs: raise ValueError('No exclusive pairs')
                for pair in pairs:
                    for desc in (pair.pre,pair.post):
                        analysis=analyze_entity_capture(desc)
                        if analysis.unknown_direction_count: raise ValueError('Unknown packet direction')
                        if analysis.packet_count!=len(analysis.tcp_packets): raise ValueError('Unexpected non-TCP/unparsed packet')
                        packets=list(analysis.packet_measures)
                        if not packets: raise ValueError('Empty capture')
                        groups[desc.capture_side].append(packets)
                        times=[p.timestamp_ns for p in packets]
                        syns=[{'direction':p.direction,'seq':p.seq} for p in analysis.tcp_packets if p.flags & 2 and not p.flags & 16]
                        result['captures'].append({'session_id':row['session_id'],'path':str(desc.capture_path),
                            'side':desc.capture_side,'packet_count':len(packets),
                            'nonempty_packets':sum(p.transport_payload_len>0 for p in packets),
                            'first_ns':min(times),'last_ns':max(times),
                            'time_inversions':sum(b<a for a,b in zip(times,times[1:])),
                            'initial_syn_json':json.dumps(syns)})
                for selection in ('observed','nonempty','exclude_full_retransmission'):
                    record={'session_id':row['session_id'],'content_id':row['content_id'],
                            'label_id':row['label_id'],'protocol':row['protocol'],'repetition':row['repetition'],
                            'primary_candidate':row['primary_candidate'],'selection':selection}
                    for side,entity_groups in groups.items():
                        selected=[[p for p in g if (selection!='nonempty' or p.transport_payload_len>0)
                            and (selection!='exclude_full_retransmission' or p.tcp_classification!='full_retransmission')] for g in entity_groups]
                        record[side]=describe(selected,config)
                        if not record[side] or not record[side]['nonempty_packets']:
                            raise ValueError('No nonempty traffic on one side')
                    result['summaries'].append(record)
            except Exception as exc:
                result['errors']=[str(exc)]; result['summaries']=[]
            write_json(dest,result)
        summaries.extend(result['summaries']); audits.extend(result['captures'])
        statuses.append({'session_id':row['session_id'],'primary_candidate':row['primary_candidate'],
                         'state':'error' if result['errors'] else 'complete','errors':result['errors']})
        if (index+1)%10==0: print(json.dumps({'completed':index+1,'total':len(rows),'errors':sum(s['state']=='error' for s in statuses)}),flush=True)
    write_table(out/'side-summaries.parquet',summaries)
    write_table(out/'capture-audit.parquet',audits)
    write_json(out/'extraction-status.json',statuses)
    observed=[r for r in summaries if r['selection']=='observed']
    for side in ('pre','post'):
        write_table(out/f'{side}-features.parquet',[{k:r[k] for k in ('session_id','content_id','label_id','protocol','repetition','primary_candidate')}|
                    {name:r[side].get(name) for name in SCALAR_NAMES} for r in observed])
    primary=[r for r in observed if r['primary_candidate']]
    write_table(out/'primary-cohort.parquet',[{k:v for k,v in r.items() if k not in ('pre','post')} for r in primary])
    write_json(out/'extraction-gate.json',{'expected_primary':240,'actual_primary':len(primary),
        'completed_sessions':len(observed),'failed_sessions':sum(s['state']=='error' for s in statuses),
        'primary_passed':len(primary)==240,'identity_audit_pending':True})
    if len(primary)!=240: raise ValueError('Primary cohort incomplete: user confirmation required')


def main():
    p=argparse.ArgumentParser(); p.add_argument('--config',default='configs/content-generalization-20260916-business.yaml')
    p.add_argument('--mode',choices=['freeze','extract'],required=True); args=p.parse_args(); cfg=load_config(args.config)
    if args.mode=='freeze': freeze(cfg,args.config)
    else: extract(cfg)


if __name__=='__main__': main()
