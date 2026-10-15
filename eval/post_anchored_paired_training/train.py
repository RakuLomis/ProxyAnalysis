"""Independent CUDA models, joint post/aux CE, and detached decision targets."""
import time
import argparse
from common import *
from models import Batched, init
from objectives import objective
from sampling import supervised_schedule, independent_schedule, routing


def load_jobs(fold, arms=ARMS, seeds=SEEDS):
    spec = read(OUT/'scalers'/f'f{fold}.json'); classes = read(OUT/'contract.json')['classes']
    jobs, states_e, states_h = [], [], []
    xp, xa, mp, yp, ya, ips, ias, rs, masks = [], [], [], [], [], [], [], [], []
    for seed in seeds:
        for arm in arms:
            cap = Bundle(fold, arm); post = cap.get('post')
            pre = post if arm in ['J0', 'J7'] else cap.get('pre')
            ip = supervised_schedule(post, seed)
            ia = independent_schedule(post, pre, ip) if arm == 'J5' else ip.copy()
            rr = routing(post, pre, ip, ia, arm == 'J5')
            xs = scaled(post[W].to_numpy(float), spec['post'])
            ax = scaled(pre[W].to_numpy(float), spec['post'] if arm in ['J0', 'J7'] else spec['pre'])
            ypost = tensor([classes.index(v) for v in post.label_id], torch.long)
            yaux = tensor([classes.index(v) for v in pre.label_id], torch.long)
            condition = tensor(pre[M].to_numpy(float)) if arm in CONDITIONS else torch.zeros_like(ax)
            assert xs.shape == ax.shape == condition.shape == (480, 6)
            for k in range(4):
                target_y = tensor(rr[k])@torch.nn.functional.one_hot(yaux[tensor(ia[k], torch.long)], 6).float()
                assert torch.equal(target_y.argmax(-1), ypost[tensor(ip[k], torch.long)])
            # Post-only baseline has no pre capability and receives no pre or condition values.
            assert cap.access == (['post'] if arm in ['J0', 'J7'] else ['post', 'pre'])
            estate, hstate = init(seed, 'E'), init(seed, 'H')
            mm = np.random.default_rng(seed+410000+fold).integers(0, 6, size=(2000, 120), dtype=np.int64)
            jobs.append({'fold': fold, 'seed': seed, 'arm': arm, 'reads': cap.access,
                         'initial_encoder_hash': state_hash(estate), 'initial_head_hash': state_hash(hstate),
                         'post_schedule_hash': digest(ip.tolist()), 'aux_schedule_hash': digest(ia.tolist()),
                         'post_500_exposures_hash': digest((np.bincount(ip.ravel(), minlength=480)*2).tolist()),
                         'aux_500_exposures_hash': digest((np.bincount(ia.ravel(), minlength=480)*2).tolist()),
                         'mask_hash': digest(mm.tolist()) if arm == 'J7' else None,
                         'post_matrix_hash': hashlib.sha256(xs.cpu().numpy().tobytes()).hexdigest(),
                         'aux_matrix_hash': hashlib.sha256(ax.cpu().numpy().tobytes()).hexdigest(),
                         'source_coordinate': 'post' if arm in ['J0', 'J7'] else 'pre'})
            states_e.append(estate); states_h.append(hstate)
            xp.append(xs); xa.append(ax); mp.append(condition); yp.append(ypost); ya.append(yaux)
            ips.append(ip); ias.append(ia); rs.append(rr); masks.append(mm)
    return {'jobs': jobs, 'E': Batched(states_e), 'H': Batched(states_h),
            'A': torch.nn.Parameter(torch.zeros(len(jobs), 32, 6, device=device())),
            'xp': torch.stack(xp), 'xa': torch.stack(xa), 'm': torch.stack(mp),
            'yp': torch.stack(yp), 'ya': torch.stack(ya),
            'ip': tensor(np.stack(ips), torch.long), 'ia': tensor(np.stack(ias), torch.long),
            'routing': tensor(np.stack(rs)), 'masks': tensor(np.stack(masks), torch.long)}


