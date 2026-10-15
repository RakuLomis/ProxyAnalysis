"""Q00-Q20 staged pipeline. Every outer score is after sealed qualification."""
import argparse
import platform
import sys
from common import *

def tests():
    configure(); records=[]
    def check(name,ok): require(ok,name); records.append({'test':name,'pass':True})
    a=tensor([[3.,1.],[1.,3.]])
    n=a[None].expand(6,-1,-1).clone(); kt,q=smooth(n.sum(0))
    check('no-Y identical conditional rows',torch.equal(conditional(n,kt,'1')[0],conditional(n,kt,'1')[5]))
    dep=torch.stack([tensor([[4.,0.],[4.,0.]]) if y<3 else tensor([[0.,4.],[0.,4.]]) for y in range(6)])
    kc,qc=smooth(dep.sum(0)); kd=conditional(dep,kc,'1')
    check('known business effect improves known target',float(kd[0,0,0])>float(kc[0,0]))
    sparse=dep.clone(); sparse[:,1]=0
    check('empty class row falls back common',torch.equal(conditional(sparse,kc,'1')[:,1],kc[1].expand(6,-1)))
    check('infinite shrink exact common',torch.equal(conditional(dep,kc,'inf'),kc.expand(6,-1,-1)))
    check('infinite post shrink exact pooled',torch.equal(post_conditional(dep,qc,'inf'),qc.expand(6,-1)))
    for tag,row in [('empirical',empirical_rows(dep)),('smoothed',kd)]:
        w,b,t,mean,nu=covariance(dep,row)
        check(tag+' covariance adds',float((w+b-t).abs().max())<1e-12)
        check(tag+' PSD',min(float(torch.linalg.eigvalsh(v).min()) for v in [w,b,t])>-1e-12)
        z=tensor([2.,3.]); check(tag+' scaled covariance adds',float(((w/z[:,None]/z)+(b/z[:,None]/z)-(t/z[:,None]/z)).abs().max())<1e-12)
    S=dep.sum(2)/dep.sum((1,2))[:,None]
    marginal=(S[:,:,None]*empirical_rows(dep)).sum(1)
    check('unsmoothed S times K equals class post',float((marginal-dep.sum(1)/dep.sum((1,2))[:,None]).abs().max())<1e-12)
    asymmetric=dep.clone(); asymmetric[0,0,0]=9
    ac,_=smooth(asymmetric.sum(0)); ar=conditional(asymmetric,ac,'1')
    check('inconsistent smoothing not equated to original common',float((covariance(asymmetric,ar)[3]-ac).abs().max())>1e-6)
    idx=tensor([0,1,1],torch.long); mass=tensor([.3,.2,.5])
    check('deterministic weighted counts',torch.equal(weighted(idx,mass,2),tensor([.3,.7])))
    check('empty interval rejected',not interval(.5,[-.1,-.05])[-1])
    check('joint moment PI conversion',abs(PI*.6-.1)<1e-15)
    x=torch.nn.Parameter(tensor([1.])); zero=x.sum()*0; zero.backward()
    check('empty regularizer zero gradient',float(x.grad)==0)
    write(OUT/'manifests/unit-tests.json',records)

