"""Finite interventions approved after failed pilot; no numerical repair."""
from common import *
import objectives as O
import influence as I

COMPARISONS=[('P-small','S'),('P-small','G-small'),('P-full','S'),('P-full','G-full')]

def authorization():
    path=OUT/'manifests/continuation.json';a=read(path)
    require(sha(path)==read(OUT/'manifests/continuation-seal.json')['sha256'],'Continuation changed')
    require(sha(OUT/'manifests/experiment-contract.json')==a['parent_contract_sha256'],'Parent contract changed')
    require(sha(OUT/'pilot/promotion.json')==a['pilot_promotion_sha256'],'Pilot state rewritten')
    require(sha(OUT/'awaiting-decision.json')==a['pause_record_sha256'],'Original pause record changed')
    for p,h in a['source_sha256'].items():checked(ROOT/p,h,'continuation-source')
    require(a['user_authorized_finite_interventions'] and not a['local_derivative_precision_claim'], 'Unapproved policy')
    return a

def register():
    start('continuation-register')
    require(not (OUT/'manifests/continuation-seal.json').exists(),'Continuation already registered')
    require(not read(OUT/'pilot/promotion.json')['passed'],'Expected failed numerical pilot')
    sources=[Path(__file__),Path(__file__).with_name('formal_report.py')]
    require(all(p.exists() for p in sources),'Implement and review report before registration')
    a={'version':'TI-finite-continuation-v1','registered_unix':time.time(),
       'user_authorization':'User replied 继续 to proposal: continue fixed finite interventions, retain influence only as unvalidated approximation.',
       'user_authorized_finite_interventions':True,'local_derivative_precision_claim':False,
       'parent_contract_sha256':sha(OUT/'manifests/experiment-contract.json'),
       'pilot_promotion_sha256':sha(OUT/'pilot/promotion.json'),
       'pause_record_sha256':sha(OUT/'awaiting-decision.json'),
       'source_sha256':{rel(p):sha(p) for p in sources},
       'betas':[0.,.1,1.],'eta_rule':'original JA2 choice','t_rule':'original StrongPost choice',
       'solver_policy_unchanged':True,'formal_endpoint_cap':240,'new_map_fits':0,
       'comparisons':COMPARISONS,'no_checkpoint_or_test_selection':True,'optional_half_C':False}
    write(OUT/'manifests/continuation.json',a)
    write(OUT/'manifests/continuation-seal.json',{'sha256':sha(OUT/'manifests/continuation.json')})
    progress('finite_continuation_registered',original_pilot_promoted=False,formal_endpoint_cap=240)

def endpoint_path(r,arm):return OUT/'models'/r['id']/(arm+'.pt')

def audit_model(model,s,t,log):
    require(torch.equal(model['mu'],s['mu']) and torch.equal(model['scale'],s['scale']),'Classifier coordinates changed')
    val=float(O.loss(model,s,t));gw,gb=O.gradient(model,s,t)
    maximum=max(float(gw.abs().max()),float(gb.abs().max()))
    require(maximum<=1e-5 and abs(val-log['objective'])<1e-10,'Classifier original objective/gradient')
    require(abs(maximum-log['max_gradient'])<1e-10,'Classifier gradient replay')
    return {'objective':val,'gradient_inf':maximum,'objective_replay_error':abs(val-log['objective']),
            'gradient_replay_error':abs(maximum-log['max_gradient'])}

