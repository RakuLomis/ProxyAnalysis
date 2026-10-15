"""One bounded P3 engineering closeout; never run training or H evaluation."""
from common import *
import seal as p3
import verify


def main():
    require(not OUT.exists(), 'Refuse overwrite/retry of repair run')
    require(not (SOURCE/'stage.lock').exists(), 'Historical stage active')
    require(not (SOURCE/'manifests/models-complete.json').exists(), 'Historical P3 already sealed')
    started = time.perf_counter()
    before = snapshot()
    oldstop = read(SOURCE/'completion.json')
    require(oldstop['status'] == 'stop_stage_gate' and oldstop['stage'] == 'P3_final_train'
            and oldstop['reason'] == "'WindowsPath' object is not subscriptable", 'Unexpected historical stop')
    ledger = read(SOURCE/'ledger.json')
    write(OUT/'manifests/historical-snapshot.json', dict(files=before, passed=True, method='SHA256 all files in both historical runs and original experiment code plus plan'))
    code = [p for p in CODE.glob('*.py')]
    seal(OUT/'manifests/repair-code.json', code, passed=True, scope='P3_path_join_and_exact_fallback_only')
    write(OUT/'manifests/repair-contract.json', dict(
        authorization='User authorized P3 seal interface and exact fallback verification only; preserve original stop, no training, no scientific changes.',
        source_run=rel(SOURCE), source_completion_sha256=sha(SOURCE/'completion.json'),
        source_scientific_contract=rel(SOURCE/'manifests/experiment-contract.json'),
        source_scientific_contract_sha256=sha(SOURCE/'manifests/experiment-contract.json'),
        source_decisions_sha256=sha(SOURCE/'selections/decisions.json'),
        science_unchanged=True, model_unchanged=True, loss_unchanged=True, permission_unchanged=True, gates_unchanged=True,
        allowed_execution=['immutable source hash checks','existing all-fallback endpoint sealing','CUDA synthetic-input exact inference replay'],
        forbidden_execution=['trainer import/call','new fitting','actual H/U data reads','H scoring','hyperparameter selection','Stage B'],
        synthetic_seed=20261014, cases_per_role=75, endpoint_count=720, role_count=60))
    contract = p3.run()
    result = verify.run(contract)
    after = snapshot()
    require(before == after, 'Historical outputs/code/stop/plan changed')
    require(read(SOURCE/'ledger.json') == ledger, 'Historical training ledger changed')
    immutable = dict(passed=True, historical_files=len(before), added=0, removed=0, changed=0,
                     source_stop_unchanged=True, source_ledger_unchanged=True, original_code_unchanged=True,
                     source_decisions_unchanged=True, scientific_contract_unchanged=True)
    write(OUT/'audits/historical-integrity.json', immutable)
    write(OUT/'audits/access.json', dict(passed=True, reads=ACCESS,
        immutable_scan_scope='Historical run outputs/code only, byte hashes; no external PCAP or H/U data packages.',
        H_reads=0, actual_U_reads=0, trainer_imports=0, training_fits=0))
    write(OUT/'ledger.json', dict(new_teacher_fits=0, new_residual_fits=0, new_LR_fits=0,
        new_training_wall_seconds=0, inherited_training_ledger=ledger, engineering_wall_seconds=time.perf_counter()-started))
    files = [p for p in OUT.rglob('*') if p.is_file()]
    seal(OUT/'verification.json', files, passed=True, P3_sealed=True, fallback_verified=True,
        immutable_verified=True, exact_fallback_decisions=180, exact_fallback_seed_endpoints=540,
        reference_seed_endpoints=180, new_training_fits=0, actual_H_reads=0, actual_U_reads=0)
    write(OUT/'completion.json', dict(status='closed_all_exact_fallback', passed=True,
        engineering_closeout_complete=True, stage_a_candidate_closed=True,
        P3_sealed=True, fallback_verified=True, new_training_fits=0,
        formal_complete=False, H_scored=False, primary_comparisons_scored=False,
        scientific_outcome='No source-qualified residual branch; all 180 decisions remain exact P-small fallback.',
        original_stop_preserved=True, verification_sha256=sha(OUT/'verification.json')))
    print('closeout_complete', json.dumps(dict(historical_files=len(before), endpoints=720,
        training_fits=0, H_scored=False, seconds=time.perf_counter()-started)), flush=True)


if __name__ == '__main__':
    main()
