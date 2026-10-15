"""Sealed CUDA training stages; inference does not load pre or routing metadata."""
import time
from common import *
from models import Batched, encoder, head, init, loss_matrix, restore, symmetric
from sampling import ssl_schedule, independent_schedule, supervised_schedule, metadata_codes


def ssl_fold(fold, steps=1000, smoke=False):
    dest = OUT/('engineering-tasks' if smoke else 'ssl')/f'f{fold}'
    if not smoke and completed(dest): return read(dest/'complete.json')
    dest.mkdir(parents=True, exist_ok=True)
    specs = read(OUT/'scalers'/f'f{fold}.json')
    jobs, postarrays, prearrays, conditions, postix, preix, ps, gs, pa, ga, masks = [], [], [], [], [], [], [], [], [], [], []
    seeds = SEEDS[:1] if smoke else SEEDS
    for seed in seeds:
        for arm in SSL:
            b = Bundle(fold, arm); post = b.get('post')
            pre = b.get('pre') if arm != 'B1' else post.copy()
            ix = ssl_schedule(post, seed, steps)
            ip = independent_schedule(post, pre, ix) if arm in ['B2', 'B6'] else ix
            if arm in ['B3', 'B4', 'B5']: assert post.row_token.tolist() == pre.row_token.tolist()
            if arm in ['B2', 'B6']: assert set(post.row_token).isdisjoint(pre.row_token)
            dep = sorted(post.deployment.unique()); cnt = sorted(post.group_id.unique())
            p, g = metadata_codes(post, dep, cnt); pp, gp = metadata_codes(pre, dep, cnt)
            postarrays.append(scaled(post[W].to_numpy(float), specs['post']))
            prearrays.append(scaled(pre[W].to_numpy(float), specs['post'] if arm == 'B1' else specs['pre']))
            conditions.append(tensor(pre[M].to_numpy(float)) if arm in CENTERS else tensor(np.zeros((480, 6))))
            ps.append(p); gs.append(g); pa.append(pp); ga.append(gp)
            postix.append(ix); preix.append(ip)
            masks.append(np.random.default_rng(seed+400000).integers(0, 6, (steps, 4, 120)))
            jobs.append({'fold': fold, 'seed': seed, 'arm': arm, 'reads': b.access,
                         'post_schedule_hash': digest(ix.tolist()), 'pre_schedule_hash': digest(ip.tolist()),
                         'common_mask_hash': digest(masks[-1][:, :2].tolist()),
                         'initial_encoder_hash': state_hash(init(seed, 'E')),
                         'initial_projector_hash': state_hash(init(seed, 'P'))})
    E = Batched([init(j['seed'], 'E') for j in jobs]); P = Batched([init(j['seed'], 'P') for j in jobs])
    active = tensor([j['arm'] in CENTERS for j in jobs])
    A = torch.nn.Parameter(torch.zeros((len(jobs), 32, 6), device=device()))
    opt = torch.optim.Adam([*E.parameters(), *P.parameters(), A], lr=.001, foreach=False)
    x = torch.stack(postarrays); a = torch.stack(prearrays); m = torch.stack(conditions)
    ix = tensor(np.stack(postix), torch.long); ip = tensor(np.stack(preix), torch.long)
    masks = tensor(np.stack(masks), torch.long)
    ids = torch.arange(len(jobs), device=device())[:, None]; rr = torch.arange(120, device=device())[None, :]
    # Mask tables use metadata only; not passed through encoder.
    pm, gm = tensor(np.stack(ps), torch.long), tensor(np.stack(gs), torch.long)
    pam, gam = tensor(np.stack(pa), torch.long), tensor(np.stack(ga), torch.long)
    negpost, negpre, negcross, poscross = [], [], [], []
    eye = torch.eye(120, device=device(), dtype=torch.bool)[None].expand(len(jobs), -1, -1)
    for block in range(4):
        pi, gi = pm[ids, ix[:, block]], gm[ids, ix[:, block]]
        ai, ag = pam[ids, ip[:, block]], gam[ids, ip[:, block]]
        npst = (pi[:, :, None] == pi[:, None, :]) & (gi[:, :, None] != gi[:, None, :])
        npre = (ai[:, :, None] == ai[:, None, :]) & (ag[:, :, None] != ag[:, None, :])
        nc = (ai[:, :, None] == pi[:, None, :]) & (ag[:, :, None] != gi[:, None, :])
        pc = eye.clone()
        for ji, j in enumerate(jobs):
            if j['arm'] == 'B6': pc[ji] = (ai[ji, :, None] == pi[ji, None, :]) & (ag[ji, :, None] == gi[ji, None, :])
        assert npst.sum(-1).eq(20).all() and npre.sum(-1).eq(20).all() and nc.sum(-1).eq(20).all()
        negpost.append(npst); negpre.append(npre); negcross.append(nc); poscross.append(pc)
    kinds = [j['arm'] for j in jobs]; L, terms = [], []; start = time.perf_counter()
    torch.cuda.reset_peak_memory_stats()
    for step in range(steps):
        opt.zero_grad(set_to_none=True); b0 = x[ids, ix[:, step]]; a0 = a[ids, ip[:, step]]
        views = []
        for slot in range(4):
            view = b0.clone() if slot < 2 else a0.clone()
            view[ids, rr, masks[:, step, slot]] = 0; views.append(view)
        z1, z2 = P(E(views[0])), P(E(views[1]))
        common = symmetric(z1, z2, negpost[step%4], eye)
        # Four encoder passes for every arm, including the ample post-only reference.
        in3, in4 = views[2].clone(), views[3].clone()
        for ji, kind in enumerate(kinds):
            if kind not in ['B1', 'B2']: in3[ji] = a0[ji]; in4[ji] = b0[ji]
        entrance = E(in3)
        shift = torch.bmm(m[ids, ip[:, step]], A.transpose(1, 2))*active[:, None, None]
        z3, z4 = P(entrance+shift), P(E(in4))
        aux = loss_matrix(z3, z4, negcross[step%4], poscross[step%4])
        side = symmetric(z3, z4, negpre[step%4], eye)
        for ji, kind in enumerate(kinds):
            if kind in ['B1', 'B2']: aux[ji] = side[ji]
        reg = .5e-4*(E.l2()+P.l2()+A.square().flatten(1).sum(1)*active)
        losses = common+aux+reg
        assert torch.isfinite(losses).all(), 'nonfinite SSL loss'
        losses.sum().backward()
        assert all(p.grad is None or torch.isfinite(p.grad).all() for p in [*E.parameters(), *P.parameters(), A])
        opt.step(); L.append(losses.detach()); terms.append(torch.stack([common.detach(), aux.detach()], -1))
    torch.cuda.synchronize()
    seconds = time.perf_counter()-start
    for i, j in enumerate(jobs):
        j.update({'final_encoder_hash': state_hash(E.one(i)), 'steps': steps, 'CUDA': True,
                  'four_encoder_slots': True, 'visits_per_slot': steps*120,
                  'post_slots': 4 if j['arm'] == 'B1' else 2 if j['arm'] == 'B2' else 3,
                  'pre_slots': 0 if j['arm'] == 'B1' else 2 if j['arm'] == 'B2' else 1,
                  'encoder_changed': state_hash(E.one(i)) != j['initial_encoder_hash'],
                  'condition_A_norm': float(A[i].norm())})
        assert j['encoder_changed'] and (j['arm'] not in CENTERS or j['condition_A_norm'] > 0)
    torch.save({'jobs': jobs, 'E': [E.one(i) for i in range(len(jobs))],
                'P': [P.one(i) for i in range(len(jobs))], 'A': A.detach(),
                'post_scaler': specs['post'], 'pre_scaler': specs['pre']}, dest/'checkpoint.pt')
    np.savez_compressed(dest/'losses.npz', losses=torch.stack(L).cpu().numpy(), terms=torch.stack(terms).cpu().numpy())
    complete(dest, {'fold': fold, 'tasks': len(jobs), 'steps': steps, 'seconds': seconds,
                    'peak_allocated_bytes': torch.cuda.max_memory_allocated(), 'jobs': jobs,
                    'SSL_business_label_reads': 0, 'test_reads': 0})
    print('SSL', fold, len(jobs), 'tasks', round(seconds, 2), 'seconds', flush=True)
    return read(dest/'complete.json')


