"""Independent closed-form reliability, identity, initialization and budget audits."""
import argparse
from collections import defaultdict
import numpy as np

from .group_anchor_contract import CONFIG, verify, identity_check
from .group_anchor_reliability import feature_groups, normalize_fit, normalized
from .natural_pair_ssl_data import prepare_train, fingerprint
from .business_representations import matrix
from .mechanism_contract import read, cohort
from .paired_structure_contract import seal, validate_complete
from ..paired_information.prepare import table, digest
from ..reproducibility.preflight import write_json


def preparation(config=CONFIG):
    cfg, source, root = verify(config); identity = identity_check(source)
    raw = {r['session_id']: r for r in cohort(source)}; checks = []; max_error = 0.
    for fold in range(5):
        name = f'six_business-{fold}'; data = read(root/'prepared'/f'{name}.json')
        ssl = read(root/'prepared'/f'{name}.ssl.json'); anchor = read(root/'prepared'/f'{name}.anchor.json')
        # Only allowed training identifiers access the raw matrix builder below.
        ids = ssl['session_ids']; rows = [raw[i] for i in ids]
        rebuilt, state, _ = prepare_train(rows)
        if fingerprint(rebuilt) != fingerprint(ssl) or fingerprint(state) != fingerprint(data['preprocessing']):
            raise ValueError('Train-only scaler/input replay failed')
        pre = matrix(rows, 'pre', 'distribution157'); post = matrix(rows, 'post', 'distribution157')
        target_state = normalize_fit(pre, cfg['numerical_eps'])
        if fingerprint(target_state) != fingerprint(anchor['target_scaler']):
            raise ValueError('Target scaling differs')
        if not np.array_equal(np.asarray(anchor['target_mask']), np.isfinite(pre) & np.array(target_state['valid'])):
            raise ValueError('Target mask differs')
        if not np.allclose(anchor['target'], normalized(pre, target_state)):
            raise ValueError('Target matrix differs')
        indices = {v: i for i, v in enumerate(ids)}
        for relation in ('true', 'mismatched'):
            result = read(root/'reliability'/name/f'{relation}.json')
            records = table(root/'reliability'/name/f'{relation}-oof.parquet')
            record_lookup = {(r['session_id'], r['feature_index']): r for r in records}
            replayed = {}; fits = 0
            for split in result['splits']:
                tr = [indices[i] for i in split['train_ids']]; va = [indices[i] for i in split['validation_ids']]
                dt = [indices[i] for i in split['train_donor_ids']]; dv = [indices[i] for i in split['validation_donor_ids']]
                for part in ('train', 'validation'):
                    if set(split[part+'_ids']) != set(split[part+'_donor_ids']):
                        raise ValueError('Donor not closed')
                xs = normalize_fit(post[tr]); ys = normalize_fit(pre[dt])
                if fingerprint(xs) != fingerprint(split['post_scaler']) or fingerprint(ys) != fingerprint(split['pre_scaler']):
                    raise ValueError('Inner scaler differs')
                a = normalized(post[tr], xs); b = normalized(pre[dt], ys)
                av = normalized(post[va], xs); bv = normalized(pre[dv], ys)
                for j in range(157):
                    if not ys['valid'][j]: continue
                    good = np.isfinite(pre[dt, j]); x = a[good, j]; y = b[good, j]
                    coef = np.dot(x-x.mean(), y-y.mean())/(np.dot(x-x.mean(), x-x.mean())+cfg['ridge_alpha'])
                    pred = av[:, j]*coef+y.mean()-coef*x.mean(); fits += 1
                    for k, idx in enumerate(va):
                        if not np.isfinite(pre[dv[k], j]): continue
                        r = record_lookup[(ids[idx], j)]
                        error = max(abs(pred[k]-r['prediction_z']), abs(bv[k, j]-r['target_z']))
                        max_error = max(max_error, float(error))
                        replayed[ids[idx], j] = ((pred[k]-bv[k, j])**2, bv[k, j]**2)
            # Independently reduce replayed residuals: dimensions, repetitions, contents.
            reliabilities = []
            for g in feature_groups():
                skills = []
                for protocol in sorted({r['protocol'] for r in rows}):
                    by_content = defaultdict(list)
                    for r in rows:
                        if r['protocol'] != protocol: continue
                        values = [replayed[r['session_id'], j] for j in g['indices'] if (r['session_id'], j) in replayed]
                        if values: by_content[r['content_id']].append(np.mean(values, axis=0))
                    content_values = [np.mean(v, axis=0) for v in by_content.values()]
                    error, null = np.mean(content_values, axis=0) if content_values else (0., 0.)
                    skills.append(float(1-error/null) if null > cfg['numerical_eps'] else None)
                reliabilities.append(max(0., min(skills)) if all(v is not None for v in skills) else 0.)
            weights = np.array(reliabilities)/sum(reliabilities) if sum(reliabilities) else np.zeros(6)
            if not np.allclose(weights, result['weights'], atol=1e-10) or fits != result['fit_count']:
                raise ValueError('Independent reliability score differs')
            expected = anchor['weights']['R4' if relation == 'true' else 'R6']
            if not np.allclose(weights, expected, atol=1e-10): raise ValueError('Wrong model weights')
            checks.append({'context': name, 'relation': relation, 'replayed_coefficients': fits,
                           'weights': weights.tolist(), 'test_raw_rows_loaded': 0})
    if max_error > 1e-9: raise ValueError('Crossfit replay residual too large')
    out = root/'pretraining-audit'
    write_json(out/'validation.json', {'passed': True, 'checks': checks, 'max_prediction_error': max_error,
        'additional_sklearn_fits': 0, 'closed_form_reconstructions': sum(c['replayed_coefficients'] for c in checks),
        'historical_identity_gate': identity, 'fresh_raw_reaudit': False,
        'training_inputs_reconstructed': True, 'evaluation_arrays_used_to_compute_weights': False})
    seal(out, passed=True)
    print(f'Pretraining audit passed; max closed-form error={max_error}', flush=True)


