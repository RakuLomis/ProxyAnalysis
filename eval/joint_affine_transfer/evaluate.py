"""Fixed-model content bootstrap; never retrains or selects candidates."""
from common import *

def reference_replay():
    c=start('reference_replay');sealed_predictions()
    oldchoices={(v['outer'],v['target'],v['group'],v['arm']):v for v in read(V4/'selection/choices.json')}
    extras={(v['outer'],v['protocol']):v for v in read(V4/'manifests/reused-post-models.json')}
    expected=pd.read_parquet(V4/'predictions/visits.parquet');pc=[f'p{i}' for i in range(6)]
    require(sha(V4/'predictions/visits.parquet')==c['baseline_sha256'][rel(V4/'predictions/visits.parquet')],'Frozen prediction changed')
    error=0.;models=0
    for r in c['roles']:
        if r['inner'] is not None:continue
        q=package(rolepath(r)/'query.parquet','query')
        for arm in ['CT0','CT1','CT2','CT3','CT4','StrongPost','CT5']:
            if arm=='CT5':v=extras[(r['outer'],r['target'])];path=ROOT/v['path']
            else:
                v=oldchoices[(r['outer'],r['target'],r['group'],arm)]
                actual=v['selected_arm'] if arm=='StrongPost' else arm
                path=V4/'models'/r['id']/f'{actual}-t{v["t"]:g}.pt'
            info=read(path.with_suffix('.json'));require(sha(path)==info['sha256'],'Reference model changed')
            m=torch.load(path,map_location=device(),weights_only=True);z=predict(m,q).set_index('visit_id')
            target=expected[expected.outer.eq(r['outer'])&expected.target.eq(r['target'])&expected.group.eq(r['group'])&expected.arm.eq(arm)].set_index('visit_id')
            diff=float(np.max(np.abs(z.loc[target.index,pc].to_numpy()-target[pc].to_numpy())))
            require(diff<1e-12,'Reference probability replay differs');error=max(error,diff);models+=1
    save(expected,OUT/'predictions/reference-visits.parquet')
    write(OUT/'manifests/reference-replay.json',{'passed':True,'models_replayed':models,'probability_max_error':error,
        'source_predictions_sha256':sha(V4/'predictions/visits.parquet'),'new_fits':0})
    finish('reference_replay',models=420,maximum_error=error)

def labeled():
    c=contract();sealed_predictions();rows=[]
    for r in c['roles']:
        if r['inner'] is not None:continue
        d=package(rolepath(r)/'labels.parquet','score').drop(columns='protocol')
        for k in ['outer','target','group']:d[k]=r[k]
        rows.append(d)
    pred=pd.concat([pd.read_parquet(OUT/'predictions/visits.parquet'),
                    pd.read_parquet(OUT/'predictions/reference-visits.parquet')],ignore_index=True)
    require(len(pred)==14400,'New and reference row budget')
    return pred.merge(pd.concat(rows),on=['outer','target','group','visit_id'],validate='many_to_one')