def prepare():
    configure(); require(not (OUT/'manifests/experiment-contract.json').exists(),'Contract exists; use following stages')
    old=read(KSR/'manifests/experiment-contract.json'); baseline={}
    for p,h in old['source_sha256'].items():
        require(sha(ROOT/p)==h,'Old source differs'); baseline[p]=h
    for p,h in old['packages_sha256'].items():
        require(sha(ROOT/p)==h,'Old package differs'); baseline[p]=h
    for p in [PLAN,KSR/'manifests/experiment-contract.json',KSR/'verification.json',
              Q/'cohorts/pairs.parquet',Q/'cohorts/folds.parquet',Q/'features/paired-flow-features.parquet']:
        baseline[rel(p)]=sha(p)
    df=pd.read_parquet(Q/'features/paired-flow-features.parquet')
    require(len(df)==23566 and df.session_id.nunique()==480 and df.content_id.nunique()==30,'Frozen cohort changed')
    require(df.pair_id.is_unique,'Pair duplicate')
    for field in ['session_id','pair_id','logical_id','carrier_id','registered_epoch_proxy']:
        require(df.groupby(field).fold.nunique().max()==1,'Registered entity crosses content folds')
    packages={}; roles=old['roles']; audits=[]
    for r in roles:
        tr=set(r['train_contents']); va=set(r['validation_contents'])
        require(len(tr)==(24 if r['inner'] is None else 18) and len(va)==6 and not tr&va,'Role overlap')
        require(not tr&set(r.get('outer_test_contents',[])) and not va&set(r.get('outer_test_contents',[])),'Inner/test overlap')
        src=folder('packages',r,KSR); dst=folder('packages',r)
        pre=pd.read_parquet(src/'fit-pre.parquet'); post=pd.read_parquet(src/'fit-post.parquet')
        hist=pd.read_parquet(src/'fit-post-hist.parquet')
        require(pre.pair_id.equals(post.pair_id) and set(pre.content_id)==tr,'Pair alignment')
        labelmap=hist[['content_id','label_id']].drop_duplicates().sort_values('content_id')
        require(labelmap.content_id.is_unique and hist.groupby('label_id').size().eq(len(tr)//6*4).all(),'Label balance')
        paired=pre.merge(post,on=['pair_id','session_id','content_id','fit_mass'],validate='one_to_one')
        paired=paired.merge(labelmap,on='content_id',validate='many_to_one')
        require(abs(paired.fit_mass.sum()-len(tr))<1e-10,'Training mass')
        items={'train-paired':paired,'train-label-map':labelmap,'train-post-hist':hist,
               'group-pre':pd.read_parquet(src/'group-pre.parquet'),
               'group-post':pd.read_parquet(src/'group-post.parquet')}
        for side in ['pre','post']:
            require(set(items['group-'+side])=={'content_id','fit_mass',*[side+'_'+f for f in FEATURES]},'Group contains instance IDs')
        labels=pd.read_parquet(src/'score-labels.parquet'); query=pd.read_parquet(src/'query-post-hist.parquet')
        mscore=query.merge(labels[['visit_id','content_id','label_id']],on='visit_id',validate='one_to_one')
        require(set(mscore.content_id)==va and mscore.groupby('content_id').size().eq(4).all(),'Score role')
        items['moment-score']=mscore
        if r['inner'] is None:
            queryflow=df[(df.protocol==r['protocol'])&df.content_id.isin(va)].copy().sort_values('pair_id')
            queryflow['pair_token']=[hashlib.sha256(('conditional-flow-v1:'+p).encode()).hexdigest() for p in queryflow.pair_id]
            queryflow['visit_id']=[hashlib.sha256(('business-query-v1:'+p).encode()).hexdigest() for p in queryflow.session_id]
            require(not set(queryflow.pair_id)&set(paired.pair_id),'Query/train flow overlap')
            items['oracle-pre-Y']=queryflow[['pair_token','visit_id','label_id',*['pre_'+f for f in FEATURES]]]
            items['score-post']=queryflow[['pair_token','visit_id','content_id','label_id',*['post_'+f for f in FEATURES]]]
        for name,frame in items.items():
            p=dst/(name+'.parquet'); save(frame,p); packages[rel(p)]=sha(p)
        for feature in FEATURES:
            p=folder('kernels',r,KSR)/(feature+'.pt')
            require(read(p.parent/'complete.json')['sha256'][p.name]==sha(p),'Old kernel SHA'); baseline[rel(p)]=sha(p)
        p=folder('models',r,KSR)/'zero.pt'
        require(read(p.parent/'complete.json')['sha256'][p.name]==sha(p),'Zero model SHA'); baseline[rel(p)]=sha(p)
        audits.append({'role':key(r),'train_contents':len(tr),'validation_contents':6,
                       'train_visits':hist.session_id.nunique(),'train_pairs':len(paired),'registered_overlap':0})
    tests()
    files=sorted(Path(__file__).parent.glob('*.py'))+[Path(__file__).parent/'README.md']
    write(OUT/'manifests/experiment-contract.json',{'registered_unix':time.time(),'roles':roles,
        'source_sha256':{rel(p):sha(p) for p in files},'packages_sha256':packages,'baseline_sha256':baseline,
        'main_kappa':'1','sensitivity':KAPPAS,'features':FEATURES,'weights':WEIGHTS,'labels':LABELS,
        'tail_first_bin':4,'pi':PI,'family_size':12,'bootstrap_samples':10000,'bootstrap_seed':20261005,
        'qualification':{'max_error':.10*PI,'max_width':.50*PI,'relevance':.05,
                         'min_mae_gain':.01*PI,'positive_folds':3,'cap_total':6,'cap_family':2,
                         'cap_business':2,'cap_feature':1},
        'classifier_training':False,'stop_after_report':True,'oracle_labels_not_attack_inference':True})
    write(OUT/'manifests/role-audit.json',audits)
    write(OUT/'manifests/environment.json',{'python':sys.version,'executable':sys.executable,'torch':torch.__version__,
        'cuda':torch.version.cuda,'gpu':torch.cuda.get_device_name(0),'dtype':'float64','platform':platform.platform(),
        'deterministic':True,'arrow_imported_before_torch':True})
    finish('Q00-Q08',roles=len(roles),pairs=len(df),visits=480,contents=30)

def fit(inner):
    c=start('fit'); targetrows=[]; covrows=[]; support=[]; replays=[]
    for r in c['roles']:
        if (r['inner'] is not None)!=inner: continue
        dst=folder('kernels',r); dst.mkdir(parents=True,exist_ok=True)
        paired=package(r,'train-paired','fit'); gp=package(r,'group-pre','fit'); gb=package(r,'group-post','fit')
        labels=package(r,'train-label-map','fit'); hist=package(r,'train-post-hist','fit')
        ys=tensor(paired.label_id.map({l:i for i,l in enumerate(LABELS)}),torch.long); mass=tensor(paired.fit_mass)
        contentlist=sorted(labels.content_id); lookup={u:i for i,u in enumerate(contentlist)}
        ci=tensor(gp.content_id.map(lookup),torch.long); cj=tensor(gb.content_id.map(lookup),torch.long)
        yc=tensor(labels.set_index('content_id').loc[contentlist].label_id.map({l:i for i,l in enumerate(LABELS)}),torch.long)
        wm=tensor(gp.fit_mass); wb=tensor(gb.fit_mass)
        cm=weighted(ci,wm,len(contentlist)); require(float((cm-1).abs().max())<1e-10,'Content mass not one')
        frozen=load_old('models',r,'zero') if not inner else None
        scale=tensor(hist[HIST]).std(0,unbiased=False); scale=torch.where(scale>0,scale,torch.ones_like(scale))
        if frozen is not None: require(float((scale-frozen['scale']).abs().max())<1e-12,'Scale replay')
        offset=0
        for j,f in enumerate(FEATURES):
            k=size(j); a=bins(paired['pre_'+f],j); b=bins(paired['post_'+f],j)
            n=weighted((ys*k+a)*k+b,mass,6*k*k).reshape(6,k,k)
            ca=weighted(ci*k+bins(gp['pre_'+f],j),wm,len(contentlist)*k).reshape(-1,k)
            cb=weighted(cj*k+bins(gb['post_'+f],j),wb,len(contentlist)*k).reshape(-1,k)
            contentjoint=ca[:,:,None]*cb[:,None,:]/cm[:,None,None]
            g=F.one_hot(yc,6).to(torch.float64).T@contentjoint.reshape(len(contentlist),-1); g=g.reshape(6,k,k)
            old=load_old('kernels',r,f)
            replay=max(float((n.sum(0)-old['true_counts']).abs().max()),float((g.sum(0)-old['group_counts']).abs().max()))
            require(replay<1e-10,'Wrong old kernel scope or count replay')
            require(max(float((n.sum(1)-g.sum(1)).abs().max()),float((n.sum(2)-g.sum(2)).abs().max()))<1e-10,'Class margins differ')
            kt,q=smooth(n.sum(0)); kg,qg=smooth(g.sum(0))
            require(float((q-qg).abs().max())<1e-10,'Shared post marginal differs')
            bundle={'true_by_y':n,'group_by_y':g,'common_true':kt,'common_group':kg,'pooled_post':q}
            for v in KAPPAS:
                bundle['true_'+v]=conditional(n,kt,v); bundle['group_'+v]=conditional(g,kg,v)
                bundle['post_'+v]=post_conditional(n,q,v)
                for name in ['true_'+v,'group_'+v,'post_'+v]:
                    p=bundle[name]; require(float(p.min())>0 and float((p.sum(-1)-1).abs().max())<1e-10,'Probability invalid')
            torch.save(bundle,dst/(f+'.pt'))
            replays.append({'role':key(r),'feature':f,'max_count_error':replay})
            for y in range(6):
                support.append({'outer':r['outer'],'inner':r['inner'],'protocol':r['protocol'],'y':y,'feature':f,
                    'class_mass':float(n[y].sum()),'empty_A_rows':int((n[y].sum(1)==0).sum()),'bins':k})
            ts=moment_targets(bundle)
            for y in range(6): targetrows.append({'outer':r['outer'],'inner':r['inner'],'protocol':r['protocol'],
                'y':y,'j':j,**{t:float(ts[t][y]) for t in TARGETS}})
            if not inner:
                covs={}
                for tag,rows in [('empirical',empirical_rows(n)),('smoothed',bundle['true_1'])]:
                    wi,be,total,mean,nu=covariance(n,rows)
                    err=float((wi+be-total).abs().max()); eig=min(float(torch.linalg.eigvalsh(x).min()) for x in [wi,be,total])
                    require(err<1e-10 and eig>-1e-10,'Covariance law/PSD failed')
                    common=kt if tag=='smoothed' else n.sum(0)/n.sum((0,2))[:,None].clamp_min(1e-300)
                    commoncov=(nu[:,None,None]*(torch.diag_embed(common)-common[:,:,None]*common[:,None,:])).sum(0)
                    ss=scale[offset:offset+k]; weight=WEIGHTS[j]
                    wi_x=wi/ss[:,None]/ss[None,:]*weight; be_x=be/ss[:,None]/ss[None,:]*weight
                    wc=frozen['weight'][:,offset:offset+k]; wc=wc-wc.mean(0,keepdim=True)
                    ew=float(torch.trace(wc@wi_x@wc.T)/5); eb=float(torch.trace(wc@be_x@wc.T)/5)
                    tw=float(torch.trace(wi)); tb=float(torch.trace(be)); denom=tw+tb
                    covs[tag]={'within':wi,'between':be,'total':total,'mixture':mean,'nu':nu,
                               'within_scaled':wi_x,'between_scaled':be_x,'common_covariance':commoncov}
                    covrows.append({'outer':r['outer'],'protocol':r['protocol'],'j':j,'feature':f,'distribution':tag,
                        'within_trace':tw,'between_trace':tb,'between_fraction':tb/denom if denom>0 else 0.,
                        'within_score_energy':ew,'between_score_energy':eb,'add_error':err,'min_eigenvalue':eig,
                        'mixture_common_max_gap':float(((mean-common)*((nu>0)[:,None])).abs().max()),
                        'covariance_common_max_gap':float((total-commoncov).abs().max())})
                folder('decomposition',r).mkdir(parents=True,exist_ok=True)
                torch.save(covs,folder('decomposition',r)/(f+'.pt'))
            offset+=k
        complete(dst,role=key(r),train_contents=r['train_contents'])
        if not inner: complete(folder('decomposition',r),role=key(r))
        print('fit',key(r),flush=True)
    part='inner' if inner else 'outer'
    save(pd.DataFrame(targetrows),OUT/f'moments/{part}-targets.parquet')
    save(pd.DataFrame(support),OUT/f'scores/{part}-support.parquet')
    if covrows: save(pd.DataFrame(covrows),OUT/'scores/decomposition.parquet')
    write(OUT/'manifests'/f'{part}-count-replay.json',replays)
    finish('Q09-Q10' if inner else 'Q12',bundles=len(replays),numerical_device='cuda:0')

def actual_moments(r,stage):
    h=package(r,'moment-score',stage); rows=[]
    for y,label in enumerate(LABELS):
        sub=h[h.label_id==label]; require(sub.content_id.nunique()==1 and len(sub)==4,'One held-out content/class required')
        for j in range(10):
            cols=[f'h{j:02d}_{b:02d}' for b in range(4,size(j))]
            rows.append({'y':y,'j':j,'actual':float(tensor(sub[cols]).sum(1).mean()*PI)})
    return pd.DataFrame(rows)

def inner_score():
    c=start('inner_score'); targets=pd.read_parquet(OUT/'moments/inner-targets.parquet'); allrows=[]
    for r in c['roles']:
        if r['inner'] is None: continue
        t=targets[(targets.outer==r['outer'])&(targets.protocol==r['protocol'])&(targets.inner==r['inner'])]
        allrows.append(t.merge(actual_moments(r,'inner_score'),on=['y','j'],validate='one_to_one'))
    df=pd.concat(allrows,ignore_index=True)
    for t in TARGETS: df['error_'+t]=df.actual-df[t]
    save(df,OUT/'moments/inner-oof.parquet'); finish('Q11',relations=len(df))

def qualify():
    c=start('qualify'); d=pd.read_parquet(OUT/'moments/inner-oof.parquet'); full=pd.read_parquet(OUT/'moments/outer-targets.parquet'); records=[]
    for r in c['roles']:
        if r['inner'] is not None: continue
        rr=d[(d.outer==r['outer'])&(d.protocol==r['protocol'])]
        targets=full[(full.outer==r['outer'])&(full.protocol==r['protocol'])].set_index(['y','j'])
        for y in range(6):
            for j in range(10):
                sub=rr[(rr.y==y)&(rr.j==j)].sort_values('inner'); e=sub.error_T1.to_numpy()
                require(len(sub)==4 and sub.inner.nunique()==4,'Four residual contents required')
                support=np.isfinite(e).all(); target=float(targets.loc[(y,j),'T1'])
                rl,rh,lo,hi,nonempty=interval(target,e)
                other=rr[(rr.y!=y)&(rr.j==j)]
                relevance=abs(sub.actual.mean()/PI-other.actual.mean()/PI)
                reliable=bool(support and max(abs(e))<=.10*PI and nonempty and hi-lo<=.50*PI and relevance>=.05)
                gains={t:float((abs(sub['error_'+t])-abs(sub.error_T1)).mean()) for t in ['G1','P0','P1']}
                positives={t:int((abs(sub['error_'+t])>abs(sub.error_T1)).sum()) for t in ['G1','P0','P1']}
                incremental=all(gains[t]>=.01*PI and positives[t]>=3 for t in gains)
                failed=[]
                if not support: failed.append('support')
                if max(abs(e))>.10*PI: failed.append('max_error')
                if not nonempty: failed.append('empty_interval')
                if nonempty and hi-lo>.50*PI: failed.append('width')
                if relevance<.05: failed.append('task_relevance')
                if not incremental: failed.append('no_increment_vs_all_three_controls')
                records.append({'outer':r['outer'],'protocol':r['protocol'],'y':y,'j':j,'business':LABELS[y],
                    'feature':FEATURES[j],'family':family(j),'target':target,'raw_lower':rl,'raw_upper':rh,
                    'lower':lo,'upper':hi,'interval_nonempty':nonempty,'width':hi-lo,'bias':float(e.mean()),
                    'mae':float(abs(e).mean()),'max_abs_error':float(max(abs(e))), 'relevance':float(relevance),
                    'reliable':reliable,'incremental':bool(incremental),'rank_gain':min(gains.values()),
                    'selected':False,'failures':';'.join(failed),
                    **{'gain_'+t:v for t,v in gains.items()},**{'positive_'+t:v for t,v in positives.items()}})
    df=pd.DataFrame(records)
    for (outer,proto),sub in df.groupby(['outer','protocol']):
        candidates=sub[sub.reliable&sub.incremental].sort_values(['rank_gain','y','j'],ascending=[False,True,True])
        fs={}; bs={}; used=set(); chosen=[]
        for i,row in candidates.iterrows():
            if len(chosen)>=6: break
            if fs.get(row.family,0)>=2 or bs.get(row.y,0)>=2 or row.j in used: continue
            chosen.append(i); fs[row.family]=fs.get(row.family,0)+1; bs[row.y]=bs.get(row.y,0)+1; used.add(row.j)
        df.loc[chosen,'selected']=True
    save(df,OUT/'qualification/all-relations.parquet')
    complete(OUT/'qualification',sealed_before_outer_prediction_and_scoring=True,
             inner_oof_sha256=sha(OUT/'moments/inner-oof.parquet'),outer_targets_sha256=sha(OUT/'moments/outer-targets.parquet'),
             source_sha256=c['source_sha256'],selected=int(df.selected.sum()),reliable=int(df.reliable.sum()))
    finish('Q13',selected=int(df.selected.sum()),reliable=int(df.reliable.sum()),incremental=int(df.incremental.sum()))

def activity():
    c=start('activity'); q=pd.read_parquet(OUT/'qualification/all-relations.parquet'); records=[]; gradients=[]
    for r in c['roles']:
        if r['inner'] is not None: continue
        h=package(r,'train-post-hist','activity'); m=load_old('models',r,'zero')
        w=m['weight'].clone().requires_grad_(); b=m['bias'].clone().requires_grad_()
        x=(tensor(h[HIST])-m['mu'])/m['scale']; p=torch.softmax(x@w.T+b,1)
        sub=q[(q.outer==r['outer'])&(q.protocol==r['protocol'])]
        penalties=[]
        for row in sub.itertuples():
            cols=[f'h{row.j:02d}_{v:02d}' for v in range(4,size(row.j))]
            tail=tensor(h[cols]).sum(1); moment=(p[:,row.y]*tail).mean()
            if row.interval_nonempty:
                violation=F.relu(row.lower-moment)+F.relu(moment-row.upper)
                pen=(violation/PI).square()
            else: violation=moment*0; pen=moment*0
            if row.selected: penalties.append(pen)
            records.append({'outer':r['outer'],'protocol':r['protocol'],'y':row.y,'j':row.j,
                'm_theta':float(moment.detach()),'lower':row.lower,'upper':row.upper,
                'interval_nonempty':row.interval_nonempty,'violation':float(violation.detach()),
                'reliable':row.reliable,'selected':row.selected})
        regularizer=torch.stack(penalties).mean() if penalties else (w.sum()+b.sum())*0
        gw,gb=torch.autograd.grad(regularizer,[w,b]); norm=float(torch.sqrt(gw.square().sum()+gb.square().sum()))
        require(torch.equal(w.detach(),m['weight']) and torch.equal(b.detach(),m['bias']),'Frozen parameters mutated')
        gradients.append({'outer':r['outer'],'protocol':r['protocol'],'relations':len(penalties),
                          'regularizer':float(regularizer.detach()),'gradient_norm':norm,'no_optimization':True})
    save(pd.DataFrame(records),OUT/'scores/constraint-activity.parquet')
    save(pd.DataFrame(gradients),OUT/'scores/constraint-gradients.parquet'); finish('Q14',roles=len(gradients))

def predict():
    c=start('oracle'); require((OUT/'manifests/Q14-ledger.json').exists(),'Activity first')
    for r in c['roles']:
        if r['inner'] is not None: continue
        query=package(r,'oracle-pre-Y','oracle')
        require(set(query)=={'pair_token','visit_id','label_id',*['pre_'+f for f in FEATURES]},'Oracle includes forbidden fields')
        y=tensor(query.label_id.map({l:i for i,l in enumerate(LABELS)}),torch.long)
        dst=folder('predictions',r); dst.mkdir(parents=True,exist_ok=True)
        save(query[['pair_token','visit_id']],dst/'index.parquet')
        for j,f in enumerate(FEATURES):
            b=load_bundle(r,j); a=bins(query['pre_'+f],j)
            pred={'D0':b['common_true'][a],'DG':b['common_group'][a],
                  'DB':b['pooled_post'].expand(len(query),-1).clone()}
            for v in KAPPAS:
                pred['D1-'+v]=b['true_'+v][y,a]; pred['D2-'+v]=b['group_'+v][y,a]
                pred['D3-'+v]=b['post_'+v][y]
            torch.save(pred,dst/(f+'.pt'))
        complete(dst,oracle_Y=True,no_actual_post_read=True)
    finish('Q15-Q16',probability_roles=20,moment_targets_sha256=sha(OUT/'moments/outer-targets.parquet'))

def score():
    c=start('outer_score'); require((OUT/'manifests/Q15-Q16-ledger.json').exists(),'Prediction seal first')
    rows=[]; momentrows=[]; targets=pd.read_parquet(OUT/'moments/outer-targets.parquet')
    for r in c['roles']:
        if r['inner'] is not None: continue
        post=package(r,'score-post','outer_score'); dst=folder('predictions',r)
        idx=pd.read_parquet(dst/'index.parquet'); require(idx.pair_token.equals(post.pair_token),'Pair index changed')
        require(read(dst/'complete.json')['sha256']['index.parquet']==sha(dst/'index.parquet'),'Index seal')
        actual=actual_moments(r,'outer_score')
        t=targets[(targets.outer==r['outer'])&(targets.protocol==r['protocol'])]
        momentrows.append(t.merge(actual,on=['y','j'],validate='one_to_one'))
        for j,f in enumerate(FEATURES):
            pred=load_bundle(r,j,'predictions'); actualbin=bins(post['post_'+f],j); index=torch.arange(len(post),device=device())
            onehot=F.one_hot(actualbin,size(j)).to(torch.float64)
            for arm,p in pred.items():
                prob=p[index,actualbin]; loss=-torch.log2(prob); brier=(p-onehot).square().sum(1)
                tail=p[:,4:].sum(1); event=(actualbin>=4).to(torch.float64)
                detail=post[['visit_id','content_id','label_id']].copy()
                detail['loss']=loss.cpu().numpy(); detail['brier']=brier.cpu().numpy()
                detail['tail_forecast']=tail.cpu().numpy(); detail['tail_actual']=event.cpu().numpy()
                detail['tail_brier']=(tail-event).square().cpu().numpy()
                visit=detail.groupby(['visit_id','content_id','label_id'],as_index=False).mean(numeric_only=True)
                content=visit.groupby(['content_id','label_id'],as_index=False).mean(numeric_only=True)
                for z in content.to_dict('records'): rows.append({'outer':r['outer'],'protocol':r['protocol'],'j':j,'feature':f,'arm':arm,**z})
    save(pd.DataFrame(rows),OUT/'scores/content-feature-probabilities.parquet')
    md=pd.concat(momentrows,ignore_index=True)
    for t in TARGETS: md['error_'+t]=md.actual-md[t]
    q=pd.read_parquet(OUT/'qualification/all-relations.parquet')
    md=md.merge(q[['outer','protocol','y','j','lower','upper','interval_nonempty','reliable','incremental','selected']],on=['outer','protocol','y','j'],validate='one_to_one')
    md['covered']=md.interval_nonempty&(md.actual>=md.lower)&(md.actual<=md.upper)
    save(md,OUT/'scores/outer-moments.parquet'); finish('Q17',content_feature_scores=len(rows),moment_scores=len(md))

def bootstrap():
    c=start('bootstrap'); d=pd.read_parquet(OUT/'scores/content-feature-probabilities.parquet')
    d['composite']=d.loss*d.j.map(dict(enumerate(WEIGHTS)))
    comp=d.groupby(['protocol','arm','content_id','label_id','outer'],as_index=False).composite.sum()
    save(comp,OUT/'scores/content-composite.parquet')
    summary=comp.groupby(['protocol','arm'],as_index=False).composite.mean(); save(summary,OUT/'scores/probability-summary.parquet')
    folds=pd.read_parquet(Q/'cohorts/folds.parquet').sort_values('content_id'); contents=folds.content_id.tolist()
    rng=np.random.default_rng(20261005); draw=np.zeros((10000,30),dtype=np.int16)
    for label in LABELS:
        where=np.flatnonzero(folds.label_id.to_numpy()==label); require(len(where)==5,'Five contents/class')
        indices=rng.choice(where,size=(10000,5),replace=True)
        for i in range(5): np.add.at(draw,(np.arange(10000),indices[:,i]),1)
    np.save(OUT/'scores/bootstrap-content-counts.npy',draw)
    records=[]
    for proto in PROTOCOLS:
        x=comp[comp.protocol==proto].pivot(index='content_id',columns='arm',values='composite').loc[contents]
        for ref in ['D0','D2-1','D3-1']:
            diff=(x[ref]-x['D1-1']).to_numpy(); samples=draw@diff/30
            lo,hi=np.quantile(samples,[.025,.975]); adjlo,adjhi=np.quantile(samples,[.05/24,1-.05/24])
            records.append({'protocol':proto,'contrast':ref+' minus D1-1','gain_bits':float(diff.mean()),
                'lower_95':float(lo),'upper_95':float(hi),'lower_adjusted':float(adjlo),'upper_adjusted':float(adjhi),
                'positive_adjusted':bool(adjlo>0),'samples':10000,'family':12,'conditional_on_fixed_kernels':True})
    save(pd.DataFrame(records),OUT/'scores/main-contrasts.parquet'); finish('Q18',comparisons=12)

def verify():
    c=start('verify'); maxreplay=0.; covmax=0.; qual=read(OUT/'qualification/complete.json')
    for p,h in c['baseline_sha256'].items(): require(sha(ROOT/p)==h,'Old source/artifact mutated')
    for p,h in c['packages_sha256'].items(): require(sha(ROOT/p)==h,'New sealed package mutated')
    for name,h in qual['sha256'].items(): require(sha(OUT/'qualification'/name)==h,'Qualification seal mutated')
    require(qual['time_unix']<read(OUT/'manifests/Q15-Q16-ledger.json').get('completed_unix',float('inf')),'Qualification ordering')
    q=pd.read_parquet(OUT/'qualification/all-relations.parquet'); d=pd.read_parquet(OUT/'moments/inner-oof.parquet')
    for r in c['roles']:
        # Recalculate all class frequencies from permitted pairs and compare each sealed bundle.
        pairs=package(r,'train-paired','verify'); ys=tensor(pairs.label_id.map({l:i for i,l in enumerate(LABELS)}),torch.long)
        mass=tensor(pairs.fit_mass)
        for j in range(10):
            b=load_bundle(r,j); k=size(j); a=bins(pairs['pre_'+FEATURES[j]],j); z=bins(pairs['post_'+FEATURES[j]],j)
            n=weighted((ys*k+a)*k+z,mass,6*k*k).reshape(6,k,k)
            err=float((n-b['true_by_y']).abs().max()); require(err<1e-12,'Class count replay'); maxreplay=max(maxreplay,err)
            require(torch.equal(b['true_inf'],b['common_true'].expand(6,-1,-1)),'Infinity replay')
            for target,v in moment_targets(b).items(): require(torch.isfinite(v).all(),'Target replay')
            if r['inner'] is None:
                for tag,row in [('empirical',empirical_rows(n)),('smoothed',b['true_1'])]:
                    w,be,t,_,_=covariance(n,row); err=float((w+be-t).abs().max()); covmax=max(covmax,err)
                pred=load_bundle(r,j,'predictions'); query=package(r,'oracle-pre-Y','verify')
                qa=bins(query['pre_'+FEATURES[j]],j); y=tensor(query.label_id.map({l:i for i,l in enumerate(LABELS)}),torch.long)
                expected={'D0':b['common_true'][qa],'DG':b['common_group'][qa],'DB':b['pooled_post'].expand(len(query),-1)}
                for v in KAPPAS:
                    expected['D1-'+v]=b['true_'+v][y,qa]; expected['D2-'+v]=b['group_'+v][y,qa]; expected['D3-'+v]=b['post_'+v][y]
                for arm,p in expected.items(): require(torch.equal(p,pred[arm]),'Probability replay')
                require(torch.equal(pred['D1-inf'],pred['D0']) and torch.equal(pred['D2-inf'],pred['DG']) and torch.equal(pred['D3-inf'],pred['DB']),'Prediction infinity identity')
        if r['inner'] is None:
            sub=q[(q.outer==r['outer'])&(q.protocol==r['protocol'])]; sel=sub[sub.selected]
            require(len(sel)<=6 and (sel.reliable&sel.incremental).all(),'Selection rule')
            require(sel.groupby('family').size().max()<=2 if len(sel) else True,'Family cap')
            require(sel.groupby('y').size().max()<=2 if len(sel) else True,'Business cap')
            require(sel.j.is_unique,'Feature cap')
            for row in sub.itertuples():
                es=d[(d.outer==row.outer)&(d.protocol==row.protocol)&(d.y==row.y)&(d.j==row.j)].error_T1
                rawlo,rawhi,lo,hi,nonempty=interval(row.target,es.to_numpy())
                require(max(abs(rawlo-row.raw_lower),abs(rawhi-row.raw_upper),abs(lo-row.lower),abs(hi-row.upper))<1e-12 and nonempty==row.interval_nonempty,'Interval replay')
    oracle=read(OUT/'manifests/Q15-Q16-ledger.json')['reads']
    require(not any('score-post' in z['path'] or 'moment-score' in z['path'] for z in oracle),'Prediction read actual post')
    fitreads=read(OUT/'manifests/Q09-Q10-ledger.json')['reads']+read(OUT/'manifests/Q12-ledger.json')['reads']
    require(not any('score' in z['path'].split('/')[-1] or 'oracle' in z['path'] for z in fitreads),'Fitting read query')
    for ledger in ['Q13','Q14']:
        require(not any('/packages/outer/' in z['path'] and ('score' in z['path'] or 'oracle' in z['path']) for z in read(OUT/'manifests'/f'{ledger}-ledger.json')['reads']),'Qualification/activity read outer outcome')
    write(OUT/'verification.json',{'pass':True,'cuda_float64':True,'roles':100,'bundles':1000,
        'true_counts_replay_max':maxreplay,'covariance_add_max':covmax,'old_sources_artifacts_unchanged':True,
        'registered_entity_crossfold_overlap':0,'universal_TCP_epoch_proof':False,'new_business_classifier_fits':0,
        'all_probability_arrays_exact_replay':True,'qualification_before_outer_scores':True,
        'read_whitelist_not_OS_sandbox':True,'permission_checks':True})
    finish('Q20',verified=True)

if __name__=='__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('stage',choices=['prepare','inner','inner-score','outer','qualify','activity','predict','score','bootstrap','verify'])
    args=parser.parse_args()
    {'prepare':prepare,'inner':lambda:fit(True),'inner-score':inner_score,'outer':lambda:fit(False),
     'qualify':qualify,'activity':activity,'predict':predict,'score':score,'bootstrap':bootstrap,'verify':verify}[args.stage]()
