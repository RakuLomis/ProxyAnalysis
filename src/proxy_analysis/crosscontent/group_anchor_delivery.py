"""Read-only NumPy anchor-head replay and historical-control equivalence."""
import argparse
from pathlib import Path
import numpy as np

from .group_anchor_contract import CONFIG, verify
from .group_anchor_reliability import feature_groups
from .natural_pair_ssl_data import fingerprint
from .natural_pair_ssl_report import mlp
from .mechanism_contract import read
from .paired_structure_contract import validate_complete, seal
from ..paired_information.prepare import digest, table
from ..reproducibility.preflight import write_json


def huber(x):
    a = abs(x)
    return np.where(a < 1, .5*a*a, a-.5)


def deliver(config=CONFIG):
    cfg, _, root = verify(config); validate_complete(root/'report')
    comparisons = []; effects = []; max_error = 0.
    for job in sorted((root/'jobs').iterdir()):
        validate_complete(job); mem = read(job/'membership.json'); arm = mem['arm']
        if arm in ('R0','R1','R2'):
            old_arm = {'R0':'B0', 'R1':'B1', 'R2':'B2'}[arm]
            old = Path(cfg['historical_root'])/'jobs'/f'{mem["context"]}-{mem["seed"]}-{old_arm}'
            validate_complete(old)
            old_fit = read(old/'finetune-fit.json'); new_fit = read(job/'finetune-fit.json')
            equal = fingerprint(old_fit) == fingerprint(new_fit)
            if arm != 'R0':
                equal = equal and fingerprint(read(old/'probe-fit.json')) == fingerprint(read(job/'probe-fit.json'))
            if not equal: raise ValueError('Historical equivalent baseline changed')
            comparisons.append({'job': job.name, 'reference': str(old), 'parameters_identical': equal,
                                'reference_seal_sha256': digest(old/'complete.json')})
            continue
        info = read(job/'ssl-fit.json'); ssl = read(root/'prepared'/f'{mem["context"]}.ssl.json')
        anchor = read(root/'prepared'/f'{mem["context"]}.anchor.json')
        donors = ssl['donor_indices'] if arm in ('R5','R6') else np.arange(len(ssl['post']))
        target = np.asarray(anchor['target'])[donors]; mask = np.asarray(anchor['target_mask'])[donors]
        h = mlp(ssl['post'], info['encoder']); trace = table(job/'ssl-trajectory.parquet')
        for i, g in enumerate(feature_groups()):
            pred = h@np.asarray(info['heads'][f'{i}.weight']).T+info['heads'][f'{i}.bias']
            valid = mask[:, g['indices']]; count = valid.sum(1); used = count > 0
            y = target[:, g['indices']]
            loss = float(((huber(pred-y)*valid).sum(1)[used]/count[used]).mean())
            null = float(((huber(y)*valid).sum(1)[used]/count[used]).mean())
            max_error = max(max_error, abs(loss-info['train_group_huber'][i]), abs(null-info['train_null_huber'][i]))
            effects.append({'context': mem['context'], 'seed': mem['seed'], 'arm': arm, 'group': g['group'],
                'weight': info['weights'][i], 'train_prediction_huber': loss, 'train_mean_huber': null,
                'train_loss_reduction': null-loss,
                'encoder_gradient_l2_first': trace[0][g['group']+'_encoder_gradient_l2'],
                'encoder_gradient_l2_last': trace[-1][g['group']+'_encoder_gradient_l2'],
                'scope': 'training fit diagnostic, not out-of-sample auxiliary performance'})
    if max_error > 1e-10 or len(comparisons) != 45 or len(effects) != 360:
        raise ValueError('Supplemental delivery audit failed')
    out = root/'mechanism-audit'
    write_json(out/'historical-control-equivalence.json', comparisons)
    write_json(out/'group-prediction-diagnostics.json', effects)
    write_json(out/'validation.json', {'passed': True, 'max_numpy_group_huber_error': max_error,
        'identical_historical_control_jobs': 45, 'group_diagnostics': 360,
        'additional_training_fits': 0, 'audit_code_sha256': digest(Path(__file__)),
        'note': 'Independent delivery audit added after training contract; no training code or inputs modified'})
    seal(out, passed=True); print('Supplemental anchor-head replay and historical equivalence passed', flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('--config', default=str(CONFIG)); args = parser.parse_args()
    deliver(args.config)
