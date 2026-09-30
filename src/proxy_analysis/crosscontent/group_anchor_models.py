"""Post-self VICReg plus group-normalized predictive anchors; post-only inference."""
import argparse
import copy
import time
import numpy as np
import pyarrow
import torch
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression

from .group_anchor_contract import CONFIG, verify
from .group_anchor_reliability import feature_groups
from .natural_pair_ssl import (networks, state, vicreg, views, diagnostics, encoded,
                               supervised, pretrain as baseline_pretrain, prediction_rows)
from .natural_pair_ssl_data import fingerprint
from .mechanism_contract import read
from .paired_structure_contract import seal, validate_complete
from ..paired_information.prepare import digest
from ..reproducibility.preflight import write_json, write_table


def group_losses(predictions, target, mask, groups):
    values = []
    for g, pred in zip(groups, predictions):
        jj = g['indices']; valid = mask[:, jj]
        loss = torch.nn.functional.smooth_l1_loss(pred, target[:, jj], reduction='none', beta=1.)
        count = valid.sum(1); rows = count > 0
        if rows.any():
            values.append(((loss*valid).sum(1)[rows]/count[rows]).mean())
        else:
            values.append(pred.sum()*0.)
    return torch.stack(values)


def pretrain(ssl, anchor, arm, seed, cfg):
    if arm in ('R1', 'R2'):
        encoder, info, trace = baseline_pretrain(ssl, {'R1':'B1', 'R2':'B2'}[arm], seed, cfg)
        info['arm'] = arm
        return encoder, info, trace
    if arm not in ('R3', 'R4', 'R5', 'R6'):
        raise ValueError('Unknown anchor arm')
    if set(ssl) != {'session_ids', 'pre', 'post', 'donor_indices'} or set(anchor) != {
            'session_ids', 'target', 'target_mask', 'target_scaler', 'weights'}:
        raise ValueError('Unexpected training fields')
    if ssl['session_ids'] != anchor['session_ids']:
        raise ValueError('Target order differs')
    groups = feature_groups(); encoder, projector = networks(seed)
    heads = torch.nn.ModuleList([torch.nn.Linear(32, len(g['indices']), dtype=torch.float64) for g in groups])
    initial = {'encoder': state(encoder), 'projector': state(projector), 'heads': state(heads)}
    parameters = list(encoder.parameters()) + list(projector.parameters()) + list(heads.parameters())
    opt = torch.optim.Adam(parameters, lr=cfg['learning_rate'], foreach=False)
    post = torch.tensor(ssl['post'], dtype=torch.float64)
    target = torch.tensor(anchor['target'], dtype=torch.float64)
    mask = torch.tensor(anchor['target_mask'], dtype=torch.bool)
    donors = ssl['donor_indices'] if arm in ('R5', 'R6') else list(range(len(post)))
    target = target[donors]; mask = mask[donors]
    weights = torch.tensor(anchor['weights'][arm], dtype=torch.float64)
    if not torch.isfinite(target).all() or not torch.isfinite(weights).all() or not torch.isclose(weights.sum(), weights.new_tensor(1.)):
        raise ValueError('Invalid anchor targets or weights')
    gen = torch.Generator().manual_seed(seed+100000); trace = []
    for step in range(cfg['steps']):
        a, b = views(post, post, donors, 'B1', step, cfg, gen)
        opt.zero_grad()
        ssl_loss, parts = vicreg(projector(encoder(a)), projector(encoder(b)), cfg)
        h = encoder(post); outputs = [head(h) for head in heads]
        losses = group_losses(outputs, target, mask, groups)
        contribution = cfg['anchor_lambda'] * weights * losses
        loss = ssl_loss + contribution.sum()
        # Sparse diagnostics: six separate encoder-gradient norms, no extra updates.
        grad_contrib = {}
        if step in (0, cfg['steps']-1):
            for i, g in enumerate(groups):
                gradients = torch.autograd.grad(contribution[i], tuple(encoder.parameters()), retain_graph=True)
                grad_contrib[f'{g["group"]}_encoder_gradient_l2'] = float(torch.sqrt(sum(v.square().sum() for v in gradients)))
        loss.backward()
        grad = max(float(p.grad.abs().max()) for p in parameters)
        if not np.isfinite(float(loss.detach())) or not np.isfinite(grad):
            raise ValueError('Nonfinite anchor optimization')
        opt.step()
        record = {'step': step, 'objective': float(loss.detach()), 'ssl_objective': float(ssl_loss.detach()),
                  'invariance': float(parts[0].detach()), 'variance': float(parts[1].detach()),
                  'covariance': float(parts[2].detach()), 'gradient_inf': grad}
        for i, g in enumerate(groups):
            record[f'{g["group"]}_loss'] = float(losses[i].detach())
            record[f'{g["group"]}_contribution'] = float(contribution[i].detach())
            record[f'{g["group"]}_encoder_gradient_l2'] = grad_contrib.get(f'{g["group"]}_encoder_gradient_l2')
        trace.append(record)
    with torch.no_grad():
        h = encoder(post); z = projector(h); predictions = [head(h) for head in heads]
        final_losses = group_losses(predictions, target, mask, groups)
        null_losses = group_losses([torch.zeros_like(p) for p in predictions], target, mask, groups)
    info = {'initial': initial, 'encoder': state(encoder), 'projector': state(projector), 'heads': state(heads),
            'input_sha256': fingerprint(ssl), 'anchor_input_sha256': fingerprint(anchor),
            'target_sha256': fingerprint({'target': target.tolist(), 'mask': mask.tolist()}),
            'train_ids': ssl['session_ids'], 'donor_ids': [ssl['session_ids'][i] for i in donors],
            'weights': weights.tolist(), 'steps': cfg['steps'], 'arm': arm, 'seed': seed, 'labels_used': False,
            'row_view_exposures': 3*len(post)*cfg['steps'],
            'encoder_diagnostics': diagnostics(h.numpy()), 'projection_diagnostics': diagnostics(z.numpy()),
            'train_group_huber': final_losses.tolist(), 'train_null_huber': null_losses.tolist()}
    check_collapse(info)
    return encoder, info, trace


