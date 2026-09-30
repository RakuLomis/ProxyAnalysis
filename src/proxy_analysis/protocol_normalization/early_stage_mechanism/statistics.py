import numpy as np
import pandas as pd
from scipy.optimize import linprog
from scipy import sparse

from .common import *
from ..targeted_diagnostics.core import pair_ledger,PAIR,KEY

BINS=['zero','(0,4KiB)','[4,16KiB)','[16,64KiB)','[64,256KiB)','[256KiB,1MiB)','[1MiB,inf)']

def load_bin(value):
    if value==0:return BINS[0]
    return BINS[1+int(np.searchsorted([4096,16384,65536,262144,1048576],value,side='right'))]

def lad_fit(x,y):
    """Fixed-order rank reduction, train-only scale, exact linear absolute loss LP."""
    x=np.asarray(x,float);y=np.asarray(y,float)
    scale=np.maximum(np.max(abs(x),axis=0),1.)
    z=x/scale;keep=[]
    for j in range(z.shape[1]):
        if np.linalg.matrix_rank(z[:,keep+[j]])>len(keep):keep.append(j)
    z=z[:,keep];n,p=z.shape;ident=sparse.eye(n,format='csr')
    mat=sparse.vstack([sparse.hstack([sparse.csr_matrix(z),-ident]),sparse.hstack([-sparse.csr_matrix(z),-ident])],format='csr')
    result=linprog(np.r_[np.zeros(p),np.ones(n)/n],A_ub=mat,b_ub=np.r_[y,-y],bounds=[(None,None)]*p+[(0,None)]*n,method='highs')
    if not result.success:raise ValueError(result.message)
    coef=np.zeros(x.shape[1]);coef[keep]=result.x[:p]/scale[keep]
    return coef,keep

def build():
    z=pair_ledger(pd.read_parquet(BASE/'tcp-byte-ledger.parquet'))
    z=z[z.S_valid&(z.main_route=='proxy')].copy()
    reg=pd.read_parquet(BASE/'registry.parquet');reg=reg[reg.is_final]
    # target_key spans protocol/repetition. URL identity also ties repeated content across batches.
    group=reg[['session_id','target_url']].copy()
    group['content_group']=group.target_url.map(stable)
    z=z.merge(group[['session_id','content_group']],on='session_id',validate='many_to_one')
    old=pd.read_parquet(BASE/'byte-direction-runs.parquet');old=old[old.threshold_bytes==0]
    valid4=z.groupby(PAIR).direction.nunique();ids=set(valid4[valid4==2].index)
    rs=[]
    for r in old.to_dict('records'):
        if (r['session_id'],r['connection_id']) not in ids:continue
        for d in [-1,1]:rs.append({**{k:r[k] for k in PAIR+['side']},'direction':d,
            'direction_runs':sum(int(v==d) for v in r['directions']),'total_runs':r['run_count']})
    rs=pd.DataFrame(rs)
    for side in ['pre','post']:
        q=rs[rs.side==side].drop(columns='side').rename(columns={'direction_runs':side+'_direction_runs','total_runs':side+'_total_runs'})
        z=z.merge(q,on=KEY,how='left',validate='one_to_one')
    z['run_difference']=z.post_total_runs-z.pre_total_runs
    z['load_bin']=z.pre.map(load_bin)
    # Full 0914/0916 scope is not the old 240-row cohort; fixed global content hashes.
    groups=sorted(z.content_group.unique(),key=stable)
    foldmap={g:i%5 for i,g in enumerate(groups)}
    z['fold']=z.content_group.map(foldmap)
    z['partition']=z.content_group.map(lambda g:'discovery' if int(stable('partition|'+g),16)%2==0 else 'verification')
    assert z.groupby('session_id').fold.nunique().eq(1).all()
    assert z.groupby('content_group').fold.nunique().eq(1).all()
    keep=KEY+['batch','item_id','protocol','repetition','content_group','fold','partition','pre','post','difference','ratio','log_ratio','load_bin',
              'pre_direction_runs','post_direction_runs','pre_total_runs','post_total_runs','run_difference']
    keep += [c+'_'+s for c in ['fin_count','rst_count','prefix_observed','suffix_observed','final_internal_gap_count','closed_contiguous_capture_candidate'] for s in ['pre','post']]
    z=save('connection-load-table',z[keep]);save('group-folds',z[['session_id','content_group','fold','partition']].drop_duplicates())
    js('eligibility.json',{'direction_rows':len(z),'with_run_qualification':int(z.pre_direction_runs.notna().sum()),
        'fold_method':'global canonical target_url SHA256 group, hash sorted round robin 5 folds',
        'old_fold_reuse':False,'reason':'old business cohort 240 visits is a strict subset; three-batch full measurement scope includes additional content and repeats',
        'scope':'retrospective internal descriptive validation, not old classification fold replication',
        'same_content_same_fold':True,'same_parent_same_fold':True})
    rows=[]
    for (b,p,d),g in z.groupby(['batch','protocol','direction']):
        for bn in BINS:
            q=g[g.load_bin==bn];vals=q.difference
            visit=q.groupby(['item_id','session_id']).difference.median()
            items=visit.groupby('item_id').median()
            rows.append(dict(batch=b,protocol=p,direction=d,load_bin=bn,connections=len(q),visits=q.session_id.nunique(),items=q.item_id.nunique(),
                median=vals.median(),mad=(vals-vals.median()).abs().median(),iqr=vals.quantile(.75)-vals.quantile(.25),q05=vals.quantile(.05),q95=vals.quantile(.95),
                positive_fraction=(vals>0).mean() if len(q) else np.nan,negative_fraction=(vals<0).mean() if len(q) else np.nan,
                zero_fraction=(vals==0).mean() if len(q) else np.nan,ratio_median=q.ratio.median(),ratio_q05=q.ratio.quantile(.05),ratio_q95=q.ratio.quantile(.95),item_equal_median=items.median()))
    save('load-strata-summary',rows)
    print('E1-E2',len(z),'direction rows',flush=True)