def run():
    c=start('score');d=labeled();pc=[f'p{i}' for i in range(6)];tables=[];classes=[];matrices=[]
    for (arm,target,group),part in d.groupby(['arm','target','group']):
        require(len(part)==120 and part.visit_id.is_unique and part.content_id.nunique()==30,'Outer OOF coverage')
        m,cm,f=metrics(truths(part),part[pc].to_numpy(),MASKS[group]);tables.append({'arm':arm,'target':target,'group':group,**m})
        matrices.append({'arm':arm,'target':target,'group':group,'matrix':cm.tolist()})
        for y in range(6):classes.append({'arm':arm,'target':target,'group':group,'label':LABELS[y],'label_index':y,
            'F1':float(f[y]),'uncovered':y in MASKS[group],'support':int(cm[y].sum()),
            'true_positive':int(cm[y,y]),'false_positive':int(cm[:,y].sum()-cm[y,y]),'false_negative':int(cm[y].sum()-cm[y,y])})
    scene=pd.DataFrame(tables);valuecols=['F1_all','F1_uncovered','F1_aux','accuracy','CE_nats','CE_bits','Brier']
    pooled=scene.groupby('arm')[valuecols].mean().reset_index()
    targets=scene.groupby(['arm','target'])[valuecols].mean().reset_index()
    pooled=pooled.merge(targets.groupby('arm').F1_uncovered.min().rename('worst_target_uncovered'),on='arm')
    save(scene,OUT/'scores/scenarios.parquet');save(targets,OUT/'scores/targets.parquet')
    save(pooled,OUT/'scores/pooled.parquet');save(pd.DataFrame(classes),OUT/'scores/classes.parquet')
    outerrows=[]
    for (arm,target,group,outer),part in d.groupby(['arm','target','group','outer']):
        require(len(part)==24 and part.content_id.nunique()==6,'Per-fold outer coverage')
        m,_,_=metrics(truths(part),part[pc].to_numpy(),MASKS[group])
        outerrows.append({'arm':arm,'target':target,'group':group,'outer':int(outer),**m})
    save(pd.DataFrame(outerrows),OUT/'scores/outer-folds.parquet')
    write(OUT/'scores/confusion-matrices.json',matrices);save(d,OUT/'scores/labeled-predictions.parquet')
    require(abs(float(pooled.set_index('arm').loc['StrongPost','F1_uncovered'])-.772708)<1e-6,'Historical metric reproduction')
    # Fixed content-wise array, shared across protocols, visits, masks and methods.
    arms=sorted(d.arm.unique());contents=sorted(d.content_id.unique());aix={a:i for i,a in enumerate(arms)};uix={u:i for i,u in enumerate(contents)}
    groups=list(MASKS);cm=np.zeros((len(arms),4,3,30,6,6),dtype=np.int32)
    for (a,p,g,u),part in d.groupby(['arm','target','group','content_id']):
        y=truths(part);z=part[pc].to_numpy().argmax(1)
        cm[aix[a],PROTOCOLS.index(p),groups.index(g),uix[u]]=np.bincount(y*6+z,minlength=36).reshape(6,6)
    content_labels=d[['content_id','label_id']].drop_duplicates().set_index('content_id').loc[contents].label_id
    require(len(content_labels)==30,'Global content label count')
    rng=np.random.default_rng(20261007);weights=np.zeros((10000,30),dtype=np.int32)
    for label in LABELS:
        ids=np.where(content_labels.to_numpy()==label)[0];require(len(ids)==5,'Five contents per class')
        picks=rng.choice(ids,size=(10000,5),replace=True)
        for b in range(10000):weights[b]+=np.bincount(picks[b],minlength=30)
    uncovered=np.empty((10000,len(arms)));auxiliary=np.empty_like(uncovered)
    for left in range(0,10000,250):
        cc=np.einsum('bc,apgcyz->bapgyz',weights[left:left+250],cm,optimize=True)
        den=cc.sum(-1)+cc.sum(-2)
        f1=np.divide(2*np.diagonal(cc,axis1=-2,axis2=-1),den,out=np.zeros_like(den,dtype=float),where=den>0)
        uu=[];aa=[]
        for gi,g in enumerate(groups):
            uu.append(np.take(f1[:,:,:,gi,:],MASKS[g],axis=-1).mean(-1))
            aa.append(np.delete(f1[:,:,:,gi,:],MASKS[g],axis=-1).mean(-1))
        uncovered[left:left+250]=np.stack(uu,-1).mean((2,3));auxiliary[left:left+250]=np.stack(aa,-1).mean((2,3))
    comparisons=[];point=pooled.set_index('arm');truthidx=aix['JA1']
    for ref in c['primary_comparators']:
        delta=uncovered[:,truthidx]-uncovered[:,aix[ref]]
        lo,hi=np.quantile(delta,[.00625,.99375]);lo95,hi95=np.quantile(delta,[.025,.975])
        comparisons.append({'candidate':'JA1','reference':ref,
            'delta_F1_uncovered':float(point.loc['JA1','F1_uncovered']-point.loc[ref,'F1_uncovered']),
            'CI_98_75':[float(lo),float(hi)],'CI_95':[float(lo95),float(hi95)],'positive_increment':bool(lo>0)})
    margins={r:float(point.loc['JA1','F1_aux']-point.loc[r,'F1_aux']) for r in ['StrongPost','CT1','JA2']}
    t=targets.set_index(['arm','target']);worst=min(float(t.loc[('JA1',p),'F1_aux']-t.loc[('StrongPost',p),'F1_aux']) for p in PROTOCOLS)
    safety=all(v>=-.02 for v in margins.values()) and worst>=-.05
    full=all(v['positive_increment'] for v in comparisons[:3]) and safety
    write(OUT/'comparisons/primary.json',{'comparisons':comparisons,'family':4,'bootstrap_samples':10000,
        'bootstrap_seed':20261007,'model_conditional_not_external_validation':True,'aux_margins':margins,
        'worst_target_aux_gap':worst,'safety_screen_passed':safety,'statistical_noninferiority':False,
        'full_business_claim_passed':full,'structure_claim_passed':comparisons[3]['positive_increment']})
    dst=writable(OUT/'comparisons/bootstrap.npz');dst.parent.mkdir(parents=True,exist_ok=True)
    np.savez_compressed(dst,arms=np.asarray(arms),content_ids=np.asarray(contents),weights=weights,uncovered=uncovered,auxiliary=auxiliary)
    # Both directions of decision changes; preserve all visits and content grouping.
    flips=[]
    for (outer,target,group),part in d.groupby(['outer','target','group']):
        a=part[part.arm.eq('JA1')].set_index('visit_id')
        for ref in ['JA0','JA2','StrongPost','CT4']:
            b=part[part.arm.eq(ref)].set_index('visit_id').loc[a.index]
            y=truths(a);good=a.prediction.to_numpy()==y;before=b.prediction.to_numpy()==y
            for j,visit in enumerate(a.index):
                flips.append({'outer':int(outer),'target':target,'group':group,'visit_id':visit,
                    'content_id':a.iloc[j].content_id,'label_id':a.iloc[j].label_id,'uncovered':int(y[j]) in MASKS[group],
                    'reference':ref,'reference_correct':bool(before[j]),'JA1_correct':bool(good[j]),
                    'fixed_error':bool(good[j] and not before[j]),'new_error':bool(before[j] and not good[j])})
    save(pd.DataFrame(flips),OUT/'scores/error-flips.parquet')
    finish('score',scenes=120,rows=len(d),full_business_claim_passed=full)

if __name__=='__main__':{'references':reference_replay,'score':run}[sys.argv[1]]()
