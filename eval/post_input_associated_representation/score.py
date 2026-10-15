"""Three-method family, shared stratified content bootstrap, seed-wise metrics."""
from common import *
ARMS=['A0','A1','A2','A3'];MASKS={'G0':[2,4],'G1':[0,3],'G2':[1,5]}
PC=[f'p{i}' for i in range(6)];LC=[f'l{i}' for i in range(6)]

def metric(d,g):
    y=truths(d);z=d.prediction.to_numpy(int);cm=np.bincount(y*6+z,minlength=36).reshape(6,6)
    den=cm.sum(0)+cm.sum(1);f=np.divide(2*np.diag(cm),den,out=np.zeros(6),where=den>0)
    use=np.isin(y,MASKS[g]);p=d[PC].to_numpy();lp=d[LC].to_numpy()
    ce=-lp[np.arange(len(y)),y];br=((p-np.eye(6)[y])**2).sum(1)
    return dict(F1_all=float(f.mean()),F1_U=float(f[MASKS[g]].mean()),F1_C=float(np.delete(f,MASKS[g]).mean()),
                CE=float(ce.mean()),CE_U=float(ce[use].mean()),CE_C=float(ce[~use].mean()),
                Brier=float(br.mean()),Brier_U=float(br[use].mean()),Brier_C=float(br[~use].mean())),cm,f

def bootstrap(data):
    contents=sorted(data.content_id.unique());ix={u:i for i,u in enumerate(contents)};groups=list(MASKS)
    cm=np.zeros((4,4,3,3,30,6,6),np.int32)
    for (arm,proto,g,seed,u),d in data.groupby(['arm','target','group','seed','content_id']):
        y=truths(d);z=d.prediction.to_numpy(int)
        cm[ARMS.index(arm),PROTOCOLS.index(proto),groups.index(g),SEEDS.index(seed),ix[u]]=np.bincount(y*6+z,minlength=36).reshape(6,6)
    labels=data[['content_id','label_id']].drop_duplicates().set_index('content_id').loc[contents].label_id.to_numpy()
    require(len(labels)==30,'Thirty content labels');rng=np.random.default_rng(20261014);mass=np.zeros((10000,30),np.int32)
    for label in LABELS:
        ids=np.where(labels==label)[0];require(len(ids)==5,'Five contents per class')
        picks=rng.choice(ids,size=(10000,5),replace=True)
        for i in range(10000):mass[i]+=np.bincount(picks[i],minlength=30)
    values=np.empty((10000,4))
    for left in range(0,10000,125):
        c=np.einsum('bc,apgscyz->bapgsyz',mass[left:left+125],cm,optimize=True)
        den=c.sum(-1)+c.sum(-2);f=np.divide(2*np.diagonal(c,axis1=-2,axis2=-1),den,out=np.zeros_like(den,dtype=float),where=den>0)
        picked=[np.take(f[:,:,:,j,:,:],MASKS[g],axis=-1).mean(-1) for j,g in enumerate(groups)]
        values[left:left+125]=np.stack(picked,-1).mean((2,3,4))
    return contents,mass,values

def run():
    with stage('P4_score'):
        verifyseal(OUT/'manifests/engineering-code.json');verifyseal(OUT/'predictions/complete.json');labels=[]
        for r in contract()['roles']:
            l=oldpackage(PREP/'packages'/r['id']/'labels.parquet',r,'H-score');l['role_id']=r['id'];labels.append(l.drop(columns='protocol'))
        data=pd.read_parquet(OUT/'predictions/visits.parquet').merge(pd.concat(labels),on=['visit_id','role_id'],validate='many_to_one')
        require(len(data)==17280,'Label coverage');scenes=[];classes=[]
        for (a,p,g,seed),part in data.groupby(['arm','target','group','seed']):
            require(len(part)==120 and part.content_id.nunique()==30,'OOF coverage')
            m,cm,f=metric(part,g);scenes.append(dict(arm=a,target=p,group=g,seed=seed,**m))
            for y in range(6):classes.append(dict(arm=a,target=p,group=g,seed=seed,label=LABELS[y],F1=float(f[y]),matrix_row=cm[y].tolist()))
        scenes=pd.DataFrame(scenes);cols=[c for c in scenes if c not in ['arm','target','group','seed']]
        targets=scenes.groupby(['arm','target'])[cols].mean().reset_index();pooled=scenes.groupby('arm')[cols].mean().reset_index()
        pooled=pooled.merge(targets.groupby('arm').F1_U.min().rename('worst_deployment_F1_U'),on='arm')
        for name,d in [('labeled-predictions',data),('scenarios',scenes),('targets',targets),('pooled',pooled),('classes',pd.DataFrame(classes))]:save(d,OUT/'scores'/(name+'.parquet'))
        contents,w,b=bootstrap(data);point=pooled.set_index('arm');contrasts=[]
        for ref in ['A0','A1','A2']:
            v=b[:,3]-b[:,ARMS.index(ref)];lo,hi=np.quantile(v,[.05/6,1-.05/6])
            contrasts.append(dict(candidate='A3',reference=ref,delta_F1_U=float(point.loc['A3','F1_U']-point.loc[ref,'F1_U']),
                                  CI_98_333333=[float(lo),float(hi)],positive_increment=bool(lo>0)))
        write(OUT/'comparisons/primary.json',dict(family=3,bootstrap=10000,seed=20261014,comparisons=contrasts))
        np.savez_compressed(writable(OUT/'comparisons/bootstrap.npz'),contents=np.array(contents),arms=np.array(ARMS),weights=w,F1_U=b)
        guards=[]
        for p,d in targets.groupby('target'):
            t=d.set_index('arm');delta=float(t.loc['A3','F1_C']-t.loc['A0','F1_C']);guards.append(dict(target=p,delta=delta,passed=delta>=-.02))
        delta=float(point.loc['A3','F1_C']-point.loc['A0','F1_C'])
        write(OUT/'comparisons/C-cost-guard.json',dict(overall_delta=delta,overall_passed=delta>=-.01,targets=guards,
                passed=delta>=-.01 and all(v['passed'] for v in guards),does_not_trigger_H_fallback=True))
        flips=[]
        for ref in ['A0','A1','A2']:
            a=data[data.arm.eq('A3')];r=data[data.arm.eq(ref)][['role_id','visit_id','seed','prediction']].rename(columns={'prediction':'ref_prediction'})
            z=a.merge(r,on=['role_id','visit_id','seed'],validate='one_to_one');y=truths(z)
            z['repaired']=(z.prediction.to_numpy()==y)&(z.ref_prediction.to_numpy()!=y)
            z['introduced']=(z.prediction.to_numpy()!=y)&(z.ref_prediction.to_numpy()==y)
            z['changed']=z.prediction.ne(z.ref_prediction);z['reference']=ref
            z['scope']=['U' if yy in MASKS[g] else 'C' for yy,g in zip(y,z.group)];flips.append(z)
        save(pd.concat(flips),OUT/'scores/error-flips.parquet')
        progress('P4_scored',primary=contrasts)

if __name__=='__main__':run()
