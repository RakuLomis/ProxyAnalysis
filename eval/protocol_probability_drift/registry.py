"""Q00-Q06: fixed parents, pairing eligibility, safe config and source hashes."""
from pathlib import Path
import shutil
import pandas as pd
from common import (ROOT, OUT, EXTRACT, PARENTS, REGISTRY, PLAN, PROTOCOLS, EXPECTED,
                    read, write, relative, hash_file, environment, git_state, require, checkpoint)
from bins import schema


def run():
    require(not (OUT / 'manifests/registry-complete.json').exists(),
            'Registry already completed; use its existing artifacts, do not overwrite')
    OUT.mkdir(parents=True, exist_ok=True)
    write(OUT / 'manifests/environment.json', environment())
    c = pd.read_parquet(PARENTS / 'cohort.parquet').sort_values('session_id').reset_index(drop=True)
    require(len(c) == 600 and c.content_id.nunique() == 30, 'Parent cohort changed')
    require(c.groupby('content_id').fold.nunique().eq(1).all(), 'Content crosses folds')
    require(c.groupby(['protocol', 'content_id']).repetition.agg(set).map(
        lambda x: x == {1, 2, 3, 4}).all(), 'Repetitions changed')
    require(c.groupby('protocol').size().eq(120).all(), 'Protocol visit counts changed')
    ledger = {r['session_id']: r for r in read(REGISTRY / 'session-profile-ledger.json')}
    identity = read(EXTRACT / 'identity-source-evidence/qualification.json')
    old_isolation = read(EXTRACT / 'isolation-01/summary.json')
    require(identity['qualified_for_registered_entity_grouping'], 'Identity qualification absent')
    for key in ['cross_fold_registered_carriers', 'cross_fold_SYN_signatures',
                'cross_fold_positive_IP_packet_hash_matches', 'overlapping_windows', 'repeated_raw_file_hashes']:
        require(old_isolation[key] == 0, 'Historical isolation failure: ' + key)
    hashes = {}
    fixed = [PLAN, PARENTS / 'cohort.parquet', PARENTS / 'global-folds.parquet',
             EXTRACT / 'full-coverage.parquet', EXTRACT / 'full-W-features.parquet',
             EXTRACT / 'full-T-features.parquet', EXTRACT / 'identity-source-evidence/qualification.json',
             EXTRACT / 'isolation-01/summary.json', REGISTRY / 'implementation-registry.json',
             REGISTRY / 'protocol-profile-registry.json', REGISTRY / 'mechanism-contract.json',
             REGISTRY / 'session-profile-ledger.json',
             ROOT / 'docs/post-anchored-paired-training-extend/formal-results.md',
             ROOT / 'docs/post-anchored-paired-training-extend/result-interpretation.md',
             ROOT / 'outputs/post-anchored-paired-training-extend/run-01/repair-v1/score-complete.json']
    for path in fixed:
        hashes[relative(path)] = hash_file(path)
    members, entities, parent_rows = [], [], []
    coverage = pd.read_parquet(EXTRACT / 'full-coverage.parquet').set_index('session_id')
    for index, row in c.iterrows():
        sid = row.session_id
        folder = EXTRACT / 'sessions' / sid
        complete = read(folder / 'complete.json')
        scope = read(folder / 'scope.json')
        require(complete['content_id'] == row.content_id and complete['protocol'] == row.protocol,
                'Session parent/config identity mismatch')
        require(complete['repetition'] == row.repetition and complete['W_gate_passed'], 'Parent eligibility changed')
        for name in ['T-pairs.json', 'scope.json', 'complete.json', 'common-window.json',
                     'pre-W-events.parquet', 'post-W-events.parquet',
                     'T-newbyte-events.parquet', 'T-direction-ledger.parquet']:
            hashes[relative(folder / name)] = hash_file(folder / name)
        meta = row.to_dict()
        meta.update({'dataset_id': 'Extend-content-generalization-qualified',
                     'deployment_id': row.protocol, 'config_profile_hash': ledger[sid]['profile_id'],
                     'implementation_sha': identity['source_commit'],
                     'window_start_ns': complete['start_ns'], 'window_end_ns': complete['end_ns']})
        parent_rows.append(meta)
        for carrier in scope['carriers']:
            entities.append({'carrier_id': carrier, 'session_id': sid, 'content_id': row.content_id,
                             'protocol': row.protocol, 'fold': row.fold})
        pairs = read(folder / 'T-pairs.json')
        good = [p for p in pairs if p['common_valid_nonempty']]
        require(len(good) == int(coverage.loc[sid, 'T_common_pairs']), 'Pair count mismatch')
        if row.protocol not in PROTOCOLS:
            require(len(pairs) == 0, 'AnyTLS unexpectedly has TCP pair qualification')
            continue
        for pair in good:
            logical, carrier = pair['logical_id'], pair['carrier_id']
            require(set(scope['carriers'][carrier]) == {logical}, 'Nonexclusive carrier in TCP main cohort')
            require(pair['summaries']['pre'] is not None and pair['summaries']['post'] is not None,
                    'Qualified pair has missing side')
            members.append({**meta, 'pair_id': sid + ':' + logical, 'logical_id': logical,
                            'carrier_id': carrier, 'registered_epoch_proxy': carrier,
                            'complete_TCP_epoch_reconstruction_claimed': False,
                            'common_valid_nonempty': True})
        if index % 100 == 0:
            print('registry parents', index + 1, '/', len(c), flush=True)
    e = pd.DataFrame(entities)
    cross = int(e.groupby('carrier_id').fold.nunique().gt(1).sum())
    p = pd.DataFrame(members)
    require(cross == 0, 'Registered carrier crosses content folds: confirmation required')
    require(p.groupby('protocol').size().to_dict() == EXPECTED, 'Fixed 23566 member counts changed')
    require(not p.pair_id.duplicated().any(), 'Pair identifier duplicated')
    require(p.groupby('logical_id').fold.nunique().max() == 1, 'Logical flow crosses folds')
    (OUT / 'cohorts').mkdir(exist_ok=True)
    pd.DataFrame(parent_rows).to_parquet(OUT / 'cohorts/parents.parquet', index=False)
    p.to_parquet(OUT / 'cohorts/pairs.parquet', index=False)
    e.to_parquet(OUT / 'cohorts/carriers.parquet', index=False)
    c[['content_id', 'fold', 'label_id']].drop_duplicates().to_parquet(OUT / 'cohorts/folds.parquet', index=False)
    write(OUT / 'manifests/isolation-audit.json', {
        'cross_fold_registered_carriers': cross, 'new_pair_members': len(p),
        'pair_logical_fold_consistent': True, 'content_fold_consistent': True,
        'qualification_basis': identity, 'historical_isolation': old_isolation,
        'boundary': 'registered entities; five SYN-unobserved cases retained under prior source qualification; not universal epoch proof',
        'historical_training_allowed_flags_not_rewritten': True,
        'new_protocol_extraction_or_classification': False})
    write(OUT / 'manifests/bin-schema.json', schema())
    for name in ['implementation-registry.json', 'protocol-profile-registry.json', 'mechanism-contract.json']:
        shutil.copyfile(REGISTRY / name, OUT / 'manifests' / name)
    write(OUT / 'manifests/baseline-manifest.json', {'git': git_state(), 'sha256': hashes,
          'old_experiments_frozen': True, 'raw_captures_opened': 0})
    write(OUT / 'manifests/registry-complete.json', {'pairs': len(p), 'parents': 600, 'contents': 30,
          'pairs_by_protocol': EXPECTED, 'cross_fold_registered_carriers': cross})
    checkpoint('Q06_registry_complete', {'parents': 600, 'pairs': len(p)})
    print('Registry complete:', len(p), 'pairs; zero registered-carrier cross-fold conflicts', flush=True)


if __name__ == '__main__':
    run()