def train():
    with stage('formal_fit'):
        authorization();c=contract();sol=solver();endpoints=[];directions=[];new=0;reused=0
        for ri,r in enumerate(c['roles']):
            v=artifact(viewpath(r));ref=artifact(basemodel(r));slotS=O.slot(v,'P',0.)
            refmeta=read(basemodel(r).with_suffix('.json'))
            audit_model(ref,slotS,r['t'],refmeta['optimizer'])
            for arm in ARMS[1:]:
                side=arm[0];beta=.1 if arm.endswith('small') else 1.
                s=O.slot(v,side,beta);oldarm='JA1' if side=='P' else 'JA2'
                oldeta=r['old_P_eta'] if side=='P' else r['eta'];oldt=r['old_P_t'] if side=='P' else r['old_G_t']
                reuse=beta==1 and oldeta==r['eta'] and oldt==r['t']
                if reuse:
                    path=oldmodel(r,oldarm,r['eta'],r['t']);prior=artifact(oldslot(r,oldarm,r['eta']))
                    require(torch.equal(s['y'],prior['y']) and torch.equal(s['mass'],prior['mass']),'Reuse labels/masses')
                    require(residual(s['x'],prior['x'])<1e-12,'Reuse weighted design changed')
                    model=artifact(path);log=read(path.with_suffix('.json'))['optimizer'];reused+=1
                else:
                    path=endpoint_path(r,arm);sp=OUT/'slots'/r['id']/(arm+'.pt')
                    if not path.exists():
                        put(s,sp,role_id=r['id'],arm=arm,beta=beta,t=r['t'],eta=r['eta'])
                        context={'role_id':r['id'],'arm':arm,'t':r['t'],'eta':r['eta'],'beta':beta,'input_sha256':sha(sp)}
                        model,log=sol.fit_preconditioned(s['x'],s['y'],s['mass'],r['t'],context)
                        model.update(mu=v['mu'],scale=v['scale'])
                        put(model,path,optimizer=log,role_id=r['id'],arm=arm,beta=beta,t=r['t'],eta=r['eta'])
                    else:model=artifact(path);log=read(path.with_suffix('.json'))['optimizer']
                    new+=1
                audit=audit_model(model,s,r['t'],log)
                endpoints.append({'role_id':r['id'],'target':r['target'],'group':r['group'],'outer':r['outer'],
                    'arm':arm,'beta':beta,'t':r['t'],'eta':r['eta'],'model_path':rel(path),
                    'model_sha256':sha(path),'reused':reuse,**audit})
            data,info=I.directions(r,v,ref,False)
            put(data,OUT/'training-directions'/r['id']/'direction.pt',**info,
                local_derivative_precision_validated=False,interpretation='unvalidated local approximation only')
            directions.append(info)
            if (ri+1)%5==0:progress('formal_training',roles=ri+1,total=60,new_fits=new,reused_models=reused)
        require(len(endpoints)==240 and new==199 and reused==41,'Formal endpoint accounting')
        save(pd.DataFrame(endpoints),OUT/'manifests/formal-endpoints.parquet')
        save(pd.DataFrame(directions),OUT/'training-directions/hessian-checks.parquet')
        write(OUT/'manifests/formal-models-complete.json',{'endpoint_count':240,'new_classifier_fits':new,
            'reused_full_classifiers':reused,'reused_S':60,'new_mapping_fits_this_continuation':0,
            'endpoints_sha256':sha(OUT/'manifests/formal-endpoints.parquet'),
            'directions_sha256':sha(OUT/'training-directions/hessian-checks.parquet'),
            'H_labels_read':False,'test_pre_read':False,'target_U_training_read':False,
            'local_derivative_precision_validated':False})

def predict_all():
    with stage('formal_predict'):
        authorization();c=contract();complete=read(OUT/'manifests/formal-models-complete.json')
        checked(OUT/'manifests/formal-endpoints.parquet',complete['endpoints_sha256'],'formal-model-seal')
        endpoints=pd.read_parquet(OUT/'manifests/formal-endpoints.parquet').set_index(['role_id','arm'])
        reference=pd.read_parquet(V4/'predictions/visits.parquet');pc=[f'p{i}' for i in range(6)]
        rows=[];maximum=0.
        for r in c['roles']:
            query=package(rolepath(r)/'query.parquet','query')
            for arm in ARMS:
                if arm=='S':path=basemodel(r)
                else:
                    e=endpoints.loc[(r['id'],arm)];path=ROOT/e.model_path
                    checked(path,e.model_sha256,'formal-model')
                d=predict(artifact(path),query)
                if arm=='S':
                    old=reference[reference.outer.eq(r['outer'])&reference.target.eq(r['target'])&
                         reference.group.eq(r['group'])&reference.arm.eq('StrongPost')].set_index('visit_id')
                    err=float(np.abs(d.set_index('visit_id').loc[old.index,pc].to_numpy()-old[pc].to_numpy()).max())
                    require(err<1e-12,'Frozen StrongPost probability replay');maximum=max(maximum,err)
                for k in ['outer','target','group']:d[k]=r[k]
                d['role_id']=r['id'];d['arm']=arm;d['eta']=r['eta'];d['t']=r['t'];rows.append(d)
        d=pd.concat(rows,ignore_index=True)
        require(len(d)==7200 and d.visit_id.nunique()==480,'Prediction coverage')
        save(d,OUT/'predictions/visits.parquet')
        write(OUT/'predictions/complete.json',{'sha256':sha(OUT/'predictions/visits.parquet'),
            'rows':7200,'unique_visits':480,'arms':5,'roles':60,'StrongPost_probability_max_error':maximum,
            'all_models_and_training_directions_sealed':True,'H_labels_read':False,'test_pre_read':False})

