"""Source-only finite selection, then global H scoring and shared content CIs."""
from common import *
from workflow import LABELS,ARMS,package,barrier,saveframe,seal,recipes

PC=[f'p{i}' for i in range(6)];LC=[f'l{i}' for i in range(6)]

def truths(d):
    require(set(d.label_id)<=set(LABELS),'Unknown business label')
    return d.label_id.map({s:i for i,s in enumerate(LABELS)}).to_numpy(int)

def metric(d,g):
    y=truths(d);pred=d.prediction.to_numpy(int);cm=np.bincount(y*6+pred,minlength=36).reshape(6,6)
    den=cm.sum(0)+cm.sum(1);f=np.divide(2*np.diag(cm),den,out=np.zeros(6),where=den>0)
    mask=np.isin(y,MASKS[g]);p=d[PC].to_numpy();lp=d[LC].to_numpy();ce=-lp[np.arange(len(y)),y];br=((p-np.eye(6)[y])**2).sum(1)
    return dict(F1_all=float(f.mean()),F1_U=float(f[MASKS[g]].mean()),F1_C=float(np.delete(f,MASKS[g]).mean()),
        CE=float(ce.mean()),CE_U=float(ce[mask].mean()),CE_C=float(ce[~mask].mean()),
        Brier=float(br.mean()),Brier_U=float(br[mask].mean()),Brier_C=float(br[~mask].mean())),cm,f

def labeled(outer):
    barrier('H-predictions-complete.json' if outer else 'inner-predictions-complete.json');ls=[]
    for r in contract()['roles' if outer else 'inner_roles']:
        d=package(r,'labels',outer);d['role_id']=r['id'];ls.append(d.drop(columns='protocol'))
    pred=pd.read_parquet(OUT/('H-predictions' if outer else 'inner-predictions')/'visits.parquet')
    data=pred.merge(pd.concat(ls,ignore_index=True),on=['role_id','visit_id'],validate='many_to_one')
    require(len(data)==len(pred),'Labels/predictions join loss');return data

def select():
    marker=OUT/'manifests/selections-complete.json'
    if marker.exists():return barrier('selections-complete.json')
    data=labeled(False);lookup={(r['outer'],r['target'],r['group']):r['id'] for r in contract()['roles']}
    data['outer_role']=[lookup[(f,p,g)] for f,p,g in zip(data.outer,data.target,data.group)];rows=[]
    for (rid,arm,cid,pseudo),d in data[~data.arm.eq('B0')].groupby(['outer_role','arm','recipe','query_deployment']):
        require(len(d)==96 and d.role_id.nunique()==4,'All four inner folds required')
        m,_,_=metric(d,d.group.iloc[0]);rows.append(dict(role_id=rid,arm=arm,recipe=cid,query_deployment=pseudo,**m))
    per=pd.DataFrame(rows);require(len(per)==60*4*6*3,'Source comparison coverage')
    cols=[c for c in per if c not in ['role_id','arm','recipe','query_deployment']]
    scores=per.groupby(['role_id','arm','recipe'])[cols].mean().reset_index();selected={};details=[]
    for (rid,arm),d in scores.groupby(['role_id','arm']):
        require(len(d)==6,'Same six-choice budget required')
        keep=d[d.F1_U>=d.F1_U.max()-1e-6];keep=keep[keep.CE_U<=keep.CE_U.min()+1e-6]
        rr={c['id']:c for c in recipes(arm)}
        cid=min(keep.recipe,key=lambda c:(rr[c]['lam'],-rr[c]['gamma'],rr[c]['lr'],c))
        selected.setdefault(rid,{})[arm]=cid
        details.append(dict(role_id=rid,arm=arm,**rr[cid],**d.set_index('recipe').loc[cid,cols].to_dict()))
    require(len(selected)==60 and all(len(v)==4 for v in selected.values()),'Selection completeness')
    paths=[]
    for name,frame in [('per-pseudo-deployment',per),('candidate-scores',scores),('chosen',pd.DataFrame(details))]:
        p=OUT/'selections'/(name+'.parquet');saveframe(p,frame);paths.append(p)
    p=OUT/'selections/selected.json';immutable(p,selected);paths.append(p)
    seal(marker,paths,passed=True,source_roles=720,outer_role_choices=240,no_C_eligibility_gate=True,no_H_reads=True)
    progress('source_selection_sealed',choices=240)

