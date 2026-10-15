"""Post-seal offline retrieval; test pre is never a business-model input."""
import sys
from common import *
saved_path = list(sys.path)
sys.path.insert(0, str(ROOT/'eval/hy2_carrier_calibration'))
import window_model as frozen_wm
sys.path[:] = saved_path
from models import restore


def fit_center(pre, post, group=False, mechanism=False):
    a, b, aux = tensor(pre[W].to_numpy(float), torch.float64), tensor(post[W].to_numpy(float), torch.float64), tensor(pre[AUX].to_numpy(float), torch.float64)
    z, target, rawtarget = phi(a), phi(b), b
    if group:
        # Only content membership, never common visit ID or repetition.
        target = torch.stack([phi(b)[tensor(post.group_id.eq(g).to_numpy(), torch.bool)].mean(0) for g in pre.group_id])
        rawtarget = torch.stack([b[tensor(post.group_id.eq(g).to_numpy(), torch.bool)].mean(0) for g in pre.group_id])
    n = torch.round(torch.expm1(aux[:, :2])); beta = torch.zeros(2, device=device(), dtype=torch.float64)
    if mechanism:
        denominator = n.square().sum(0)
        beta = torch.where(denominator > 0, (n*(rawtarget[:, :2]-a[:, :2])).sum(0)/denominator.clamp_min(1), 0.).clamp_min(0)
    def origin(values, proxy):
        c = values.clone()
        if mechanism: c[:, :2] += torch.floor(torch.round(torch.expm1(proxy[:, :2]))*beta+.5)
        return phi(c)
    q = torch.cat([torch.log1p(a), aux], 1); mu = q.mean(0); sd = q.std(0, unbiased=False); sd = torch.where(sd < 1e-10, 1., sd)
    zs = z.std(0, unbiased=False); zs = torch.where(zs < 1e-10, 1., zs)
    X = torch.cat([(q-mu)/sd, torch.ones((len(q), 1), device=device(), dtype=q.dtype)], 1)
    penalty = torch.eye(15, device=device(), dtype=q.dtype); penalty[-1, -1] = 0
    weight = torch.linalg.solve(X.T@X/len(X)+penalty, X.T@((target-origin(a, aux))/zs)/len(X))
    def predict(frame):
        aa, uu = tensor(frame[W].to_numpy(float), torch.float64), tensor(frame[AUX].to_numpy(float), torch.float64)
        qq = (torch.cat([torch.log1p(aa), uu], 1)-mu)/sd
        xx = torch.cat([qq, torch.ones((len(qq), 1), device=device(), dtype=q.dtype)], 1)
        pred = origin(aa, uu)+(xx@weight)*zs
        return frozen_wm.decode(pred)[0]
    return predict, beta


def rank_rows(q, k, groups, similarity=True):
    score = (torch.nn.functional.normalize(q, dim=-1, eps=1e-12) @
             torch.nn.functional.normalize(k, dim=-1, eps=1e-12).T) if similarity else -torch.cdist(q, k).square()
    g = tensor(groups, torch.long); neg = g[:, None] != g[None, :]
    target = score.diagonal(); ranks = 1+((score >= target[:, None]) & neg).sum(1)
    gaps = target-score.masked_fill(~neg, -torch.inf).max(1).values
    return ranks.cpu().numpy(), gaps.cpu().numpy()


