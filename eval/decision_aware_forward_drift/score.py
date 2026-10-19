"""Source-only six-class evaluation and content-cluster uncertainty."""
from common import *

def metrics(y,lp,missing):
    z=lp.argmax(1);p=np.exp(lp);cm=np.bincount(y*6+z,minlength=36).reshape(6,6)
    den=cm.sum(0)+cm.sum(1);f=np.divide(2*np.diag(cm),den,out=np.zeros(6),where=den>0);u=np.isin(y,missing)
    ce=-lp[np.arange(len(y)),y];br=((p-np.eye(6)[y])**2).sum(1)
    return dict(F1_U=float(f[missing].mean()),F1_C=float(np.delete(f,missing).mean()),F1_all=float(f.mean()),
        CE_U=float(ce[u].mean()),CE_C=float(ce[~u].mean()),CE_all=float(ce.mean()),Brier_U=float(br[u].mean()),Brier_C=float(br[~u].mean()),Brier_all=float(br.mean())),cm,f

def bootstrap(data):
    contents=sorted(data.content_id.unique());labels=data[['content_id','y']].drop_duplicates().set_index('content_id').loc[contents].y.to_numpy(int)
    require(len(contents)==24,'24 independent contents');idx={u:i for i,u in enumerate(contents)}
    cells=sorted({(r['target'],r['group']) for r in roles()});cm=np.zeros((5,12,24,6,6),np.int32)
    for (a,role,g,u),d in data.groupby(['pipeline','role_target','group','content_id']):
        require(len(d)==4,'Pooled content repeat grid');cm[PIPES.index(a),cells.index((role,g)),idx[u]]=np.bincount(d.y.to_numpy()*6+d.prediction.to_numpy(),minlength=36).reshape(6,6)
    rng=np.random.default_rng(20261017);weights=np.zeros((10000,24),np.int32)
    for k in range(6):
        ids=np.flatnonzero(labels==k);require(len(ids)==4,'Four per stratum');picks=rng.integers(0,4,size=(10000,4))
        for j in range(4):weights[:,ids[j]]=(picks==j).sum(1)
    # Use CUDA FP64 for bootstrap matrix products, CPU independent verification.
    tensorcm=tensor(cm);classu=tensor([[k in MASKS[g] for k in range(6)] for _,g in cells]);draws=[]
    for start in range(0,10000,200):
        w=tensor(weights[start:start+200]);c=(w@tensorcm.permute(2,0,1,3,4).reshape(24,-1)).reshape(len(w),5,12,6,6)
        den=c.sum(-1)+c.sum(-2);f=2*c.diagonal(dim1=-2,dim2=-1)/den.clamp_min(1)
        draws.append(cpu(((f*classu).sum(-1)/2).mean(-1)))
    draws=np.concatenate(draws);check=[]
    for start in range(0,10000,200):
        c=np.einsum('bc,amcij->bamij',weights[start:start+200],cm,optimize=True);den=c.sum(-1)+c.sum(-2)
        f=np.divide(2*np.diagonal(c,axis1=-2,axis2=-1),den,out=np.zeros_like(den,dtype=float),where=den>0)
        check.append(((f*cpu(classu)).sum(-1)/2).mean(-1))
    check=np.concatenate(check);err=float(np.max(abs(check-draws)));require(err<=1e-12,'Independent bootstrap replay')
    np.savez_compressed(writable(OUT/'scores/bootstrap.npz'),contents=np.array(contents),weights=weights,pipelines=np.array(PIPES),F1_U=draws)
    return draws,err

