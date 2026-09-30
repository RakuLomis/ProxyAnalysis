"""Read-only provenance checks, including connection/capture identities; no fitting."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'src'))
from proxy_analysis.calibration_budget.common import *

def main():
    source=ROOT/'outputs/conditional-proxy-drift-0916/run-01'
    for name,key in [('contract.json','inputs'),('worker-contract.json','inputs'),('training-contract.json','files')]:
        for path,h in read(OUT/name)[key].items():assert sha(path)==h,(name,path)
    captures_path=ROOT/'outputs/content-generalization-20260916/business-01/capture-files.parquet'
    old=read(source/'contract.json')['inputs'];assert sha(captures_path)==old[str(captures_path)]
    captures=pd.read_parquet(captures_path);pairs=pd.read_parquet(source/'eligible-pairs.parquet');roles=pd.read_parquet(OUT/'roles.parquet')
    rows=[]
    for scenario,g in roles.groupby('scenario'):
        sets={r:set(h.session_id) for r,h in g.groupby('role')}
        for a,b in [('C','U'),('C','H'),('U','H')]:
            assert not sets[a]&sets[b]
            assert not set(pairs[pairs.session_id.isin(sets[a])].connection_id)&set(pairs[pairs.session_id.isin(sets[b])].connection_id)
            assert not set(captures[captures.session_id.isin(sets[a])].sha256)&set(captures[captures.session_id.isin(sets[b])].sha256)
        rows.append({'scenario':scenario,'sessions_disjoint':True,'connection_ids_disjoint':True,'capture_hashes_disjoint':True})
    save('identity-audit',rows)
    seal=read(OUT/'prediction-seal.json');assert seal['passed'] and sha(OUT/'predictions.parquet')==seal['predictions_hash']
    assert read(OUT/'statistics-complete.json')['passed']
    # Historical reference is accessed only after new predictions and statistics are sealed.
    history=pd.read_parquet(source/'classification-summary.parquet')
    save('historical-full-post-reference',history[history.arm=='T6'])
    files=[*Path(__file__).parent.glob('*.py'),*Path(ROOT/'src/proxy_analysis/calibration_budget').glob('*.py'),CONFIG]
    write(OUT/'completion.json',{'status':'complete','stages':[f'CB{i}' for i in range(9)],'classifiers':2160,'ridge_fits':3120,
        'predictions':51840,'generated_views':552960,'CUDA_training_and_inference':True,'identity_audit_scenarios':120,
        'historical_inputs_unchanged':True,'U_post_fitting_allowed':False,'historical_qualification_used_post':True,
        'software_hashes':{str(p):sha(p) for p in files},'prediction_seal':sha(OUT/'prediction-seal.json'),
        'statistics_seal':sha(OUT/'statistics-complete.json'),'scope':'Existing dual-side-audited 0916 cohort; permission simulation, not end-to-end capture saving'})
    print('CB0-CB8 complete; identity and original-input audits passed',flush=True)

if __name__=='__main__':main()
