"""S00-S07: read-only inventory, nested packages, tests and exact zero replay."""
import platform
import shutil
import sys
from common import *
from matrices import tests

def inventory():
    configure(); require(not (OUT/'manifests/experiment-contract.json').exists(),'Already sealed')
    require(read(G/'verification.json')['passed'] and read(Q/'verification.json')['passed'],'Previous verification absent')
    old=read(G/'manifests/experiment-contract.json')
    for key in ['source_sha256','packages_sha256','kernels_sha256']:
        for p,h in old[key].items(): require(sha(ROOT/p)==h,'Frozen G input changed: '+p)
    prior=read(G/'manifests/baseline-manifest.json')
    for p,h in prior['sha256'].items(): require(sha(ROOT/p)==h,'Frozen upstream changed: '+p)
    files={rel(p):sha(p) for p in G.rglob('*') if p.is_file() and '__pycache__' not in str(p)}
    files[rel(PLAN)]=sha(PLAN)
    for p in (ROOT/'eval/drift_kernel_business').glob('*.py'): files[rel(p)]=sha(p)
    # Include only the cached upstream records needed; never access raw PCAP.
    for name in ['cohorts/pairs.parquet','cohorts/folds.parquet','features/paired-flow-features.parquet']:
        path=Q/name; files[rel(path)]=sha(path)
    files.update(old['kernels_sha256'])
    pairs=pd.read_parquet(Q/'cohorts/pairs.parquet')
    require(len(pairs)==23566 and pairs.session_id.nunique()==480 and pairs.content_id.nunique()==30,'Cohort changed')
    require(pairs.groupby('protocol').size().to_dict()==dict(zip(PROTOCOLS,[5608,5957,5919,6082])),'Deployment counts changed')
    for col in ['pair_id','session_id','logical_id','carrier_id','content_id']:
        require(pairs.groupby(col).fold.nunique().max()==1,'Registered entity crosses folds: '+col)
    write(OUT/'manifests/baseline-manifest.json',{'sha256':files,'raw_PCAP_reads':0,
          'pairs':len(pairs),'visits':480,'contents':30,'registered_entity_cross_fold':0,
          'universal_complete_TCP_epoch_claimed':False})
    probe=torch.arange(4,device=cuda(),dtype=torch.float64)
    require(float((probe*probe).sum())==14,'CUDA float64 failed')
    write(OUT/'manifests/environment.json',{'python':platform.python_version(),'torch':torch.__version__,
         'cuda':torch.version.cuda,'gpu':torch.cuda.get_device_name(0),'matrix_fit_inference_dtype':'float64',
         'matrix_fit_inference_device':'cuda:0','CPU_fallback':False,'TF32':False,
         'Arrow_import_before_torch':True,'deterministic_algorithms':True})
    print('S00-S01 frozen sources and CUDA checked',flush=True)

def put_packages(target,pre,post,hist,query,score,seed):
    require(set(pre.pair_id)==set(post.pair_id),'Training pairs differ')
    for side,df in [('pre',pre),('post',post)]:
        df=df[['pair_id','session_id','content_id','fit_mass',*[side+'_'+f for f in FEATURES]]]
        saveparquet(df,target/f'fit-{side}.parquet')
        anonymous=df[['content_id','fit_mass',*[side+'_'+f for f in FEATURES]]].sample(frac=1,random_state=seed+(side=='post')).reset_index(drop=True)
        saveparquet(anonymous,target/f'group-{side}.parquet')
    saveparquet(hist,target/'fit-post-hist.parquet')
    require(set(query)=={'visit_id',*HIST},'Unsafe post query')
    saveparquet(query,target/'query-post-hist.parquet')
    saveparquet(score,target/'score-labels.parquet')