def run():
    configure('score');barrier('predictions-complete.json');barrier('diagnostics-complete.json');pred=pd.read_parquet(OUT/'predictions/post-only.parquet');meta=[]
    for r in roles():
        labels=external(PREP/'packages'/r['id']/'labels.parquet',r['id'],'labels');require(len(labels)==24 and set(labels.protocol)=={r['calibration']},'Label routing')
        require(set(labels.content_id)==set(r['validation_contents']),'Label content');labels['role_id']=r['id'];labels['y']=yvalues(labels);meta.append(labels)
    data=pred.merge(pd.concat(meta),on=['role_id','visit_id'],validate='many_to_one');require(len(data)==5760 and data.visit_id.nunique()==384 and data.content_id.nunique()==24,'Source prediction independence')
    require(data.query_deployment.eq(data.protocol).all(),'Actual query deployment label routing')
    lc=[f'l{k}' for k in range(6)];lp=data[lc].to_numpy();y=data.y.to_numpy();p=np.exp(lp)
    data['CE']=-lp[np.arange(len(data)),y];data['Brier']=((p-np.eye(6)[y])**2).sum(1);data['correct']=data.prediction.eq(data.y);data['confidence']=p.max(1)
    data['scope']=['U' if yy in MASKS[g] else 'C' for yy,g in zip(y,data.group)]
    scenes=[];classes=[];matrices=[]
    for (a,role,dep,g),d in data.groupby(['pipeline','role_target','query_deployment','group']):
        require(len(d)==96 and d.inner.nunique()==4,'Pool four inner folds')
        m,cm,f=metrics(d.y.to_numpy(),d[lc].to_numpy(),MASKS[g]);scenes.append(dict(pipeline=a,role_target=role,query_deployment=dep,group=g,**m))
        for k in range(6):classes.append(dict(pipeline=a,role_target=role,query_deployment=dep,group=g,business=LABELS[k],F1=float(f[k]),scope='U' if k in MASKS[g] else 'C'))
        matrices.append(dict(pipeline=a,role_target=role,query_deployment=dep,group=g,cm=cm.tolist()))
    scene=pd.DataFrame(scenes);cols=[k for k in scene if k not in ['pipeline','role_target','query_deployment','group']]
    pooled=scene.groupby('pipeline')[cols].mean().reset_index();deploy=scene.groupby(['pipeline','query_deployment'])[cols].mean().reset_index()
    draws,berr=bootstrap(data);point=pooled.set_index('pipeline');comps=[]
    for ref in ['B0','DA-G','Full-P']:
        delta=draws[:,PIPES.index('DA-P')]-draws[:,PIPES.index(ref)]
        comps.append(dict(reference=ref,delta_F1_U=float(point.loc['DA-P','F1_U']-point.loc[ref,'F1_U']),CI95=np.quantile(delta,[.025,.975]).tolist(),
            family_CI=np.quantile(delta,[.05/6,1-.05/6]).tolist(),positive_family_increment=bool(np.quantile(delta,.05/6)>0),
            delta_CE_U=float(point.loc['DA-P','CE_U']-point.loc[ref,'CE_U']),delta_Brier_U=float(point.loc['DA-P','Brier_U']-point.loc[ref,'Brier_U'])))
    cdelta=float(point.loc['DA-P','F1_C']-point.loc['B0','F1_C']);depc=[]
    for proto,d in deploy.groupby('query_deployment'):
        d=d.set_index('pipeline');v=float(d.loc['DA-P','F1_C']-d.loc['B0','F1_C']);depc.append(dict(query_deployment=proto,delta_F1_C=v,passed=v>=-.02))
    passed=(all(x['delta_F1_U']>0 for x in comps[:2]) and all(x['delta_CE_U']<=0 for x in comps[:2]) and cdelta>=-.01 and all(x['passed'] for x in depc))
    primary=dict(comparisons=comps,family=3,confidence=1-.05/3,bootstrap=10000,seed=20261017,conditioned_on_fixed_models=True)
    immutable(OUT/'scores/primary.json',primary)
    immutable(OUT/'scores/progression-screen.json',dict(passed=passed,overall_C_delta=cdelta,overall_C_pass=cdelta>=-.01,deployments=depc,
        rule='positive U F1 vs B0 and G, nonworse U CE vs both, C guards',not_confirmatory_success=True,actual_H_not_read=True,full_run_automatically_authorized=False))
    flips=[];main=data[data.pipeline=='DA-P']
    for ref in ['B0','DA-G','Full-P','B0-R']:
        other=data[data.pipeline==ref][['role_id','visit_id','correct','CE','Brier','prediction','confidence']]
        z=main.merge(other,on=['role_id','visit_id'],suffixes=('','_reference'),validate='one_to_one')
        z['flip']=np.select([z.correct&~z.correct_reference,~z.correct&z.correct_reference,z.correct&z.correct_reference],['repaired','introduced','both_correct'],default='both_wrong')
        z['reference']=ref;z['delta_CE']=z.CE-z.CE_reference;z['delta_Brier']=z.Brier-z.Brier_reference;flips.append(z)
    for name,d in [('labeled-predictions',data),('scenarios',scene),('pooled',pooled),('deployments',deploy),('classes',pd.DataFrame(classes)),('error-flips',pd.concat(flips,ignore_index=True))]:save(OUT/'scores'/(name+'.parquet'),d)
    immutable(OUT/'scores/confusions.json',matrices)
    # Source-query reconstruction diagnostics acquire class information only now.
    gen=pd.read_parquet(OUT/'diagnostics/generation-errors.parquet').merge(pd.concat(meta)[['role_id','visit_id','content_id','y']],on=['role_id','visit_id'],validate='many_to_one')
    save(OUT/'scores/generation-errors-labeled.parquet',gen)
    covrows=[]
    for r in roles():
        d=own(OUT/'diagnostics'/r['id']/'outputs.pt',r['id']);labels=pd.concat(meta);labels=labels[labels.role_id.eq(r['id'])].set_index('visit_id').loc[d['visit_ids']];yt=labels.y.to_numpy(int)
        for arm,z in d['outputs'].items():
            for yy in range(6):
                ix=tensor(np.flatnonzero(yt==yy),torch.long);a=z[ix]@d['Q'];b=d['true_post'][ix]@d['Q'];ac=a-a.mean(0);bc=b-b.mean(0);k=d['Q'].shape[1]
                covrows.append(dict(role_id=r['id'],pipeline=arm,y=yy,scope='U' if yy in r['missing'] else 'C',mean_error=float((a.mean(0)-b.mean(0)).square().mean()),
                    covariance_error=float(((ac.T@ac)/4-(bc.T@bc)/4).square().sum()/k**2)))
    save(OUT/'scores/generation-conditional-moments.parquet',covrows)
    # Independent metrics without original metrics() helper.
    maxerr=0.
    for row in scene.to_dict('records'):
        d=data[(data.pipeline==row['pipeline'])&(data.role_target==row['role_target'])&(data.group==row['group'])];fs=[]
        for k in range(6):
            tp=((d.y==k)&(d.prediction==k)).sum();den=(d.y==k).sum()+(d.prediction==k).sum();fs.append(2*tp/den if den else 0)
        maxerr=max(maxerr,abs(float(np.array(fs)[MASKS[row['group']]].mean())-row['F1_U']))
    require(maxerr<=1e-12,'Independent CM metrics');flush('score')
    immutable(OUT/'tests/final-verification.json',dict(passed=True,bootstrap_max_error=berr,metric_max_error=maxerr,actual_H_U_reads=0,source_query_pre_after_predictions=True,
        full_experiment=False,unique_visits=384,unique_contents=24,physical_LR=192,generator_paths=144))
    seal(OUT/'manifests/scores-complete.json',list((OUT/'scores').glob('*'))+[OUT/'tests/final-verification.json'],scored=True)
    progress('source_scored',progression_screen=passed,comparisons=comps)

if __name__=='__main__':
    try:run()
    except BaseException as e:failure('score',e);raise
