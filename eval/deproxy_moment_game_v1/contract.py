"""Bind historical assets without decoding deferred query/labels."""
from common import *
import platform,inspect

def register():
    configure('trusted');require(not (OUT/'manifests/contract.json').exists(),'Contract already exists')
    parent=ASSOC/'manifests/experiment-contract.json';require(sha(parent)==read(parent.with_name('seal.json'))['sha256'],'Parent contract seal')
    c=read(parent);files={};rr=[];pack=read(ASSOC/'packages/complete.json');require(pack['passed'],'Old packages incomplete')
    fields=['id','outer','inner','target','calibration','sources','group','missing','train_contents','C_contents','U_contents','validation_contents']
    def bind(p,kind,rid=None,expected=None,defer=False):
        p=Path(p);require(p.exists(),'Missing source '+str(p));h=expected if defer else sha(p)
        if expected is not None and not defer:require(h==expected,'Source hash changed '+rel(p))
        files[rel(p)]=dict(kind=kind,role_id=rid,sha256=h,deferred=defer)
    for p in [parent,ASSOC/'packages/complete.json',ASSOC/'manifests/pair-join-audit.parquet',
              PREP/'manifests/content-folds.parquet',PREP/'manifests/cohort-visits.parquet']:
        bind(p,'metadata')
    bind(NATIVE,'native-training-only',expected=c['bindings'][rel(NATIVE)])
    for old in c['inner_roles']+c['roles']:
        r={k:old[k] for k in fields};rid=r['id'];inner=r['inner'] is not None
        require(len(r['train_contents'])==(18 if inner else 24) and len(r['validation_contents'])==6,'Role size')
        require(not set(r['train_contents'])&set(r['validation_contents']) and not set(r['C_contents'])&set(r['U_contents']),'Content conflict')
        require(r['missing']==MASKS[r['group']],'Business mask')
        if inner:require(r['target'] not in r['sources']+[r['calibration']],'Actual target in source task')
        for name in ['source-post','source-pre','C-post','query','labels']:
            p=PREP/'packages'/rid/(name+'.parquet');i=c['packages'][rel(p)]
            require(i['role_id']==rid,'Package role binding')
            bind(p,name,rid,i['sha256'],defer=name in ['query','labels'])
        p=ASSOC/'base-models'/rid/'P-small.pt';bind(p,'base',rid,pack['files'][rel(p)])
        bind(p.with_suffix('.json'),'metadata',rid)
        rr.append(r)
    require(len(rr)==780,'Context count')
    cfg=dict(version='DP-GAN1-M-v1',authorized_by_user=True,plan_sha256=sha(PLAN),proposal_sha256=sha(PROPOSAL),
        training_enabled=False,training_permission='P0-complete seal required for P1; P1 cost/numeric pass required for full',
        files=files,inner_roles=rr[:720],roles=rr[720:],recipes=RECIPES,gammas=GAMMAS,betas=BETAS,seeds=SEEDS,
        primary='F-P-FUSE',alpha=1.,rank=8,steps=2000,rec=1.,fid=1.,gap=1.,dev=.1,
        activity_cap=86400,forecast_limit=69120,clip=5.,dtype='float64',CPU_training=False,H_pre=False,
        source_seed=20261014,outer_seeds=SEEDS,selection_tie=1e-12,bootstrap=10000,bootstrap_seed=20261016,
        simplex_sum_gate=1e-10,simplex_min_gate=-1e-12,head_gradient_gate=1e-5,replay_gate=1e-10,
        worker_permissions={'P':'paired training','G':'independent margins/centers; no pair identity','E':'post only'},
        authorization='2026-10-16 user approved saved P0-P6 plan; P0/P1 first, no pilot F1 gate')
    immutable(OUT/'manifests/contract.json',cfg);immutable(OUT/'manifests/contract.seal.json',dict(sha256=sha(OUT/'manifests/contract.json')))
    save(OUT/'manifests/source-bindings.parquet',pd.DataFrame([dict(path=p,**v) for p,v in files.items()]))
    save(OUT/'manifests/role-membership.parquet',pd.DataFrame(rr))
    for name,p in [('proposal.md',PROPOSAL),('approved-plan.md',PLAN)]:writable(OUT/'manifests'/name).write_bytes(p.read_bytes())
    immutable(OUT/'environment.json',dict(python=sys.executable,python_version=platform.python_version(),torch=torch.__version__,cuda=torch.version.cuda,
        GPU=torch.cuda.get_device_name(),GPU_memory_MiB=torch.cuda.get_device_properties(0).total_memory/1048576,
        AMP=False,TF32=False,deterministic=True,LBFGS_file=inspect.getfile(torch.optim.LBFGS),LBFGS_sha256=sha(inspect.getfile(torch.optim.LBFGS))))
    immutable(OUT/'budget.json',dict(cap_seconds=86400,used_seconds=0.,items=[]))
    progress('P0_registered',contexts=780,training_enabled=False)