def batch_loss(d, step, coefficients=None):
    n = len(d['jobs']); task = torch.arange(n, device=device())[:, None]; phase = step%1000
    bp = d['ip'][:, phase]; ba = d['ia'][:, phase]
    px = d['xp'][task, bp]; ax = d['xa'][task, ba].clone()
    masked = [i for i, j in enumerate(d['jobs']) if j['arm'] == 'J7']
    if masked:
        row = torch.arange(120, device=device()); ids = tensor(masked, torch.long)
        ax[ids[:, None], row[None], d['masks'][ids, step]] = 0.
    pl = d['H'](d['E'](px))
    al = d['H'](d['E'](ax)+torch.bmm(d['m'][task, ba], d['A'].transpose(1, 2)))
    beta = (tensor([.5 if j['arm'] in ['J2', 'J3', 'J4', 'J5', 'J7'] else 0. for j in d['jobs']])
            if coefficients is None else coefficients)
    reg = 5e-5*(d['E'].l2()+d['H'].l2()+d['A'].square().flatten(1).sum(1))
    return objective(pl, al, d['yp'][task, bp], d['ya'][task, ba], d['routing'][:, phase%4], beta, reg)


def fit(fold, arms=ARMS, seeds=SEEDS, steps=2000, smoke=False):
    folder = OUT/('smoke' if smoke else 'fit')/f'f{fold}'
    if completed(folder): print('already complete', folder, flush=True); return
    assert not folder.exists(), 'partial fit preserved, do not silently restart'
    folder.mkdir(parents=True); d = load_jobs(fold, arms, seeds)
    params = [*d['E'].parameters(), *d['H'].parameters(), d['A']]
    opt = torch.optim.Adam(params, lr=.001, foreach=False)
    torch.cuda.reset_peak_memory_stats(); started = time.perf_counter(); history = []
    for step in range(steps):
        if step == 1000: opt = torch.optim.Adam(params, lr=.001, foreach=False)
        opt.zero_grad(set_to_none=True); loss, parts = batch_loss(d, step)
        assert torch.isfinite(loss).all(); loss.sum().backward()
        assert all(p.grad is None or torch.isfinite(p.grad).all() for p in params)
        opt.step(); history.append(torch.stack([loss, *parts], -1).detach())
        if not smoke and (step+1)%500 == 0:
            print(f'fold{fold}: {step+1}/{steps} CUDA steps, {len(d["jobs"])} independent models', flush=True)
    torch.cuda.synchronize(); seconds = time.perf_counter()-started
    for i, j in enumerate(d['jobs']):
        assert (j['arm'] in CONDITIONS) or torch.count_nonzero(d['A'][i]).item() == 0
        j.update({'steps': steps, 'CUDA': True, 'test_reads': 0, 'score_reads': 0,
                  'encoder_final_hash': state_hash(d['E'].one(i)), 'head_final_hash': state_hash(d['H'].one(i)),
                  'A_final_hash': state_hash({'weight': d['A'][i]}), 'Adam_reset_at': 1000 if steps > 1000 else None})
    torch.save({'jobs': d['jobs'], 'E': [d['E'].one(i) for i in range(len(d['jobs']))],
                'H': [d['H'].one(i) for i in range(len(d['jobs']))],
                'A': [d['A'][i].detach().clone() for i in range(len(d['jobs']))]}, folder/'models.pt')
    np.savez_compressed(folder/'losses.npz', values=torch.stack(history).cpu().numpy(),
                        columns=np.array(['total', 'post_CE_nats', 'aux_CE_nats', 'T2_KL', 'L2']))
    write(folder/'fit-ledger.json', d['jobs'])
    complete(folder, {'tasks': len(d['jobs']), 'steps': steps, 'CUDA': True, 'seconds': seconds,
          'peak_allocated_bytes': torch.cuda.max_memory_allocated(), 'test_reads': 0, 'smoke': smoke})
    print(f'fold{fold} complete: {len(d["jobs"])} CUDA fits in {seconds:.2f}s', flush=True)


def main():
    p = argparse.ArgumentParser(); p.add_argument('--fold', type=int); args = p.parse_args(); authorize()
    for f in range(5) if args.fold is None else [args.fold]: fit(f)


if __name__ == '__main__': main()