def labeled():
    c=contract();seal=read(OUT/'predictions/complete.json')
    checked(OUT/'predictions/visits.parquet',seal['sha256'],'all-predictions-seal')
    labs=[]
    for r in c['roles']:
        d=package(rolepath(r)/'labels.parquet','score').drop(columns='protocol')
        for k in ['outer','target','group']:d[k]=r[k]
        labs.append(d)
    return pd.read_parquet(OUT/'predictions/visits.parquet').merge(pd.concat(labs),
            on=['outer','target','group','visit_id'],validate='many_to_one')

def bootstrap(d):
    arms=ARMS;contents=sorted(d.content_id.unique());uix={u:i for i,u in enumerate(contents)}
    groups=list(MASKS);cm=np.zeros((5,4,3,30,6,6),dtype=np.int32)
    for (a,p,g,u),part in d.groupby(['arm','target','group','content_id']):
        y=truths(part);z=part.prediction.to_numpy()
        cm[arms.index(a),PROTOCOLS.index(p),groups.index(g),uix[u]]=np.bincount(y*6+z,minlength=36).reshape(6,6)
    labels=d[['content_id','label_id']].drop_duplicates().set_index('content_id').loc[contents].label_id
    require(len(labels)==30,'Content identity label conflict')
    rng=np.random.default_rng(20261009);weights_=np.zeros((10000,30),dtype=np.int32)
    for label in LABELS:
        ids=np.where(labels.to_numpy()==label)[0];require(len(ids)==5,'Five contents/class')
        picks=rng.choice(ids,size=(10000,5),replace=True)
        for bi in range(10000):weights_[bi]+=np.bincount(picks[bi],minlength=30)
    uncovered=np.empty((10000,5));auxiliary=np.empty_like(uncovered)
    for left in range(0,10000,250):
        cc=np.einsum('bc,apgcyz->bapgyz',weights_[left:left+250],cm,optimize=True)
        den=cc.sum(-1)+cc.sum(-2)
        f1=np.divide(2*np.diagonal(cc,axis1=-2,axis2=-1),den,out=np.zeros_like(den,dtype=float),where=den>0)
        uu=[];aa=[]
        for gi,g in enumerate(groups):
            uu.append(np.take(f1[:,:,:,gi,:],MASKS[g],axis=-1).mean(-1))
            aa.append(np.delete(f1[:,:,:,gi,:],MASKS[g],axis=-1).mean(-1))
        uncovered[left:left+250]=np.stack(uu,-1).mean((2,3))
        auxiliary[left:left+250]=np.stack(aa,-1).mean((2,3))
    return contents,weights_,uncovered,auxiliary

