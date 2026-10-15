"""P0 metadata only registration; no H/U feature arrays."""
from common import *

def run():
    configure();require(not (OUT/'manifests/seal.json').exists(),'New run already registered')
    parent=read(FORMAL/'manifests/experiment-contract.json')
    require(sha(FORMAL/'manifests/experiment-contract.json')==read(FORMAL/'manifests/seal.json')['contract_sha256'],'Parent seal')
    rs=parent['roles'];ins=parent['inner_roles'];require(len(rs)==60 and len(ins)==720,'Role count')
    refs={x['role_id']:x for x in parent['references'] if x['arm']=='P-small'}
    packages={};bindings={};rows=[];cache=hashlib.sha256(np.ones(10,dtype=np.float64).tobytes()).hexdigest()
    def bind(p,h=None):
        h=h or sha(p);require(sha(p)==h,'Changed source');bindings[rel(p)]=h
    bind(NATIVE,parent['fixed_files'][rel(NATIVE)] if rel(NATIVE) in parent['fixed_files'] else None)
    # Native digest must agree with original trusted CT inventory, not just current file.
    original=read(PREP/'manifests/input-inventory.json')['sha256'][rel(NATIVE)]
    require(bindings[rel(NATIVE)]==original,'Native source binding changed')
    bind(FORMAL/'manifests/experiment-contract.json')
    for r in ins+rs:
        require(not set(r['train_contents'])&set(r['validation_contents']),'Content overlap')
        require(not set(r['C_contents'])&set(r['U_contents']),'C/U overlap')
        if r['inner'] is not None:require(r['target'] not in r['sources']+[r['calibration']],'Actual target in source feedback')
        for name in ['source-pre.parquet','source-post.parquet','C-post.parquet','query.parquet','labels.parquet']:
            p=PREP/'packages'/r['id']/name
            info=dict(parent['packages'][rel(p)]);info['role_id']=r['id'];packages[rel(p)]=info
            if name not in ['query.parquet','labels.parquet']:bind(p,info['sha256'])
        tp=FORMAL/'tasks'/r['id']/'P.pt';bind(tp,parent['fixed_files'].get(rel(tp)))
        require(sha(tp)==read(tp.with_suffix('.json'))['sha256'],'Task sidecar')
        r['old_task']=rel(tp)
        if r['inner'] is None:
            r['base_path']=refs[r['id']]['model_path'];bind(ROOT/r['base_path'],refs[r['id']]['model_sha256'])
        else:
            p=FORMAL/'feedback-cache/P'/r['id']/(cache+'.pt')
            require(p.exists(),'Missing qualified q=1 source base')
            bind(p,read(p.with_suffix('.json'))['sha256']);r['base_path']=rel(p)
        rows.append(dict(role_id=r['id'],inner=r['inner'],outer=r['outer'],target=r['target'],calibration=r['calibration'],group=r['group'],t=r['t'],eta=r['eta'],base_path=r['base_path'],train_contents=r['train_contents'],validation_contents=r['validation_contents']))
    pairsmeta=read(PREP/'manifests/cohort-audit.json')
    require(pairsmeta['pairs']==23566 and pairsmeta['visits']==480 and pairsmeta['contents']==30,'Cohort')
    c=dict(version='post-associated-residual-stage-A-v1',authorized='2026-10-14 user approved saved plan',plan_sha256=sha(PLAN),
           roles=rs,inner_roles=ins,bindings=bindings,packages=packages,seeds=SEEDS,configs=CONFIGS,
           teacher=[96,16,8,6],branch=[96,16,8],head=[104,6],steps=1000,lr=.001,weight_L2=.01,
           residual_alpha=.1,gradient_clip=5.,teacher_seed=20261014,activation='ReLU',
           enable=dict(CE_U_improvement=.002,F1_U_nonnegative=True,C_overall_margin=-.01,C_per_deployment_margin=-.02),
           training_cap_seconds=43200,preflight_limit_seconds=34560,bootstrap=10000,bootstrap_seed=20261014,
           primary=['A3-A0','A3-A1','A3-A2'],confidence=1-.05/3,Stage_B_authorized=False,
           H_pre_forbidden=True,actual_U_forbidden=True,PCAP_forbidden=True,CPU_training_fallback=False,
           environment=dict(python=sys.version,torch=torch.__version__,cuda=torch.version.cuda,gpu=torch.cuda.get_device_name(0),TF32=False))
    write(OUT/'manifests/experiment-contract.json',c);write(OUT/'manifests/seal.json',dict(sha256=sha(OUT/'manifests/experiment-contract.json')))
    write(OUT/'ledger.json',dict(training_wall_seconds=0.,source_LR_new=0,teachers=0,residual_fits=0))
    save(pd.DataFrame(rows),OUT/'manifests/role-index.parquet')
    write(OUT/'manifests/source-bindings.json',bindings)
    write(OUT/'manifests/permission-contract.json',dict(actual_U_forbidden=True,H_pre_forbidden=True,
          H_post_after_all_models=True,H_labels_after_all_predictions=True,anonymous_group_no_pair_ID=True,
          zero_lambda_does_not_read_targets=True,role_filtered_native_training_only=True))
    write(OUT/'inventory.json',dict(passed=True,roles=60,source_tasks=720,visits=480,contents=30,pairs=23566,
          source_bases_reused=720,outer_bases_reused=60,new_fits=0,H_numeric_reads=0,U_numeric_reads=0,
          native_read='digest and schema only',CUDA=True))
    progress('P0_inventory_complete',roles=60,inner_roles=720,new_fits=0)

if __name__=='__main__':run()
