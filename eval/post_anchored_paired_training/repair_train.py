"""Exactly fifteen J0 refits; immutable attempt1 and all other arms preserved."""
import time
import argparse
from common import *
from models import Batched, init
from sampling import supervised_schedule

REPAIR = OUT/'repair-v1'


def ensure_seal():
    authorize()
    if (REPAIR/'repair-seal.json').exists():
        sealed = read(REPAIR/'repair-seal.json')
        assert sealed['parent_seal'] == sha(OUT/'seal.json')
        for n, h in sealed['sources'].items(): assert sha(ROOT/n) == h
        return
    assert not REPAIR.exists(), 'partial repair preserved'
    REPAIR.mkdir(parents=True)
    write(REPAIR/'repair-contract.json', {'approval': '同意，请你继续', 'date': '2026-10-04',
          'additional_fits': 15, 'arm': 'J0', 'unchanged_other_model_count': 105,
          'failed_original_J0_count': 15, 'total_actual_full_length_fits': 135,
          'selected_comparison_models': 120, 'objective_changed': False, 'steps': 2000,
          'first_stage_layout_slots': 24, 'active_slots': [1, 9, 17],
          'first_stage_inactive_slots_are_frozen': True, 'second_stage_models': 3,
          'equivalent_CE_collapsed': True, 'lr': .001, 'L2_sum_coefficient': 5e-5,
          'probability_tolerance': 1e-5, 'test_score_selection': False, 'E2': False})
    sources = {str(Path(__file__).relative_to(ROOT)): sha(Path(__file__)),
               str((DOC/'repair-contract.md').relative_to(ROOT)): sha(DOC/'repair-contract.md')}
    write(REPAIR/'repair-seal.json', {'parent_seal': sha(OUT/'seal.json'), 'sources': sources,
          'contract_sha256': sha(REPAIR/'repair-contract.json'), 'original_prediction': sha(OUT/'oof.parquet')})


