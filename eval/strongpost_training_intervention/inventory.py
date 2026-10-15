"""TI00--TI05: freeze legal inputs and numeric pilot without reading test labels."""
from common import *

def run():
    configure();require(not (OUT/'manifests/seal.json').exists(),'Inventory already sealed')
    jc=read(JA/'manifests/experiment-contract.json');js=read(JA/'manifests/seal.json')
    require(sha(JA/'manifests/experiment-contract.json')==js['contract_sha256'],'Parent contract seal')
    close=read(JA/'closeout-20261009/completion.json')
    require(close['passed'] and close['postprocess_complete'],'JA additive closeout')
    require(sha(JA/'closeout-20261009/verification.json')==close['verification_sha256'],'Closeout seal')
    dc=ROOT/'outputs/paired-identity-decomposition-20261009/run-01'
    end=read(dc/'completion.json');require(end['passed'] and end['new_fits']==0,'Decomposition completion')
    require(sha(dc/'verification.json')==end['verification_sha256'],'Decomposition seal')
    require(read(V4/'completion.json')['verification_passed'] and read(V4/'verification.json')['passed'],'CT v4 completion')
    require((JA/'failure.json').exists() and not (JA/'completion.json').exists(),'Preserve parent terminal state')
    require(sha(JA/'failure.json')==close['original_failure_sha256'],'Parent failure changed')
    strong={ (v['outer'],v['target'],v['group']):v for v in read(V4/'selection/choices.json') if v['arm']=='StrongPost'}
    ja={ (v['outer'],v['target'],v['group'],v['arm']):v for v in read(JA/'selection/choices.json')}
    for runroot in [JA,V4]:
        require(sha(runroot/'selection/choices.json')==read(runroot/'selection/complete.json')['sha256'],'Selection seal')
    roles=[];pilots=[]
    for r0 in jc['roles']:
        if r0['inner'] is not None:continue
        k=(r0['outer'],r0['target'],r0['group']);s=strong[k];g=ja[(*k,'JA2')];p=ja[(*k,'JA1')]
        require(s['selected_arm']=='CT2','Unexpected StrongPost choice')
        r=dict(r0,t=s['t'],eta=g['eta'],old_P_eta=p['eta'],old_P_t=p['t'],old_G_t=g['t'])
        roles.append(r)
        if r['outer']==0:
            candidates=[v for v in jc['roles'] if v['inner'] is not None and v['outer']==0 and v['target']==r['target'] and v['group']==r['group']]
            v=min(candidates,key=lambda a:(a['calibration'],a['inner']))
            pilots.append(dict(v,t=r['t'],eta=r['eta']))
    require(len(roles)==60 and len(pilots)==12 and all(r['inner']==1 for r in pilots),'Registered role count')
    fixed={};arts={};packages={};pilotpk=[];outerpk=[]
    def fix(p):fixed[rel(p)]=sha(p)
    def art(p):
        require(p.exists() and p.with_suffix('.json').exists(),'Missing historical input '+rel(p))
        info=read(p.with_suffix('.json'));require(sha(p)==info['sha256'],'Artifact hash changed')
        arts[rel(p)]=info['sha256'];fix(p.with_suffix('.json'))
    for p in [JA/'manifests/experiment-contract.json',JA/'manifests/seal.json',JA/'failure.json',
              JA/'closeout-20261009/completion.json',JA/'closeout-20261009/verification.json',
              JA/'manifests/preparation-complete.json',
              JA/'selection/choices.json',JA/'selection/complete.json',
              V4/'completion.json',V4/'verification.json',V4/'selection/choices.json',
              V4/'selection/complete.json',V4/'manifests/contract-seal.json',
              V4/'manifests/experiment-contract-v4.json',V4/'manifests/adopted-artifacts.json',
              dc/'completion.json',dc/'verification.json',dc/'input-manifest.json',
              V4/'predictions/visits.parquet',V4/'predictions/complete.json']:
        fix(p)
    adopted=read(V4/'manifests/adopted-artifacts.json')['files']
    for r in roles+pilots:
        require(not set(r['validation_contents'])&set(r['train_contents']),'Cross-content leakage')
        require(not set(r['C_contents'])&set(r['U_contents']),'C/U overlap')
        if r['inner'] is not None:require(r['target'] not in r['sources']+[r['calibration']],'Actual target in pilot')
        pk=[]
        for fn in ['source-pre.parquet','source-post.parquet','C-post.parquet','query.parquet','labels.parquet']:
            path=rolepath(r)/fn;info=jc['packages'][rel(path)];require(sha(path)==info['sha256'],'Package hash changed')
            packages[rel(path)]=info;pk.append(rel(path))
        (pilotpk if r['inner'] is not None else outerpk).extend(pk)
        for k in ['C_paired','C_group_pre','C_group_post']:
            p=ROOT/r[k];info=jc['packages'][rel(p)];require(sha(p)==info['sha256'],'C package hash changed')
            packages[rel(p)]=info
        art(basemodel(r))
        for fn in ['CT2.pt','CT1.pt','coral.pt']:
            p=PREP/'slots'/r['id']/fn;require(adopted.get(rel(p))==sha(p),'Unadopted slot');art(p)
        for arm in ['JA1','JA2']:
            m=oldmap(r,arm,r['eta'])
            if m.exists():art(m);art(oldslot(r,arm,r['eta']))
        if r['inner'] is None:
            for arm in ['JA1','JA2']:
                e=r['old_P_eta'] if arm=='JA1' else r['eta'];t=r['old_P_t'] if arm=='JA1' else r['old_G_t']
                if e==r['eta'] and t==r['t']:art(oldmodel(r,arm,e,t))
    historical=dict(js['source_sha256'])
    historical.update(read(V4/'manifests/experiment-contract-v4.json')['source_sha256'])
    historical.update(read(V4/'manifests/experiment-contract-v4.json')['previous_source_sha256'])
    for p,h in historical.items():require(sha(ROOT/p)==h,'Historical source changed: '+p)
    files=list(Path(__file__).parent.glob('*.py'))
    own={rel(p):sha(p) for p in files}
    env={'python':sys.executable,'torch':torch.__version__,'cuda':torch.version.cuda,
         'gpu':torch.cuda.get_device_name(0),'device':'cuda:0','dtype':'float64',
         'CPU_fallback':False,'installed_LBFGS_path':inspect.getfile(torch.optim.LBFGS),
         'installed_LBFGS_sha256':sha(Path(inspect.getfile(torch.optim.LBFGS)))}
    write(OUT/'manifests/numeric-policy.json',POLICY)
    c={'version':'TI-v1','registered_unix':time.time(),'plan_sha256':sha(PLAN),'roles':roles,'pilot_roles':pilots,
       'packages':packages,'pilot_packages':pilotpk,'outer_packages':outerpk,'artifacts':arts,
       'fixed_files':fixed,'historical_source_sha256':historical,'source_sha256':own,'environment':env,
       'epsilons':[.01,.02],'betas':[0.,.1,1.],'formal_model_cap':240,'diagnostic_model_cap':60,
       'mapping_cap':11,'family':4,'bootstrap_seed':20261009,'bootstrap_samples':10000,
       'gates':{'hessian':1e-10,'symmetry':1e-12,'linear_system':1e-10,'stationarity_ratio':.1,
                'direction_relative':.1,'direction_near_zero':1e-8,'direction_absolute':1e-6,
                'risk_relative':.1,'risk_absolute':1e-4},
       'test_pre_read':False,'target_U_training_read':False,'optional_half_C_authorized':False}
    write(OUT/'manifests/experiment-contract.json',c)
    write(OUT/'manifests/seal.json',{'contract_sha256':sha(OUT/'manifests/experiment-contract.json')})
    progress('inventory_complete',outer_roles=60,pilot_roles=12,packages=len(packages),artifacts=len(arts))

if __name__=='__main__':run()