def bootstrap(data):
    contents=sorted(data.content_id.unique());ix={u:i for i,u in enumerate(contents)};groups=list(MASKS)
    cm=np.zeros((8,4,3,3,30,6,6),np.int32)
    for (a,p,g,s,u),d in data.groupby(['arm','target','group','seed','content_id']):
        y=truths(d);pred=d.prediction.to_numpy(int)
        cm[ARMS.index(a),PROTOCOLS.index(p),groups.index(g),SEEDS.index(s),ix[u]]=np.bincount(y*6+pred,minlength=36).reshape(6,6)
    labs=data[['content_id','label_id']].drop_duplicates().set_index('content_id').loc[contents].label_id.to_numpy()
    require(len(labs)==30,'Thirty global content clusters');rng=np.random.default_rng(20261016);weights=np.zeros((10000,30),np.int32)
    for label in LABELS:
        ids=np.where(labs==label)[0];require(len(ids)==5,'Five contents per business')
        picks=rng.choice(ids,size=(10000,5),replace=True)
        for i in range(10000):weights[i]+=np.bincount(picks[i],minlength=30)
    def f1(c,xp):
        den=c.sum(-1)+c.sum(-2)
        if xp=='torch':f=2*torch.diagonal(c,dim1=-2,dim2=-1)/den.clamp_min(1)
        else:f=np.divide(2*np.diagonal(c,axis1=-2,axis2=-1),den,out=np.zeros_like(den,dtype=float),where=den>0)
        picked=[f[:,:,:,j,:,:][...,MASKS[g]].mean(-1) for j,g in enumerate(groups)]
        return torch.stack(picked,-1).mean((2,3,4)) if xp=='torch' else np.stack(picked,-1).mean((2,3,4))
    values=np.empty((10000,8));tc=tensor(cm)
    for left in range(0,10000,100):
        c=torch.einsum('bc,apgscyz->bapgsyz',tensor(weights[left:left+100]),tc)
        values[left:left+100]=cpu(f1(c,'torch'))
    independent=f1(np.einsum('bc,apgscyz->bapgsyz',weights[:32],cm,optimize=True),'numpy')
    error=float(np.max(np.abs(independent-values[:32])))
    require(error<1e-12,'Independent bootstrap replay differs')
    return contents,weights,values,error