def design(g,model):
    x=[np.ones(len(g)),np.log2(1+g.pre.to_numpy())];names=['intercept','log2_pre_bytes_plus1']
    if model=='M2':
        x.append(np.log2(1+g.pre_direction_runs.to_numpy()));names.append('log2_pre_direction_runs_plus1')
        for side in ['pre','post']:
            for flag in ['fin_count','rst_count']:
                x.append((g[flag+'_'+side]>0).astype(float).to_numpy());names.append(flag+'_'+side)
    return np.column_stack(x),names

def models():
    z=load('connection-load-table');fits=[];predictions=[]
    for (batch,protocol,direction),g0 in z.groupby(['batch','protocol','direction']):
        for scope in ['byte_all','run_common']:
            g=g0 if scope=='byte_all' else g0[g0.pre_direction_runs.notna()]
            for model in (['M0','M1'] if scope=='byte_all' else ['M0','M1','M2']):
                for fold in [-1,0,1,2,3,4]:
                    train=g if fold==-1 else g[g.fold!=fold];test=g if fold==-1 else g[g.fold==fold]
                    meta=dict(batch=batch,protocol=protocol,direction=int(direction),scope=scope,model=model,fold=fold,n_train=len(train),n_test=len(test))
                    if len(train)==0 or len(test)==0:
                        fits.append({**meta,'status':'empty_train_or_test'});continue
                    assert fold==-1 or not set(train.content_group)&set(test.content_group)
                    try:
                        if model=='M0':
                            coef=[float(train.difference.median())];names=['intercept'];kept=[0];est=np.full(len(test),coef[0])
                        else:
                            x,names=design(train,model);coef,kept=lad_fit(x,train.difference);est=design(test,model)[0]@coef;coef=coef.tolist()
                        fits.append({**meta,'status':'ok','coefficients':coef,'names':names,'kept_columns':kept,'rank':len(kept)})
                        out=test[KEY+['item_id','content_group','load_bin','difference']].copy()
                        for k,v in meta.items():out[k]=v
                        out['prediction']=est;out['residual']=out.difference-out.prediction
                        predictions.extend(out.to_dict('records'))
                    except ValueError as exc:fits.append({**meta,'status':'fit_failed','error':str(exc)})
        print('E3',batch,protocol,direction,flush=True)
    js('descriptive-models.json',fits);pr=save('model-residuals',predictions)
    oof=save('oof-residuals',pr[pr.fold>=0])
    summaries=[]
    for key,g in oof.groupby(['batch','protocol','direction','scope','model']):
        item=g.assign(a=abs(g.residual)).groupby(['item_id','session_id']).a.mean().groupby('item_id').mean()
        summaries.append(dict(zip(['batch','protocol','direction','scope','model'],key))|dict(rows=len(g),mae=float(abs(g.residual).mean()),median_absolute_error=float(abs(g.residual).median()),
                      signed_median=float(g.residual.median()),item_equal_mae=float(item.mean())))
    save('model-summary',summaries)
    save('residuals-by-load',oof.groupby(['batch','protocol','direction','scope','model','load_bin'],as_index=False).agg(
        rows=('residual','size'),mae=('residual',lambda v:abs(v).mean()),signed_median=('residual','median')))
    js('fit-audit.json',{'descriptive_successful_fits':sum(r['status']=='ok' for r in fits),'descriptive_failed_fits':sum(r['status']=='fit_failed' for r in fits),'classifier_fits':0})