def run_fold(fold):
    ensure_seal(); folder = REPAIR/'refits'/f'f{fold}'
    if (folder/'complete.json').exists():
        meta = read(folder/'complete.json')
        for n, h in meta['files'].items(): assert sha(folder/n) == h
        print(f'J0 repair fold{fold} already complete', flush=True); return
    assert not folder.exists(), 'partial repair fit preserved; no silent restart'
    folder.mkdir(parents=True)
    f = Bundle(fold, 'J0').get('post'); spec = read(OUT/'scalers'/f'f{fold}.json')['post']
    classes = read(OUT/'contract.json')['classes']
    x = scaled(f[W].to_numpy(float), spec); y = tensor([classes.index(v) for v in f.label_id], torch.long)
    original = torch.load(OUT/'fit'/f'f{fold}'/'models.pt', map_location=device(), weights_only=False)
    reference = torch.load(OLD/'finetune'/f'f{fold}'/'models.pt', map_location=device(), weights_only=False)[0]
    oldarms = ['B0', 'B0L', 'B1', 'B2', 'B3', 'B4', 'B5', 'B6']
    es, hs, schedules, jobs = [], [], [], []
    for seed in SEEDS:
        for oldarm in oldarms:
            es.append(init(seed, 'E')); hs.append(init(seed, 'H'))
            schedules.append(supervised_schedule(f, seed))
            jobs.append({'seed': seed, 'old_layout_arm': oldarm})
    active = [i for i, j in enumerate(jobs) if j['old_layout_arm'] == 'B0L']
    assert active == [1, 9, 17]
    # Frozen numerical padding, not 21 extra trained models. Only selected slices contribute loss.
    H, E = Batched(hs), Batched(es)
    opt = torch.optim.Adam([*E.parameters(), *H.parameters()], lr=.001, foreach=False)
    X = torch.stack([x]*24); Y = torch.stack([y]*24); I = tensor(np.stack(schedules), torch.long)
    ids = torch.arange(24, device=device())[:, None]
    active_gpu = tensor(active, torch.long); inactive = [i for i in range(24) if i not in active]
    logs, start = [], time.perf_counter(); initial_e = [E.one(i) for i in inactive]; initial_h = [H.one(i) for i in inactive]
    for step in range(1000):
        opt.zero_grad(set_to_none=True); batch = X[ids, I[:, step]]; scores = H(E(batch))
        c = -scores.log_softmax(-1).gather(-1, Y[ids, I[:, step]][..., None]).squeeze(-1).mean(1)
        loss = c+.5e-4*(H.l2()+E.l2())
        assert torch.isfinite(loss[active_gpu]).all(); loss[active_gpu].sum().backward()
        for p in [*E.parameters(), *H.parameters()]:
            assert torch.count_nonzero(p.grad[inactive]).item() == 0
        opt.step(); logs.append(loss[active_gpu].detach())
    for k, i in enumerate(inactive):
        assert state_hash(E.one(i)) == state_hash(initial_e[k])
        assert state_hash(H.one(i)) == state_hash(initial_h[k])
    trace = torch.stack(logs).cpu().numpy()
    old_index = [next(i for i, j in enumerate(reference['jobs']) if j['arm'] == 'B0L' and j['seed'] == seed) for seed in SEEDS]
    old_trace = reference['losses'][:, old_index].cpu().numpy()
    first_loss_difference = float(np.max(np.abs(trace-old_trace)))
    write(folder/'first-stage-audit.json', {'maximum_training_loss_difference': first_loss_difference,
          'inactive_padding_unchanged': True, 'active_models': 3, 'test_reads': 0})
    # Compare intermediate weights to the independently co-initialized B0, not test scores.
    mid = []
    for k, seed in enumerate(SEEDS):
        oi = next(i for i, j in enumerate(reference['jobs']) if j['arm'] == 'B0' and j['seed'] == seed)
        max_e = max(float((E.one(active[k])[n]-v).abs().max()) for n, v in reference['E'][oi].items())
        max_h = max(float((H.one(active[k])[n]-v).abs().max()) for n, v in reference['H'][oi].items())
        mid.append({'seed': seed, 'E_weight_max_difference': max_e, 'H_weight_max_difference': max_h})
    write(folder/'intermediate-weights.json', mid)
    # Exact frozen computation layout of the original three B0L continuations.
    el, hl = Batched([E.one(i) for i in active]), Batched([H.one(i) for i in active])
    optl = torch.optim.Adam([*el.parameters(), *hl.parameters()], lr=.001, foreach=False)
    bs, yyall = X[active], Y[active]; jj = torch.arange(3, device=device())[:, None]
    for step in range(1000):
        optl.zero_grad(set_to_none=True); ii = I[active, step]
        scores = hl(el(bs[jj, ii])); yy = yyall[jj, ii]
        loss = -scores.log_softmax(-1).gather(-1, yy[..., None]).squeeze(-1).mean(1)+.5e-4*(el.l2()+hl.l2())
        assert torch.isfinite(loss).all(); loss.sum().backward(); optl.step(); logs.append(loss.detach())
    final_jobs, comparisons = [], []
    for k, seed in enumerate(SEEDS):
        oi = old_index[k]; orig_job = next(j for j in original['jobs'] if j['arm'] == 'J0' and j['seed'] == seed)
        assert orig_job['initial_encoder_hash'] == reference['jobs'][oi]['initial_encoder_hash']
        assert orig_job['initial_head_hash'] == reference['jobs'][oi]['initial_head_hash']
        assert orig_job['post_schedule_hash'] == reference['jobs'][oi]['schedule_hash']
        e, h = el.one(k), hl.one(k)
        we = max(float((e[n]-v).abs().max()) for n, v in reference['E'][oi].items())
        wh = max(float((h[n]-v).abs().max()) for n, v in reference['H'][oi].items())
        comparisons.append({'seed': seed, 'E_weight_max_difference': we, 'H_weight_max_difference': wh,
                            'same_encoder_hash': state_hash(e) == state_hash(reference['E'][oi]),
                            'same_head_hash': state_hash(h) == state_hash(reference['H'][oi])})
        final_jobs.append({**orig_job, 'encoder_final_hash': state_hash(e), 'head_final_hash': state_hash(h),
                           'repair_version': 'v1', 'original_J0_preserved': True,
                           'direct_CE_reproduction': True, 'source_reads': ['post'],
                           'actual_post_forward_per_update': 1, 'duplicate_aux_CE_collapsed': True,
                           'fitted_steps': 2000, 'test_reads': 0, 'score_reads': 0})
    torch.cuda.synchronize(); seconds = time.perf_counter()-start
    torch.save({'jobs': final_jobs, 'E': [el.one(k) for k in range(3)], 'H': [hl.one(k) for k in range(3)],
                'A': [torch.zeros(32, 6, device=device()) for _ in range(3)]}, folder/'models.pt')
    np.savez_compressed(folder/'losses.npz', total=torch.stack(logs).cpu().numpy())
    write(folder/'training-reproduction.json', {'first1000_max_loss_difference': first_loss_difference,
          'final_weight_comparisons': comparisons, 'test_labels_read': False, 'extra_tasks': 3})
    write(folder/'complete.json', {'tasks': 3, 'steps': 2000, 'CUDA': True, 'seconds': seconds,
          'repair_seal_sha256': sha(REPAIR/'repair-seal.json'),
          'files': {p.name: sha(p) for p in folder.iterdir() if p.is_file() and p.name != 'complete.json'}})
    print(f'J0 repair fold{fold}: three refits {seconds:.2f}s; first-stage loss delta {first_loss_difference:.3g}; final weights {comparisons}', flush=True)


def main():
    p = argparse.ArgumentParser(); p.add_argument('--fold', type=int); args = p.parse_args()
    for fold in range(5) if args.fold is None else [args.fold]: run_fold(fold)


if __name__ == '__main__': main()
