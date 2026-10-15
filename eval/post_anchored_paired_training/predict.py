"""Export deployment E/H only; formal interface cannot receive pre or metadata."""
from common import *
from models import restore


class PostPredictor:
    def __init__(self, artifact):
        if set(artifact) != {'E', 'H', 'post_scaler', 'features'}: raise PermissionError('invalid deployment artifact')
        assert artifact['features'] == W
        self.E = restore(artifact['E'], 'E'); self.H = restore(artifact['H'], 'H')
        self.scaler = artifact['post_scaler']

    @torch.no_grad()
    def predict(self, test_post_six, batch_size=120):
        if not isinstance(test_post_six, pd.DataFrame) or list(test_post_six) != W:
            raise PermissionError('only six ordered post numeric fields accepted')
        values = test_post_six.to_numpy(float)
        assert np.isfinite(values).all() and (values >= 0).all()
        x = scaled(values, self.scaler)
        return torch.cat([self.H(self.E(a)).softmax(-1) for a in x.split(batch_size)]).cpu().numpy()


def main():
    authorize()
    if (OUT/'prediction-seal.json').exists():
        assert sha(OUT/'oof.parquet') == read(OUT/'prediction-seal.json')['oof_sha256']; print('predictions sealed'); return
    rows, replays = [], []
    for fold in range(5):
        folder = OUT/'fit'/f'f{fold}'; assert completed(folder)
        model = torch.load(folder/'models.pt', map_location=device(), weights_only=False)
        inf = Bundle(fold, 'inference').get('test_post'); spec = read(OUT/'scalers'/f'f{fold}.json')['post']
        for i, job in enumerate(model['jobs']):
            artifact = {'E': model['E'][i], 'H': model['H'][i], 'post_scaler': spec, 'features': W}
            assert sum(v.numel() for v in artifact['E'].values())+sum(v.numel() for v in artifact['H'].values()) == 3782
            path = OUT/'inference'/f'f{fold}'/f'{job["arm"]}-s{job["seed"]}.pt'
            path.parent.mkdir(parents=True, exist_ok=True); torch.save(artifact, path)
            predictor = PostPredictor(torch.load(path, map_location=device(), weights_only=False))
            p = predictor.predict(inf[W], 120); r = predictor.predict(inf[W], 17)
            delta = float(np.max(np.abs(p-r))); same = bool(np.array_equal(p.argmax(1), r.argmax(1)))
            assert delta <= 1e-5 and same
            for forbidden in ['pre', 'protocol', 'SNI', 'm0', 'label_id', 'group_id']:
                try: predictor.predict(inf[W].assign(**{forbidden: 0}))
                except PermissionError: pass
                else: raise AssertionError('extra field accepted')
            replays.append({'fold': fold, 'arm': job['arm'], 'seed': job['seed'], 'maximum_probability_difference': delta,
                            'same_decisions': same, 'CUDA': True, 'deployment_parameters': 3782, 'extra_fields_rejected': True})
            for sid, prob in zip(inf.session_id, p):
                rows.append({'fold': fold, 'arm': job['arm'], 'seed': job['seed'], 'session_id': sid,
                             **{f'p{k}': float(v) for k, v in enumerate(prob)}})
    pred = pd.DataFrame(rows); assert len(pred) == 14400 and not pred.duplicated(['arm', 'seed', 'session_id']).any()
    pred.to_parquet(OUT/'oof.parquet', index=False)
    write(OUT/'prediction-seal.json', {'oof_sha256': sha(OUT/'oof.parquet'), 'rows': 14400,
          'test_pre_reads': 0, 'score_reads': 0, 'CUDA': True, 'checkpoints': 'fixed final2000'})
    write(OUT/'cuda-replay.json', {'passed': True, 'tasks': replays,
          'maximum_probability_difference': max(x['maximum_probability_difference'] for x in replays),
          'all_same_decisions': True, 'CUDA': True})
    print('14400 OOF probabilities sealed, 120 CUDA replays passed; no test labels/pre used', flush=True)


if __name__ == '__main__': main()
