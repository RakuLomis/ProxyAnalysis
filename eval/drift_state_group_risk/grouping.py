"""Scoped CF fits, identity-free anonymous queries and frozen training states."""
import sys
from common import *

def sourcemodel(s):
    return oldartifact('models',s['old_role'],'zero') if s['kind']=='old18' else artifact(sourcefolder('models',s)/'zero.pt')
def sourcekernel(s,j):
    return oldartifact('kernels',s['old_role'],FEATURES[j]) if s['kind']=='old18' else artifact(sourcefolder('kernels',s)/(FEATURES[j]+'.pt'))

def fit_sources():
    c=start('sources'); logs=[]; reuse=[]
    for s in c['sources']:
        if s['kind']=='old18':
            r=s['old_role']; p=oldfolder('packages',r)
            for f in ['fit-pre','fit-post','group-pre','group-post','fit-post-hist']:
                checked(p/(f+'.parquet'),c['baseline_sha256'],'reuse-fit-input')
            a=pd.read_parquet(p/'fit-pre.parquet'); b=pd.read_parquet(p/'fit-post.parquet')
            paired=a.merge(b,on=['pair_id','session_id','content_id','fit_mass'],validate='one_to_one')
            gp=pd.read_parquet(p/'group-pre.parquet'); gb=pd.read_parquet(p/'group-post.parquet')
            hist=pd.read_parquet(p/'fit-post-hist.parquet'); x,mu,scale=standardize(hist); model=sourcemodel(s)
            require(set(hist.content_id)==set(s['train_contents']) and len(hist)==72,'Reused model scope')
            require(torch.equal(mu,model['mu']) and torch.equal(scale,model['scale']),'Reused model coordinate mismatch')
            maximum=0.
            for j in range(10):
                fresh=kernel(paired,gp,gb,j); old=sourcekernel(s,j)
                err=max(float((fresh[name]-old[name]).abs().max()) for name in ['M1','M2','true_counts','group_counts'])
                require(err<1e-10,'Reused kernel replay mismatch'); maximum=max(maximum,err)
            reuse.append({'source':s['id'],'max_replay':maximum,'visits':72,'train_contents':18})
            continue
        src=sourcefolder('packages',s); dst=sourcefolder('kernels',s); dst.mkdir(parents=True,exist_ok=True)
        p=package(src/'fit-paired.parquet','kernel-fit'); gp=package(src/'group-pre.parquet','kernel-fit'); gb=package(src/'group-post.parquet','kernel-fit')
        require(set(p.content_id)==set(s['train_contents']) and abs(p.fit_mass.sum()-12)<1e-10,'New source scope')
        for j,f in enumerate(FEATURES): torch.save(kernel(p,gp,gb,j),dst/(f+'.pt'))
        complete(dst,source=s['id'],train_contents=s['train_contents'])
        h=package(src/'train-post.parquet','lr-fit'); require(len(h)==48,'CF12 histogram support')
        x,mu,scale=standardize(h); y=tensor(truths(h),torch.long); state,log=optimize(x,y)
        dst=sourcefolder('models',s); dst.mkdir(parents=True,exist_ok=True)
        torch.save({'mu':mu,'scale':scale,**state},dst/'zero.pt'); log['source']=s['id']; logs.append(log)
        complete(dst,train_contents=s['train_contents'],optimizer=log)
        print('CF12 CUDA fit',s['id'],flush=True)
    save(pd.DataFrame(logs),OUT/'manifests/CF12-optimizer.parquet'); write(OUT/'manifests/reuse-replay.json',reuse)
    finish('D10-D11',independent_CF12_fits=len(logs),reused_CF18_roles=len(reuse),new_kernels=10*len(logs))

def visit_mean(frame,values,order):
    i=tensor(frame.visit_id.map(dict(zip(order,range(len(order))))),torch.long)
    sums=weighted(i,values,len(order)); count=weighted(i,torch.ones_like(values),len(order))
    return sums/count

