"""Seal all methods and code before any real classifier is fitted or scored."""
from common import *

def run():
    path=OUT/'manifests/experiment-contract.json'
    require(not path.exists(),'Contract already exists; no implicit overwrite')
    require(read(OUT/'manifests/unit-tests.json')['passed'],'Artificial tests required before registration')
    b=read(OUT/'manifests/baseline-manifest.json')
    pkg=read(OUT/'manifests/package-manifest.json')
    source={rel(p):sha(p) for p in Path(__file__).parent.rglob('*.py')}
    write(path,{'date':'2026-10-05','registered_before_classification_results':True,
        'roles':pkg['roles'],'features':FEATURES,'histogram_columns':HIST,'labels':LABELS,
        'arms':ARMS,'seeds':SEEDS,'source_sha256':source,'packages_sha256':pkg['sha256'],
        'kernels_sha256':b['kernel_sha256'],'plan_sha256':sha(PLAN),'CUDA_required':True,
        'byte_edges':BYTE_EDGES,'count_edges':COUNT_EDGES,'feature_weights':WEIGHTS,
        'source_and_direct_post_alpha_beta':1,'class_prior':'uniform 1/6','softmax_temperature':1,
        'probability_interpretation':'length-normalized composite score, not exact calibrated bag posterior',
        'LR':{'regularization':1e-3,'bias_regularized':False,'dtype':'float64','optimizer':'LBFGS',
              'max_iter':500,'tolerance_grad':1e-9,'tolerance_change':1e-12,'line_search':'strong_wolfe'},
        'MLP':{'architecture':[96,32,6],'activation':'ReLU','parameters':3302,'optimizer':'AdamW',
               'lr':1e-3,'weight_decay':1e-4,'updates':1000,'batch_size':96,'dtype':'float32',
               'dropout':False,'BatchNorm':False,'early_stopping':False},
        'primary_family':{'size':8,'comparators':['G3','G5'],'endpoint':'macro_F1'},
        'baseline_family':{'size':8,'comparators':['G0','G2'],'endpoint':'macro_F1'},
        'bootstrap':{'samples':10000,'seed':20261005,'unit':'content, stratified by six labels',
                     'shared_across_protocols_and_arms':True,'model_conditional':True},
        'no_test_pre_inference':True,'no_test_based_hyperparameter_or_feature_selection':True,
        'no_new_PCAP_reads':True,'no_new_SSL_training':True})
    print('Sealed experiment contract before fitting and real predictions',flush=True)

if __name__=='__main__':
    run()
