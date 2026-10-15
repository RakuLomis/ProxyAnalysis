"""All-model numerical replay, sealed inputs and explicit incomplete observation stage."""
from common import *
from diagnostics import modelpath as diagpath
from main_experiment import modelpath as mainpath

def replay(m, x, y, mass, t):
    w = m['weight'].clone().requires_grad_(); b = m['bias'].clone().requires_grad_()
    loss = objective(w, b, x, y, mass, t); gw, gb = torch.autograd.grad(loss, (w, b))
    return float(loss.detach()), max(float(gw.abs().max()), float(gb.abs().max()))

def run():
    c = start('verify'); oldcount = 0
    for p, h in c['baseline_sha256'].items(): require(sha(ROOT/p) == h, 'Historical input changed: '+p); oldcount += 1
    for p, info in c['packages'].items(): require(sha(ROOT/p) == info['sha256'], 'Role package changed')
    count = 0; objective_error = 0.; gradient_max = 0.; constant_count = 0
    diagchoices = {(r['kind'], r['outer'], r['protocol']): r['t'] for r in read(OUT/'diagnostics/choices.json')}
    for r in c['diagnostics']:
        d = package(rolepath(r)/'train.parquet', 'verify'); raw = tensor(d[HIST]); mu, scale = scaler(raw)
        x = (raw-mu)/scale; y = tensor(truths(d), torch.long)
        mass = torch.full((len(d),), 1/len(d), device=device(), dtype=torch.float64)
        ts = TS if r['inner'] is not None else [diagchoices[(r['kind'], r['outer'], r['protocol'])]]
        for t in ts:
            p = diagpath(r, t); m = artifact(p); log = read(p.with_suffix('.json'))['optimizer']
            value, gradient = replay(m, x, y, mass, t)
            objective_error = max(objective_error, abs(value-log['objective'])); gradient_max = max(gradient_max, gradient)
            require(torch.equal(m['mu'], mu) and torch.equal(m['scale'], scale), 'Diagnostic scaler replay')
            count += 1
    choices = {(v['outer'], v['target'], v['group'], v['arm']): v['t']
               for v in read(OUT/'selection/choices.json') if v['arm'] in ARMS}
    for r in c['main']:
        require(not set(r['train_contents'])&set(r['validation_contents']), 'Content leakage')
        require(not set(r['C_contents'])&set(r['U_contents']), 'C/U leakage')
        if r['inner'] is not None: require(r['target'] not in r['sources']+[r['calibration']], 'Target selection leak')
        for arm in ARMS:
            slot = artifact(OUT/'slots'/r['id']/(arm+'.pt'))
            ts = TS if r['inner'] is not None else [choices[(r['outer'], r['target'], r['group'], arm)]]
            for t in ts:
                p = mainpath(r, arm, t); m = artifact(p); log = read(p.with_suffix('.json'))['optimizer']
                value, gradient = replay(m, slot['x'], slot['y'], slot['mass'], t)
                objective_error = max(objective_error, abs(value-log['objective'])); gradient_max = max(gradient_max, gradient)
                require(torch.equal(m['mu'], slot['mu']) and torch.equal(m['scale'], slot['scale']), 'Main coordinates changed')
                require(log['iterations'] < 500 and log['device'] == 'cuda:0' and log['dtype'] == 'float64', 'Optimizer budget/device')
                count += 1
        if count % 100 == 0: progress('CT47_verifying', model_count=count, expected=15380)
    require(count == 15380 and objective_error < 1e-10 and gradient_max <= 1e-5, 'All-model numerical quality')
    # Negative IO tests against actual sealed role packages.
    r = next(v for v in c['main'] if v['inner'] is None); rejected = []
    for name, p, role in [('query cannot read labels', rolepath(r)/'labels.parquet', 'main-predict'),
                          ('fit cannot read outer query', rolepath(r)/'query.parquet', 'view-fit'),
                          ('select cannot read outer labels', rolepath(r)/'labels.parquet', 'main-select')]:
        try: package(p, role)
        except RuntimeError: rejected.append(name)
    require(len(rejected) == 3, 'Permission negative tests')
    pred = pd.read_parquet(OUT/'predictions/visits.parquet')
    require(len(pred) == 10080, 'Prediction counts')
    result = {'passed': True, 'new_formal_LR_fits': count, 'historical_files_unchanged': oldcount,
        'objective_replay_max_error': objective_error, 'all_model_max_gradient': gradient_max,
        'registered_entity_crossfold_overlap': 0, 'universal_TCP_epoch_proof': False,
        'target_U_training_pre_post_used': False, 'test_pre_feedback': False,
        'permission_whitelist_not_OS_sandbox': True, 'negative_IO_tests': rejected,
        'all_fit_and_predict_CUDA_float64': True, 'stage3_physical_only_extraction_completed': False}
    write(OUT/'verification.json', result); finish('verify', **result)

if __name__ == '__main__': run()
