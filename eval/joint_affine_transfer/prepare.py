"""Trusted once-only packer; no model selection or target test scoring."""
import platform
import inspect
from common import *

def run():
    configure()
    require(not (OUT/'manifests/preparation-complete.json').exists(),'Preparation already complete; do not overwrite')
    require(not (OUT/'manifests/seal.json').exists(),'Run already sealed')
    require(read(V4/'completion.json')['verification_passed'] and read(V4/'verification.json')['passed'],'V4 not complete')
    old=base.contract(); v4=read(V4/'manifests/experiment-contract-v4.json')
    require(sha(V4/'manifests/experiment-contract-v4.json')==read(V4/'manifests/contract-seal.json')['sha256'],'V4 seal')
    baseline={**old['source_sha256'],**v4['previous_source_sha256'],**v4['source_sha256']}
    for p,h in baseline.items(): require(sha(ROOT/p)==h,'Historical source changed: '+p)
    for p in [V4/'completion.json',V4/'verification.json',V4/'predictions/visits.parquet',
              V4/'predictions/complete.json',V4/'selection/choices.json',
              PREP/'manifests/experiment-contract-amended-io-v1.json',
              Q/'features/paired-flow-features.parquet',Q/'cohorts/folds.parquet',
              ROOT/'docs/calibrated-deployment-business-transfer/v4/detailed-final-report-20261007.md']:
        baseline[rel(p)]=sha(p)
    require(sha(V4/'predictions/visits.parquet')==read(V4/'predictions/complete.json')['sha256'],'Old prediction seal')
    fields=['session_id','protocol','content_id','repetition','fold','label_id','pair_id','logical_id',
            'carrier_id','registered_epoch_proxy',*['pre_'+f for f in FEATURES],*['post_'+f for f in FEATURES]]
    raw=pd.read_parquet(Q/'features/paired-flow-features.parquet',columns=fields)
    require(len(raw)==23566 and raw.session_id.nunique()==480 and raw.content_id.nunique()==30,'Frozen counts')
    require(raw.groupby('protocol').size().to_dict()==dict(zip(PROTOCOLS,[5608,5957,5919,6082])),'Pair counts')
    require(set(raw.repetition)=={1,2,3,4} and raw.pair_id.is_unique,'Repetitions/identities')
    for field in ['pair_id','session_id','logical_id','carrier_id','registered_epoch_proxy','content_id']:
        require(raw[field].notna().all() and raw.groupby(field).fold.nunique().max()==1,'Cross-fold '+field)
    pool={}; maxerr=0.
    for side in ['pre','post']:
        rows=[]
        for sid,d in raw.groupby('session_id',sort=True):
            a=d.iloc[0]; r={k:a[k] for k in ['protocol','content_id','repetition','fold','label_id']}
            r['visit_id']=base.visitid(sid)
            for j,f in enumerate(FEATURES):
                h=F.one_hot(bins(d[side+'_'+f],j),size(j)).to(torch.float64).mean(0)
                r.update({HIST[block(j)][b]:float(h[b]) for b in range(size(j))})
            rows.append(r)
        pool[side]=pd.DataFrame(rows).set_index('visit_id',drop=False)
    # Compare both sides against frozen source packages; test rows only reside in trusted packer.
    for side in ['pre','post']:
        for protocol in PROTOCOLS:
            roles=[r for r in old['main'] if r['inner'] is None and protocol in r['sources']]
            for outer in range(5):
                r=next(a for a in roles if a['outer']==outer)
                path=rolepath(r)/('source-'+side+'.parquet'); info=old['packages'][rel(path)]
                require(sha(path)==info['sha256'],'Old source package changed')
                d=pd.read_parquet(path); d=d[d.protocol.eq(protocol)]
                # Source-pre identity is deliberately absent; compare sorted numerical rows by content/label.
                cols=['content_id','label_id',*HIST]
                a=d[cols].sort_values(cols).reset_index(drop=True)
                b=pool[side][pool[side].protocol.eq(protocol)&pool[side].content_id.isin(r['train_contents'])]
                b=b[cols].sort_values(cols).reset_index(drop=True)
                require(a[['content_id','label_id']].equals(b[['content_id','label_id']]),'Replay members')
                maxerr=max(maxerr,float(np.max(np.abs(a[HIST].to_numpy()-b[HIST].to_numpy()))))
    require(maxerr<1e-14,'Histogram replay mismatch')
    packages={}; roles=[]; writes=set(); cohortchecks=[]
    def external(p):
        info=old['packages'][rel(p)]; require(sha(p)==info['sha256'],'Frozen package changed')
        packages[rel(p)]=info
    def store(d,p,kind,scope):
        save(d,p); packages[rel(p)]={'sha256':sha(p),'columns':list(d),'rows':len(d),'kind':kind,'scope':scope}
    for ix,r0 in enumerate(old['main']):
        r=dict(r0); held=set(r['validation_contents']); tr=set(r['train_contents']); cc=set(r['C_contents']); uu=set(r['U_contents'])
        require(not tr&held and cc|uu==tr and not cc&uu,'Content isolation')
        if r['inner'] is not None: require(r['target'] not in r['sources']+[r['calibration']],'Actual target in inner role')
        root=rolepath(r)
        for fn in ['source-pre.parquet','source-post.parquet','C-post.parquet','query.parquet','labels.parquet']:
            external(root/fn)
        if r['inner'] is None: external(root/'test-paired.parquet')
        cp=OUT/'packages/C'/r['kernel_id']; r['C_paired']=rel(cp/'paired.parquet')
        r['C_group_pre']=rel(cp/'group-pre.parquet'); r['C_group_post']=rel(cp/'group-post.parquet')
        if r['kernel_id'] not in writes:
            a=pool['pre'][pool['pre'].protocol.eq(r['calibration'])&pool['pre'].content_id.isin(cc)].sort_index()
            b=pool['post'].loc[a.index]
            require(a.content_id.equals(b.content_id),'Paired content identity')
            expected=64 if r['inner'] is None else 48
            require(len(a)==expected and not set(a.content_id)&uu and a.groupby('content_id').size().eq(4).all(),'C only')
            tokens=[hashlib.sha256(('ja-content:'+str(u)).encode()).hexdigest() for u in a.content_id]
            columns={'visit_id':a.visit_id.to_numpy(),'content_token':tokens,'fit_mass':np.full(len(a),1/len(a))}
            for side,z in [('pre',a),('post',b)]:
                for h in HIST: columns[side+'_'+h]=z[h].to_numpy()
            d=pd.DataFrame(columns)
            paired_schema(d); store(d,cp/'paired.parquet','JA-C-paired',{'calibration':r['calibration'],'C_contents':r['C_contents']})
            for side,seed in [('pre',103),('post',209)]:
                g=d[['content_token','fit_mass',*[(side+'_'+h) for h in HIST]]].rename(columns={side+'_'+h:h for h in HIST})
                g=g.sample(frac=1,random_state=seed).reset_index(drop=True); group_schema(g)
                store(g,cp/f'group-{side}.parquet','JA-C-group',{'calibration':r['calibration'],'C_contents':r['C_contents']})
            writes.add(r['kernel_id'])
        roles.append(r)
        cohortchecks.append({'id':r['id'],'C_visits':64 if r['inner'] is None else 48,
                            'content_overlap':0,'target_U_rows':0,'inner_actual_target_used':False})
        if (ix+1)%100==0: progress('prepare_packages',roles=ix+1,total=780)
    require(len(roles)==780 and len(writes)==300,'Role/cache counts')
    # No test scores are read. Historical references are only hashed here.
    write(OUT/'manifests/baseline-manifest.json',{'sha256':baseline,'old_main_models_adopted_as_new':0,
            'v4_new_main_fits':14700,'passed':True})
    write(OUT/'manifests/histogram-replay.json',{'passed':True,'maximum_error':maxerr,'visits':480,'pairs':23566})
    write(OUT/'manifests/role-ledger.json',{'roles':roles,'packages':packages,'audit':cohortchecks})
    save(pd.read_parquet(Q/'cohorts/folds.parquet'),OUT/'manifests/content-folds.parquet')
    write(OUT/'manifests/numeric-policy.json',POLICY)
    write(OUT/'manifests/environment.json',{'python':platform.python_version(),'torch':torch.__version__,
        'cuda':torch.version.cuda,'gpu':torch.cuda.get_device_name(0),'MiB':torch.cuda.get_device_properties(0).total_memory/1048576,
        'device':'cuda:0','dtype':'float64','CPU_fallback':False,'Arrow_before_torch':True,'TF32':False})
    write(OUT/'manifests/pilot-contract.json',{'role_ids':v4['pilot_roles'],'classification_candidates':720,
        'mapping_candidates':180,'selection_labels_read':False,'replay_role':v4['pilot_roles'][0]})
    complete(OUT/'manifests/preparation-complete.json',roles=780,C_packages=900,post_histogram_max_error=maxerr)
    progress('JA_prepared',roles=780,C_cache_groups=300)

