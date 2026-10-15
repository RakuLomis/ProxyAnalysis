"""Training-only audit of the stopped baseline gate; no test labels or refit."""
from common import *
from train import load_jobs, batch_loss
from objectives import ce


def main():
    authorize(); checks = []; trajectory = []
    for fold in range(5):
        new = torch.load(OUT/'fit'/f'f{fold}'/'models.pt', map_location=device(), weights_only=False)
        old = torch.load(OLD/'finetune'/f'f{fold}'/'models.pt', map_location=device(), weights_only=False)[0]
        vals = np.load(OUT/'fit'/f'f{fold}'/'losses.npz', allow_pickle=False)['values']
        oldpost = source_frame(OLD/'packages'/f'f{fold}'/'supervised', 'post')
        newpost = Bundle(fold, 'J0').get('post')
        assert np.array_equal(oldpost[W], newpost[W]) and list(oldpost.label_id) == list(newpost.label_id)
        for seed in SEEDS:
            ni = next(i for i, j in enumerate(new['jobs']) if j['arm'] == 'J0' and j['seed'] == seed)
            oi = next(i for i, j in enumerate(old['jobs']) if j['arm'] == 'B0L' and j['seed'] == seed)
            nj, oj = new['jobs'][ni], old['jobs'][oi]
            assert nj['initial_encoder_hash'] == oj['initial_encoder_hash']
            assert nj['initial_head_hash'] == oj['initial_head_hash']
            assert nj['post_schedule_hash'] == oj['schedule_hash']
            delta = np.abs(vals[:1000, ni, 0]-old['losses'][:, oi].cpu().numpy())
            trajectory.append({'fold': fold, 'seed': seed, 'step0_loss_difference': float(delta[0]),
                               'first1000_max_loss_difference': float(delta.max()),
                               'first_loss_difference_above_1e6': int(np.flatnonzero(delta > 1e-6)[0])+1 if np.any(delta > 1e-6) else None})
            checks.append({'fold': fold, 'seed': seed, 'same_input': True, 'same_initial_E_H': True,
                           'same_schedule': True, 'same_scaler': read(OUT/'scalers'/f'f{fold}.json')['post'] == read(OLD/'scalers'/f'f{fold}.json')['post']})
    d = load_jobs(0); loss, _ = batch_loss(d, 0)
    pars = [*d['E'].parameters(), *d['H'].parameters()]
    g = torch.autograd.grad(loss.sum(), pars, retain_graph=True)
    ids = torch.arange(24, device=device())[:, None]; ix = d['ip'][:, 0]
    logits = d['H'](d['E'](d['xp'][ids, ix]))
    direct = ce(logits, d['yp'][ids, ix])+5e-5*(d['H'].l2()+d['E'].l2())
    gg = torch.autograd.grad(direct.sum(), pars)
    ji = tensor([i for i, j in enumerate(d['jobs']) if j['arm'] == 'J0'], torch.long)
    difference = max(float((a[ji]-b[ji]).abs().max()) for a, b in zip(g, gg))
    write(OUT/'numerical-audit.json', {'input_initialization_schedule_checks': checks,
          'first1000_trajectory': trajectory, 'duplicateCE_vs_directCE_max_initial_gradient_difference': difference,
          'old_second_stage_model_batch': 3, 'new_second_stage_model_batch': 24,
          'test_labels_read': False, 'additional_fit_tasks': 0, 'gate_relaxed': False,
          'interpretation': 'same mathematical loss/data/init; non-identical floating gradient accumulation and continuation batch path. Full contribution is not isolated by this audit.'})
    print('All 15 input/init/schedule/scaler checks passed; duplicate-vs-direct initial gradient max:', difference)
    print(pd.DataFrame(trajectory).to_string(index=False))


if __name__ == '__main__': main()