def score():
    marker=OUT/'manifests/scores-complete.json'
    if marker.exists():return barrier('scores-complete.json')
    data=labeled(True);require(len(data)==34560 and data.visit_id.nunique()==480,'Full H coverage')
    scenes=[];classes=[]
    for (a,p,g,s),d in data.groupby(['arm','target','group','seed']):
        require(len(d)==120 and d.content_id.nunique()==30,'Five-fold OOF coverage')
        m,cm,f=metric(d,g);scenes.append(dict(arm=a,target=p,group=g,seed=s,**m))
        for y in range(6):classes.append(dict(arm=a,target=p,group=g,seed=s,label=LABELS[y],F1=float(f[y]),matrix_row=cm[y].tolist()))
    scenes=pd.DataFrame(scenes);cols=[c for c in scenes if c not in ['arm','target','group','seed']]
    bytarget=scenes.groupby(['arm','target'])[cols].mean().reset_index();pooled=scenes.groupby('arm')[cols].mean().reset_index()
    pooled=pooled.merge(bytarget.groupby('arm').F1_U.min().rename('worst_deployment_F1_U'),on='arm')
    byseed=scenes.groupby(['arm','seed'])[cols].mean().reset_index();detail=data.copy();y=truths(detail)
    detail['CE']=-detail[LC].to_numpy()[np.arange(len(detail)),y]
    detail['Brier']=((detail[PC].to_numpy()-np.eye(6)[y])**2).sum(1)
    detail['accuracy']=(detail.prediction.to_numpy()==y).astype(float)
    detail['confidence']=detail[PC].to_numpy().max(1);detail['true_probability']=detail[PC].to_numpy()[np.arange(len(detail)),y]
    detail['scope']=['U' if yy in MASKS[g] else 'C' for yy,g in zip(y,detail.group)]
    content=detail.groupby(['arm','target','content_id','label_id'])[['CE','Brier','accuracy','confidence']].mean().reset_index()
    # Independent sklearn replay of the complete confusion-matrix metric.
    from sklearn.metrics import f1_score
    err=0.
    for (_,_,g,_),d in data.groupby(['arm','target','group','seed']):
        f=f1_score(truths(d),d.prediction,labels=list(range(6)),average=None,zero_division=0)
        m,_,_=metric(d,g);err=max(err,abs(m['F1_U']-f[MASKS[g]].mean()))
    require(err<1e-12,'Independent F1 replay differs')
    paths=[]
    for name,d in [('labeled-predictions',detail),('scenarios',scenes),('targets',bytarget),('pooled',pooled),
                   ('classes',pd.DataFrame(classes)),('seed-means',byseed),('contents',content)]:
        p=OUT/'scores'/(name+'.parquet');saveframe(p,d);paths.append(p)
    contents,w,v,booterr=bootstrap(data);point=pooled.set_index('arm');contrasts=[]
    for ref in ['B0','JC','JG','FR']:
        diff=v[:,ARMS.index('JP')]-v[:,ARMS.index(ref)];lo,hi=np.quantile(diff,[.00625,.99375]);l95,h95=np.quantile(diff,[.025,.975])
        contrasts.append(dict(candidate='JP',reference=ref,delta_F1_U=float(point.loc['JP','F1_U']-point.loc[ref,'F1_U']),
              CI_98_75=[float(lo),float(hi)],CI_95=[float(l95),float(h95)],positive_increment=bool(lo>0)))
    p=OUT/'comparisons/primary.json';immutable(p,dict(family=4,bootstrap=10000,seed=20261016,comparisons=contrasts,
        conditional_on_fixed_models=True,external_validation=False));paths.append(p)
    p=writable(OUT/'comparisons/bootstrap.npz');require(not p.exists(),'Bootstrap already exists')
    np.savez_compressed(p,contents=np.array(contents),arms=np.array(ARMS),weights=w,F1_U=v);paths.append(p)
    guards=[]
    for proto,d in bytarget.groupby('target'):
        t=d.set_index('arm');delta=float(t.loc['JP','F1_C']-t.loc['B0','F1_C']);guards.append(dict(target=proto,delta=delta,passed=delta>=-.02))
    delta=float(point.loc['JP','F1_C']-point.loc['B0','F1_C']);p=OUT/'comparisons/C-cost-guard.json'
    immutable(p,dict(overall_delta=delta,overall_passed=delta>=-.01,targets=guards,passed=delta>=-.01 and all(g['passed'] for g in guards),does_not_trigger_fallback=True));paths.append(p)
    flips=[]
    for ref in ['B0','JC','JG','FR']:
        a=detail[detail.arm.eq('JP')];b=detail[detail.arm.eq(ref)][['role_id','visit_id','seed','prediction','confidence','CE','Brier']].rename(columns={c:'ref_'+c for c in ['prediction','confidence','CE','Brier']})
        z=a.merge(b,on=['role_id','visit_id','seed'],validate='one_to_one');y=truths(z)
        z['repaired']=(z.prediction.to_numpy()==y)&(z.ref_prediction.to_numpy()!=y)
        z['introduced']=(z.prediction.to_numpy()!=y)&(z.ref_prediction.to_numpy()==y)
        z['shared_wrong']=(z.prediction.to_numpy()!=y)&(z.ref_prediction.to_numpy()!=y)
        z['changed']=z.prediction.ne(z.ref_prediction);z['reference']=ref;flips.append(z)
    p=OUT/'scores/error-flips.parquet';saveframe(p,pd.concat(flips,ignore_index=True));paths.append(p)
    interaction=float(point.loc['JP','F1_U']-point.loc['MX01','F1_U']-point.loc['MX10','F1_U']+point.loc['MX00','F1_U'])
    p=OUT/'audits/score-replay.json';immutable(p,dict(independent_F1_error=err,independent_bootstrap_error=booterr,
        matrix_interaction_F1_U_descriptive=interaction,not_causal=True));paths.append(p)
    seal(marker,paths,passed=True,rows=len(data),contents=30,visits=480)
    progress('H_scored',primary=contrasts)