def prepare():
    require(not (OUT/'manifests/experiment-contract.json').exists(),'Cannot repack sealed files')
    folds=pd.read_parquet(Q/'cohorts/folds.parquet'); foldmap=dict(zip(folds.content_id,folds.fold))
    pairs=pd.read_parquet(Q/'cohorts/pairs.parquet'); roles=[]; hashlist={}; members=[]
    for outer in range(5):
      for p in PROTOCOLS:
        original=G/'packages'/f'f{outer}'/p
        pre=pd.read_parquet(original/'fit-pre.parquet'); post=pd.read_parquet(original/'fit-post.parquet')
        hist=pd.read_parquet(original/'fit-post-hist.parquet')
        query=pd.read_parquet(original/'query-post-hist.parquet'); score=pd.read_parquet(original/'score-labels.parquet')
        put_packages(folder('packages',outer,p),pre,post,hist,query,score,20261005+outer)
        tr=set(hist.content_id); te=set(score.content_id)
        require(len(tr)==24 and len(te)==6 and not tr&te and len(hist)==96 and len(query)==24,'Outer split changed')
        roles.append({'outer':outer,'protocol':p,'inner':None,'train_contents':sorted(tr),
                      'validation_contents':sorted(te),'train_visits':96,'query_visits':24,'train_pairs':len(pre)})
        for inner in range(5):
            if inner==outer: continue
            val=hist.content_id.map(foldmap).eq(inner); ih=hist[~val].copy()
            ip=pre[pre.content_id.isin(ih.content_id)].copy(); iz=post[post.content_id.isin(ih.content_id)].copy()
            vh=hist[val].copy(); mapping={s:hashlib.sha256(('business-query-v1:'+s).encode()).hexdigest() for s in vh.session_id}
            iq=vh[HIST].copy(); iq['visit_id']=vh.session_id.map(mapping); iq=iq.sort_values('visit_id').reset_index(drop=True)
            iscore=vh[['session_id','content_id','label_id']].copy(); iscore['visit_id']=vh.session_id.map(mapping)
            iscore['fold']=inner; iscore['protocol']=p
            ti=set(ih.content_id); vi=set(vh.content_id)
            require(len(ti)==18 and len(vi)==6 and not (ti&vi or ti&te or vi&te),'Nested content leak')
            require(len(ih)==72 and len(iq)==24,'Nested visit support changed')
            require(ih.groupby('label_id').content_id.nunique().eq(3).all() and vh.groupby('label_id').content_id.nunique().eq(1).all(),'Nested class support changed')
            for col in ['pair_id','session_id','logical_id','carrier_id']:
                f=pairs[pairs.protocol.eq(p)]
                a=set(f[f.content_id.isin(ti)][col]); b=set(f[f.content_id.isin(vi|te)][col])
                require(not a&b,'Nested registered entity overlap: '+col)
            target=folder('packages',outer,p,inner)
            put_packages(target,ip,iz,ih,iq,iscore,20261005+100*outer+inner)
            roles.append({'outer':outer,'protocol':p,'inner':inner,'train_contents':sorted(ti),
                          'validation_contents':sorted(vi),'outer_test_contents':sorted(te),
                          'train_visits':72,'query_visits':24,'train_pairs':len(ip)})
            for u in sorted(ti|vi|te):
                members.append({'outer':outer,'inner':inner,'protocol':p,'content_id':u,
                                'role':'train' if u in ti else 'validation' if u in vi else 'outer_test'})
    for path in (OUT/'packages').rglob('*.parquet'): hashlist[rel(path)]=sha(path)
    saveparquet(pd.DataFrame(members),OUT/'manifests/nested-content-roles.parquet')
    write(OUT/'manifests/package-manifest.json',{'sha256':hashlist,'roles':roles,'outer_roles':20,'inner_roles':80,
          'registered_nested_entity_overlap':0,'query_columns':['visit_id',*HIST],
          'anonymous_columns':['content_id','fit_mass','one side feature values'],
          'OS_security_sandbox_claimed':False})
    print('S02-S03 100 isolated role packages prepared',flush=True)

