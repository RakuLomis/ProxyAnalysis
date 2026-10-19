"""Freeze the 48 predetermined roles and reconstruct train-only four-slot views."""
from common import *
from subspaces import projectors,geometry,synthetic_tests

def register():
    configure()
    require(not OUT.exists(),'ST1 output exists; inspect before resuming')
    ap=ASSOC/'manifests/experiment-contract.json';jp=JA/'manifests/experiment-contract.json'
    require(sha(ap)==read(ASSOC/'manifests/seal.json')['sha256'],'Associated manifest seal')
    require(sha(jp)==read(JA/'manifests/seal.json')['contract_sha256'],'JA manifest seal')
    a=read(ap);j=read(jp);packseal=read(ASSOC/'packages/complete.json')
    require(packseal['passed'] and packseal['roles']==780,'Associated training package seal incomplete')
    selected=[]
    for i in range(1,5):
        for ix,target in enumerate(PROTOCOLS):
            cal=PROTOCOLS[(ix+1)%4]
            for group in MASKS:
                candidates=[r for r in a['inner_roles'] if r['outer']==0 and r['inner']==i and r['target']==target and r['calibration']==cal and r['group']==group]
                require(len(candidates)==1,'Role not unique')
                # Drop paths pointing to mixed query caches / heldout/native inputs.
                r={k:v for k,v in candidates[0].items() if k not in {'base_path','old_task','heldout_visits','C_paired','C_group_pre','C_group_post'}}
                require(len(r['train_contents'])==18 and len(r['validation_contents'])==6,'Role content count')
                require(not set(r['train_contents'])&set(r['validation_contents']),'Train/query content overlap')
                require(set(r['C_contents'])|set(r['U_contents'])==set(r['train_contents']) and not set(r['C_contents'])&set(r['U_contents']),'C/U split')
                require(len(r['C_contents'])==12 and len(r['U_contents'])==6,'C/U count')
                require(r['target'] not in r['sources']+[r['calibration']] and len(r['sources'])==2,'Actual target permission')
                require(r['missing']==MASKS[group],'Mask changed')
                selected.append(r)
    require(len(selected)==48,'48 roles required')
    files={}
    def add(path,kind,r=None,expected=None,metadata=None,deferred=False):
        path=Path(path);require(path.is_file(),'Missing asset '+str(path))
        actual=expected if deferred else sha(path)
        if expected is not None and not deferred:require(actual==expected,'Historical hash mismatch '+rel(path))
        files[rel(path)]=dict(kind=kind,sha256=actual,role_id=None if r is None else r['id'],deferred_hash=deferred,**(metadata or {}))
    for p in [ap,jp,ASSOC/'manifests/seal.json',JA/'manifests/seal.json',ASSOC/'packages/complete.json']:
        add(p,'provenance')
    for r in selected:
        rid=r['id']
        for name in ['source-pre','source-post','C-post','query','labels']:
            p=PREP/'packages'/rid/(name+'.parquet');info=a['packages'][rel(p)]
            require(info['role_id']==rid,'Package role mismatch')
            require(info['kind']==({'query':'main-query','labels':'main-inner-labels'}.get(name,name)),'Wrong package kind')
            require(info['scope']['train_contents']==r['train_contents'] and info['scope']['validation_contents']==r['validation_contents'],'Package scope mismatch')
            add(p,name,r,info['sha256'],dict(columns=info['columns'],rows=info['rows']),deferred=name in {'query','labels'})
        for arm in ['CT1','CT2']:
            p=PREP/'slots'/rid/(arm+'.pt');s=read(p.with_suffix('.json'))
            require(s['role_id']==rid and s['raw_target_U_read'] is False,'CT provenance')
            add(p,'slot',r,s['sha256']);add(p.with_suffix('.json'),'sidecar',r)
        for arm in ['JA1','JA2']:
            for directory,kind in [('maps','map'),('slots','slot')]:
                p=JA/directory/rid/f'{arm}-eta{r["eta"]:g}.pt';s=read(p.with_suffix('.json'))
                require(s['role_id']==rid and s['eta']==r['eta'],'JA role/eta')
                if kind=='map':require(s['mapping']['accepted'] and s['target_U_read'] is False,'Mapping not accepted')
                add(p,kind,r,s['sha256']);add(p.with_suffix('.json'),'sidecar',r)
        for p,kind in [(ASSOC/'packages'/rid/'classification.pt','classification'),(ASSOC/'base-models'/rid/'P-small.pt','old-base')]:
            add(p,kind,r,packseal['files'][rel(p)]);add(p.with_suffix('.json'),'sidecar',r)
    sources=list((ROOT/'eval/shape_source_task_attribution').glob('*.py'))
    sources += [ROOT/'eval/calibrated_deployment_transfer_v4'/s for s in ['numeric_policy.py','optimizer_preconditioning.py']]
    cfg=dict(experiment='ST1',version=1,date='2026-10-16',roles=selected,files=files,arms=ARMS,
             plan_sha256=sha(PLAN),source_sha256={rel(p):sha(p) for p in sources},
             numeric_policy=POLICY,physical_fit_limit=192,activity_seconds_limit=3600,
             bootstrap=dict(count=10000,seed=20261016,strata=6,contents_per_stratum=4),
             comparisons=COMPARISONS,default_all_models_new=True,actual_H_U_authorized=False,
             inherited_parameter_selection='historical source-inner retrospective; not a new unbiased nested estimate')
    write(OUT/'contract.json',cfg);write(OUT/'seal.json',dict(contract_sha256=sha(OUT/'contract.json')))
    write(OUT/'numeric-policy.json',POLICY);write(OUT/'manifests/numeric-policy.json',POLICY)
    solver=solver_module();write(OUT/'manifests/installed-solver-reference.json',solver.reference_metadata())
    write(OUT/'environment.json',dict(python=sys.executable,torch=torch.__version__,numpy=np.__version__,
          pandas=pd.__version__,cuda=torch.version.cuda,gpu=torch.cuda.get_device_name(0),dtype='float64',device='cuda:0'))
    save(pd.DataFrame([dict(path=k,**v) for k,v in files.items()]).drop(columns=['columns'],errors='ignore'),'source-bindings')
    save(pd.DataFrame([dict(role_id=r['id'],role_target=r['target'],query_deployment=r['calibration'],group=r['group'],inner=r['inner'],eta=r['eta'],t=r['t'],train_contents=18,query_contents=6) for r in selected]),'role-membership')
    write(OUT/'stages/P0.json',dict(complete=True,registered_roles=48,query_numeric_reads=0,label_reads=0))
    progress('P0_complete',roles=48,physical_fit_limit=192)

