"""Frozen-candidate rejection diagnosis. C/U only; no fit, repair or classification."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'src'))
from proxy_analysis.cross_business_calibration.common import *
from proxy_analysis.conditional_drift.model import torch,device

DEST=OUT/'rejection-diagnostic'
KEY=['protocol','business_group','arm','business_role']

def violations(raw,F):
    raw=np.asarray(raw);v=np.rint(raw);U=v[...,0:2];E=v[...,2:4];R=v[...,4:6]
    out={'nonfinite':~np.isfinite(v).all(-1),'negative':(raw<0).any(-1),'overflow':(v>2**53-1).any(-1),
        'E_gt_U_up':E[...,0]>U[...,0],'E_gt_U_down':E[...,1]>U[...,1],
        'R_gt_E_up':R[...,0]>E[...,0],'R_gt_E_down':R[...,1]>E[...,1],
        'zero_mismatch':(((U==0)&((E!=0)|(R!=0)))|((U>0)&((E<1)|(R<1)))).any(-1),
        'runs_below_F':R.sum(-1)<F,'direction_imbalance':abs(R[...,0]-R[...,1])>F}
    out['any_invalid']=np.logical_or.reduce(list(out.values()));return out

def predict(state,a,F):
    dev=device()
    with torch.no_grad():
        q=torch.tensor(np.log1p(np.column_stack([a,F])),device=dev,dtype=torch.float64)
        x=torch.cat([(q-state['mean'])/state['scale'],torch.ones((len(a),1),device=dev,dtype=q.dtype)],1)
        return (q[:,:6]+(x@state['weight'])*state['scale'][:6]).cpu().numpy()

def main():
    DEST.mkdir(parents=True,exist_ok=True)
    for p,h in read(OUT/'worker-contract.json')['files'].items():assert sha(p)==h
    for p,h in read(OUT/'contract.json')['inputs'].items():assert sha(p)==h
    # Column/row filtered training identity ledger. No H labels are loaded.
    roles=pd.read_parquet(OUT/'roles.parquet',filters=[('role','in',['C','U'])])
    observed=[];queries=[];donors=[];margins=[];inputs={};checked=0
    for kind in ['paired','group']:
      for folder in sorted((OUT/'generation'/kind).iterdir()):
        meta=read(OUT/'bundles'/kind/folder.name/'manifest.json');done=read(folder/'complete.json')
        for p,h in done['files'].items():assert sha(p)==h
        inputs[str(folder/'complete.json')]=sha(folder/'complete.json')
        bundle=Bundle(OUT/'bundles'/kind/folder.name,kind);q=bundle.get('U_pre')
        pre=bundle.get('C_pre' if kind=='paired' else 'G_pre')
        q=q.merge(roles[(roles.scenario==folder.name)&(roles.role=='U')][['session_id','label_id','business_role']],on='session_id',validate='one_to_one')
        a=q[FEATURES].to_numpy(float);F=q.F.to_numpy(float)
        state=torch.load(folder/'models.pt',map_location=device(),weights_only=False)
        z={arm:predict(s,a,F) for arm,s in state.items()}
        if kind=='paired':z.update({'X2':np.log1p(a)+state['X4']['center'],'X3':np.log1p(a)})
        saved=pd.concat([pd.read_parquet(p) for p in sorted(folder.glob('samples-*.parquet'))],ignore_index=True)
        saved=saved.merge(q[['session_id','business_role','label_id']],on='session_id',validate='many_to_one')
        flags=violations(saved[['first_raw_'+k for k in FEATURES]].to_numpy(),saved.F.to_numpy())
        assert np.array_equal(flags['any_invalid'],saved.first_invalid.to_numpy())
        detail=saved[['protocol','business_group','arm','business_role','label_id','scenario','session_id','attempts']].copy()
        for k,v in flags.items():detail[k]=v
        obs=detail.groupby(KEY+['label_id','scenario','session_id']).agg({**{k:'sum' for k in flags},'attempts':['sum','max'],'session_id':'size'})
        obs.columns=[k if k in flags else ('attempts_sum' if (k,v)==('attempts','sum') else 'attempts_max' if k=='attempts' else 'views') for k,v in obs.columns]
        observed.append(obs.reset_index())
        support=pd.read_parquet(folder/'query-support.parquet').set_index('session_id')
        for arm,base in z.items():
            if arm=='X2':pool=None;res=np.zeros((1,6));content=np.array(['constant'])
            else:
                pool=pd.read_parquet(folder/('X4-pool.parquet' if arm=='X3' else arm+'-pool.parquet'))
                res=pool[[('drift_' if arm=='X3' else 'residual_')+k for k in FEATURES]].to_numpy();content=pool.content_id.to_numpy()
            # All six equally sized groups are candidates. Thus every residual has equal proposal probability.
            raw=np.expm1(base[:,None,:]+res[None,:,:]);bad=violations(raw,F[:,None]);basebad=violations(np.expm1(base),F)
            n=len(res);accept=~bad['any_invalid'];prob=accept.mean(1)
            assert (prob>0).all(),'Zero acceptance support must be reported separately'
            sf=saved[saved.arm==arm]
            for i,r in enumerate(q.to_dict('records')):
                record={k:meta[k] for k in ['scenario','protocol','business_group','rotation','fold']}
                record.update({k:r[k] for k in ['session_id','content_id','label_id','business_role']});record['arm']=arm
                record.update({'candidate_count':n,'center_invalid':bool(basebad['any_invalid'][i]),'exact_rejection_probability':1-prob[i],
                    'valid_center_rejected_fraction':float(bad['any_invalid'][i].mean()) if not basebad['any_invalid'][i] else 0.,
                    'invalid_center_rescued_fraction':float(prob[i]) if basebad['any_invalid'][i] else 0.,
                    'expected_attempts_unbounded':1/prob[i], 'all_33_invalid_probability':float((1-prob[i])**33),
                    'residual_index_TV_after_conditioning':1-prob[i],
                    'outside_C_range_dimensions':int(support.loc[r['session_id'],'outside_C_range_dimensions']),
                    'nearest_C_centroid_distance':float(support.loc[r['session_id'],'nearest_C_centroid_distance'])})
                for k,v in bad.items():record['exact_'+k]=float(v[i].mean())
                for direction,j in [('up',0),('down',1)]:
                    record['pre_log_E_R_margin_'+direction]=float(np.log1p(a[i,2+j])-np.log1p(a[i,4+j]))
                    record['center_log_E_R_margin_'+direction]=float(base[i,2+j]-base[i,4+j])
                    # Negative final log gap implies raw R>E; rounding may repair sub-unit differences.
                    gap=base[i,2+j]-base[i,4+j]+res[:,2+j]-res[:,4+j]
                    record['raw_R_gt_E_'+direction]=float((gap<0).mean())
                if pool is not None:
                    old=np.array([(content==c).mean() for c in sorted(set(content))])
                    new=np.array([accept[i,content==c].sum()/accept[i].sum() for c in sorted(set(content))])
                    record['donor_content_TV_after_conditioning']=float(abs(new-old).sum()/2)
                else:record['donor_content_TV_after_conditioning']=0.
                queries.append(record)
            if pool is not None:
                # Donor composition conditional on acceptance, not a new sampler or repaired generator.
                for role in ['new','cal']:
                    ix=q.business_role.eq(role).to_numpy();masses=accept[ix]/accept[ix].sum(1,keepdims=True)
                    for c in sorted(set(content)):
                        samples=sf[(sf.business_role==role)&sf.donor_content.eq(c)]
                        donors.append({'scenario':folder.name,'protocol':meta['protocol'],'business_group':meta['business_group'],'arm':arm,'business_role':role,'donor_content':c,
                            'proposal_mass':float((content==c).mean()),'accepted_theoretical_mass':float(masses[:,content==c].sum(1).mean()),
                            'observed_final_mass':len(samples)/len(sf[sf.business_role==role])})
                for direction,j in [('up',0),('down',1)]:
                    v=res[:,2+j]-res[:,4+j]
                    margins.append({'scenario':folder.name,'protocol':meta['protocol'],'business_group':meta['business_group'],'arm':arm,'direction':direction,
                        'q05':float(np.quantile(v,.05)),'q50':float(np.quantile(v,.5)),'q95':float(np.quantile(v,.95)),'negative_fraction':float((v<0).mean())})
        checked+=1
        if checked%80==0:print('diagnosed',checked,'/480',flush=True)
    obs=pd.concat(observed,ignore_index=True);qq=pd.DataFrame(queries);dd=pd.DataFrame(donors);mm=pd.DataFrame(margins)
    for name,df in [('observed-by-query',obs),('exact-by-query',qq),('donor-selection',dd),('residual-gap-summary',mm)]:df.to_parquet(DEST/(name+'.parquet'),index=False)
    sums=obs.groupby(KEY).sum(numeric_only=True);sums['attempts_max']=obs.groupby(KEY).attempts_max.max()
    for col in flags:sums[col+'_rate']=sums[col]/sums.views
    sums['mean_attempts']=sums.attempts_sum/sums.views;sums.reset_index().to_parquet(DEST/'observed-summary.parquet',index=False)
    qq.groupby(KEY).mean(numeric_only=True).reset_index().to_parquet(DEST/'exact-summary.parquet',index=False)
    qq.groupby(KEY+['label_id']).mean(numeric_only=True).reset_index().to_parquet(DEST/'exact-by-business.parquet',index=False)
    qq['support_bin']=np.where(qq.outside_C_range_dimensions==0,'inside_C_marginal_ranges','outside_C_marginal_ranges')
    qq.groupby(KEY+['support_bin']).agg(queries=('session_id','size'),exact_rejection_probability=('exact_rejection_probability','mean')).reset_index().to_parquet(DEST/'support-strata.parquet',index=False)
    write(DEST/'completion.json',{'status':'complete','source_hashes_unchanged':True,'workers':480,'observed_views':int(obs.views.sum()),'query_arm_instances':len(qq),
        'model_inference':'cuda_float64_saved_models','new_fits':0,'classifier_training':False,'U_post_read':False,'H_pre_read':False,'H_post_read':False,'test_labels_read':False,
        'proposal_analysis':'exact enumeration of frozen finite pools, no new random views or parameter selection','inputs':inputs,'script_hash':sha(__file__)})
    print('Diagnostic complete',len(qq),int(obs.views.sum()),flush=True)

if __name__=='__main__':main()
