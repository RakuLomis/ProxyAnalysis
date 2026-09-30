"""Frozen Extend v3 execution settings; imports do not read experimental data."""
import sys, json, importlib.util
from pathlib import Path
import numpy as np
import pandas as pd
import torch

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'src'))
from proxy_analysis.extend_calibration.audit import read,write,file_hash,digest
from proxy_analysis.extend_calibration.bundles import Bundle
BASE=ROOT/'outputs/extend-calibration-20260930/run-01/extraction-03'
PREP=BASE/'training-preparation-01'
OUT=BASE/'formal-01'
SEEDS=[20260918,20260919,20260920]
ARMS=['raw','center','marginal','paired','cyclic','group']
FEATURES={'W':['W_up','W_down','P_up','P_down','R_up','R_down'],
          'T':['U_up','U_down','E_up','E_down','R_up','R_down']}
NUMERIC={'W':FEATURES['W'],'T':FEATURES['T']+['F']}

def sha(path):
    """JSON paths are strings; normalize at the formal worker's I/O boundary."""
    return file_hash(Path(path))

def contract_path():return OUT/'execution-contract-revision-02.json'

def contract_hash():return sha(contract_path())

def assert_artifact_contract(done,path):
    if done['contract']==contract_hash():return
    registry=OUT/'repair-02/compatibility.json'
    current=read(contract_path())
    assert sha(registry)==current['repair']['compatibility_sha256'],'Compatibility registry changed'
    accepted=read(registry)
    assert done['contract']==accepted['old_contract_sha256'],'Unregistered artifact contract'
    key=str(Path(path).resolve())
    assert key in accepted['generation_seals'],'Only individually audited generation artifacts are compatible'
    assert sha(path)==accepted['generation_seals'][key],'Historical generation seal changed'

def device():
    if not torch.cuda.is_available():raise RuntimeError('CUDA required; no CPU fallback')
    return torch.device('cuda')

def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);return mod

def metadata(name):
    track,protocol,f,g,r=name.split('-')
    return dict(scenario=name,track=track,protocol=protocol,fold=int(f[1:]),business_group=int(g[1:]),rotation=int(r[1:]))

def folders():
    result=sorted((PREP/'packages/paired').iterdir())
    assert len(result)==1080
    return result

def checkseal(path):
    path=Path(path);done=read(path)
    assert_artifact_contract(done,path)
    for p,h in done['files'].items():assert sha(p)==h,p
    return done

def checkpoint(dest,extra):
    write(dest/'complete.json',{**extra,'contract':contract_hash(),
          'files':{str(p):sha(p) for p in dest.iterdir() if p.is_file() and p.name!='complete.json'}})

def later_package(name,kind,role):
    # Deliberately unavailable to generation/training Bundle. Reference unlocks only after predictions seal.
    assert (kind,role) in [('reference','U_post'),('scoring','H_post'),('scoring','H_labels')]
    mode='restricted' if kind=='reference' else None
    if mode:
        seal=read(OUT/(mode+'-prediction-seal.json'))
        assert seal['passed'] and sha(OUT/(mode+'-predictions.parquet'))==seal['predictions_hash']
    if role=='H_labels':
        for mode in ['restricted','reference']:
            seal=read(OUT/(mode+'-prediction-seal.json'))
            assert seal['passed'] and sha(OUT/(mode+'-predictions.parquet'))==seal['predictions_hash']
    folder=PREP/'packages'/kind/name;meta=read(folder/'manifest.json');item=meta['files'][role]
    path=folder/item['filename'];assert path.resolve().parent==folder.resolve() and sha(path)==item['sha256']
    f=pd.read_parquet(path);assert list(f)==item['columns'];return f

def freeze():
    device();pr=read(PREP/'preregistration.json')
    # Verify all originally registered inputs, without rewriting preparation's historical authorization flag.
    for field,value in pr.items():
        if isinstance(value,dict) and value and all(isinstance(v,str) and len(v)==64 for v in value.values()):
            for p,h in value.items():assert sha(ROOT/p)==h,p
    assert read(PREP/'package-gate.json')['passed'] and read(PREP/'cuda-smoke.json')['passed']
    legacy=[ROOT/'src/proxy_analysis/feasible_summary_calibration/model.py',ROOT/'eval/hy2_carrier_calibration/window_model.py',
            ROOT/'eval/hy2_carrier_calibration/experiment.py',ROOT/'eval/paired_calibration_budget/train.py']
    paths=[*Path(__file__).parent.glob('formal_*.py'),*legacy,
           Path(__file__).with_name('run_formal_pipeline.py'),Path(__file__).with_name('register_repair_v3.py'),
           ROOT/'tests/test_extend_formal_v3.py']
    contract={'parent_preregistration':sha(PREP/'preregistration.json'),'formal_training_authorized':True,
        'authorization':'User: 是的，请你继续; approval of 19440 restricted + 3240 reference fits',
        'files':{str(p):sha(p) for p in sorted(paths)},'learning':pr['learning'],
        'new_repetitions':[1,2,3,4],'classifier_scale':'C_pre log1p only',
        'reference_after_restricted_prediction_seal':True,'no_parameter_search':True,
        'W_sampling':'legacy uniform 24 residual rows / 96 Cartesian group rows',
        'T_sampling':'legacy scenario-query-view seeded content/donor draw',
        'OS_security_sandbox_claimed':False}
    old=read(OUT/'execution-contract.json')
    assert {k:v for k,v in contract.items() if k!='files'}=={k:v for k,v in old.items() if k!='files'},'Scientific contract changed'
    registry=OUT/'repair-02/compatibility.json';accepted=read(registry)
    assert accepted['passed'] and accepted['old_contract_sha256']==sha(OUT/'execution-contract.json')
    contract['repair']={'revision':2,'reason':'JSON string path normalization and explicitly audited generation resumption',
        'authorization':'User approved repair plan; no scientific changes',
        'old_contract_sha256':sha(OUT/'execution-contract.json'),'compatibility_sha256':sha(registry)}
    p=contract_path()
    if p.exists():assert read(p)==contract,'Execution code/input changed after freeze'
    else:write(p,contract)
    return contract
