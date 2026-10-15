"""Fixed exploratory load comparisons and separate access-window joint tables."""
import numpy as np
import pandas as pd
from common import OUT, EXTRACT, PROTOCOLS, read, write
from bins import encode, size
from kernels import tensor, joint_counts, group_counts, smooth
from information import information
from weights import mass
from uncertainty import draws


def run():
    content=pd.read_parquet(OUT/'scores/content-composite-scores.parquet')
    folds,index=draws()
    rows=[]
    for p in PROTOCOLS:
        primary=content[content.variant.eq('primary')&content.protocol.eq(p)].pivot(index='content_id',columns='arm',values='CE_bits').reindex(folds.content_id)
        extra=content[content.variant.eq('load')&content.protocol.eq(p)].pivot(index='content_id',columns='arm',values='CE_bits').reindex(folds.content_id)
        for name,delta in [('M0-M1_L',primary.M0-extra.M1),('M1-M1_L',primary.M1-extra.M1),
                           ('M2_L-M1_L',extra.M2-extra.M1)]:
            values=delta.to_numpy();low,high=np.quantile(values[index].mean(1),[.025,.975])
            rows.append({'protocol':p,'contrast':name,'gain_bits':values.mean(),
                         'low95':low,'high95':high,'exploratory':True,'additional_pre_information':True})
    pd.DataFrame(rows).to_parquet(OUT/'comparisons/load-contrasts.parquet',index=False)
    contract=read(OUT/'manifests/experiment-contract.json')
    parents=pd.read_parquet(OUT/'cohorts/parents.parquet')
    window=pd.read_parquet(EXTRACT/'full-W-features.parquet')
    wide=window.pivot(index='session_id',columns='side',values=['W_up','W_down','P_up','P_down','R_up','R_down'])
    wide.columns=[f'{side}_{name}' for name,side in wide.columns]
    f=parents.merge(wide.reset_index(),on='session_id',validate='one_to_one')
    f.rename(columns={f'{s}_R_{d}':f'{s}_R_window_{d}' for s in ['pre','post'] for d in ['up','down']},inplace=True)
    tables,info=[],[]
    for p,frame in f.groupby('protocol'):
        for feature in contract['window_features']:
            k=size(feature);a=tensor(encode(frame['pre_'+feature],feature),True);b=tensor(encode(frame['post_'+feature],feature),True)
            w=tensor(mass(frame));n=joint_counts(a,b,w,k,k)
            groups={u:i for i,u in enumerate(sorted(frame.content_id.unique()))};g=tensor(frame.content_id.map(groups),True)
            anonymous=group_counts(a,b,w,w,g,g,len(groups),k,k)
            _,kernel=smooth(n)
            for name,joint in [('empirical_true',n),('empirical_group',anonymous),
                               ('smoothed_true',n.sum(1)[:,None]/n.sum()*kernel)]:
                info.append({'protocol':p,'feature':feature,'estimator':name,
                             'unit':'parent access common W window','visits':len(frame),'contents':len(groups),
                             **{key:float(v.item()) for key,v in information(joint).items()}})
            for aa in range(k):
              for bb in range(k):
                rowmass=float(n[aa].sum().item())
                tables.append({'protocol':p,'feature':feature,'A':aa,'B':bb,'weighted_mass':float(n[aa,bb].item()),
                               'joint_probability':float((n[aa,bb]/n.sum()).item()),
                               'conditional_empirical':float(n[aa,bb].item())/rowmass if rowmass>0 else np.nan,
                               'unit':'parent access common W window'})
    dest=OUT/'window-supplement';dest.mkdir(exist_ok=True)
    pd.DataFrame(tables).to_parquet(dest/'joint-and-conditional.parquet',index=False)
    pd.DataFrame(info).to_parquet(dest/'information-summary.parquet',index=False)
    write(dest/'qualification.json',{'visits':600,'contents':30,'protocols':5,
          'AnyTLS_exclusive_TCP_pair_qualification':False,'Hy2_included':False,'shared_with_TCP_joint_tables':False})


if __name__=='__main__':run()
