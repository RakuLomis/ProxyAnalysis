"""Descriptive joint information, support, drift and training-only kernel JS."""
from itertools import combinations
import numpy as np
import pandas as pd
import torch
from common import OUT, PROTOCOLS, FEATURES, read, write, checkpoint, cuda, require
from bins import encode, size
from kernels import tensor, joint_counts, group_counts, smooth
from information import information, js, artificial_checks
from weights import mass
from uncertainty import draws


def weighted_quantile(x, w, levels=(.25,.5,.75)):
    order=np.argsort(x,kind='stable');x=np.asarray(x)[order];w=np.asarray(w)[order]
    return x[np.minimum(np.searchsorted(np.cumsum(w)/np.sum(w),levels),len(x)-1)]


def descriptive():
    f=pd.read_parquet(OUT/'features/paired-flow-features.parquet')
    folders, index=draws()
    frequency_rows, info_rows, drift_rows, zero_rows=[],[],[],[]
    for protocol, frame in f.groupby('protocol'):
      frame=frame.reset_index(drop=True)
      for weighting in ['hierarchical','flow_equal']:
        w_np=mass(frame,weighting);w=tensor(w_np)
        group_ids={u:i for i,u in enumerate(folders.content_id)}
        g=tensor(frame.content_id.map(group_ids),True)
        ng=len(group_ids)
        for feature in FEATURES:
            k=size(feature)
            a_np=encode(frame['pre_'+feature],feature);b_np=encode(frame['post_'+feature],feature)
            a,b=tensor(a_np,True),tensor(b_np,True)
            n=joint_counts(a,b,w,k,k)
            anonymous=group_counts(a,b,w,w,g,g,ng,k,k)
            qb,ktrue=smooth(n);_,kgroup=smooth(anonymous)
            conditions={}
            for aa in range(k):
                row=frame.iloc[np.where(a_np==aa)[0]]
                conditions[aa]=(row.content_id.nunique(),row.session_id.nunique())
                for bb in range(k):
                    cells=frame.iloc[np.where((a_np==aa)&(b_np==bb))[0]]
                    weights_cell=w_np[(a_np==aa)&(b_np==bb)]
                    mc=(pd.Series(weights_cell,index=cells.content_id).groupby(level=0).sum().max()
                        if len(cells) else 0.)
                    nc=float(n[aa,bb].item());rowmass=float(n[aa].sum().item())
                    frequency_rows.append({'protocol':protocol,'weighting':weighting,'feature':feature,'A':aa,'B':bb,
                      'physical_pairs':len(cells),'visits':cells.session_id.nunique(),'contents':cells.content_id.nunique(),
                      'weighted_mass':nc,'joint_probability':nc/float(n.sum().item()),
                      'conditional_empirical':nc/rowmass if rowmass>0 else np.nan,
                      'conditional_model_M1':float(ktrue[aa,bb].item()),
                      'conditional_model_M2':float(kgroup[aa,bb].item()),
                      'A_contents':conditions[aa][0],'A_visits':conditions[aa][1],
                      'max_content_mass_fraction':float(mc/nc) if nc>0 else np.nan})
            # Per-content masses, preserving the actual cluster and raw-bin supports.
            joint_by_content=torch.bincount(g*k*k+a*k+b,weights=w,minlength=ng*k*k).reshape(ng,k,k)
            counts_boot=joint_by_content[tensor(index,True)].sum(1)
            info_boot=information(counts_boot)
            for name, joint in [('empirical_true',n),('empirical_group',anonymous),
                                ('smoothed_true',n.sum(1)[:,None]/n.sum()*ktrue),
                                ('smoothed_group',n.sum(1)[:,None]/n.sum()*kgroup)]:
                s={name_:float(value.item()) for name_,value in information(joint).items()}
                row={'protocol':protocol,'weighting':weighting,'feature':feature,'estimator':name,**s,
                     'pair_count':len(frame),'visits':frame.session_id.nunique(),'contents':frame.content_id.nunique(),
                     'occupied_cells':int((joint>0).sum().item()),'A_occupied':int((joint.sum(1)>0).sum().item()),
                     'B_occupied':int((joint.sum(0)>0).sum().item())}
                if name=='empirical_true':
                    for key in ['H_A','H_B','H_B_given_A','H_A_given_B','MI','entropy_delta']:
                        q=torch.quantile(info_boot[key],tensor([.025,.975])).cpu().numpy()
                        row[key+'_low95'],row[key+'_high95']=q
                require(abs(s['entropy_delta']-s['H_B_given_A']+s['H_A_given_B'])<1e-10,'Entropy identity failure')
                info_rows.append(row)
            del counts_boot
            pre=frame['pre_'+feature].to_numpy();post=frame['post_'+feature].to_numpy();delta=post-pre
            qs=weighted_quantile(delta,w_np)
            drift_rows.append({'protocol':protocol,'weighting':weighting,'feature':feature,
                 'delta_q25':qs[0],'delta_median':qs[1],'delta_q75':qs[2],
                 'negative_delta_fraction':float(np.average(delta<0,weights=w_np)),
                 'zero_delta_fraction':float(np.average(delta==0,weights=w_np)),
                 'positive_delta_fraction':float(np.average(delta>0,weights=w_np)),
                 'zero_pre_fraction':float(np.average(pre==0,weights=w_np)),
                 'positive_pre_ratio_median':float(weighted_quantile(post[pre>0]/pre[pre>0],w_np[pre>0],[.5])[0]) if (pre>0).any() else np.nan})
            if (pre==0).any():
                zero_rows.append({'protocol':protocol,'weighting':weighting,'feature':feature,
                  'zero_pre_pairs':int((pre==0).sum()),'positive_post_given_zero_pre':
                  float(np.average(post[pre==0]>0,weights=w_np[pre==0])),
                  'zero_pre_contents':frame.loc[pre==0,'content_id'].nunique()})
        print('descriptive',protocol,weighting,flush=True)
    (OUT/'information').mkdir(exist_ok=True);(OUT/'probability-tables').mkdir(exist_ok=True)
    pd.DataFrame(frequency_rows).to_parquet(OUT/'probability-tables/joint-and-conditional.parquet',index=False)
    pd.DataFrame(info_rows).to_parquet(OUT/'information/information-summary.parquet',index=False)
    pd.DataFrame(drift_rows).to_parquet(OUT/'information/drift-summary.parquet',index=False)
    pd.DataFrame(zero_rows).to_parquet(OUT/'information/zero-direction-summary.parquet',index=False)
    write(OUT/'information/artificial-checks.json',artificial_checks())