def seal():
    require(not (OUT/'manifests/seal.json').exists(),'Already sealed')
    for f in ['affine-tests.json','access-tests.json','parser-unit-tests.json']:
        require(read(OUT/'manifests'/f)['passed'],'Required test failed: '+f)
    require((OUT/'observability/audit.json').exists(),'Observability audit required')
    rr=read(OUT/'manifests/role-ledger.json'); pilot=read(OUT/'manifests/pilot-contract.json')
    old=read(OUT/'manifests/baseline-manifest.json')['sha256']
    # Bind only the historical artifacts actually used; never import old main models as new fits.
    adopted=V4/'manifests/adopted-artifacts.json'
    v4=read(V4/'manifests/experiment-contract-v4.json')
    require(sha(adopted)==v4['adopted_artifacts_sha256'],'Historical adoption manifest changed')
    for p,h in read(adopted)['files'].items():
        require(sha(ROOT/p)==h,'Historical adopted artifact changed: '+p)
        old[p]=h
    for p in [adopted,V4/'manifests/reused-post-models.json',V4/'selection/complete.json']:
        old[rel(p)]=sha(p)
    installed=Path(inspect.getfile(torch.optim.LBFGS))
    require(sha(installed)==v4['installed_LBFGS_sha256'],'Installed optimizer differs from v4')
    files=list(Path(__file__).parent.glob('*.py'))+[Path(__file__).parent/'README.md']
    deps=[ROOT/'eval/calibrated_deployment_transfer/common.py',
          ROOT/'eval/calibrated_deployment_transfer/representation.py',
          ROOT/'eval/calibrated_deployment_transfer_v4/optimizer_preconditioning.py',
          ROOT/'eval/calibrated_deployment_transfer_v4/numeric_policy.py']
    files+=deps
    files += [ROOT/'src/proxy_analysis/protocol_normalization/early_stage_mechanism/records.py',
              ROOT/'src/proxy_analysis/protocol_normalization/tcp_ledger.py',
              ROOT/'src/proxy_analysis/extend_calibration/reassembly.py',
              ROOT/'src/proxy_analysis/extend_calibration/extraction_v3.py',
              ROOT/'src/proxy_analysis/extend_calibration/audit.py',
              ROOT/'src/proxy_analysis/parsing/packet_decoder.py',ROOT/'src/proxy_analysis/parsing/pcapng.py']
    sources={rel(p):sha(p) for p in files}
    c={'version':'JA-v1','registered_unix':time.time(),'plan_sha256':sha(PLAN),
       'source_sha256':sources,'baseline_sha256':old,'roles':rr['roles'],'packages':rr['packages'],
       'pilot_roles':pilot['role_ids'],'replay_role':pilot['replay_role'],
       'arms':ARMS,'eta_grid':ETAS,'t_grid':TS,'main_inner_fits':34560,'main_outer_fits':180,
       'mapping_tasks':8820,'bootstrap':{'samples':10000,'seed':20261007,'family':4},
       'installed_LBFGS_path':str(installed),'installed_LBFGS_sha256':sha(installed),
       'primary_comparators':['StrongPost','CT1','JA2','JA0'],
       'safety_screen':{'pooled_aux_margin':-.02,'worst_target_aux_margin':-.05},
       'same_content_all_deployments_and_repetitions_grouped':True,'target_U_numeric_rows':0,
       'permission_whitelist_not_OS_sandbox':True,'test_pre_after_all_predictions_only':True,
       'fit_objective':'weighted MSE/96 + eta*tau*||M-I||F^2/96; unpenalized bias',
       'tau':'max(trace(C_pre_cov)/96,1e-12)','coordinate':'frozen source-post plus C-post population scaler',
       'tie_rule':'within 1e-12: larger eta then smaller t',
       'user_authorization':'2026-10-07 user approved implementation of saved JA plan'}
    for p,h in sources.items(): require(sha(ROOT/p)==h,'Source changed while sealing')
    write(OUT/'manifests/experiment-contract.json',c)
    write(OUT/'manifests/seal.json',{'contract_sha256':sha(OUT/'manifests/experiment-contract.json'),
        'time_unix':time.time(),'source_sha256':sources})
    progress('JA_sealed',inner_fits=34560,outer_fits=180)