def score():
    with stage('formal_score'):
        authorization();d=labeled();pc=[f'p{i}' for i in range(6)];scenes=[];classes=[];cms=[];folds=[]
        for (a,p,g),part in d.groupby(['arm','target','group']):
            require(len(part)==120 and part.visit_id.is_unique and part.content_id.nunique()==30,'OOF membership')
            m,cm,f=metrics(truths(part),part[pc].to_numpy(),MASKS[g]);scenes.append({'arm':a,'target':p,'group':g,**m})
            cms.append({'arm':a,'target':p,'group':g,'matrix':cm.tolist()})
            for y in range(6):classes.append({'arm':a,'target':p,'group':g,'label':LABELS[y],'label_index':y,
                'F1':float(f[y]),'uncovered':y in MASKS[g],'support':int(cm[y].sum()),
                'TP':int(cm[y,y]),'FP':int(cm[:,y].sum()-cm[y,y]),'FN':int(cm[y].sum()-cm[y,y])})
        for (a,p,g,f),part in d.groupby(['arm','target','group','outer']):
            m,_,_=metrics(truths(part),part[pc].to_numpy(),MASKS[g]);folds.append({'arm':a,'target':p,'group':g,'outer':int(f),**m})
        scene=pd.DataFrame(scenes);cols=['F1_all','F1_uncovered','F1_aux','accuracy','CE_nats','CE_bits','Brier']
        pooled=scene.groupby('arm')[cols].mean().reset_index();targets=scene.groupby(['arm','target'])[cols].mean().reset_index()
        pooled=pooled.merge(targets.groupby('arm').F1_uncovered.min().rename('worst_target_uncovered'),on='arm')
        require(abs(float(pooled.set_index('arm').loc['S','F1_uncovered'])-.772708)<1e-6,'Historical StrongPost score')
        for name,df in [('scenarios',scene),('targets',targets),('pooled',pooled),('classes',pd.DataFrame(classes)),
                        ('outer-folds',pd.DataFrame(folds)),('labeled-predictions',d)]:save(df,OUT/'scores'/(name+'.parquet'))
        write(OUT/'scores/confusion-matrices.json',cms)
        contents,w,u,aux=bootstrap(d);point=pooled.set_index('arm');comparisons=[]
        for a,b in COMPARISONS:
            delta=u[:,ARMS.index(a)]-u[:,ARMS.index(b)];lo,hi=np.quantile(delta,[.00625,.99375]);l95,h95=np.quantile(delta,[.025,.975])
            comparisons.append({'candidate':a,'reference':b,'delta_F1_uncovered':float(point.loc[a,'F1_uncovered']-point.loc[b,'F1_uncovered']),
                'CI_98_75':[float(lo),float(hi)],'CI_95':[float(l95),float(h95)],'positive_increment':bool(lo>0)})
        write(OUT/'comparisons/primary.json',{'family':4,'comparisons':comparisons,'bootstrap_samples':10000,
             'bootstrap_seed':20261009,'model_conditional_not_external_validation':True,'selected_winner':None,
             'local_derivative_precision_validated':False})
        dst=writable(OUT/'comparisons/bootstrap.npz');dst.parent.mkdir(parents=True,exist_ok=True)
        np.savez_compressed(dst,arms=np.array(ARMS),contents=np.array(contents),weights=w,uncovered=u,auxiliary=aux)
        flips=[]
        for (p,g,f),part in d.groupby(['target','group','outer']):
            for a,b in COMPARISONS:
                x=part[part.arm.eq(a)].set_index('visit_id');y=part[part.arm.eq(b)].set_index('visit_id').loc[x.index]
                truth=truths(x);ac=x.prediction.to_numpy()==truth;bc=y.prediction.to_numpy()==truth
                for j,visit in enumerate(x.index):flips.append({'target':p,'group':g,'outer':int(f),'visit_id':visit,
                    'content_id':x.iloc[j].content_id,'label_id':x.iloc[j].label_id,'uncovered':int(truth[j]) in MASKS[g],
                    'candidate':a,'reference':b,'fixed_error':bool(ac[j] and not bc[j]),'new_error':bool(bc[j] and not ac[j]),
                    'changed':bool(x.iloc[j].prediction!=y.iloc[j].prediction),
                    'probability_L1':float(np.abs(x.iloc[j][pc].to_numpy(float)-y.iloc[j][pc].to_numpy(float)).sum())})
        save(pd.DataFrame(flips),OUT/'scores/error-flips.parquet')
        progress('formal_primary_results',comparisons=comparisons)