def main():
    cli(__doc__).parse_args(); authorize()
    assert sha(OUT/'oof.parquet') == read(OUT/'prediction-seal.json')['oof_sha256']
    rows, representations, parameters = [], [], []
    for fold in range(5):
        package = Bundle(fold, 'diagnostic'); trpre, trpost = package.get('train_pre'), package.get('train_post')
        tepre, tepost = package.get('test_pre'), package.get('test_post')
        scalers = read(OUT/'scalers'/f'f{fold}.json')
        ck = torch.load(OUT/'ssl'/f'f{fold}'/'checkpoint.pt', map_location=device(), weights_only=False)
        centers = {}
        for protocol in sorted(trpre.deployment.unique()):
            ia = trpre.deployment.eq(protocol); ib = trpost.deployment.eq(protocol)
            qa = tepre[tepre.deployment.eq(protocol)].reset_index(drop=True)
            for arm in CENTERS:
                aa = trpre[ia].reset_index(drop=True); bb = trpost[ib].reset_index(drop=True)
                if arm == 'B6':
                    aa = aa.sort_values(['group_id', *W, *AUX]).reset_index(drop=True)
                    bb = bb.sort_values(['group_id', *W]).reset_index(drop=True)
                    aa = aa.drop(columns=['session_id']); bb = bb.drop(columns=['session_id'])
                else: bb = bb.set_index('session_id').loc[aa.session_id].reset_index()
                predict, beta = fit_center(aa, bb, arm == 'B6', arm != 'B4')
                raw = predict(qa); validate(raw)
                for sid, v in zip(qa.session_id, raw.cpu().numpy()): centers[arm, sid] = v
                parameters.append({'fold': fold, 'deployment': protocol, 'arm': arm,
                                   'fit_contents': 24, 'fit_visits': 96, 'beta': beta.cpu().tolist(),
                                   'test_fit': False, 'CUDA': True})
        for ji, job in enumerate(ck['jobs']):
            e, p = restore(ck['E'][ji], 'E'), restore(ck['P'][ji], 'P')
            with torch.no_grad():
                testh = e(scaled(tepost[W].to_numpy(float), scalers['post']))
                rank = torch.linalg.matrix_rank(testh-testh.mean(0)).item()
                representations.append({'fold': fold, 'arm': job['arm'], 'seed': job['seed'],
                                        'embedding_variance': float(testh.var(0, unbiased=False).mean()),
                                        'centered_rank': int(rank), 'condition_A_norm': float(ck['A'][ji].norm())})
                for protocol in sorted(tepost.deployment.unique()):
                    b = tepost[tepost.deployment.eq(protocol)].reset_index(drop=True)
                    a = tepre.set_index('session_id').loc[b.session_id].reset_index()
                    groups = pd.factorize(b.group_id, sort=True)[0]
                    entrance = e(scaled(a[W].to_numpy(float), scalers['pre']))
                    k = p(e(scaled(b[W].to_numpy(float), scalers['post'])))
                    mm = tensor(np.zeros((24, 6)))
                    if job['arm'] in CENTERS:
                        raw = np.stack([centers[job['arm'], sid] for sid in a.session_id])
                        mm = scaled(phi(raw)-phi(a[W].to_numpy(float)), scalers['conditions'][job['arm']])
                        direct = scaled(raw, scalers['post'])
                        rr, gap = rank_rows(direct, scaled(b[W].to_numpy(float), scalers['post']), groups, False)
                        for sid, r, gg in zip(b.session_id, rr, gap):
                            rows.append({'fold': fold, 'deployment': protocol, 'seed': job['seed'], 'arm': job['arm'],
                                         'mode': 'center_direct', 'session_id': sid, 'rank': int(r), 'gap': float(gg)})
                    variants = {'predicted': mm}
                    if job['arm'] in CENTERS:
                        variants['zero_condition'] = torch.zeros_like(mm)
                        variants['permuted_condition'] = mm.roll(4, 0)
                    for mode, m in variants.items():
                        shift = m@ck['A'][ji].T; q = p(entrance+shift)
                        rr, gap = rank_rows(q, k, groups)
                        for sid, r, gg in zip(b.session_id, rr, gap):
                            rows.append({'fold': fold, 'deployment': protocol, 'seed': job['seed'], 'arm': job['arm'],
                                         'mode': mode, 'session_id': sid, 'rank': int(r), 'gap': float(gg)})
    pd.DataFrame(rows).to_parquet(OUT/'retrieval.parquet', index=False)
    pd.DataFrame(representations).to_parquet(OUT/'embedding-diagnostics.parquet', index=False)
    write(OUT/'diagnostic-centers.json', {'fits': parameters, 'count': len(parameters),
          'post_seal_diagnostic_only': True, 'classification_test_pre': False})
    assert len(parameters) == 75
    write(OUT/'diagnosis-complete.json', {'passed': True, 'center_fits': 75,
          'prediction_hash_unchanged': sha(OUT/'oof.parquet') == read(OUT/'prediction-seal.json')['oof_sha256'],
          'classification_or_selection_uses_test_pre': False})
    print('Offline diagnostics complete; 75 source-only centers; business predictions unchanged', flush=True)


if __name__ == '__main__': main()
