"""Q10-Q12: explicit pre-only queries, separate scorers and anonymous group inputs."""
from pathlib import Path
import numpy as np
import pandas as pd
from common import (OUT, EXTRACT, FEATURES, FAMILIES, PROTOCOLS, WINDOW_PROTOCOLS, read, write, hash_file, relative,
                    require, verify_sources, checkpoint, SEED)
from weights import mass
from bins import schema


def run():
    require(not (OUT / 'manifests/experiment-contract.json').exists(), 'Contract exists: no implicit replacement')
    verify_sources()
    frame = pd.read_parquet(OUT / 'features/paired-flow-features.parquet')
    ids = ['pair_id', 'session_id', 'content_id', 'protocol', 'fold', 'label_id']
    pre_cols = ['pre_' + f for f in FEATURES]
    post_cols = ['post_' + f for f in FEATURES]
    files, roles = {}, []
    rng = np.random.default_rng(SEED)
    parents = pd.read_parquet(OUT / 'cohorts/parents.parquet')
    window = pd.read_parquet(EXTRACT / 'full-W-features.parquet')
    window = window.pivot(index='session_id', columns='side', values=['W_up','W_down','P_up','P_down','R_up','R_down'])
    window.columns = [f'{side}_{feature}' for feature, side in window.columns]
    window = parents.merge(window.reset_index(), on='session_id', validate='one_to_one')
    window['pair_id'] = window.session_id
    window.rename(columns={f'{s}_R_{d}': f'{s}_R_window_{d}' for s in ['pre','post'] for d in ['up','down']}, inplace=True)
    window_features = ['W_up','W_down','P_up','P_down','R_window_up','R_window_down']
    window_families = {'bytes': window_features[:2], 'events': window_features[2:4], 'interaction': window_features[4:]}
    variants = {'primary': frame, 'flow_equal': frame, 'merged': frame,
                'closed': frame[frame.closed_contiguous_all_four].copy(), 'load': frame, 'window': window}
    for variant, all_rows in variants.items():
      this_features = window_features if variant == 'window' else FEATURES
      pre_cols = ['pre_' + f for f in this_features]
      post_cols = ['post_' + f for f in this_features]
      for fold in range(5):
        for protocol in WINDOW_PROTOCOLS if variant == 'window' else PROTOCOLS:
            f = all_rows[all_rows.protocol.eq(protocol)].reset_index(drop=True)
            tr, te = f[f.fold.ne(fold)].copy(), f[f.fold.eq(fold)].copy()
            require(set(tr.content_id).isdisjoint(te.content_id), 'Contents leak')
            require(tr.content_id.nunique() == 24 and te.content_id.nunique() == 6, 'Content coverage changed')
            folder = OUT / 'packages' / variant / f'f{fold}' / protocol
            folder.mkdir(parents=True, exist_ok=True)
            train = tr[ids + pre_cols + post_cols].copy()
            train['fit_mass'] = mass(train, 'flow_equal' if variant == 'flow_equal' else 'hierarchical')
            query = te[['pair_id', 'session_id', 'protocol'] + pre_cols].copy()
            score = te[ids + post_cols].copy()
            group_pre = train[['content_id', 'fit_mass'] + pre_cols].copy()
            group_post = train[['content_id', 'fit_mass'] + post_cols].copy()
            group_pre = group_pre.iloc[rng.permutation(len(group_pre))].reset_index(drop=True)
            group_post = group_post.iloc[rng.permutation(len(group_post))].reset_index(drop=True)
            for name, value in [('train', train), ('query-pre', query), ('score-post', score),
                                ('group-pre', group_pre), ('group-post', group_post)]:
                p = folder / (name + '.parquet')
                value.to_parquet(p, index=False)
                files[relative(p)] = hash_file(p)
            roles.append({'variant': variant, 'fold': fold, 'protocol': protocol, 'features': this_features,
                          'train_pairs': len(tr), 'test_pairs': len(te),
                          'train_contents': sorted(tr.content_id.unique()), 'test_contents': sorted(te.content_id.unique()),
                          'test_pre_query_allowed': True, 'test_post_fit_allowed': False,
                          'anonymous_group_instances_have_no_identity': True})
    sources = {relative(p): hash_file(p) for p in Path(__file__).parent.glob('*.py')}
    write(OUT / 'manifests/experiment-contract.json', {
        'roles': roles, 'bins': schema(), 'families': FAMILIES, 'features': FEATURES,
        'window_features': window_features, 'window_families': window_families,
        'variants': list(variants), 'primary_composite': 'family equal, within-family feature equal',
        'primary_arms': ['M0', 'M1', 'M2'], 'primary_fits': 600,
        'additional_load_fits': 400, 'same_members': True, 'cuda_required': True,
        'bootstrap_seed': SEED, 'bootstrap_samples': 10000, 'primary_family_size': 8,
        'feature_selection_using_results': False, 'business_classifier_fitted': False,
        'packages_sha256': files, 'source_sha256': sources,
        'sealed_before_new_results': True})
    write(OUT / 'manifests/access-ledger.json', {
        'preparation_role': 'trusted data packaging; has both sides for eligibility, not probability fitting',
        'fitting_role_reads': ['train', 'group-pre', 'group-post'],
        'inference_role_reads': ['frozen model', 'query-pre'],
        'scoring_role_reads': ['frozen predictions', 'score-post'],
        'raw_pcap_reads': 0, 'query_files_contain_post': False,
        'numeric_whitelist': ['pre_' + f for f in FEATURES], 'labels_input_to_kernels': False,
        'group_M2_contains_content_group_but_no_pair_visit_or_carrier_identity': True,
        'separate_packages_are_not_OS_security_sandbox': True,
        'historical_data_seen_by_researchers': True})
    checkpoint('Q12_contract_sealed', {'roles': len(roles), 'primary_fits': 600})
    print('Sealed', len(roles), 'train/query/score packages before new probability results', flush=True)


if __name__ == '__main__':
    run()