def ssl_state(fold):
    folder = OUT/'ssl'/f'f{fold}'; assert completed(folder)
    c = torch.load(folder/'checkpoint.pt', map_location=device(), weights_only=False)
    return {(j['arm'], j['seed']): c['E'][i] for i, j in enumerate(c['jobs'])}


def downstream(fold, stage):
    dest = OUT/stage/f'f{fold}'
    if completed(dest): return
    dest.mkdir(parents=True, exist_ok=True)
    b = Bundle(fold, 'supervised'); frame = b.get('post'); spec = read(OUT/'scalers'/f'f{fold}.json')['post']
    states = ssl_state(fold); classes = read(OUT/'contract.json')['classes']
    jobs, es, hs, arrays, schedules, targets, embspecs = [], [], [], [], [], [], []
    x = scaled(frame[W].to_numpy(float), spec)
    y = tensor([classes.index(v) for v in frame.label_id], torch.long)
    # Separate head architectures are batched separately to preserve shapes.
    headkinds = ['linear', 'mlp'] if stage == 'probe' else ['mlp']
    bundles = []
    for hk in headkinds:
        jobs, es, hs, arrays, schedules, targets, embspecs = [], [], [], [], [], [], []
        for seed in SEEDS:
            for arm in SOURCES if stage == 'probe' else ARMS:
                estate = init(seed, 'E') if arm in ['R0', 'B0', 'B0L'] else states[arm, seed]
                es.append(estate); hs.append(init(seed, hk))
                embspec = None
                if stage == 'probe':
                    e = restore(estate, 'E')
                    for p in e.parameters(): p.requires_grad_(False)
                    with torch.no_grad(): h = e(x)
                    embspec = fit_scale(h); a = scaled(h, embspec)
                    assert state_hash(e.state_dict()) == state_hash(estate)
                    assert all(p.grad is None for p in e.parameters())
                else: a = x
                arrays.append(a); schedules.append(supervised_schedule(frame, seed)); targets.append(y); embspecs.append(embspec)
                jobs.append({'fold': fold, 'seed': seed, 'arm': arm, 'head': hk, 'stage': stage,
                             'initial_encoder_hash': state_hash(estate), 'initial_head_hash': state_hash(hs[-1]),
                             'schedule_hash': digest(schedules[-1].tolist()), 'embedding_scaler': embspec})
        H = Batched(hs); E = Batched(es)
        if stage == 'probe':
            for p in E.parameters(): p.requires_grad_(False)
            opt = torch.optim.Adam(H.parameters(), lr=.001, foreach=False)
        else: opt = torch.optim.Adam([*E.parameters(), *H.parameters()], lr=.001, foreach=False)
        X, I, Y = torch.stack(arrays), tensor(np.stack(schedules), torch.long), torch.stack(targets)
        ids = torch.arange(len(jobs), device=device())[:, None]; losses = []; start = time.perf_counter()
        for step in range(1000):
            opt.zero_grad(set_to_none=True); batch = X[ids, I[:, step]]
            scores = H(batch if stage == 'probe' else E(batch))
            ce = -scores.log_softmax(-1).gather(-1, Y[ids, I[:, step]][..., None]).squeeze(-1).mean(1)
            loss = ce+.5e-4*(H.l2()+(E.l2() if stage != 'probe' else 0))
            assert torch.isfinite(loss).all(); loss.sum().backward()
            assert all(p.grad is None or torch.isfinite(p.grad).all() for p in [*E.parameters(), *H.parameters()])
            opt.step(); losses.append(loss.detach())
        if stage == 'finetune':
            # Only B0L continues, with optimizer moments reset, not weights.
            longids = [i for i, j in enumerate(jobs) if j['arm'] == 'B0L']
            el = Batched([E.one(i) for i in longids]); hl = Batched([H.one(i) for i in longids])
            optl = torch.optim.Adam([*el.parameters(), *hl.parameters()], lr=.001, foreach=False)
            for step in range(1000):
                optl.zero_grad(set_to_none=True); bs = X[longids]; ii = I[longids, step]
                jj = torch.arange(len(longids), device=device())[:, None]
                scores = hl(el(bs[jj, ii])); yy = Y[longids][jj, ii]
                loss = -scores.log_softmax(-1).gather(-1, yy[..., None]).squeeze(-1).mean(1)+.5e-4*(el.l2()+hl.l2())
                assert torch.isfinite(loss).all(); loss.sum().backward(); optl.step()
            for local, idx in enumerate(longids):
                with torch.no_grad():
                    for k, p in zip(E.keys, E.weights): p[idx].copy_(el.one(local)[k])
                    for k, p in zip(H.keys, H.weights): p[idx].copy_(hl.one(local)[k])
        torch.cuda.synchronize(); seconds = time.perf_counter()-start
        for i, j in enumerate(jobs):
            j.update({'CUDA': True, 'steps': 2000 if j['arm'] == 'B0L' else 1000,
                      'encoder_final_hash': state_hash(E.one(i)), 'head_final_hash': state_hash(H.one(i)),
                      'frozen': stage == 'probe', 'test_reads': 0})
            if stage == 'probe':
                assert j['encoder_final_hash'] == j['initial_encoder_hash']
                assert all(p.grad is None for p in E.parameters())
            assert j['head_final_hash'] != j['initial_head_hash']
        bundles.append({'jobs': jobs, 'E': [E.one(i) for i in range(len(jobs))],
                        'H': [H.one(i) for i in range(len(jobs))], 'losses': torch.stack(losses).cpu(),
                        'seconds': seconds, 'input_scaler': spec})
        print(stage, fold, hk, len(jobs), 'tasks', round(seconds, 2), 'seconds', flush=True)
    torch.save(bundles, dest/'models.pt')
    complete(dest, {'fold': fold, 'tasks': sum(len(v['jobs']) for v in bundles),
                    'seconds': sum(v['seconds'] for v in bundles), 'CUDA': True,
                    'reads': b.access, 'real_post_only': True, 'test_reads': 0})


