"""Secondary, matched-budget removal of IP byte VOLUME (not identity fields)."""
import json
from pathlib import Path

import numpy as np

from ..reproducibility.preflight import write_json, write_table
from .next_stage import data, load, verify
from .prepare import digest, metrics
from .uncertainty import evaluate_refit


def main():
    cfg = load('configs/paired-value-next-stage-0914.yaml')
    verify(cfg)
    rows, spec = data(cfg)
    spec = [m for m in spec if m['id'] != 'ip_bytes']
    out = Path(cfg['output_root'])/'ip-volume-ablation'
    out.mkdir(exist_ok=False)
    write_json(out/'contract.json', {'removed': ['ip_bytes'], 'config': cfg,
        'code_sha256': digest(Path(__file__)),
        'runner_sha256': digest(Path(__file__).with_name('uncertainty.py')),
        'interpretation': 'secondary_volume_ablation_not_IP_address_ablation'})
    summaries, advantages = [], []
    for seed in cfg['inner_partition_seeds']:
        for view in ('delta_scalar', 'delta_distribution'):
            baseline = None
            for wrong, pair_seed in [(False, cfg['wrong_pair_seeds'][0])] + [(True, s) for s in cfg['wrong_pair_seeds']]:
                job = out/f'job-{len(summaries):04d}'
                job.mkdir()
                pred, tuning, maps, groups = evaluate_refit(rows, spec, view, cfg, seed, pair_seed, wrong)
                write_table(job/'oof.parquet', pred)
                write_table(job/'pair-map.parquet', maps)
                write_json(job/'tuning.json', tuning)
                summary = {'view': view, 'partition_seed': seed, 'pair_seed': pair_seed,
                           'wrong': wrong, **metrics(pred), 'fresh_fit_count': 140}
                summaries.append(summary)
                if not wrong:
                    baseline = summary['log_loss_bits']
                else:
                    advantages.append({'view': view, 'partition_seed': seed, 'pair_seed': pair_seed,
                                       'advantage_bits': summary['log_loss_bits']-baseline})
            print(json.dumps({'completed': len(summaries), 'total': 220}), flush=True)
    write_table(out/'summary.parquet', summaries)
    write_table(out/'paired-advantages.parquet', advantages)
    result = {'jobs': len(summaries), 'fresh_fit_count': len(summaries)*140, 'views': {}}
    for view in ('delta_scalar', 'delta_distribution'):
        a = np.asarray([r['advantage_bits'] for r in advantages if r['view']==view])
        result['views'][view] = {'mean_advantage_bits': float(a.mean()), 'minimum': float(a.min()),
                               'maximum': float(a.max()), 'positive_fraction': float(np.mean(a>0))}
    write_json(out/'result.json', result)
    print(json.dumps(result), flush=True)


if __name__ == '__main__':
    main()