def distances():
    rows=[]
    for fold in range(5):
      for feature in FEATURES:
        models,valid,marginals={}, {}, {}
        for p in PROTOCOLS:
            d=OUT/'kernels/primary'/f'f{fold}'/p
            models[p]=torch.load(d/(feature+'.pt'),map_location=cuda(),weights_only=True)
            tr=pd.read_parquet(OUT/'packages/primary'/f'f{fold}'/p/'train.parquet')
            a=encode(tr['pre_'+feature],feature)
            support=np.zeros(size(feature),bool)
            for aa in range(size(feature)):
                cells=tr.iloc[np.where(a==aa)[0]]
                support[aa]=cells.content_id.nunique()>=5 and cells.session_id.nunique()>=10
            valid[p]=tensor(support,True).bool()
            n=models[p]['row_mass'];marginals[p]=n/n.sum()
        for p,q in combinations(PROTOCOLS,2):
            common=valid[p]&valid[q];mp,mq=marginals[p],marginals[q]
            r=(mp+mq)/2;coverage_p=float(mp[common].sum().item());coverage_q=float(mq[common].sum().item())
            if bool(common.any()):
                distance=float((js(models[p]['M1'][common],models[q]['M1'][common])*r[common]/r[common].sum()).sum().item())
            else:distance=np.nan
            rows.append({'fold':fold,'feature':feature,'protocol_1':p,'protocol_2':q,
                         'conditional_JS_bits':distance,'common_A_bins':int(common.sum().item()),
                         'coverage_1':coverage_p,'coverage_2':coverage_q,
                         'minimum_contents_per_A':5,'minimum_visits_per_A':10,
                         'test_data_used_for_support':False})
    pd.DataFrame(rows).to_parquet(OUT/'comparisons/kernel-distances.parquet',index=False)


if __name__=='__main__':
    descriptive();distances();checkpoint('Q22_statistics_complete',{'raw_captures_opened':0})