def check_collapse(info):
    d = info['encoder_diagnostics']
    if d['effective_rank'] < 1.1 or d['mean_std'] < 1e-6:
        raise ValueError('Collapsed representation')


def engineering(config=CONFIG):
    cfg, _, root = verify(config); out = root/'engineering'
    if (out/'complete.json').exists():
        validate_complete(out); return
    ssl = read(root/'prepared/six_business-0.ssl.json')
    anchor = read(root/'prepared/six_business-0.anchor.json')
    cfg = {**cfg, 'steps': cfg['engineering_steps']}; fits = []
    for arm in ('R3', 'R4', 'R6'):
        _, a, trace = pretrain(ssl, anchor, arm, cfg['seeds'][0], cfg)
        _, b, _ = pretrain(ssl, anchor, arm, cfg['seeds'][0], cfg)
        if fingerprint(a) != fingerprint(b):
            raise ValueError('Deterministic engineering replay failed')
        check_collapse(a)
        write_json(out/f'{arm}-fit.json', a); write_table(out/f'{arm}-trajectory.parquet', trace)
        fits.append({'arm': arm, 'identical': True, **a['encoder_diagnostics']})
        print(f'engineering {arm}: {a["encoder_diagnostics"]}', flush=True)
    write_json(out/'validation.json', {'passed': True, 'fits': 6, 'steps_per_fit': cfg['steps'],
                                      'test_data_loaded': False, 'records': fits})
    seal(out, passed=True)


def run(config=CONFIG):
    cfg, _, root = verify(config); validate_complete(root/'engineering')
    for fold in range(5):
        name = f'six_business-{fold}'; data = read(root/'prepared'/f'{name}.json')
        ssl = read(root/'prepared'/f'{name}.ssl.json'); anchor = read(root/'prepared'/f'{name}.anchor.json')
        y = [data['labels'].index(r['label_id']) for r in data['train']]
        for seed in cfg['seeds']:
            for arm in cfg['arms']:
                job = root/'jobs'/f'{name}-{seed}-{arm}'
                if (job/'complete.json').exists():
                    validate_complete(job); continue
                start = time.time(); encoder, _ = networks(seed); predictions = []
                if arm != 'R0':
                    encoder, info, trace = pretrain(ssl, anchor, arm, seed, cfg); check_collapse(info)
                    write_json(job/'ssl-fit.json', info); write_table(job/'ssl-trajectory.parquet', trace)
                    h = encoded(encoder, ssl['post']); sc = StandardScaler().fit(h)
                    lr = LogisticRegression(C=cfg['probe_C'], max_iter=10000, tol=1e-8).fit(sc.transform(h), y)
                    if int(lr.n_iter_.max()) >= 10000:
                        raise ValueError('Linear probe failed to converge')
                    p = lr.predict_proba(sc.transform(encoded(encoder, data['test_post'])))
                    write_json(job/'probe-fit.json', {'encoder': state(encoder), 'mean': sc.mean_.tolist(),
                               'scale': sc.scale_.tolist(), 'coef': lr.coef_.tolist(), 'intercept': lr.intercept_.tolist(),
                               'classes': lr.classes_.tolist(), 'n_iter': lr.n_iter_.tolist()})
                    predictions.extend(prediction_rows(data, p, 'probe', seed, arm))
                model, info, trace = supervised(copy.deepcopy(encoder), ssl['post'], y, len(data['labels']), seed, cfg)
                write_json(job/'finetune-fit.json', info); write_table(job/'finetune-trajectory.parquet', trace)
                with torch.no_grad():
                    p = torch.softmax(model(torch.tensor(data['test_post'], dtype=torch.float64)), 1).numpy()
                predictions.extend(prediction_rows(data, p, 'finetune', seed, arm))
                write_table(job/'predictions.parquet', predictions)
                write_json(job/'membership.json', {'context': name, 'arm': arm, 'seed': seed,
                           'train_ids': ssl['session_ids'], 'test_ids': [r['session_id'] for r in data['test']],
                           'stages': 1 if arm == 'R0' else 3, 'prepared_sha256': digest(root/'prepared'/f'{name}.json'),
                           'ssl_input_sha256': fingerprint(ssl), 'anchor_input_sha256': fingerprint(anchor),
                           'wall_seconds': time.time()-start})
                seal(job, passed=True)
                print(f'completed {job.name}: {time.time()-start:.1f}s', flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('command', choices=['engineering', 'run'])
    parser.add_argument('--config', default=str(CONFIG)); args = parser.parse_args()
    globals()[args.command](args.config)
