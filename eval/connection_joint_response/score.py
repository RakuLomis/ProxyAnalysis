"""Frozen six-class endpoints and preregistered content bootstrap, no refits."""
from common import *

def from_cm(cm):
    den=cm.sum(-1)+cm.sum(-2); diag=torch.diagonal(cm,dim1=-2,dim2=-1)
    return torch.where(den>0,2*diag/den,torch.zeros_like(den))

def f1_uncovered(cms):
    # Layout bootstrap x protocol x mask x arm x truth x prediction.
    f=from_cm(cms)
    u=torch.stack([f[:,:,g,:,MASKS[name]].mean(-1) for g,name in enumerate(['G0','G1','G2'])],2)
    return u.mean((1,2))

def run():
    with stage('score'):
        require((OUT/'stages/formal_remaining.json').exists(),'Formal prediction matrix incomplete')
        source={rel(p):sha(p) for p in [Path(__file__),ROOT/'eval/connection_joint_response/common.py']}
        write(OUT/'manifests/scoring-source.json',{'sha256':source,'sealed_before_H_label_read':True,
              'scientific_contract_changed':False,'bootstrap_samples':10000,'CI_coverage':.99})
        p=OUT/'predictions/visits.parquet'; checked(p,read(p.with_name('complete.json'))['sha256'],'sealed-classifier-predictions')
        preds=pd.read_parquet(p); labels=[]
        for r in contract()['roles']:
            q=package(rolepath(r)/'labels.parquet','score'); q['role_id']=r['id']; q['target']=r['target']; q['group']=r['group']
            labels.append(q)
        data=preds.merge(pd.concat(labels,ignore_index=True),on=['role_id','visit_id'],validate='many_to_one')
        require(len(data)==11520 and data.visit_id.nunique()==480,'Classification cohort')
        save(data,OUT/'scores/scored-visits.parquet')
        summaries=[]; classes=[]; contents=sorted(data.content_id.unique()); cells=[]
        for protocol in PROTOCOLS:
            for group in ['G0','G1','G2']:
                for arm in ARMS:
                    d=data[data.target.eq(protocol)&data.group.eq(group)&data.arm.eq(arm)]
                    require(len(d)==120 and d.content_id.nunique()==30 and d.visit_id.is_unique,'Full fold pool')
                    probs=d[[f'p{i}' for i in range(6)]].to_numpy(); y=truths(d)
                    m,cm,fi=metrics(y,probs,MASKS[group]); summaries.append({'target':protocol,'group':group,'arm':arm,**m})
                    for j in range(6):classes.append({'target':protocol,'group':group,'arm':arm,'label':LABELS[j],'F1':float(fi[j])})
                    save(pd.DataFrame(cm),OUT/'scores/confusion'/protocol/group/(arm+'.parquet'))
                    member=[]
                    for content in contents:
                        dd=d[d.content_id.eq(content)]; yy=truths(dd); zz=dd.prediction.to_numpy(int)
                        require(len(dd)==4,'Four test repetitions per content')
                        member.append(np.bincount(yy*6+zz,minlength=36).reshape(6,6))
                    cells.append(member)
        summary=pd.DataFrame(summaries); save(summary,OUT/'scores/deployment-mask-scores.parquet')
        save(pd.DataFrame(classes),OUT/'scores/business-scores.parquet')
        pooled=summary.groupby('arm',sort=False).mean(numeric_only=True).reset_index(); save(pooled,OUT/'scores/pooled.parquet')
        cube=tensor(np.asarray(cells)).reshape(4,3,8,30,6,6)
        rng=np.random.default_rng(20261010); labels_by_content=data.groupby('content_id').label_id.first(); mult=np.zeros((10000,30))
        for label in LABELS:
            ix=np.array([i for i,u in enumerate(contents) if labels_by_content[u]==label]); require(len(ix)==5,'Five independent contents per business')
            draws=rng.choice(ix,size=(10000,5),replace=True)
            for column in range(5):np.add.at(mult,(np.arange(10000),draws[:,column]),1)
        bootstrap=[]
        for begin in range(0,10000,256):
            mm=tensor(mult[begin:begin+256]); cm=torch.einsum('bc,pgacij->bpgaij',mm,cube)
            bootstrap.append(f1_uncovered(cm).cpu().numpy())
        draws=np.concatenate(bootstrap); original=f1_uncovered(cube.sum(3)[None]).cpu().numpy()[0]
        comparison=[]
        for a,b in COMPARISONS:
            ia,ib=ARMS.index(a),ARMS.index(b); d=draws[:,ia]-draws[:,ib]; lo,hi=np.quantile(d,[.005,.995])
            comparison.append({'candidate':a,'reference':b,'delta_F1_U':float(original[ia]-original[ib]),
                'CI99_low':float(lo),'CI99_high':float(hi),'positive_increment':bool(lo>0),
                'bootstrap_unit':'global independent content','conditional_on_fixed_models':True})
        write(OUT/'scores/primary.json',{'family':5,'CI_coverage':.99,'bootstrap_samples':10000,'comparisons':comparison})
        flips=[]
        for a,b in COMPARISONS+[('J-P-small','J-RawPost-small'),('J-P-small','J-Marginal-small')]:
            da=data[data.arm.eq(a)]; db=data[data.arm.eq(b)]
            z=da.merge(db,on=['role_id','visit_id'],suffixes=('_a','_b'),validate='one_to_one')
            ya=truths(z.rename(columns={'label_id_a':'label_id'})); ac=z.prediction_a.eq(ya); bc=z.prediction_b.eq(ya)
            for i,row in z.iterrows():
                flips.append({'candidate':a,'reference':b,'role_id':row.role_id,'visit_id':row.visit_id,
                    'content_id':row.content_id_a,'target':row.target_a,'repaired':bool(ac.iloc[i] and not bc.iloc[i]),
                    'added':bool(bc.iloc[i] and not ac.iloc[i]),'changed':bool(row.prediction_a!=row.prediction_b)})
        save(pd.DataFrame(flips),OUT/'scores/error-flips.parquet')
        write(OUT/'scores/complete.json',{'classifier_refits':0,'primary_family':5,'CI_coverage':.99,
             'physical_post_input_qualified':False,'scored_rows':len(data)})

if __name__=='__main__':run()