def true_scores(raw,bundles):
    require(set(raw)=={'visit_id','content_id',*['pre_'+f for f in FEATURES],*['post_'+f for f in FEATURES]},'True score schema')
    order=sorted(raw.visit_id.unique()); result={'visit_id':order}; total=torch.zeros(len(order),device=device(),dtype=torch.float64)
    zero=torch.zeros_like(total); low=torch.zeros_like(total)
    for j,f in enumerate(FEATURES):
        b=bundles[j]; a=bins(raw['pre_'+f],j); z=bins(raw['post_'+f],j)
        score=visit_mean(raw,-torch.log2(b['M1'][a,z]),order); result['true_'+f]=score.cpu().numpy(); total+=WEIGHTS[j]*score
        row=b['true_counts'].sum(1)[a]; zerof=visit_mean(raw,(row==0).to(torch.float64),order); lowf=visit_mean(raw,(row<1).to(torch.float64),order)
        result['zero_'+f]=zerof.cpu().numpy(); result['low_'+f]=lowf.cpu().numpy(); zero+=WEIGHTS[j]*zerof; low+=WEIGHTS[j]*lowf
    result['d_true']=total.cpu().numpy(); result['zero_support']=zero.cpu().numpy(); result['low_support']=low.cpu().numpy()
    result['connections']=raw.groupby('visit_id').size().loc[order].to_numpy()
    return pd.DataFrame(result)

def group_scores(raw,pre,bundles):
    require(set(raw)=={'visit_id','content_id',*['post_'+f for f in FEATURES]},'Anonymous query contains pre or pair identity')
    require(set(pre)=={'content_id',*HIST} and pre.content_id.is_unique,'Anonymous pre query contains identity')
    require(set(raw.content_id)==set(pre.content_id),'Anonymous content pool mismatch')
    order=sorted(raw.visit_id.unique()); total=torch.zeros(len(order),device=device(),dtype=torch.float64); result={'visit_id':order}
    for j,f in enumerate(FEATURES):
        k=size(j); z=bins(raw['post_'+f],j); cols=[f'h{j:02d}_{a:02d}' for a in range(k)]
        s=tensor(pre.set_index('content_id').loc[raw.content_id,cols]); require(float((s.sum(1)-1).abs().max())<1e-10,'Anonymous query mass')
        loss=(s*(-torch.log2(bundles[j]['M2'][:,z]).T)).sum(1)
        score=visit_mean(raw,loss,order); result['group_'+f]=score.cpu().numpy(); total+=WEIGHTS[j]*score
    result['d_group']=total.cpu().numpy(); return pd.DataFrame(result)

def score_queries(inner):
    c=start('CF-state-score'); sources={s['id']:s for s in c['sources']}; records=[]
    for q in c['queries']:
        if (q['parent']['inner'] is not None)!=inner: continue
        s=sources[q['source']]; validate_scope(s['train_contents'],q['query_contents'],q['parent']['train_contents'])
        src=queryfolder('packages',q); bundles=[sourcekernel(s,j) for j in range(10)]
        t=true_scores(package(src/'query-paired.parquet','true-state'),bundles)
        g=group_scores(package(src/'query-group-post.parquet','group-state'),package(src/'query-group-pre.parquet','group-state'),bundles)
        post=package(src/'query-post.parquet','difficulty-predict'); pred=probabilities(sourcemodel(s),post)
        dst=queryfolder('CF-predictions',q); dst.mkdir(parents=True,exist_ok=True); save(pred,dst/'post-probabilities.parquet'); complete(dst,no_pre_labels_in_LR_prediction=True)
        labels=package(src/'query-labels.parquet','difficulty-score'); pc=pred.merge(labels,on='visit_id',validate='one_to_one')
        p=tensor(pc[[f'p{i}' for i in range(6)]]); y=tensor(truths(pc),torch.long)
        pc['d_post']=(-torch.log(p[torch.arange(len(y),device=device()),y])).cpu().numpy(); pc['difficulty_correct']=pc.prediction.to_numpy()==truths(pc)
        d=t.merge(g,on='visit_id',validate='one_to_one').merge(pc[['visit_id','content_id','label_id','d_post','difficulty_correct']],on='visit_id',validate='one_to_one')
        r=q['parent']; d['outer']=r['outer']; d['inner']=r['inner']; d['protocol']=r['protocol']; d['source']=s['id']; d['CF_fold']=q['held']; records.append(d)
    part='inner' if inner else 'outer'; save(pd.concat(records,ignore_index=True),OUT/f'states/{part}-CF-scores.parquet')
    finish('D12' if inner else 'D18-CF',logical_queries=len(records),all_queries_excluded_from_source=True)

