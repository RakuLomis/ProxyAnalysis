"""Freeze both experiment designs before any held-out predictions are read."""
from common import *


def main():
    target=OUT/'contract.json';assert not target.exists()
    gates=['gate-A.json','gate-packages.json','engineering-replay.json','worker-assembly.json']
    for name in gates:assert read(OUT/name)['passed']
    code=list(Path(__file__).parent.glob('*.py'))+[
        ROOT/'eval/hy2_carrier_calibration/window_model.py',
        ROOT/'eval/hy2_carrier_calibration/experiment.py',
        ROOT/'src/proxy_analysis/conditional_drift/model.py',
        ROOT/'src/proxy_analysis/extend_calibration/audit.py']
    artifacts=[OUT/n for n in gates+['source-lock.json','cohort.parquet','global-folds.parquet','scenarios.parquet']]
    artifacts+=list((OUT/'roles').glob('*.json'))+list((OUT/'generator-roles').glob('*.json'))
    artifacts+=list((OUT/'packages').glob('*/*/manifest.json'))
    write(target,{'version':'business-protocol-eval-1','formal_training_allowed':False,
          'waiting_for':'Gate B user confirmation of 525 classifiers and 5700 production Ridge fits',
          'protocols':PROTOCOLS,'features':FEATURES,'visits':600,'contents':30,'repetitions':[1,2,3,4],
          'outer_folds':5,'internal_generation_folds':4,'seeds':SEEDS,
          'E1':{'train':480,'test':120,'shared_classifiers':75,'independent_classifiers':75},
          'E2':{'train':384,'test':24,'held_out_protocols':5,'shared_classifiers':375},
          'model':{'parameters':422,'hidden':32,'classes':6,'steps':1000,'lr':.001,'weight_penalty':.5e-4,
                   'cuda_required':True,'float':'float32','tf32':False,'scaler':'source training post log1p population mean/std',
                   'loss':'0.5 real-post CE + 0.5 auxiliary CE + L2; M0/I0 auxiliary repeats real post'},
          'generation':{'queries':100,'methods':['paired','group','cyclic'],'views':8,'fits':5700,
                        'float':'float64','alpha':1,'fit_contents':18,'inner_fit_contents':17,
                        'residual_rows':{'paired':72,'cyclic':72,'group':288},'redraws':0},
          'statistics':{'metric':'six-class macro F1','aggregation':'per seed OOF then equal deployment mean',
                        'primary':['M2-M0','M2-M1','M2-M3'],'families':'E1 and E2 separate, three contrasts each',
                        'bootstrap':10000,'bootstrap_seed':20260928,'cluster':'business-stratified content shared across protocols/seeds/arms',
                        'CI_quantiles':[.05/6,1-.05/6],'ordinary_CI':[.025,.975],
                        'conditional_on_fixed_models':True,'worst_protocol_is_secondary':True},
          'security':'software allowlists, package separation and hashes, not OS sandbox',
          'test_selection':'no early stopping, no target scaling, no checkpoint selection',
          'historical_source_limits':{'unobserved_SYN_cases':5,'complete_TCP_birth_reconstruction':False},
          'code_hashes':{str(p.relative_to(ROOT)):file_hash(p) for p in code},
          'artifact_hashes':{str(p.relative_to(ROOT)):file_hash(p) for p in artifacts}})
    print({'contract_sha256':file_hash(target),'classifiers':525,'production_Ridge_fits':5700,'formal_training_allowed':False})


if __name__=='__main__':main()
