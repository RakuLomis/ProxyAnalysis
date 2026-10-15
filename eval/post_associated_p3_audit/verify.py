"""Independent P3 seal audit. No torch import, data reads, fitting or scoring."""
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[2]
RUN = ROOT/'outputs/post-input-associated-representation-20261014/run-03'
SOURCE = RUN.parent/'run-02'


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda: f.read(1024*1024), b''):
            h.update(b)
    return h.hexdigest()


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def main():
    completion = read(RUN/'completion.json')
    assert completion['status'] == 'closed_all_exact_fallback' and completion['passed']
    assert completion['verification_sha256'] == sha(RUN/'verification.json')
    verified_files = 0
    for path in [RUN/'verification.json', RUN/'manifests/models-complete.json', RUN/'manifests/repair-code.json']:
        manifest = read(path)
        assert manifest['passed']
        for name, digest in manifest['files'].items():
            assert sha(ROOT/name) == digest, name
            verified_files += 1
    science = read(SOURCE/'manifests/experiment-contract.json')
    endpoints = read(RUN/'manifests/endpoints.json')
    assert endpoints == read(SOURCE/'manifests/endpoints.json')
    expected = {(r['id'], a, s) for r in science['roles']
                for a in ['A0','A1','A2','A3'] for s in science['seeds']}
    assert len(endpoints) == len(expected) == 720
    assert {(e['role_id'],e['arm'],e['seed']) for e in endpoints} == expected
    assert all(e['fallback'] and e['residual_path'] is None and e['lambda_value'] is None for e in endpoints)
    decisions = read(SOURCE/'selections/decisions.json')
    assert len(decisions) == 180 and all(d['fallback'] and not d['enabled'] for d in decisions)
    replay = read(RUN/'audits/fallback-replay.json')
    assert replay['passed'] and replay['endpoints'] == 720 and replay['endpoint_case_replays'] == 54000
    assert replay['new_arm_fallback_seed_endpoints'] == 540 and replay['reference_seed_endpoints'] == 180
    assert all(replay[k] == 0 for k in ['logit_max_error','logprob_max_error','probability_max_error','changed_classes','new_training_fits'])
    assert all(replay['all_checks'].values()) and replay['exact_original_parameters']
    integrity = read(RUN/'audits/historical-integrity.json')
    assert integrity['passed'] and all(integrity[k] == 0 for k in ['added','removed','changed'])
    old = read(RUN/'manifests/historical-snapshot.json')['files']
    critical = [SOURCE/'completion.json', SOURCE/'progress.json', SOURCE/'ledger.json',
                SOURCE/'selections/decisions.json', SOURCE/'selections/candidate-metrics.json',
                SOURCE/'manifests/experiment-contract.json', SOURCE/'manifests/engineering-code.json',
                ROOT/'eval/post_input_associated_representation_v3/final_train.py']
    for p in critical:
        assert sha(p) == old[p.relative_to(ROOT).as_posix()]
    stopped = read(SOURCE/'completion.json')
    assert stopped['status'] == 'stop_stage_gate' and not stopped['passed'] and not stopped['H_scored']
    ledger = read(RUN/'ledger.json')
    assert ledger['inherited_training_ledger'] == read(SOURCE/'ledger.json')
    assert all(ledger[k] == 0 for k in ['new_teacher_fits','new_residual_fits','new_LR_fits','new_training_wall_seconds'])
    assert not completion['formal_complete'] and not completion['H_scored'] and not completion['primary_comparisons_scored']
    assert not (RUN/'predictions').exists() and not (SOURCE/'predictions').exists()
    result = dict(passed=True, endpoint_product_verified=720, all_strategy_decisions_unchanged=180,
        manifest_file_bindings_verified=verified_files, critical_source_files_rechecked=len(critical),
        cuda_replay_record_verified=True, no_H_scoring=True, new_training_fits=0,
        original_stop_preserved=True, code_sha256=sha(Path(__file__)))
    path = RUN/'independent-audit.json'
    with path.open('x', encoding='utf-8') as f:
        json.dump(result,f,ensure_ascii=False,sort_keys=True,indent=2)
        f.write('\n')
    print(json.dumps(result,ensure_ascii=False,indent=2))


if __name__ == '__main__':
    main()