def paths(r,which):return JA/which/r['id']

def loss_audit(model,slot,t):
    x,y,w=slot['x'],slot['y'],slot['mass'];W,b=model['weight'],model['bias']
    z=x@W.T+b; lp=z-torch.logsumexp(z,1)[:,None]
    value=-(w*lp.gather(1,y[:,None]).squeeze(1)).sum()+.0005*(1+t)*W.square().sum()
    err=(lp.exp()-F.one_hot(y,6))*w[:,None]
    gw=err.T@x+.001*(1+t)*W;gb=err.sum(0)
    return dict(objective=float(value),gradient=max(float(gw.abs().max()),float(gb.abs().max())))

def build(r,ps):
    rid=r['id'];base=PREP/'packages'/rid
    pre=package(base/'source-pre.parquet',r,'source-pre');post=package(base/'source-post.parquet',r,'source-post');cp=package(base/'C-post.parquet',r,'C-post')
    require(len(pre)==len(post)==144 and len(cp)==48,'Visit counts')
    require(post.visit_id.is_unique and cp.visit_id.is_unique and not set(post.visit_id)&set(cp.visit_id),'Training parent collision')
    for key in ['content_id','label_id','protocol']:
        require(pre[key].value_counts().to_dict()==post[key].value_counts().to_dict(),'Anonymous source bag metadata differs')
    ct1=old_obj(PREP/'slots'/rid/'CT1.pt',r,'slot');ct2=old_obj(PREP/'slots'/rid/'CT2.pt',r,'slot')
    jp=old_obj(paths(r,'slots')/f'JA1-eta{r["eta"]:g}.pt',r,'slot');jg=old_obj(paths(r,'slots')/f'JA2-eta{r["eta"]:g}.pt',r,'slot')
    mp=old_obj(paths(r,'maps')/f'JA1-eta{r["eta"]:g}.pt',r,'map');mg=old_obj(paths(r,'maps')/f'JA2-eta{r["eta"]:g}.pt',r,'map')
    pure=old_obj(ASSOC/'packages'/rid/'classification.pt',r,'classification')
    mu,scale=ct1['mu'],ct1['scale']
    for z in [ct2,jp,jg,mp,mg,pure]:
        require(torch.equal(z['mu'],mu) and torch.equal(z['scale'],scale),'Frozen coordinate mismatch')
    require(bool((scale>0).all()),'Nonpositive scale')
    px=(tensor(pre[HIST])-mu)/scale
    require(torch.equal(px,ct1['x'][144:288]),'Independent pre order/standardization')
    require(torch.equal(tensor(truths(pre),torch.long),ct1['y'][144:288]),'Pre labels misaligned')
    rawpost=(tensor(post[HIST])-mu)/scale;rawcp=(tensor(cp[HIST])-mu)/scale
    for z in [ct1,ct2,jp,jg]:
        require(torch.equal(z['x'][:144],rawpost) and torch.equal(z['x'][288:],rawcp),'Nonchanging post/C slots differ')
    forward=[]
    for name,m,old in [('P',mp,jp),('G',mg,jg)]:
        pred=px@m['matrix'].T+m['bias'];ae,ne=error(pred,old['x'][144:288]);require(ae<1e-12,'Original affine forward replay')
        forward.append(dict(role_id=rid,predictor=name,absolute_error=ae,normalized_error=ne))
        require(torch.equal(old['y'],ct1['y']) and torch.equal(old['mass'],ct1['mass']),'JA/pre labels or weights differ')
    # Preserve the original frozen mapped views exactly; replay above verifies formula.
    p,g=jp['x'][144:288],jg['x'][144:288]
    mixed,geom=geometry(p,g,mu,scale,ps)
    y=torch.cat([ct2['y'][:288],ct1['y'][144:288],ct2['y'][288:]])
    mass=torch.cat([ct2['mass'][:144],.9*ct2['mass'][144:288],.1*ct1['mass'][144:288],ct2['mass'][288:]])
    require(abs(float(mass.sum())-1)<1e-12 and float((weighted(y,mass,6)-1/6).abs().max())<1e-12,'Small loss mass')
    slots={};diag=[]
    for arm in ARMS:
        x=torch.cat([ct2['x'][:288],mixed[arm],ct2['x'][288:]])
        s=dict(x=x,y=y,mass=mass,mu=mu,scale=scale);slots[arm]=s
        require(x.shape==(480,96) and torch.isfinite(x).all(),'Slot shape/finiteness')
        if arm=='PP':
            for k in ['x','y','mass','mu','scale']:require(torch.equal(s[k],pure[k]),'PP differs from original classification')
        put(OUT/'slots'/rid/(arm+'.pt'),s,role_id=rid,arm=arm)
        raw=mu+scale*mixed[arm]
        for j in range(10):
            b=raw[:,block(j)];orig=mu[block(j)]+scale[block(j)]*p[:,block(j)]
            diag.append(dict(role_id=rid,arm=arm,feature=FEATURES[j],negative_fraction=float((b<0).double().mean()),
                   minimum=float(b.min()),maximum=float(b.max()),mass_residual_max=float((b.sum(1)-1).abs().max()),
                   PP_raw_delta_max=float((b-orig).abs().max())))
    put(OUT/'auxiliary-views'/rid/'views.pt',dict(**mixed,mu=mu,scale=scale),role_id=rid)
    oldbase=old_obj(ASSOC/'base-models'/rid/'P-small.pt',r,'old-base')
    require(torch.equal(oldbase['mu'],mu) and torch.equal(oldbase['scale'],scale),'Old PP scaler')
    audit=loss_audit(oldbase,slots['PP'],r['t'])
    require(audit['gradient']<=1e-5,'Old PP compatible objective failed')
    compatibility=dict(role_id=rid,PP_slot_exact=True,old_base_objective=audit['objective'],old_base_gradient=audit['gradient'],reuse=False,reason='Historical q=1 model includes additional Newton refinement; all four arms fit fresh under original v4')
    ledger=[]
    parts=[('source-post',post,range(0,144)),('CORAL',post,range(144,288)),('mapped-pre',pre,range(288,432)),('C-post',cp,range(432,480))]
    for name,d,ix in parts:
        for k,row in enumerate(ix):
            item=d.iloc[k];ledger.append(dict(role_id=rid,row=row,row_key=f'{rid}:{row}',input_view=name,slot_type=name,
                 label=int(y[row]),sample_mass=float(mass[row]),content_key=item.content_id,protocol=item.protocol,
                 parent_visit_key=None if name=='mapped-pre' else item.visit_id,
                 anonymous_pre_row=k if name=='mapped-pre' else None))
    return geom,forward,diag,compatibility,ledger