def diagnose():
    with stage('formal_diagnose'):
        authorization();c=contract();d=labeled();rows=[];contributions=[]
        for r in c['roles']:
            v=artifact(viewpath(r));direction=artifact(OUT/'training-directions'/r['id']/'direction.pt')
            model=O.normalized_model(artifact(basemodel(r)));q=direction['q']
            query=package(rolepath(r)/'query.parquet','query')
            labs=package(rolepath(r)/'labels.parquet','score').set_index('visit_id').loc[query.visit_id]
            x=(tensor(query[HIST])-v['mu'])/v['scale'];y=tensor(truths(labs),torch.long)
            sourcepost=package(rolepath(r)/'source-post.parquet','train')
            sourcepre=package(rolepath(r)/'source-pre.parquet','train')
            grads={}
            for scope in ['all','C','U']:
                mask=torch.ones(len(y),device=device(),dtype=torch.bool) if scope=='all' else torch.isin(y,tensor(r['missing'],torch.long))
                if scope=='C':mask=~mask
                ss={'x':x[mask],'y':y[mask],'mass':torch.full((int(mask.sum()),),1/int(mask.sum()),device=device(),dtype=torch.float64)}
                riskgrad=I.pack_gradient(O.gradient(model,ss,r['t'],False),q);grads[scope]=riskgrad
                # This is retrospective, unvalidated local CE approximation, never a training signal.
                for side in ['P','G']:
                    estimate=float(riskgrad@direction['d_'+side]);norm=float(direction['d_'+side].norm())
                    ratio=float(direction['e0'].norm())/max(1e-12,.01*norm)
                    for size in ['small','full']:
                        arm=side+'-'+size;part=d[d.role_id.eq(r['id'])]
                        pc=[f'p{i}' for i in range(6)]
                        a=part[part.arm.eq(arm)].set_index('visit_id').loc[query.visit_id]
                        b=part[part.arm.eq('S')].set_index('visit_id').loc[query.visit_id]
                        yy=truths(labs);include=mask.cpu().numpy();ix=np.arange(len(yy))
                        delta=float((-np.log(a[pc].to_numpy()[ix,yy])+np.log(b[pc].to_numpy()[ix,yy]))[include].mean())
                        rows.append({'role_id':r['id'],'target':r['target'],'group':r['group'],'outer':r['outer'],
                            'scope':scope,'arm':arm,'beta':.1 if size=='small' else 1.,'I_unvalidated':estimate,
                            'actual_delta_CE':delta,'stationarity_ratio':ratio,'local_precision_validated':False,
                            'sign_agreement_descriptive_only':bool(np.sign(estimate)==np.sign(delta))})
            require(residual(grads['all'],2/3*grads['C']+1/3*grads['U'])<=1e-10,'C/U risk gradient decomposition')
            # Match content/deployment bags, not source pre/post visit rows.
            for side in ['P','G']:
                total=torch.zeros(581,device=device(),dtype=torch.float64)
                for (proto,content),source_rows in sourcepost.groupby(['protocol','content_id']):
                    si=source_rows.index.to_numpy();pi=sourcepre.index[(sourcepre.protocol==proto)&(sourcepre.content_id==content)].to_numpy()
                    gparts=[]
                    for a,indices in [('S',si),(side,pi)]:
                        z=O.auxiliary(v,a);ss={k:t[indices] for k,t in z.items()};gparts.append(I.pack_gradient(O.gradient(model,ss,r['t'],False),q))
                    delta=gparts[1]-gparts[0];total+=delta
                    localdir=-torch.cholesky_solve(delta[:,None],direction['cholesky']).squeeze(1)
                    contributions.append({'role_id':r['id'],'target':r['target'],'group':r['group'],'outer':r['outer'],
                        'arm':side,'source_protocol':proto,'source_content':content,
                        **{'I_'+scope:float(g@localdir) for scope,g in grads.items()},'local_precision_validated':False})
                require(residual(total,direction['delta_'+side])<=1e-10,'Source bag gradient contributions do not sum')
        table=pd.DataFrame(rows);parts=pd.DataFrame(contributions)
        require(len(table)==720 and len(parts)==8640,'Diagnostic coverage')
        for r in c['roles']:
            for a in ['P','G']:
                for scope in ['all','C','U']:
                    pt=parts[parts.role_id.eq(r['id'])&parts.arm.eq(a)]['I_'+scope].sum()
                    expected=table[table.role_id.eq(r['id'])&table.arm.eq(a+'-small')&table.scope.eq(scope)].I_unvalidated.iloc[0]
                    require(abs(pt-expected)<=1e-10*max(1.,abs(expected)),'Influence contribution sum')
        save(table,OUT/'influences/unvalidated-local-vs-actual.parquet')
        save(parts,OUT/'influences/source-content-contributions.parquet')
        write(OUT/'influences/complete.json',{'rows':720,'source_content_rows':8640,
            'local_derivative_precision_validated':False,'retrospective_only':True,
            'gradients_additive_not_F1_additive':True,'target_U_training_read':False,'test_pre_read':False})

