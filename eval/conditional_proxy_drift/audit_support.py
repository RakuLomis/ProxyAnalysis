"""Descriptive support ranges and generated-view legality, no model adaptation."""
from phase2 import *

def audit():
    paired=paired_table().set_index('session_id');folds=load('outer-folds');rows=[]
    for dep in config()['deployments']:
      for fold in range(5):
        f=folds[(folds.protocol==dep)&(folds.fold==fold)]
        a=paired.loc[f[f.split=='train'].session_id];q=paired.loc[f[f.split=='test'].session_id]
        cols=[k+'_pre' for k in FEATURES]+['F'];lo=a[cols].min().to_numpy();hi=a[cols].max().to_numpy()
        for sid,r in q.iterrows():
            x=r[cols].to_numpy(float);outside=(x<lo)|(x>hi)
            rows.append({'protocol':dep,'outer_fold':fold,'session_id':sid,'content_id':r.content_id,
               'outside_axis_aligned_train_range':bool(outside.any()),'outside_dimensions':int(outside.sum()),
               'outside_features_json':json.dumps([c for c,v in zip(cols,outside) if v])})
    support=save('test-source-support',pd.DataFrame(rows));assert len(support)==240
    quality=load('quality-energy-per-visit').merge(support,on=['protocol','outer_fold','session_id','content_id'],validate='many_to_one')
    save('quality-by-source-support',quality.groupby(['protocol','arm','outside_axis_aligned_train_range']).agg(energy_score=('energy_score','mean'),seed_visits=('session_id','size'),distinct_visits=('session_id','nunique')).reset_index())
    stats=[]
    for name in ['training-oof-synthetic','test-synthetic-offline']:
        x=load(name);invalid=0
        for r in x[FEATURES+['F']].itertuples(index=False,name=None):invalid+=bool(illegal(r[:6],r[6]))
        assert invalid==0
        stats.append({'table':name,'rows':len(x),'final_invalid':invalid,'fallback':int(x.fallback.sum())})
    js('support-and-decoding-audit.json',{'passed':True,'tables':stats,'range_is_not_joint_support_proof':True})
    with (DOC/'generation-quality-report.md').open('a',encoding='utf-8') as f:
        f.write('\n\n## 源条件外推范围\n\n'+table(support.groupby('protocol').agg(visits=('session_id','size'),outside_axis_aligned_train_range=('outside_axis_aligned_train_range','sum')).reset_index())+'\n\n此处只检查入口七维是否越出训练逐维min/max范围，不证明联合支持重叠。样本未删除；按范围内/外的energy分层见quality-by-source-support.parquet。全部最终生成值经必要摘要约束复核，但这不证明能构造合法PCAP。\n')
    print(stats,flush=True)

if __name__=='__main__':audit()
