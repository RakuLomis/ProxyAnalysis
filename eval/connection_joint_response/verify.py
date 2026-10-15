"""Independent preparation and probability audit; not a classification completion."""
from common import *

def run():
    with stage('initial_verification'):
        c=contract(); pp=preparations(); p=c['fixed_files']
        ancestor=read(ROOT/'outputs/calibrated-deployment-business-transfer-20261006/run-01/manifests/experiment-contract.json')
        require(ancestor['baseline_sha256'][rel(NATIVE)]==p[rel(NATIVE)],'Original native cache seal')
        require(len(pp['packages'])==2640,'Package count')
        for rp,info in pp['packages'].items():
            checked(ROOT/rp,info['sha256'],'independent-package-verification')
        audit=read(OUT/'audits/cohort-and-native.json')
        require(audit['pairs']==23566 and audit['visits']==480 and not any(audit['registered_crossfold'].values()),'Cohort audit')
        require(audit['M_replay_error']<=1e-14,'Marginal replay')
        tests=read(OUT/'audits/information-and-permission-tests.json'); require(tests['passed'],'Tests incomplete')
        require(all(t['passed'] for t in tests['checks']),'Test rejection')
        d=OUT/'diagnostics/predictions/flows.parquet'; ds=read(d.with_name('complete.json'))
        checked(d,ds['sha256'],'diagnostic-prediction-verification'); require(ds['tables']==2880,'Conditional table budget')
        scores=pd.read_parquet(OUT/'diagnostics/scores/content-scores.parquet')
        require(len(scores)==11520 and np.isfinite(scores[['CE_nats','Brier','unseen_pre']]).all().all(),'Diagnostic scores')
        files={rel(q):sha(q) for q in [OUT/'manifests/experiment-contract.json',OUT/'manifests/preparation.json',
              OUT/'audits/cohort-and-native.json',OUT/'audits/information-and-permission-tests.json',d,
              OUT/'diagnostics/scores/content-scores.parquet',OUT/'diagnostics/scores/native-C-responses.parquet']}
        write(OUT/'initial-verification.json',{'passed':True,'files':files,'steps_complete':'A01-A18',
            'packages':2640,'tests':len(tests['checks']),'probability_tables':2880,'classification_complete':False,
            'classifier_fits':len(list((OUT/'models').rglob('*.pt'))),'target_U_worker_rows':0,'H_pre_worker_rows':0,
            'raw_capture_reads':0,'universal_flow_epoch_proof':False,'physical_post_input_qualified':False})

if __name__=='__main__':run()