def training(config=CONFIG):
    cfg, _, root = verify(config); validate_complete(root/'pretraining-audit')
    initializations = defaultdict(dict); anchor_initials = defaultdict(list); updates = 0; fits = 0
    jobs = sorted((root/'jobs').iterdir())
    if len(jobs) != 105: raise ValueError('Expected 105 jobs')
    for job in jobs:
        validate_complete(job); mem = read(job/'membership.json'); name = mem['context']
        data = read(root/'prepared'/f'{name}.json'); ssl = read(root/'prepared'/f'{name}.ssl.json')
        anchor = read(root/'prepared'/f'{name}.anchor.json'); arm = mem['arm']; key = (name, mem['seed'])
        if mem['train_ids'] != ssl['session_ids'] or mem['test_ids'] != [r['session_id'] for r in data['test']]:
            raise ValueError('Job membership differs')
        if set(mem['train_ids']) & set(mem['test_ids']): raise ValueError('Visit leakage')
        if mem['ssl_input_sha256'] != fingerprint(ssl) or mem['anchor_input_sha256'] != fingerprint(anchor):
            raise ValueError('Input fingerprint differs')
        fit = read(job/'finetune-fit.json'); encoder = {k[2:]: v for k, v in fit['initial'].items() if k.startswith('0.')}
        head = {k: v for k, v in fit['initial'].items() if k.startswith('1.')}; init = encoder
        if arm != 'R0':
            info = read(job/'ssl-fit.json'); init = info['initial']['encoder']
            if fingerprint(info['encoder']) != fingerprint(encoder) or fingerprint(info['encoder']) != fingerprint(read(job/'probe-fit.json')['encoder']):
                raise ValueError('Checkpoint initialization differs')
            if info['train_ids'] != mem['train_ids'] or info['labels_used']: raise ValueError('SSL membership/labels')
            if info['encoder_diagnostics']['effective_rank'] < 1.1 or info['encoder_diagnostics']['mean_std'] < 1e-6:
                raise ValueError('Representation collapsed')
            exposures = (3 if arm in ('R3','R4','R5','R6') else 2)*len(mem['train_ids'])*cfg['steps']
            if info['row_view_exposures'] != exposures: raise ValueError('View budget differs')
            if arm in ('R3','R4','R5','R6'):
                donors = ssl['donor_indices'] if arm in ('R5','R6') else list(range(len(mem['train_ids'])))
                target = np.asarray(anchor['target'])[donors].tolist(); mask = np.asarray(anchor['target_mask'])[donors].tolist()
                if info['target_sha256'] != fingerprint({'target': target, 'mask': mask}): raise ValueError('Target hash differs')
                if info['donor_ids'] != [ssl['session_ids'][i] for i in donors]: raise ValueError('Donor identities differ')
                if info['weights'] != anchor['weights'][arm]: raise ValueError('Anchor weights changed')
                anchor_initials[key].append(fingerprint(info['initial']))
        initializations[key][arm] = (fingerprint(init), fingerprint(head))
        for stage in (['ssl'] if arm != 'R0' else []) + ['finetune']:
            trace = table(job/f'{stage}-trajectory.parquet')
            if [r['step'] for r in trace] != list(range(cfg['steps'])): raise ValueError('Update budget differs')
            if not all(np.isfinite(v) for r in trace for v in r.values() if v is not None): raise ValueError('Nonfinite training')
            fits += 1; updates += len(trace)
    if len(initializations) != 15 or any(set(v) != set(cfg['arms']) or len(set(v.values())) != 1 for v in initializations.values()):
        raise ValueError('Unmatched initialization')
    if any(len(v) != 4 or len(set(v)) != 1 for v in anchor_initials.values()): raise ValueError('Anchor init differs')
    if fits != 195 or updates != 195000: raise ValueError('Unexpected optimization budget')
    out = root/'training-audit'
    write_json(out/'validation.json', {'passed': True, 'jobs': 105, 'gradient_fits': fits,
        'gradient_updates': updates, 'probe_fits': 90, 'total_stages': 285,
        'matched_initialization_contexts': 15, 'target_donors_rebuilt': True, 'raw_data_scope': 'historical verified identity evidence'})
    seal(out, passed=True); print('Training membership, target, initialization and budget audit passed', flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('command', choices=['preparation','training'])
    parser.add_argument('--config', default=str(CONFIG)); args = parser.parse_args(); globals()[args.command](args.config)
