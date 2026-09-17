"""Scoped target-level user confirmation; never overwrite capture telemetry."""
from pathlib import Path
from ..paired_information.prepare import table
from ..reproducibility.registry import read_json
from ..reproducibility.preflight import write_json, write_table
from .audit_capture import file_hash


def main():
    config = Path('configs/activity-confirmations-20260916.json')
    policy = read_json(config)
    root = Path(policy['audit_root'])
    source = root/'session-eligibility.parquet'
    rows = table(source)
    route_path = root/'routing/session-routing.parquet'
    routes = {r['session_id']: r for r in table(route_path)}
    urls = set(policy['urls'])
    matched = [r for r in rows if r['target_domain']=='bilibili.com' and r['target_url'] in urls]
    if len(matched)!=75 or {r['target_url'] for r in matched}!=urls:
        raise ValueError('Confirmation scope changed')
    effective = []
    for row in rows:
        manual = row['target_domain']=='bilibili.com' and row['target_url'] in urls
        valid = manual or row['automated_label_valid']
        route = routes[row['session_id']]
        pair = valid and row['indexed_pair_candidate'] and row['capture_integrity_state']=='passed'
        effective.append({**row, 'manual_confirmation_applied': manual,
            'effective_label_valid': valid, 'effective_label_id': row['label_id'],
            'effective_evidence_source': 'user_target_confirmation' if manual else 'capture_summary',
            'effective_evidence_granularity': policy['evidence_granularity'] if manual else 'session_summary',
            'effective_index_pair_candidate': pair,
            'effective_main_target_proxy_pair_candidate': pair and route['exact_target_proxy'] and not route['exact_target_direct']})
    out = root/'activity-confirmation-20260917'
    out.mkdir(exist_ok=False)
    write_table(out/'effective-session-eligibility.parquet', effective)
    confirmed = [r for r in effective if r['manual_confirmation_applied']]
    summary = {'policy':policy, 'config_sha256':file_hash(config), 'source_sha256':file_hash(source),
        'route_sha256':file_hash(route_path), 'confirmed_targets':len(urls),
        'sessions_receiving_target_level_label':len(confirmed),
        'per_session_manual_observation_asserted':False,
        'bilibili_index_only_pair_candidates':sum(r['effective_index_pair_candidate'] for r in confirmed),
        'bilibili_main_target_proxy_pair_candidates':sum(r['effective_main_target_proxy_pair_candidate'] for r in confirmed),
        'raw_telemetry_and_routing_unchanged':True, 'models_retrained':False}
    write_json(out/'summary.json', summary)
    print(summary)


if __name__=='__main__': main()