def infer():
    rows, replays = [], []
    for fold in range(5):
        f = Bundle(fold, 'inference').get('test_post')
        for stage in ['finetune', 'probe']:
            folder = OUT/stage/f'f{fold}'; assert completed(folder)
            ck = torch.load(folder/'models.pt', map_location=device(), weights_only=False)
            for block in ck:
                x = scaled(f[W].to_numpy(float), block['input_scaler'])
                for i, j in enumerate(block['jobs']):
                    e, h = restore(block['E'][i], 'E'), restore(block['H'][i], j['head'])
                    def predict(bs):
                        result = []
                        with torch.no_grad():
                            for t in x.split(bs):
                                z = e(t)
                                if j['embedding_scaler'] is not None: z = scaled(z, j['embedding_scaler'])
                                result.append(h(z).softmax(-1))
                        return torch.cat(result)
                    p, replay = predict(120), predict(17)
                    error = float((p-replay).abs().max()); assert error <= 1e-5
                    assert p.argmax(-1).eq(replay.argmax(-1)).all()
                    assert torch.isfinite(p).all() and torch.allclose(p.sum(-1), torch.ones(120, device=device()))
                    replays.append({'fold': fold, 'stage': stage, 'arm': j['arm'], 'seed': j['seed'],
                                    'head': j['head'], 'max_probability_error': error, 'decision_changes': 0})
                    p = p.cpu().numpy()
                    for sid, prob in zip(f.session_id, p):
                        rows.append({'fold': fold, 'stage': stage, 'arm': j['arm'], 'head': j['head'],
                                     'seed': j['seed'], 'session_id': sid, **{f'p{k}': v for k, v in enumerate(prob)}})
    frame = pd.DataFrame(rows)
    assert frame.stage.eq('finetune').sum() == 14400 and frame.stage.eq('probe').sum() == 25200
    assert not frame.duplicated(['stage', 'arm', 'head', 'seed', 'session_id']).any()
    frame.to_parquet(OUT/'oof.parquet', index=False)
    write(OUT/'cuda-replay.json', {'passed': True, 'tasks': len(replays), 'replays': replays,
                                  'test_pre_reads': 0, 'numeric_protocol_inputs': 0, 'CUDA': True})
    write(OUT/'prediction-seal.json', {'oof_sha256': sha(OUT/'oof.parquet'), 'rows': len(frame),
                                      'test_labels_read': False, 'test_pre_read': False})
    print('Post-only OOF sealed:', len(frame), 'rows', flush=True)


def main():
    p = cli(__doc__); p.add_argument('--stage', choices=['ssl', 'probe', 'finetune', 'infer', 'all'], required=True)
    args = p.parse_args(); authorize()
    stages = ['ssl', 'probe', 'finetune', 'infer'] if args.stage == 'all' else [args.stage]
    for stage in stages:
        if stage == 'infer': infer()
        else:
            for fold in range(5):
                if stage == 'ssl': ssl_fold(fold)
                else: downstream(fold, stage)
                write(OUT/'progress.json', {'stage': stage, 'completed_fold': fold, 'folds': 5,
                                           'complete': stage == 'finetune' and fold == 4})


if __name__ == '__main__': main()
