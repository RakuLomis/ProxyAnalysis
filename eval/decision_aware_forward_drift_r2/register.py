"""Bind only 48 source roles; no numeric decoding of deferred queries."""
from common import *
import platform

def run():
    configure('trusted'); require(not (OUT/'budget.json').exists() and not (OUT/'manifests').exists(),'New run only; no implicit restart')
    require(not OUT.exists() or all(p.name=='logs' for p in OUT.iterdir()),'Only initial launcher logs may preexist')
    parent=ROOT/'outputs/decision-aware-forward-drift-20261017/pilot-01'
    require((parent/'stop-record.json').exists(),'Preserve failed parent')
    start=read(parent/'budget.json')['start_unix'];inherited=time.time()-start
    immutable(OUT/'budget.json',dict(start_unix=start,cap_seconds=10800,forecast_gate_seconds=8640,
        items=[dict(stage='inherited-parent-and-engineering-repair',seconds=inherited,returncode=0)],used_seconds=inherited))
    immutable(OUT/'manifests/engineering-amendment.json',dict(parent_stop_sha256=sha(parent/'stop-record.json'),
        correction='C raw histogram replay 1e-14 with exact trusted identity ledger, not bit equality',
        zero_material_exact_unchanged=True,model_loss_permissions_numeric_gates_unchanged=True,
        inherited_seconds=inherited,diagnostic_C_max_error=1.1102230246251565e-16,
        exact_visit_content_protocol_label_order=True,failed_parent_training_paths=0))
    st=read(ST/'contract.json'); require(sha(ST/'contract.json')==read(ST/'seal.json')['contract_sha256'],'ST role contract')
    require(len(st['roles'])==48,'48 fixed source tasks')
    rawseal=read(RAW/'manifests/P0-complete.json'); rawc=read(RAW/'manifests/contract.json')
    require(sha(RAW/'manifests/contract.json')==read(RAW/'manifests/contract.seal.json')['sha256'],'Raw source contract')
    assoc=read(ASSOC/'packages/complete.json'); files={}
    def add(p,kind,rid=None,h=None):
        require(p.exists(),'Missing source '+str(p)); actual=sha(p) if h is None else h
        if kind not in ['query','labels']: require(sha(p)==actual,'Source binding changed')
        files[rel(p)]=dict(kind=kind,role_id=rid,sha256=actual)
    rs=st['roles']
    for r in rs:
        rid=r['id']; require(r['outer']==0 and r['inner'] in [1,2,3,4],'Source role only')
        require(r['target'] not in r['sources']+[r['calibration']],'Actual target excluded')
        require(not set(r['train_contents'])&set(r['validation_contents']),'Content intersection')
        for name in ['source-pre','source-post','C-post','query','labels']:
            p=PREP/'packages'/rid/(name+'.parquet'); add(p,name,rid,st['files'][rel(p)]['sha256'])
        for name,kind in [('classification','classification')]:
            p=ASSOC/'packages'/rid/(name+'.pt'); add(p,kind,rid,assoc['files'][rel(p)])
        p=ASSOC/'base-models'/rid/'P-small.pt'; add(p,'base',rid,assoc['files'][rel(p)])
        p=ROOT/'outputs/joint-affine-transfer-20261007/run-01/maps'/rid/f'JA1-eta{r["eta"]:g}.pt'
        add(p,'map',rid,st['files'][rel(p)]['sha256'])
        p=RAW/'packages'/rid/'complete.json'; require(sha(p)==rawseal['files'][rel(p)],'Raw parent seal')
        rawfiles=read(p)['files']
        for sub in ['paired/train.pt','group/pre.pt','group/post.pt']:
            p=RAW/'packages'/rid/sub; add(p,'raw-'+sub,rid,rawfiles[rel(p)])
            require(read(p.with_suffix('.json'))['role_id']==rid,'Raw role sidecar')
        p=RAW/'trusted'/rid/'paired-train-ledger.parquet';add(p,'trusted-ledger',rid,rawseal['files'][rel(p)])
    add(NATIVE,'diagnostic-native',None,rawc['files'][rel(NATIVE)]['sha256'])
    code={rel(p):sha(p) for p in sorted(CODE.glob('*.py'))}
    c=dict(experiment='DA-FGAN1-Pilot-v1',roles=rs,files=files,code=code,plan_sha256=sha(PLAN),
        raw_P0_seal_sha256=sha(RAW/'manifests/P0-complete.json'),old_ST_contract_sha256=sha(ST/'contract.json'),
        query_pre_authorized_after_predictions=True,actual_H_U_authorized=False,
        seed=20261017,rank=8,steps=2000,lr=.0003,lambda_cov=1.,lambda_rel=1.,lambda_dev=.1,generator_L2=.0001,
        cap_seconds=10800,forecast_gate_seconds=8640,arms=ARMS,head_limit=192,path_limit=144,
        old_methods_unchanged=True,inherit_40h_budget=False,native_training_decode=False)
    p=OUT/'manifests/experiment-contract.json'; immutable(p,c); immutable(p.with_suffix('.seal.json'),dict(sha256=sha(p)))
    immutable(OUT/'environment.json',dict(python=sys.executable,python_version=platform.python_version(),torch=torch.__version__,cuda=torch.version.cuda,
        gpu=torch.cuda.get_device_name(0),dtype='float64',cuda_only=True,TF32=False,AMP=False))
    progress('registered',roles=48,actual_H_U_reads=0,query_reads=0)

if __name__=='__main__':run()