def zero_replay():
    configure(); rows=[]; oldprobs=pd.read_parquet(G/'predictions/visits.parquet')
    for outer in range(5):
      for p in PROTOCOLS:
        package_path=folder('packages',outer,p)
        frame=pd.read_parquet(package_path/'fit-post-hist.parquet')
        x,mu,scale=standardize(frame); y=tensor(truths(frame),torch.int64)
        oldpath=G/'models'/f'f{outer}'/p/'G1.pt'
        require(read(oldpath.parent/'complete.json')['sha256']['G1.pt']==sha(oldpath),'Old G1 changed')
        old=torch.load(oldpath,map_location=cuda(),weights_only=True)
        require(torch.equal(mu,old['mu']) and torch.equal(scale,old['scale']),'Source coordinates differ')
        w=old['weight'].clone().requires_grad_(); b=old['bias'].clone().requires_grad_()
        original=F.cross_entropy(x@w.T+b,y)+.0005*w.square().sum()
        grad0=torch.autograd.grad(original,(w,b))
        target=loss(w,b,x,y,'KSR0',0); grad1=torch.autograd.grad(target,(w,b))
        le=abs(float(original.detach()-target.detach())); ge=max(float((a-bb).abs().max()) for a,bb in zip(grad0,grad1))
        state,log=lr_fit(x,y); model={'mu':mu,'scale':scale,**state}
        query=pd.read_parquet(package_path/'query-post-hist.parquet'); new=probabilities(model,query)
        prior=oldprobs[oldprobs.fold.eq(outer)&oldprobs.protocol.eq(p)&oldprobs.arm.eq('G1')].set_index('visit_id').loc[new.visit_id]
        pe=float(np.max(np.abs(new[[f'p{i}' for i in range(6)]].to_numpy()-prior[[f'p{i}' for i in range(6)]].to_numpy())))
        decision=bool(np.array_equal(new.prediction.to_numpy(),prior.prediction.to_numpy()))
        require(le<=1e-12 and ge<=1e-10 and pe<=1e-8 and decision,'Zero replay tolerance failed')
        targetfolder=folder('models',outer,p); targetfolder.mkdir(parents=True,exist_ok=True)
        torch.save(model,targetfolder/'zero.pt'); complete(targetfolder,fits=[log],zero_replay=True)
        saveparquet(new,OUT/'zero-replay'/f'f{outer}'/(p+'.parquet'))
        rows.append({'outer':outer,'protocol':p,'objective_error':le,'gradient_error':ge,
                     'probability_error':pe,'all_decisions_identical':decision,'fit':log})
        print('S06 zero replay',p,outer,'max probability difference',pe,flush=True)
    write(OUT/'manifests/zero-replay.json',{'passed':True,'roles':rows,'labels_opened':False,
         'probability_tolerance':1e-8,'objective_tolerance':1e-12,'gradient_tolerance':1e-10})

def register():
    require(read(OUT/'manifests/unit-tests.json')['passed'] and read(OUT/'manifests/zero-replay.json')['passed'],'Engineering gates required')
    require(not (OUT/'manifests/experiment-contract.json').exists(),'Already registered')
    packages=read(OUT/'manifests/package-manifest.json'); old=read(G/'manifests/experiment-contract.json')
    sources={rel(p):sha(p) for p in Path(__file__).parent.glob('*.py')}
    write(OUT/'manifests/experiment-contract.json',{'version':'KSR-v1','registered_unix':time.time(),
         'plan_sha256':sha(PLAN),'source_sha256':sources,'packages_sha256':packages['sha256'],
         'outer_kernels_sha256':old['kernels_sha256'],'roles':packages['roles'],
         'arms':ARMS,'t_candidates':TS,'rho0':.001,'lambda_per_t':.0025,
         'inner_selection':'96-visit six-class pooled OOF macro F1; ties <=1e-12 choose smallest t',
         'trace_normalization':'after D^-1 coordinate transform; whole trace 96',
         'sensitivity':'||P6 Theta L||_F^2 / 5; no bias penalty',
         'kernel_smoothing':{'alpha':1,'beta':1},'feature_weights':WEIGHTS,
         'classifier_parameters':582,'features':FEATURES,'byte_edges':BYTE_EDGES,'count_edges':COUNT_EDGES,
         'labels':LABELS,'post_all_real_training_labels':True,'matrix_fitting_labels_used':False,
         'main_comparisons':['KSR2-KSR1','KSR2-KSR3','KSR2-KSR4'],'family_size':12,
         'bootstrap':{'samples':10000,'seed':20261005,'stratified_by_business':True,'unit':'content; all repeats and deployments together',
                      'fixed_selected_models':True,'tail':.05/(2*12)},
         'optimizer':{'name':'LBFGS','max_iter':500,'tolerance_grad':1e-9,'tolerance_change':1e-12,'line_search_fn':'strong_wolfe'},
         'inference_inputs':['post histogram','opaque visit ID','known deployment route'],
         'inference_reads_pre_labels_content_kernel_Gamma':False,'inner_reuses_outer_kernels':False,
         'stop_after_report':True})
    print('S07 contract sealed before positive-weight fitting',flush=True)

if __name__=='__main__':
    stage=sys.argv[1]
    {'inventory':inventory,'prepare':prepare,'tests':tests,'zero':zero_replay,'register':register}[stage]()
