"""Fitting process: physically reads training packages only, never score/query."""
import time
import pandas as pd
import torch
from common import OUT, read, write, hash_file, relative, require, cuda, checkpoint
from kernels import fit_tables, native_tables


def checked(path, contract):
    require(hash_file(path) == contract['packages_sha256'][relative(path)], 'Sealed package changed')
    return pd.read_parquet(path)


def run():
    contract = read(OUT / 'manifests/experiment-contract.json')
    repair_path = OUT / 'manifests/engineering-repairs.json'
    repairs = read(repair_path)['source_changes'] if repair_path.exists() else {}
    for rel, sha in contract['source_sha256'].items():
        current = hash_file(OUT.parents[2] / rel)
        documented = rel in repairs and repairs[rel]['original_sha256']==sha and repairs[rel]['repaired_sha256']==current
        require(current == sha or documented, 'Undocumented sealed code change: ' + rel)
    cuda()
    ledger = []
    for index, role in enumerate(contract['roles']):
        v, f, p = role['variant'], role['fold'], role['protocol']
        package = OUT / 'packages' / v / f'f{f}' / p
        folder = OUT / 'kernels' / v / f'f{f}' / p
        if (folder / 'complete.json').exists():
            done = read(folder / 'complete.json')
            for name, sha in done['sha256'].items():
                require(hash_file(folder / name) == sha, 'Saved model changed')
            ledger.extend(done['fits'])
            continue
        train = checked(package / 'train.parquet', contract)
        gp = checked(package / 'group-pre.parquet', contract)
        gb = checked(package / 'group-post.parquet', contract)
        folder.mkdir(parents=True, exist_ok=True)
        require(not any(x in gp.columns or x in gb.columns for x in ['pair_id','session_id','carrier_id','logical_id']),
                'Anonymous group retained instance identity')
        require(not any(x.startswith('post_') for x in gp) and not any(x.startswith('pre_') for x in gb),
                'Anonymous side columns mixed')
        tasks = []
        started = time.monotonic()
        for feature in role['features']:
            model = fit_tables(train, train, gp, gb, train.fit_mass, feature,
                               merged=v == 'merged', conditioned=v == 'load')
            if v in ['primary', 'window']:
                model['native'] = native_tables(train, train, gp, gb, train.fit_mass, feature)
            torch.save(model, folder / (feature + '.pt'))
            for arm in ['M1','M2'] if v == 'load' else ['M0','M1','M2']:
                tasks.append({'variant': v, 'fold': f, 'protocol': p, 'feature': feature, 'arm': arm,
                              'train_pairs': len(train), 'train_contents': train.content_id.nunique(),
                              'device': 'cuda:0', 'dtype': 'float64', 'test_post_read': False})
        done = {'fits': tasks, 'seconds': time.monotonic() - started,
                'sha256': {x.name: hash_file(x) for x in folder.glob('*.pt')}}
        write(folder / 'complete.json', done)
        ledger.extend(tasks)
        print('fit', index + 1, '/', len(contract['roles']), v, p, f, flush=True)
    write(OUT / 'manifests/fit-ledger.json', {'tasks': ledger, 'total': len(ledger),
           'test_query_packages_opened': 0, 'test_score_packages_opened': 0,
           'by_variant': {v: sum(x['variant'] == v for x in ledger) for v in contract['variants']}})
    checkpoint('Q13_all_fits_complete', {'tasks': len(ledger)})


if __name__ == '__main__':
    run()
