"""Inference process reads frozen models and pre-only query packages."""
import numpy as np
import pandas as pd
import torch
from common import OUT, read, write, hash_file, relative, require, checkpoint, cuda
from kernels import predict, states, tensor


def run():
    contract = read(OUT / 'manifests/experiment-contract.json')
    accesses = []
    for i, role in enumerate(contract['roles']):
        v, f, p = role['variant'], role['fold'], role['protocol']
        source = OUT / 'packages' / v / f'f{f}' / p / 'query-pre.parquet'
        require(hash_file(source) == contract['packages_sha256'][relative(source)], 'Query changed')
        q = pd.read_parquet(source)
        require(not any(c.startswith('post_') for c in q), 'Query has target-side features')
        rows = []
        folder = OUT / 'kernels' / v / f'f{f}' / p
        completion = read(folder / 'complete.json')
        for feature in role['features']:
            model_path = folder / (feature + '.pt')
            require(hash_file(model_path) == completion['sha256'][model_path.name], 'Model changed')
            model = torch.load(model_path, map_location=cuda(), weights_only=True)
            probs = predict(model, q)
            a, _ = states(q, feature, model['merged'], model['conditioned'])
            for arm in ['M1','M2'] if v == 'load' else ['M0','M1','M2']:
                r = q[['pair_id','session_id','protocol']].copy()
                r['fold'], r['variant'], r['feature'], r['arm'] = f, v, feature, arm
                r['A'], r['row_mass'] = a, model['row_mass'][tensor(a, True)].cpu().numpy()
                z = probs[arm].cpu().numpy()
                for b in range(z.shape[1]): r['q' + str(b)] = z[:, b]
                if 'native' in model:
                    lookup = model['native'][arm]
                    a_native, _ = states(q, feature)
                    quantiles = (lookup.expand(len(q), -1) if arm == 'M0' else lookup[tensor(a_native, True)]).cpu().numpy()
                    for k, name in enumerate(['p05','p10','median','p90','p95']): r[name] = quantiles[:,k]
                rows.append(r)
        dest = OUT / 'oof' / v / f'f{f}-{p}.parquet'
        dest.parent.mkdir(parents=True, exist_ok=True)
        pd.concat(rows, ignore_index=True).to_parquet(dest, index=False)
        accesses.append({'variant': v, 'fold': f, 'protocol': p, 'query_pre': relative(source),
                         'score_post_opened': False, 'output_sha256': hash_file(dest)})
        if i % 10 == 0: print('predict', i + 1, '/', len(contract['roles']), flush=True)
    write(OUT / 'manifests/prediction-ledger.json', {'accesses': accesses, 'test_post_read': False})
    checkpoint('Q14_predictions_frozen', {'roles': len(accesses)})


if __name__ == '__main__':
    run()

