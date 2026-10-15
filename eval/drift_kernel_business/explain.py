"""Frozen, descriptive interpretation; never feeds diagnostics back into fitting."""
import itertools
from common import *

def run():
    c=start('explain')
    distances,fitgap,tables,contributions=[],[],[],[]
    for role in c['roles']:
        fold,p=role['fold'],role['protocol']
        folder=modelfolder(fold,p)
        bundle=model_load(folder/'distributions.pt','explain')
        query=load_package(rolefolder(fold,p)/'query-post-hist.parquet','explain')
        h=tensor(query[HIST])
        logits=composite(h,bundle['G4'])
        winners=torch.argsort(logits,dim=1,descending=True,stable=True)[:,:2].cpu().numpy()
        at=0
        for j,f in enumerate(FEATURES):
            k=size(f)
            for arm in ['G0','G3','G4','G5']:
                q=bundle[arm][f].cpu().numpy()
                for a,b in itertools.combinations(range(6),2):
                    distances.append({'fold':fold,'protocol':p,'arm':arm,'feature':f,'class_a':a,'class_b':b,'JS_nats':js(q[a],q[b]),'training_only':True})
                for y in range(6):
                    for b in range(k):
                        tables.append({'fold':fold,'protocol':p,'arm':arm,'feature':f,'label':LABELS[y],'bin':b,'probability':float(q[y,b])})
            for y in range(6):
                fitgap.append({'fold':fold,'protocol':p,'feature':f,'label':LABELS[y],
                 'JS_true_vs_direct':js(bundle['G4'][f][y].cpu().numpy(),bundle['G0'][f][y].cpu().numpy()),
                 'JS_group_vs_direct':js(bundle['G5'][f][y].cpu().numpy(),bundle['G0'][f][y].cpu().numpy()),'training_only':True})
            q=bundle['G4'][f]
            for i,visit in enumerate(query.visit_id):
                a,b=winners[i]
                values=WEIGHTS[j]*h[i,at:at+k]*(q[a].log()-q[b].log())
                for bin_id,value in enumerate(values.cpu().numpy()):
                    contributions.append({'visit_id':visit,'protocol':p,'fold':fold,'feature':f,'bin':bin_id,
                      'class_first':int(a),'class_second':int(b),'value':float(value)})
            at+=k
        sums=pd.DataFrame(contributions)[lambda z:z.protocol.eq(p)&z.fold.eq(fold)].groupby('visit_id').value.sum()
        expected=(logits[torch.arange(len(h),device=cuda()),tensor(winners[:,0],torch.int64)]-
                  logits[torch.arange(len(h),device=cuda()),tensor(winners[:,1],torch.int64)]).cpu().numpy()
        require(np.allclose(sums.loc[query.visit_id],expected,atol=1e-12),'Contribution does not reproduce margin')
    saveparquet(pd.DataFrame(distances),OUT/'explanations/training-class-distances.parquet')
    saveparquet(pd.DataFrame(fitgap),OUT/'explanations/training-fit-gaps.parquet')
    saveparquet(pd.DataFrame(tables),OUT/'explanations/business-probabilities.parquet')
    saveparquet(pd.DataFrame(contributions),OUT/'explanations/visit-bin-contributions.parquet')
    data=pd.read_parquet(OUT/'scores/scored-visits.parquet')
    true=data[data.arm.eq('G4')].set_index('visit_id')
    flips=[]
    for comp in ['G3','G5','G0','G1','G2']:
        for seed,g in data[data.arm.eq(comp)].groupby('seed'):
            for row in g.itertuples():
                t=true.loc[row.visit_id]
                good_t=int(t.prediction==t.truth)
                good_c=int(row.prediction==row.truth)
                flips.append({'visit_id':row.visit_id,'protocol':row.protocol,'content_id':row.content_id,
                 'label_id':row.label_id,'repetition':row.repetition,'comparator':comp,'seed':int(seed),
                 'true_prediction':int(t.prediction),'other_prediction':int(row.prediction),'truth':int(row.truth),
                 'repaired':good_t==1 and good_c==0,'new_error':good_t==0 and good_c==1,
                 'decision_changed':int(t.prediction)!=int(row.prediction)})
    flip=pd.DataFrame(flips)
    saveparquet(flip,OUT/'explanations/error-flips.parquet')
    aggregate=flip.groupby(['protocol','comparator','seed','content_id','label_id'])[['repaired','new_error','decision_changed']].sum().reset_index()
    saveparquet(aggregate,OUT/'explanations/content-flips.parquet')
    selected=data[data.arm.eq('G4')].sort_values('visit_id').groupby(['protocol','label_id']).head(1)[['visit_id','protocol','content_id','label_id']]
    saveparquet(selected,OUT/'explanations/fixed-example-visits.parquet')
    # True labels are joined only here, after prediction freezing, for offline fit-gap explanation.
    gaps=[]
    for role in c['roles']:
        fold,p=role['fold'],role['protocol']
        query=load_package(rolefolder(fold,p)/'query-post-hist.parquet','explain')
        labels=load_package(rolefolder(fold,p)/'score-labels.parquet','explain')
        q=query.merge(labels[['visit_id','label_id']],on='visit_id',validate='one_to_one')
        bundle=model_load(modelfolder(fold,p)/'distributions.pt','explain')
        at=0
        for f in FEATURES:
            k=size(f)
            for y,label in enumerate(LABELS):
                observed=q[q.label_id.eq(label)][HIST[at:at+k]].mean().to_numpy()
                gaps.append({'fold':fold,'protocol':p,'feature':f,'label':label,
                    'JS_test_hist_vs_Q':js_positive(observed,bundle['G4'][f][y].cpu().numpy())})
            at+=k
    saveparquet(pd.DataFrame(gaps),OUT/'explanations/offline-test-fit-gaps.parquet')
    finish('explain',margin_checks=480,no_refit=True,offline_test_labels_used_for_explanation_only=True)

def js_positive(p,q):
    m=(p+q)/2
    valid=p>0
    return float(.5*((p[valid]*np.log(p[valid]/m[valid])).sum()+(q*np.log(q/m)).sum()))

if __name__=='__main__':
    run()