def verify():
    with stage('formal_verify'):
        authorization();c=contract()
        for name in ['formal_fit','formal_predict','formal_score','formal_diagnose','formal_report']:
            require(read(OUT/'stages'/f'{name}.json')['passed'],'Missing formal stage')
        endpoints=pd.read_parquet(OUT/'manifests/formal-endpoints.parquet').set_index(['role_id','arm'])
        pred=pd.read_parquet(OUT/'predictions/visits.parquet');pc=[f'p{i}' for i in range(6)];error=0.;audits=[]
        for r in c['roles']:
            v=artifact(viewpath(r));query=package(rolepath(r)/'query.parquet','query')
            for arm in ARMS:
                path=basemodel(r) if arm=='S' else ROOT/endpoints.loc[(r['id'],arm)].model_path
                m=artifact(path);log=read(path.with_suffix('.json'))['optimizer']
                s=O.slot(v,'P' if arm=='S' else arm[0],0. if arm=='S' else .1 if arm.endswith('small') else 1.)
                audit=audit_model(m,s,r['t'],log);audits.append({'role_id':r['id'],'arm':arm,**audit})
                pp=predict(m,query).set_index('visit_id');expected=pred[pred.role_id.eq(r['id'])&pred.arm.eq(arm)].set_index('visit_id')
                diff=float(np.abs(pp.loc[expected.index,pc].to_numpy()-expected[pc].to_numpy()).max());error=max(error,diff)
                require(diff<1e-12,'Formal prediction replay')
        # Independent bootstrap rerun on sealed predictions, no re-selection.
        d=labeled();contents,w,u,aux=bootstrap(d);stored=np.load(OUT/'comparisons/bootstrap.npz')
        require(np.array_equal(w,stored['weights']) and np.array_equal(u,stored['uncovered']) and np.array_equal(aux,stored['auxiliary']),'Bootstrap replay')
        require(len(list((OUT/'fit-logs').rglob('*.json')))==199,'New formal fit count')
        require(len(list((OUT/'diagnostic-fit-logs').rglob('*.json')))==60,'Pilot fit count')
        require(not read(OUT/'pilot/promotion.json')['passed'],'Original pilot must remain failed')
        access=[a for marker in (OUT/'stages').glob('*.json') for a in read(marker).get('reads',[])]
        require(not any('heldout-visits' in a['path'] or 'main-test-paired' in a['path'] for a in access),'Test pre read')
        require(not (OUT/'failure.json').exists(),'Unresolved runtime failure')
        save(pd.DataFrame(audits),OUT/'scores/independent-model-audit.parquet')
        files=[p for p in DOC.rglob('*') if p.is_file()]+[OUT/'predictions/visits.parquet',OUT/'comparisons/primary.json',
            OUT/'comparisons/bootstrap.npz',OUT/'manifests/continuation.json',OUT/'manifests/formal-endpoints.parquet']
        write(OUT/'verification.json',{'passed':True,'finite_interventions_complete':True,
            'numerical_pilot_passed':False,'local_derivative_precision_validated':False,
            'new_formal_classifiers':199,'reused_full_classifiers':41,'reused_S':60,'diagnostic_classifiers':60,
            'new_mappings':11,'model_replays':300,'probability_max_error':error,'bootstrap_exactly_replayed':True,
            'target_U_training_reads':0,'test_pre_reads':0,'H_labels_after_all_prediction_seal':True,
            'all_classifier_fit_and_prediction_CUDA_float64':True,'files':{rel(p):sha(p) for p in files}})
    write(OUT/'completion.json',{'passed':True,'finite_interventions_complete':True,'numerical_pilot_passed':False,
        'local_derivative_precision_validated':False,'user_authorized_continuation':True,
        'verification_sha256':sha(OUT/'verification.json'),'time_unix':time.time()})

if __name__=='__main__':{'register':register,'train':train,'predict':predict_all,'score':score,'diagnose':diagnose,'verify':verify}[sys.argv[1]]()