def make_states(inner):
    c=start('state-grouping'); part='inner' if inner else 'outer'; d=pd.read_parquet(OUT/f'states/{part}-CF-scores.parquet'); bounds=[]; summaries=[]; stateall=[]
    for r in c['roles']:
        if (r['inner'] is not None)!=inner: continue
        h=package(mainfolder('packages',r)/'train-post.parquet','state-grouping')
        sub=d[(d.outer==r['outer'])&(d.protocol==r['protocol'])&((d.inner==r['inner']) if inner else d.inner.isna())]
        require(sub.visit_id.is_unique and set(sub.visit_id)==set(h.visit_id),'State support')
        sub=sub.set_index('visit_id').loc[h.visit_id].reset_index(); y=tensor(truths(h),torch.long)
        dst=mainfolder('states',r); dst.mkdir(parents=True,exist_ok=True)
        for arm,col in [('DSR2','d_post'),('DSR3','d_group'),('DSR4','d_true')]:
            gamma,bd=partition(tensor(sub[col]),y)
            torch.save({'gamma':gamma,'visit_id':h.visit_id.tolist()},dst/(arm+'.pt'))
            for row in bd: bounds.append({'outer':r['outer'],'inner':r['inner'],'protocol':r['protocol'],'arm':arm,**row})
            for i,state in enumerate([0,1]):
                stateframe=sub.copy(); stateframe['mass']=gamma[:,state].cpu().numpy()
                stateframe['state']=state; stateframe['arm']=arm; stateall.append(stateframe)
                for label,dd in stateframe.groupby('label_id'):
                    cm=dd.groupby('content_id').mass.sum(); cm=cm[cm>0]
                    denom=dd.mass.sum()
                    summaries.append({'outer':r['outer'],'inner':r['inner'],'protocol':r['protocol'],'arm':arm,'state':state,'label':label,
                      'mass':denom,'contents':len(cm),'max_content_fraction':float(cm.max()/denom),
                      'effective_contents':float(denom**2/(cm**2).sum()),
                      'OOF_CE':float((dd.d_post*dd.mass).sum()/denom),'OOF_accuracy':float((dd.difficulty_correct*dd.mass).sum()/denom),
                      'mean_true_score':float((dd.d_true*dd.mass).sum()/denom),'mean_zero_support':float((dd.zero_support*dd.mass).sum()/denom),
                      'mean_low_support':float((dd.low_support*dd.mass).sum()/denom),'connections':float((dd.connections*dd.mass).sum()/denom)})
        complete(dst,scope=r['train_contents'],source_scores_sha256=sha(OUT/f'states/{part}-CF-scores.parquet'))
    save(pd.DataFrame(bounds),OUT/f'states/{part}-boundaries.parquet'); save(pd.DataFrame(summaries),OUT/f'states/{part}-composition.parquet')
    save(pd.concat(stateall,ignore_index=True),OUT/f'states/{part}-visit-masses.parquet')
    finish('D13' if inner else 'D18',classification_roles=80 if inner else 20,boundaries=len(bounds))

if __name__=='__main__':
    {'sources':fit_sources,'inner-score':lambda:score_queries(True),'inner-states':lambda:make_states(True),
     'outer-score':lambda:score_queries(False),'outer-states':lambda:make_states(False)}[sys.argv[1]]()
