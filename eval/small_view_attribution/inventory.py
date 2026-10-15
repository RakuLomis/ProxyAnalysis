"""Seal only legal outer-role inputs and frozen references before fitting."""
from common import *

def run():
    configure();require(not (OUT/'manifests/seal.json').exists(),'Already registered')
    pc=PARENT/'manifests/experiment-contract.json';parent=read(pc)
    require(sha(pc)==read(pc.with_name('seal.json'))['contract_sha256'],'Parent seal')
    complete=read(PARENT/'completion.json');require(complete['passed'] and complete['finite_interventions_complete'],'Parent incomplete')
    require(sha(PARENT/'verification.json')==complete['verification_sha256'],'Parent verification seal')
    verification=read(PARENT/'verification.json')
    for p,h in verification['files'].items():require(sha(ROOT/p)==h,'Parent verified output changed '+p)
    cont=PARENT/'manifests/continuation.json'
    require(sha(cont)==read(cont.with_name('continuation-seal.json'))['sha256'],'Parent continuation')
    fixed={};arts={};packages={};end=pd.read_parquet(PARENT/'manifests/formal-endpoints.parquet')
    def fix(p,expected=None):
        h=sha(p);require(expected is None or h==expected,'Historical seal differs '+rel(p));fixed[rel(p)]=h
    def art(p,expected=None):
        require(p.exists(),'Missing artifact '+rel(p));info=read(p.with_suffix('.json'));h=sha(p)
        require(h==info['sha256'] and (expected is None or h==expected),'Artifact source changed')
        arts[rel(p)]=h;fix(p.with_suffix('.json'),parent['fixed_files'].get(rel(p.with_suffix('.json'))))
    for p in [pc,pc.with_name('seal.json'),PARENT/'completion.json',PARENT/'verification.json',
              cont,cont.with_name('continuation-seal.json'),PARENT/'manifests/formal-endpoints.parquet',
              PARENT/'predictions/visits.parquet',PARENT/'predictions/complete.json',
              PARENT/'comparisons/primary.json',PARENT/'scores/pooled.parquet',PARENT/'manifests/numeric-policy.json']:
        fix(p)
    roles=parent['roles'];refs=[]
    require(len(roles)==60 and len({r['id'] for r in roles})==60,'Role count')
    foldsets={}
    for r in roles:
        require(r['inner'] is None and not set(r['train_contents'])&set(r['validation_contents']),'Content leakage')
        require(set(r['C_contents'])|set(r['U_contents'])==set(r['train_contents']) and not set(r['C_contents'])&set(r['U_contents']),'C/U')
        require(len(r['sources'])==3 and r['target'] not in r['sources'],'Deployment scope')
        u=set(r['validation_contents']);require(foldsets.setdefault(r['outer'],u)==u,'Non-global folds')
        for fn in ['source-pre.parquet','source-post.parquet','C-post.parquet','query.parquet','labels.parquet']:
            p=rolepath(r)/fn;info=parent['packages'][rel(p)];require(sha(p)==info['sha256'],'Package changed');packages[rel(p)]=info
        for k in ['C_group_pre','C_group_post']:
            p=ROOT/r[k];info=parent['packages'][rel(p)];require(sha(p)==info['sha256'],'Anonymous C changed');packages[rel(p)]=info
        art(oldviews(r));art(basemodel(r),parent['artifacts'][rel(basemodel(r))])
        refs.append({'role_id':r['id'],'arm':'S','model_path':rel(basemodel(r)),'model_sha256':arts[rel(basemodel(r))]})
        for a in ['P-small','G-small']:
            row=end[end.role_id.eq(r['id'])&end.arm.eq(a)];require(len(row)==1,'Reference endpoint')
            row=row.iloc[0];p=ROOT/row.model_path;art(p,row.model_sha256)
            refs.append({'role_id':r['id'],'arm':a,'model_path':rel(p),'model_sha256':row.model_sha256})
    require(len(set.union(*foldsets.values()))==30 and sum(map(len,foldsets.values()))==30,'Fold disjointness')
    historical={**parent['historical_source_sha256'],**parent['source_sha256'],**read(cont)['source_sha256']}
    for p,h in historical.items():require(sha(ROOT/p)==h,'Historical code changed '+p)
    import compatibility
    import observation_audit
    for p in compatibility.SOURCES+observation_audit.SOURCES:fix(ROOT/p)
    previous=ROOT/'outputs/small-view-attribution-20261010/run-01'
    fix(previous/'manifests/experiment-contract.json');fix(previous/'manifests/seal.json');fix(previous/'startup-failure.json')
    require(read(previous/'startup-failure.json')['new_classifier_fits']==0,'Unexpected previous fits')
    own={rel(p):sha(p) for p in Path(__file__).parent.glob('*.py')}
    env={'python':sys.executable,'torch':torch.__version__,'cuda':torch.version.cuda,'gpu':torch.cuda.get_device_name(0),
         'device':'cuda:0','dtype':'float64','CPU_fallback':False,
         'installed_LBFGS_path':inspect.getfile(torch.optim.LBFGS),
         'installed_LBFGS_sha256':sha(Path(inspect.getfile(torch.optim.LBFGS)))}
    require(env['installed_LBFGS_sha256']==parent['environment']['installed_LBFGS_sha256'],'Installed optimizer differs')
    write(OUT/'manifests/numeric-policy.json',POLICY)
    c={'version':'SA-v1','user_authorization':'User: 好的，请你根据方案开始实施',
       'registered_unix':time.time(),'plan_sha256':sha(PLAN),'parent_contract_sha256':sha(pc),'roles':roles,
       'packages':packages,'artifacts':arts,'fixed_files':fixed,'historical_source_sha256':historical,
       'source_sha256':own,'environment':env,'references':refs,'arms':ARMS,'comparisons':COMPARISONS,
       'beta':.1,'family':3,'CI_coverage':1-.05/3,'bootstrap_seed':20261010,'bootstrap_samples':10000,
       'new_classifier_cap':180,'new_marginal_cap':60,'new_P_G_maps':0,
       'target_U_training_read':False,'test_pre_read':False,'PCAP_read':False,'new_hyperparameter_selection':False,
       'pilot_roles':[r['id'] for r in roles if r['outer']==0]}
    require(len(c['pilot_roles'])==12 and len(refs)==180,'Pilot/reference count')
    write(OUT/'manifests/experiment-contract.json',c)
    write(OUT/'manifests/seal.json',{'contract_sha256':sha(OUT/'manifests/experiment-contract.json')})
    progress('inventory_complete',roles=60,reference_models=180,packages=len(packages),device=env['gpu'])

if __name__=='__main__':run()
