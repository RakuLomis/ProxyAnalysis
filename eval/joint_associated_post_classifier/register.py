"""Bind only independently exported legal training assets; query files stay closed."""
from common import *

def register():
    configure();require(not (OUT/'manifests/contract.json').exists(),'Registration already exists')
    p=PARENT/'manifests/experiment-contract.json';require(sha(p)==read(PARENT/'manifests/seal.json')['sha256'],'Parent manifest')
    old=read(p);files={};rows=[]
    pack=read(PARENT/'packages/complete.json');require(pack['passed'],'Parent packages incomplete')
    def bind(p,kind,r=None,h=None,deferred=False):
        p=Path(p);require(p.is_file(),'Missing input '+str(p))
        actual=h if deferred else sha(p)
        if h is not None and not deferred:require(actual==h,'Source changed '+rel(p))
        files[rel(p)]=dict(kind=kind,role_id=None if r is None else r['id'],sha256=actual,deferred=deferred)
    for p in [PARENT/'manifests/experiment-contract.json',PARENT/'packages/complete.json',PARENT/'manifests/pair-join-audit.parquet']:
        bind(p,'provenance')
    fields=['id','outer','inner','target','calibration','sources','group','missing','eta','t',
            'train_contents','validation_contents','C_contents','U_contents']
    rs=[{k:r[k] for k in fields} for r in old['inner_roles']+old['roles']]
    require(len(old['inner_roles'])==720 and len(old['roles'])==60,'Role counts')
    for r in rs:
        rid=r['id'];inner=r['inner'] is not None
        require(not set(r['train_contents'])&set(r['validation_contents']),'Content overlap')
        require(not set(r['C_contents'])&set(r['U_contents']),'C/U overlap')
        require(len(r['train_contents'])==(18 if inner else 24) and len(r['validation_contents'])==6,'Role content sizes')
        require(r['missing']==MASKS[r['group']],'Mask mismatch')
        if inner:require(r['target'] not in r['sources']+[r['calibration']],'Actual target in inner role')
        for file,kind in [('classification.pt','classification'),('teacher/fit.pt','teacher-fit'),('trusted/groups.pt','groups')]:
            q=PARENT/'packages'/rid/file;bind(q,kind,r,pack['files'][rel(q)])
            side=read(q.with_suffix('.json'));require(side['role_id']==rid and side['sha256']==pack['files'][rel(q)],'Package origin')
            bind(q.with_suffix('.json'),'metadata',r)
        q=PARENT/'base-models'/rid/'P-small.pt';bind(q,'base',r,pack['files'][rel(q)]);bind(q.with_suffix('.json'),'metadata',r)
        if inner:
            for q,kind in [(SOURCE/'teachers'/rid/'teacher.pt','teacher'),(SOURCE/'targets'/rid/'A2.pt','target-G'),(SOURCE/'targets'/rid/'A3.pt','target-P')]:
                side=read(q.with_suffix('.json'));require(side['role_id']==rid,'Teacher/target role')
                bind(q,kind,r,side['sha256']);bind(q.with_suffix('.json'),'metadata',r)
        # Registration only: do not hash or decode any query or labels at this stage.
        for name in ['query','labels']:
            q=PREP/'packages'/rid/(name+'.parquet');meta=old['packages'][rel(q)]
            require(meta['role_id']==rid,'Deferred package role');bind(q,name,r,meta['sha256'],deferred=True)
        rows.append(dict(role_id=rid,inner=inner,target=r['target'],calibration=r['calibration'],outer=r['outer'],group=r['group']))
    audit=pd.read_parquet(PARENT/'manifests/pair-join-audit.parquet')
    require(len(audit)==780 and audit.role_id.is_unique,'Trusted pair join audit coverage')
    require(set(audit.role_id)=={r['id'] for r in rs},'Trusted audit role mismatch')
    cfg=dict(version='JAT1-v1',plan_sha256=sha(PLAN),files=files,inner_roles=rs[:720],roles=rs[720:],
             recipes=RECIPES,post_recipes=POST_RECIPES,source_seed=SOURCE_SEED,outer_seeds=SEEDS,
             steps=2000,midpoint=1000,gradient_clip=5.,training_budget_seconds=86400,
             preflight_seconds=69120,auxiliary_dimension=8,parameters=2318,
             engineering_only_until_gpu_report_accepted=True,full_matrix_authorized_now=False,
             prefix_gates=dict(float32_atol=1e-5,float32_rtol=1e-4,float64_atol=1e-9,float64_rtol=1e-8),
             permission='source-inner engineering: no query values/labels, actual H/U, native, mixed feedback or PCAP')
    immutable(OUT/'manifests/contract.json',cfg);immutable(OUT/'manifests/contract-seal.json',dict(sha256=sha(OUT/'manifests/contract.json')))
    writable(OUT/'manifests/role-index.parquet');pd.DataFrame(rows).to_parquet(OUT/'manifests/role-index.parquet',index=False)
    immutable(OUT/'environment.json',dict(python=sys.executable,torch=torch.__version__,cuda=torch.version.cuda,gpu=torch.cuda.get_device_name(0),
          total_memory_MiB=torch.cuda.get_device_properties(0).total_memory/1048576,TF32=False,AMP=False))
    progress('P0_registered',inner_roles=720,outer_roles=60,query_reads=0,numeric_H_U_reads=0)
