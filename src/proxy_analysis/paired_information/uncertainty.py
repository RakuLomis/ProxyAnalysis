"""Explicit URL partitions and URL-bootstrap refits; session-local pairing.

Bootstrapped URL multiplicities are expanded only AFTER pairing original unique
sessions. All copies of an original URL remain in one inner partition.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

from ..reproducibility.preflight import write_json, write_table
from .next_stage import data, load, verify
from .pairing import matrix
from .prepare import digest, metrics
from .reference_retrain import assert_partition, fit_model, inner_indices, loss_bits


VIEWS = ('pre', 'post', 'joint_scalar', 'joint_distribution', 'delta_scalar', 'delta_distribution')


def url_bootstrap(rows, seed):
    urls = sorted({r['target_url'] for r in rows})
    rng = np.random.default_rng(seed)
    attempts = 0
    while True:
        counts = Counter(rng.choice(urls, size=len(urls), replace=True).tolist())
        attempts += 1
        if len(counts) >= 3:
            return counts, attempts
        if attempts >= 10000:
            raise ValueError('Cannot generate eligible URL bootstrap')


def expansion(rows, counts):
    return np.repeat(np.arange(len(rows)), [counts[r['target_url']] for r in rows])


def evaluate_refit(rows, spec, view, cfg, partition_seed, pair_seed, wrong, bootstrap_seed=None):
    predictions, tuning, maps, groups = [], [], [], []
    for outer_index, url in enumerate(sorted({r['target_url'] for r in rows})):
        train = [r for r in rows if r['target_url'] != url]
        test = [r for r in rows if r['target_url'] == url]
        if bootstrap_seed is None:
            counts = dict.fromkeys({r['target_url'] for r in train}, 1)
            attempts = 1
        else:
            counts, attempts = url_bootstrap(train, bootstrap_seed + outer_index * 100003)
            train = [r for r in train if r['target_url'] in counts]
        groups.append({'outer_url': url, 'url_multiplicities': counts, 'draw_attempts': attempts})
        losses = defaultdict(list)

        def vectors(part, seed, role, inner):
            x, mapping = matrix(part, spec, view, seed=seed, wrong=wrong)
            allowed = {r['session_id']: r for r in part}
            if {m['receiver_session_id'] for m in mapping} != set(allowed):
                raise ValueError('Receiver coverage')
            if {m['donor_session_id'] for m in mapping} != set(allowed):
                raise ValueError('Donor bijection')
            for m in mapping:
                a, b = allowed[m['receiver_session_id']], allowed[m['donor_session_id']]
                if (a['target_url'], a['protocol']) != (b['target_url'], b['protocol']):
                    raise ValueError('Pair stratum mismatch')
                if wrong and a['session_id'] == b['session_id']:
                    raise ValueError('Wrong-pair fixed point')
                maps.append({**m, 'outer_url': url, 'inner_fold': inner, 'role': role})
            return x

        for inner, (tr, va) in enumerate(inner_indices(train, partition_seed)):
            a, b = [train[i] for i in tr], [train[i] for i in va]
            assert_partition(a, b, test)
            xa = vectors(a, pair_seed+inner*2, 'inner_train', inner)
            xb = vectors(b, pair_seed+inner*2+1, 'inner_validation', inner)
            ea, eb = expansion(a, counts), expansion(b, counts)
            ya = np.asarray([int(r['protocol'] == 'VLESS') for r in a])
            yb = np.asarray([int(r['protocol'] == 'VLESS') for r in b])
            for c in cfg['classification_C']:
                model = fit_model(xa[ea], ya[ea], c, cfg['seed'])
                losses[c].extend(loss_bits(yb[eb], model.predict_proba(xb[eb])[:, 1]))
        chosen = min(cfg['classification_C'], key=lambda c: (np.mean(losses[c]), c))
        assert_partition(train, [], test)
        x = vectors(train, pair_seed+100, 'outer_train', -1)
        xt = vectors(test, pair_seed+101, 'outer_test', -1)
        e = expansion(train, counts)
        y = np.asarray([int(r['protocol'] == 'VLESS') for r in train])
        model = fit_model(x[e], y[e], chosen, cfg['seed'])
        for row, probability in zip(test, model.predict_proba(xt)[:, 1]):
            truth = int(row['protocol'] == 'VLESS')
            predictions.append({'session_id': row['session_id'], 'target_url': url,
                                'truth': truth, 'prob_vless': float(probability),
                                'loss_bits': float(loss_bits([truth], [probability])[0]),
                                'selected_C': chosen, 'view': view,
                                'observation_level': cfg['observation_level']})
        tuning.append({'outer_url': url, 'selected_C': chosen,
                       'inner_losses': {str(c): float(np.mean(v)) for c, v in losses.items()}})
    return predictions, tuning, maps, groups


def run(cfg, mode, selection):
    verify(cfg)
    rows, spec = data(cfg)
    if selection != cfg['primary_selection']:
        from .prepare import table
        expected = {r['session_id'] for r in rows}
        rows = [r for r in table(Path(cfg['source_root'])/'side-summaries.parquet')
                if r['selection'] == selection and r['scope'] == cfg['scope']]
        if len(rows) != 140 or {r['session_id'] for r in rows} != expected:
            raise ValueError('Sensitivity cohort changed')
    out = Path(cfg['output_root'])/f'{mode}-{selection}'
    out.mkdir(exist_ok=True)
    contract = {'code_sha256': digest(Path(__file__)), 'mode': mode, 'selection': selection,
                'base_contract_sha256': digest(Path(cfg['output_root'])/'contract.json')}
    contract_path = out/'runner-contract.json'
    if contract_path.exists():
        if json.loads(contract_path.read_text(encoding='utf-8')) != contract:
            raise ValueError('Runner changed; use new output root')
    else:
        write_json(contract_path, contract)
    jobs = []
    if mode == 'partitions':
        for partition_seed in cfg['inner_partition_seeds']:
            for view in VIEWS:
                jobs.append((partition_seed, cfg['wrong_pair_seeds'][0], False, None, view))
            for pair_seed in cfg['wrong_pair_seeds']:
                for view in VIEWS[-2:]:
                    jobs.append((partition_seed, pair_seed, True, None, view))
    else:
        for i in range(cfg['training_group_bootstraps']):
            for view in VIEWS[-2:]:
                jobs.append((cfg['inner_partition_seeds'][0], cfg['wrong_pair_seeds'][0], False, 70001+i, view))
                for pair_seed in cfg['wrong_pair_seeds'][:cfg['wrong_seeds_per_bootstrap']]:
                    jobs.append((cfg['inner_partition_seeds'][0], pair_seed, True, 70001+i, view))
    summaries = []
    for index, (partition_seed, pair_seed, wrong, boot_seed, view) in enumerate(jobs):
        job = out/f'job-{index:04d}'
        done = job/'complete.json'
        if done.exists():
            complete = json.loads(done.read_text(encoding='utf-8'))
            for name, expected in complete['artifacts'].items():
                if digest(job/name) != expected:
                    raise ValueError('Completed job artifact changed')
            summaries.append(complete['summary'])
            continue
        job.mkdir(exist_ok=True)
        pred, tuning, maps, groups = evaluate_refit(rows, spec, view, cfg, partition_seed, pair_seed, wrong, boot_seed)
        write_table(job/'oof.parquet', pred)
        write_table(job/'pair-map.parquet', maps)
        write_json(job/'tuning.json', tuning)
        write_json(job/'training-groups.json', groups)
        summary = {'job_index': index, 'partition_seed': partition_seed, 'pair_seed': pair_seed,
                   'wrong': wrong, 'bootstrap_seed': boot_seed, 'view': view, **metrics(pred),
                   'fresh_fit_count': 14*(3*len(cfg['classification_C'])+1)}
        write_json(done, {'summary': summary, 'artifacts': {p.name: digest(p) for p in
                    (job/'oof.parquet', job/'pair-map.parquet', job/'tuning.json', job/'training-groups.json')}})
        summaries.append(summary)
        if (index+1) % 10 == 0:
            print(json.dumps({'mode': mode, 'selection': selection, 'completed': index+1, 'total': len(jobs)}), flush=True)
    write_table(out/'summary.parquet', summaries)
    advantages = []
    for true in summaries:
        if true['wrong'] or not true['view'].startswith('delta_'):
            continue
        controls = [r for r in summaries if r['wrong'] and r['view'] == true['view']
                    and r['partition_seed'] == true['partition_seed'] and r['bootstrap_seed'] == true['bootstrap_seed']]
        for wrong in controls:
            advantages.append({'view': true['view'], 'partition_seed': true['partition_seed'],
                               'bootstrap_seed': true['bootstrap_seed'], 'pair_seed': wrong['pair_seed'],
                               'true_loss_bits': true['log_loss_bits'], 'wrong_loss_bits': wrong['log_loss_bits'],
                               'advantage_bits': wrong['log_loss_bits']-true['log_loss_bits']})
    write_table(out/'paired-advantages.parquet', advantages)
    result = {'jobs': len(jobs), 'fresh_fit_count': sum(r['fresh_fit_count'] for r in summaries),
              'scope': 'internal_training_sensitivity_not_external_validation', 'views': {}}
    for view in VIEWS[-2:]:
        a = np.asarray([r['advantage_bits'] for r in advantages if r['view'] == view])
        result['views'][view] = {'n_algorithmic_comparisons_not_independent_samples': len(a),
                               'mean_advantage_bits': float(a.mean()), 'minimum': float(a.min()),
                               'maximum': float(a.max()), 'positive_fraction': float(np.mean(a > 0)),
                               'p025': float(np.quantile(a, .025)), 'p975': float(np.quantile(a, .975)),
                               'interval_type': 'algorithmic_sensitivity_quantiles_not_population_CI'}
    write_json(out/'result.json', result)
    print(json.dumps(result), flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', default='configs/paired-value-next-stage-0914.yaml')
    parser.add_argument('--mode', choices=['partitions', 'bootstrap'], required=True)
    parser.add_argument('--selection', default='observed')
    args = parser.parse_args()
    run(load(args.config), args.mode, args.selection)


if __name__ == '__main__':
    main()
