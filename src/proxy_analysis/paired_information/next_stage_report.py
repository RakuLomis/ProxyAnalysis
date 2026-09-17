"""Summarize completed refits without treating algorithm seeds as observations."""
import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

from ..reproducibility.preflight import write_json, write_table
from .next_stage import load, verify
from .prepare import digest, table
from .reference_retrain import loss_bits


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--report-name', default='report')
    args = parser.parse_args()
    if Path(args.report_name).name != args.report_name:
        raise ValueError('Report name must be one directory component')
    cfg = load('configs/paired-value-next-stage-0914.yaml')
    verify(cfg)
    root = Path(cfg['output_root'])
    names = ['partitions-observed', 'bootstrap-observed', 'partitions-nonempty',
             'partitions-exclude_full_retransmission', 'ip-volume-ablation']
    for name in names:
        if not (root/name/'result.json').is_file():
            raise ValueError(f'Incomplete stage: {name}')
    out = root/args.report_name
    out.mkdir(exist_ok=False)
    url_results, stability, tuning = [], [], []
    audited_jobs = 0
    for name in names:
        folder = root/name
        summary = table(folder/'summary.parquet')
        url_losses = {}
        for index, row in enumerate(summary):
            job = folder/f'job-{index:04d}'
            if (job/'complete.json').exists():
                complete = json.loads((job/'complete.json').read_text(encoding='utf-8'))
                for artifact, expected in complete['artifacts'].items():
                    if digest(job/artifact) != expected:
                        raise ValueError('Result artifact changed')
            predictions = table(job/'oof.parquet')
            if len(predictions) != 140 or len({r['session_id'] for r in predictions}) != 140:
                raise ValueError('Prediction coverage changed')
            by_url = defaultdict(list)
            for prediction in predictions:
                by_url[prediction['target_url']].append(float(loss_bits([prediction['truth']], [prediction['prob_vless']])[0]))
            if len(by_url) != 14 or {len(v) for v in by_url.values()} != {10}:
                raise ValueError('URL test weighting changed')
            url_losses[index] = {url: float(np.mean(values)) for url, values in by_url.items()}
            for item in json.loads((job/'tuning.json').read_text(encoding='utf-8')):
                tuning.append({'stage': name, 'view': row['view'], 'wrong': row['wrong'],
                               'outer_url': item['outer_url'], 'selected_C': item['selected_C']})
            audited_jobs += 1
        grouped = defaultdict(list)
        for index, true in enumerate(summary):
            if true['wrong'] or not true['view'].startswith('delta_'):
                continue
            for other, wrong in enumerate(summary):
                if not wrong['wrong'] or wrong['view'] != true['view']:
                    continue
                if (wrong['partition_seed'], wrong.get('bootstrap_seed')) != (true['partition_seed'], true.get('bootstrap_seed')):
                    continue
                for url, value in url_losses[index].items():
                    grouped[(true['view'], url)].append(url_losses[other][url]-value)
        for (view, url), advantages in grouped.items():
            url_results.append({'stage': name, 'view': view, 'target_url': url,
                                'mean_advantage_bits': float(np.mean(advantages)),
                                'algorithmic_comparisons': len(advantages)})
        for view in ('delta_scalar', 'delta_distribution'):
            values = np.asarray([r['mean_advantage_bits'] for r in url_results if r['stage']==name and r['view']==view])
            rng = np.random.default_rng(20260915)
            boot = rng.choice(values, size=(5000, len(values)), replace=True).mean(axis=1)
            stability.append({'stage': name, 'view': view, 'urls': len(values),
                'mean_advantage_bits': float(values.mean()), 'positive_url_count': int(np.sum(values>0)),
                'minimum_url_advantage': float(values.min()), 'maximum_url_advantage': float(values.max()),
                'minimum_leave_one_url_out_mean': float(min(np.delete(values, i).mean() for i in range(len(values)))),
                'conditional_url_bootstrap_low': float(np.quantile(boot, .025)),
                'conditional_url_bootstrap_high': float(np.quantile(boot, .975)),
                'interval_scope': 'conditional_on_completed_refit_ensemble_not_joint_training_or_external_CI'})
    write_table(out/'url-contributions.parquet', url_results)
    write_table(out/'url-stability.parquet', stability)
    write_table(out/'selected-hyperparameters.parquet', tuning)
    inventory = table(root/'business-audit/session-eligibility-inventory.parquet')
    pair_audit = {r['session_id']: r for r in table(root/'raw-and-pair-audit/business-index-pair-eligibility.parquet')}
    merged = []
    coverage = defaultdict(list)
    for row in inventory:
        item = {**row, 'index_pair_status': pair_audit[row['session_id']]['status'],
                'indexed_exclusive_tcp_pairs': pair_audit[row['session_id']]['accepted_tcp_pairs']}
        merged.append(item)
        coverage[(item['current_label_id'], item['protocol'])].append(item)
    write_table(out/'business-session-eligibility.parquet', merged)
    business_summary = []
    for (label, protocol), members in sorted(coverage.items()):
        eligible = [r for r in members if r['index_pair_status']=='indexed_pairs_files_present']
        urls = {r['target_url'] for r in members}
        available = {r['target_url'] for r in eligible}
        business_summary.append({'label_id': label, 'protocol': protocol,
            'selected_sessions': len(members), 'exact_url_upper_bound': len(urls),
            'indexed_pair_sessions': len(eligible), 'indexed_pair_url_upper_bound': len(available),
            'strict_tcp_design_applicable': protocol != 'HYSTERIA2',
            'additional_contents_lower_bound_for_five': max(0, 5-len(available)) if protocol != 'HYSTERIA2' else None,
            'warning': 'Lower bound only: existing aliases, semantic review, and capture quality can increase deficit.'})
    write_table(out/'business-content-deficits.parquet', business_summary)
    count = Counter((r['stage'], r['view'], r['wrong'], r['selected_C']) for r in tuning)
    write_json(out/'hyperparameter-counts.json', [{'stage': k[0], 'view': k[1], 'wrong': k[2], 'C': k[3], 'count': v}
                                                 for k, v in sorted(count.items())])
    summary = {'completed_jobs': audited_jobs, 'fresh_fits_uncertainty_and_sensitivity': audited_jobs*140,
               'fresh_fits_reference': 1120, 'business_training_started': False,
               'business_gate': 'insufficient_independent_content_even_at_exact_URL_upper_bound',
               'semantic_nonvideo_labels_need_user_confirmation': True,
               'full_business_capture_feature_quality_audit': 'not_completed_gate_failed_before_training',
               'stability': stability,
               'code_hashes': {str(p): digest(p) for p in Path(__file__).parent.glob('*.py')}}
    write_json(out/'summary.json', summary)
    print(json.dumps(summary, ensure_ascii=False), flush=True)


if __name__ == '__main__':
    main()
