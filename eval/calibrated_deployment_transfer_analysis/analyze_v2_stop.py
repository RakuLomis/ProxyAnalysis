"""Read-only CUDA replay of accepted and failed v2 fits; never optimize."""
from pathlib import Path
import sys
import json
from collections import Counter
from datetime import datetime, timezone, timedelta

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'eval/calibrated_deployment_transfer_v2'))
import common as c
import torch

OUT = ROOT/'outputs/calibrated-deployment-business-transfer-analysis-20261006/run-02'

def replay(p, slot, failure=False):
    model = torch.load(p, map_location=c.device(), weights_only=True)
    if failure:
        theta = model['last_original_parameters']
        w, b = theta[:, :96], theta[:, 96]
    else:
        assert torch.equal(model['mu'], slot['mu'])
        assert torch.equal(model['scale'], slot['scale'])
        w, b = model['weight'], model['bias']
    w = w.detach().clone().requires_grad_()
    b = b.detach().clone().requires_grad_()
    info = c.read(p.with_suffix('.json'))
    log = info if failure else info['optimizer']
    loss = c.objective(w, b, slot['x'], slot['y'], slot['mass'], log['t'])
    gw, gb = torch.autograd.grad(loss, (w, b))
    return {'objective': float(loss.detach()),
            'gradient_max': max(float(gw.abs().max()), float(gb.abs().max())),
            'objective_difference': abs(float(loss.detach())-log['objective']),
            'gradient_difference': abs(max(float(gw.abs().max()), float(gb.abs().max()))-log['max_gradient'])}

def run():
    scientific = c.start('analysis_only_v2_interruption')
    v2 = c.v2contract()
    checks = {}
    inventories = [
        ('historical_baseline', scientific['baseline_sha256']),
        ('role_packages', {p: i['sha256'] for p, i in scientific['packages'].items()}),
        ('adopted_artifacts', c.read(c.OUT/'manifests/adopted-artifacts.json')['files']),
        ('original_snapshots', v2['original_snapshots']),
    ]
    for name, values in inventories:
        changed = [p for p, h in values.items() if c.sha(ROOT/p) != h]
        assert not changed, (name, changed)
        checks[name] = {'files': len(values), 'changed': changed}
        print('verified', name, len(values), flush=True)
    accepted = []
    for p in sorted((c.OUT/'models').rglob('*.pt')):
        info = c.read(p.with_suffix('.json')); log = info['optimizer']
        assert info['sha256'] == c.sha(p) and log['accepted'] and all(log['gates'].values())
        slotpath = c.PREP/'slots'/log['role_id']/(log['arm']+'.pt')
        assert log['input_sha256'] == c.sha(slotpath)
        slot = c.artifact(slotpath)
        values = replay(p, slot)
        assert values['gradient_max'] <= 1e-5 and values['objective_difference'] < 1e-10
        accepted.append({'role_id': log['role_id'], 'arm': log['arm'], 't': log['t'],
                         'iterations': log['iterations'], 'seconds': log['seconds'], **values})
    failed = []
    for p in sorted((c.OUT/'failures').rglob('*.pt')):
        log = c.read(p.with_suffix('.json'))
        slotpath = c.PREP/'slots'/log['role_id']/(log['arm']+'.pt')
        assert log['input_sha256'] == c.sha(slotpath)
        assert not (c.OUT/'models'/log['role_id']/p.name).exists()
        slot = c.artifact(slotpath)
        values = replay(p, slot, True)
        failed.append({'log': log, 'replay': values,
                       'failure_parameter_sha256': c.sha(p),
                       'failure_log_sha256': c.sha(p.with_suffix('.json')),
                       'training_shape': list(slot['x'].shape),
                       'training_max_abs': float(slot['x'].abs().max()),
                       'training_scale_min': float(slot['scale'].min())})
    promotion = c.read(c.OUT/'manifests/promoted-pilot-models.json')
    per_arm = {}
    for arm in c.ARMS:
        data = [r for r in accepted if r['arm'] == arm]
        per_arm[arm] = {'accepted': len(data), 'iteration_max': max(r['iterations'] for r in data),
                        'gradient_max': max(r['gradient_max'] for r in data),
                        'mean_seconds': sum(r['seconds'] for r in data)/len(data)}
    absent = ['completion.json', 'verification.json', 'selection/choices.json',
              'selection/inner-predictions.parquet', 'predictions/visits.parquet',
              'predictions/complete.json']
    missing = {p: not (c.OUT/p).exists() for p in absent}
    assert all(missing.values())
    progress = c.read(c.OUT/'progress.json')
    result = {
        'status': 'engineering_stop_not_completed',
        'stop_time_Asia_Shanghai': datetime.fromtimestamp(progress['time_unix'],
            timezone(timedelta(hours=8))).isoformat(),
        'fit_count': {'accepted_unique_v2_main': len(accepted), 'planned_inner': 14400,
                      'planned_outer': 300, 'failed_formal': len(failed),
                      'pilot_copies': len(list((c.OUT/'pilot/models').rglob('*.pt'))),
                      'new_after_promoted_pilot': len(accepted)-60},
        'by_arm': per_arm, 'by_role': dict(Counter(r['role_id'] for r in accepted)),
        'accepted_original_objective_error_max': max(r['objective_difference'] for r in accepted),
        'accepted_original_gradient_difference_max': max(r['gradient_difference'] for r in accepted),
        'accepted_models': accepted, 'failed': failed, 'input_hash_audit': checks,
        'promoted_pilot': promotion,
        'missing_final_artifacts': missing,
        'completed_stage_markers': [p.name for p in sorted((c.OUT/'manifests/stages').glob('*.json'))],
        'sealed_source_files_checked': len(scientific['source_sha256'])+len(v2['source_sha256']),
        'new_fits': 0, 'optimizer_steps': 0, 'test_package_reads': 0,
        'device': torch.cuda.get_device_name(), 'dtype': 'float64',
        'final_quality_verification_completed': False,
    }
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT/'interrupted-run-audit.json'
    path.write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({k: result[k] for k in ['status','stop_time_Asia_Shanghai','fit_count',
        'by_arm','by_role','accepted_original_objective_error_max','completed_stage_markers']},
        ensure_ascii=False, indent=2), flush=True)
    print('failed replay', json.dumps(failed, ensure_ascii=False, indent=2), flush=True)

if __name__ == '__main__':
    run()