def prepare():
    with stage('P1'):
        with compute('synthetic-geometry'):
            synthetic=synthetic_tests();ps=projectors()
        save(pd.DataFrame(synthetic),'geometry-synthetic-tests')
        gs=[];fs=[];ds=[];cs=[];ls=[]
        for k,r in enumerate(contract()['roles']):
            with compute('train-only-views-'+r['id']):g,f,d,c,l=build(r,ps)
            gs.extend(dict(role_id=r['id'],**x) for x in g);fs.extend(f);ds.extend(d);cs.append(c);ls.extend(l)
            if (k+1)%8==0:progress('P1_views',roles=k+1,total=48)
        save(pd.DataFrame(gs),'geometry-tests');save(pd.DataFrame(fs),'affine-replay');save(pd.DataFrame(ds),'view-diagnostics')
        save(pd.DataFrame(cs),'compatibility');save(pd.DataFrame(ls),'slot-row-ledger')
        files=list((OUT/'slots').rglob('*.pt'))+list((OUT/'auxiliary-views').rglob('*.pt'))
        files += [OUT/(n+'.parquet') for n in ['geometry-tests','affine-replay','view-diagnostics','compatibility','slot-row-ledger']]
        seal(OUT/'slots-complete.json',files,logical_slots=192,roles=48,query_reads=0)
