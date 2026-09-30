"""Publish quality-labelled audit tables, NOT training permission packages."""
from pathlib import Path
import sys
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'src'))
from proxy_analysis.extend_calibration.audit import write, file_hash


def main():
    base = ROOT/'outputs/extend-calibration-20260930/run-01/extraction-01'
    out = base/'catalog-01'
    out.mkdir(exist_ok=True)
    assert not (out/'manifest.json').exists(), 'completed catalog is immutable'
    pool = pd.read_parquet(base/'metadata-qualified-pool.parquet')
    cv = pd.read_parquet(base/'full-coverage.parquet')
    metadata = pool[['session_id','protocol','content_id','label','repetition']].merge(
        cv[['session_id','W_gate_passed','review_reasons','T_candidate_pairs','T_common_pairs']],
        on='session_id', validate='one_to_one')
    files = []
    for track, columns in [('W',['W_up','W_down','P_up','P_down','R_up','R_down']),
                           ('T',['U_up','U_down','E_up','E_down','R_up','R_down','F'])]:
        f = pd.read_parquet(base/f'full-{track}-features.parquet').merge(metadata, on='session_id', validate='many_to_one')
        if track == 'T':
            f = f[f.protocol.ne('anytls') & f.F.gt(0)].copy()
            f['status'] = 'observed_common_pair_summary; visit_scope_and_isolation_not_released'
        else:
            f['status'] = f.W_gate_passed.map({True:'coverage_passed; isolation_not_released',False:'incomplete_or_ambiguous; not_usable_as_complete_summary'})
        f['training_eligible'] = False
        f['representation'] = track
        path = out/f'{track}-candidate-features.parquet'
        f.to_parquet(path, index=False)
        files.append({'file':path.name,'rows':len(f),'sha256':file_hash(path),'numeric_model_allowlist':columns})
    write(out/'manifest.json', {'purpose':'auditable candidate features; NOT restricted/group/reference/scoring packages',
        'training_allowed':False,'hy2':'measurement-only, not extracted here', 'files':files,
        'metadata_is_not_model_input':True, 'AnyTLS_zero_T_rows_removed_from_catalog':True,
        'warning':'mathematical validation does not imply complete capture, correct epoch attribution, or split isolation'})
    print({r['file']:r['rows'] for r in files})


if __name__ == '__main__':
    main()
