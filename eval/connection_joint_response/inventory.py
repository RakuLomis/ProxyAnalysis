"""Seal approved finite scope and read-only parent lineage before cache packing."""
from common import *

def run():
    configure(); require(not (OUT/'manifests/seal.json').exists(),'Run already registered')
    p=PARENT/'manifests/experiment-contract.json'; parent=read(p)
    require(sha(p)==read(p.with_name('seal.json'))['contract_sha256'],'Parent contract changed')
    completion=read(PARENT/'completion.json'); require(completion['passed'],'Parent incomplete')
    require(sha(PARENT/'verification.json')==completion['verification_sha256'],'Parent verification seal')
    fixed={}; artifacts={}
    def fix(p,h=None):
        h=h or sha(p); require(sha(p)==h,'Changed parent '+rel(p)); fixed[rel(p)]=h
    def art(p):
        info=read(p.with_suffix('.json')); require(sha(p)==info['sha256'],'Changed artifact')
        artifacts[rel(p)]=info['sha256']; fix(p.with_suffix('.json'))
    for p in [p,p.with_name('seal.json'),PARENT/'completion.json',PARENT/'verification.json',NATIVE,FOLDS]:fix(p)
    for rp,h in read(PARENT/'verification.json')['files'].items():fix(ROOT/rp,h)
    for rp,h in parent['historical_source_sha256'].items():fix(ROOT/rp,h)
    for rp,h in parent['source_sha256'].items():fix(ROOT/rp,h)
    audit=read(AUDIT/'manifest.json'); fix(AUDIT/'manifest.json')
    for entry in audit['sources']:fix(ROOT/entry['local_path'],entry['sha256'])
    roles=parent['roles']; require(len(roles)==60,'Role count')
    fold=pd.read_parquet(FOLDS); label=dict(zip(fold.content_id,fold.label_id))
    for r in roles:
        metadata=read(ROOT/'outputs/strongpost-training-intervention-20261009/run-01/slots'/r['id']/'views.json')
        for path in metadata['mappings'].values():art(ROOT/path)
        oldviews=ROOT/'outputs/strongpost-training-intervention-20261009/run-01/slots'/r['id']/'views.pt'; art(oldviews)
        marginal=PARENT/'transforms'/r['id']/'marginal.pt'; art(marginal)
        oldroot=ROOT/'outputs/calibrated-deployment-business-transfer-20261006/run-01/packages'/r['id']
        for name in ['source-pre.parquet','source-post.parquet','C-post.parquet','query.parquet']:
            src=oldroot/name; fix(src,parent['packages'][rel(src)]['sha256'])
        r['reuse_views']=rel(oldviews); r['reuse_maps']=metadata['mappings']; r['reuse_marginal']=rel(marginal)
        r['inner_validation_contents']=[sorted([u for u in r['train_contents'] if label[u]==y])[i:i+1]
            for i in range(2) for y in LABELS]
        r['inner_validation_contents']=[sum(r['inner_validation_contents'][6*i:6*i+6],[]) for i in range(2)]
        r['C_diagnostic_contents']=[sum([sorted([u for u in r['C_contents'] if label[u]==y])[i:i+1]
            for y in LABELS if LABELS.index(y) not in r['missing']],[]) for i in range(4)]
        require(all(len(v)==6 for v in r['inner_validation_contents']),'Inner coverage')
        require(all(len(v)==4 for v in r['C_diagnostic_contents']),'C internal fold')
    optimizer=Path(inspect.getfile(torch.optim.LBFGS)); environment={
        'python':sys.executable,'torch':torch.__version__,'cuda':torch.version.cuda,
        'gpu':torch.cuda.get_device_name(0),'device':'cuda:0','dtype':'float64','CPU_fallback':False,
        'installed_LBFGS_path':str(optimizer),'installed_LBFGS_sha256':sha(optimizer)}
    own={rel(q):sha(q) for q in Path(__file__).parent.glob('*.py')}
    write(OUT/'manifests/numeric-policy.json',POLICY)
    c={'version':'CJ-v1','user_authorization':'好的，请你根据计划开始实施',
       'plan_sha256':sha(PLAN),'registered_unix':time.time(),'roles':roles,'pilot_role_ids':[r['id'] for r in roles if r['outer']==0],
       'fixed_files':fixed,'artifacts':artifacts,'source_sha256':own,'historical_source_sha256':parent['historical_source_sha256'],
       'parent_contract_sha256':sha(PARENT/'manifests/experiment-contract.json'),'environment':environment,
       'representations':{'M':96,'I':162,'J':162},'joint_sizes':SIZES,'joint_names':NAMES,'arms':ARMS,
       'comparisons':COMPARISONS,'beta':.1,'eta_rule':'frozen role JA2 source selection',
       'classifier_cap':1920,'inner_classifier_cap':1440,'outer_classifier_cap':480,'diagnostic_table_cap':2880,
       'bootstrap_samples':10000,'bootstrap_seed':20261010,'family':5,'CI_coverage':.99,
       'O1':'paused','O2':'not_started','PCAP_reads_allowed':False,'target_U_learning_allowed':False,
       'test_pre_learning_allowed':False,'physical_post_input_qualified':False,
       'trusted_full_native_cache_packer_allowed':True,'trusted_packer_not_a_learner':True,
       'scope':'offline-associated common-valid TCP cohort; post-only numeric classifier',
       'mechanism_source':{'captured_build_commit':audit['captured_build_commit'],'meta_commit':audit['meta_commit']}}
    write(OUT/'manifests/experiment-contract.json',c)
    write(OUT/'manifests/seal.json',{'contract_sha256':sha(OUT/'manifests/experiment-contract.json')})
    progress('inventory_complete',roles=60,cuda=environment['gpu'],raw_capture_reads=0)

if __name__=='__main__':run()