def diagnostic_packages():
    configure();require(not (OUT/'manifests/seal.json').exists(),'Diagnostic packages must precede seal')
    rr=read(OUT/'manifests/role-ledger.json'); native=[side+'_'+f for side in ['pre','post'] for f in FEATURES]
    d=pd.read_parquet(Q/'features/paired-flow-features.parquet',
                      columns=['session_id','protocol','fold','content_id','label_id',*native])
    rows=[]
    for sid,q in d.groupby('session_id'):
        a=q.iloc[0];r={k:a[k] for k in ['protocol','fold','content_id','label_id']};r['visit_id']=base.visitid(sid)
        for side in ['pre','post']:
            for j,f in enumerate(FEATURES):
                h=F.one_hot(bins(q[side+'_'+f],j),size(j)).to(torch.float64).mean(0)
                r.update({side+'_'+HIST[block(j)][b]:float(h[b]) for b in range(size(j))})
        rows.append(r)
    pool=pd.DataFrame(rows);paths={}
    for (protocol,fold),q in pool.groupby(['protocol','fold']):
        q=q.drop(columns='fold').reset_index(drop=True);require(len(q)==24,'Diagnostic visits')
        p=OUT/'packages/heldout-visits'/protocol/f'f{fold}.parquet';save(q,p)
        rr['packages'][rel(p)]={'kind':'JA-heldout-visits','columns':list(q),'rows':24,'sha256':sha(p),
                               'scope':{'validation_contents':sorted(q.content_id.unique()),'calibration':protocol}}
        paths[(protocol,int(fold))]=rel(p)
    for r in rr['roles']:r['heldout_visits']=paths[(r['calibration'],r['outer'] if r['inner'] is None else r['inner'])]
    write(OUT/'manifests/role-ledger.json',rr)
    complete(OUT/'manifests/diagnostic-packages.json',packages=20,roles=780,test_pre_after_all_predictions_only=True)
    progress('JA_diagnostic_packages_ready',packages=20)

if __name__=='__main__':
    action=sys.argv[1]; {'prepare':run,'diagnostics':diagnostic_packages,'seal':seal}[action]()
