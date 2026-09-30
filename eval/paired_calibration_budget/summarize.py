"""Content-cluster statistics: repetitions, rotations and seeds are not independent N."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'src'))
from proxy_analysis.calibration_budget.common import *

KEY=['protocol','k','rotation','seed','arm']
METRICS=['F1','BA','CE_bits','Brier']

def measures(cm,ce,br):
    tp=np.diagonal(cm,axis1=-2,axis2=-1);support=cm.sum(-1);predicted=cm.sum(-2)
    f1=np.divide(2*tp,support+predicted,out=np.zeros_like(tp,dtype=float),where=(support+predicted)>0).mean(-1)
    ba=np.divide(tp,support,out=np.zeros_like(tp,dtype=float),where=support>0).mean(-1)
    count=cm.sum((-2,-1));return np.stack([f1,ba,ce/count,br/count],-1)

def main():
    assert sha(OUT/'scored-predictions.parquet')==read(OUT/'scoring-seal.json')['scored_hash']
    p=pd.read_parquet(OUT/'scored-predictions.parquet');contents=sorted(p.content_id.unique());assert len(contents)==30
    content_index={c:i for i,c in enumerate(contents)};keys=[];cms=[];ces=[];brs=[];recalls=[]
    for key,g in p.groupby(KEY,sort=True):
        assert len(g)==120 and g.session_id.nunique()==120 and g.content_id.nunique()==30
        cm=np.zeros((30,6,6));ce=np.zeros(30);br=np.zeros(30)
        for content,h in g.groupby('content_id'):
            ci=content_index[content];assert len(h)==4
            prob=h[[f'p{i}' for i in range(6)]].to_numpy();y=h.target.to_numpy(int);pred=h.prediction.to_numpy(int)
            np.add.at(cm[ci],(y,pred),1)
            ce[ci]=-np.log2(np.maximum(prob[np.arange(4),y],1e-30)).sum()
            br[ci]=np.square(prob-np.eye(6)[y]).sum()
        keys.append(key);cms.append(cm);ces.append(ce);brs.append(br)
        for label,h in g.groupby('label_id'):
            recalls.append({**dict(zip(KEY,key)),'label_id':label,'recall':float((h.target==h.prediction).mean())})
    cms=np.stack(cms);ces=np.stack(ces);brs=np.stack(brs)
    vals=measures(cms.sum(1),ces.sum(1),brs.sum(1));keyframe=pd.DataFrame(keys,columns=KEY)
    metrics=pd.concat([keyframe,pd.DataFrame(vals,columns=METRICS)],axis=1);save('metrics-seed-rotation',metrics)
    group=['protocol','k','arm'];summary=metrics.groupby(group)[METRICS].mean().reset_index();save('metrics-summary',summary)
    seed=metrics.groupby(group+['seed'])[METRICS].mean().reset_index();save('metrics-by-seed',seed)
    rotation=metrics.groupby(group+['rotation'])[METRICS].mean().reset_index();save('metrics-by-rotation',rotation)
    save('business-recall',recalls);recall=pd.DataFrame(recalls).groupby(group+['label_id']).recall.mean().reset_index();save('business-recall-summary',recall)
    # Same stratified content draw is shared by all deployment/budget/model cells.
    rng=np.random.default_rng(20260928);labelmap=p[['content_id','label_id']].drop_duplicates();assert len(labelmap)==30
    weights=np.zeros((2000,30),int)
    for _,g in labelmap.groupby('label_id'):
        ids=np.array([content_index[c] for c in sorted(g.content_id)]);assert len(ids)==5
        draws=rng.choice(ids,(2000,5),replace=True)
        for r in range(2000):np.add.at(weights[r],draws[r],1)
    boot=[]
    for start in range(0,2000,50):
        w=weights[start:start+50]
        cm=np.einsum('bc,mcij->bmij',w,cms,optimize=True)
        ce=np.einsum('bc,mc->bm',w,ces,optimize=True);br=np.einsum('bc,mc->bm',w,brs,optimize=True)
        boot.append(measures(cm,ce,br))
    boot=np.concatenate(boot);np.savez_compressed(OUT/'bootstrap-content-draws.npz',weights=weights,contents=np.array(contents))
    contrasts=[];drawrows=[]
    for dep in sorted(p.protocol.unique()):
      for k in [1,2,3]:
        sel=(keyframe.protocol==dep)&(keyframe.k==k)
        b4=sel&(keyframe.arm=='B4');point4=vals[b4].mean(0);draw4=boot[:,b4].mean(1)
        for ref in ['B0','B1','B2','B3','B5']:
            mask=sel&(keyframe.arm==ref);delta=point4-vals[mask].mean(0);bd=draw4-boot[:,mask].mean(1)
            for j,m in enumerate(METRICS):
                lo,hi=np.quantile(bd[:,j],[.025,.975]);contrasts.append({'protocol':dep,'k':k,'contrast':'B4-'+ref,'metric':m,
                    'delta':delta[j],'low':lo,'high':hi,'positive_favors_B4':m in ['F1','BA']})
            drawrows.extend({'protocol':dep,'k':k,'contrast':'B4-'+ref,'draw':i,**dict(zip(METRICS,v))} for i,v in enumerate(bd))
    contrast=save('contrasts',contrasts);save('bootstrap-contrasts',drawrows)
    errors=[]
    ids=['protocol','k','rotation','seed','session_id','content_id','label_id']
    a=p[p.arm=='B4'][ids+['prediction','target']]
    for ref in ['B0','B1','B2','B3','B5']:
        b=p[p.arm==ref][ids+['prediction']];g=a.merge(b,on=ids,suffixes=('_B4','_ref'),validate='one_to_one')
        g['contrast']='B4-'+ref;g['repaired']=(g.prediction_B4==g.target)&(g.prediction_ref!=g.target)
        g['introduced']=(g.prediction_B4!=g.target)&(g.prediction_ref==g.target)
        g['changed']=g.prediction_B4!=g.prediction_ref;errors.append(g)
    errors=save('error-change-ledger',pd.concat(errors))
    changes=errors.groupby(['protocol','k','contrast','rotation','seed'])[['repaired','introduced','changed']].sum().reset_index()
    save('error-change-counts',changes)
    figures(summary,rotation)
    # Include full tables in a separate appendix, without discarding poor cells.
    appendix='# 配对预算：完整统计表\n\n指标先汇总五折OOF，再平均seed/轮换；没有概率集成。CE为bits，Brier为六类概率平方误差之和。\n\n'
    for title,df in [('36格均值',summary),('逐seed（平均轮换）',seed),('逐轮换（平均seed）',rotation),('业务召回',recall),('B4主对照与95%内容bootstrap区间',contrast),('修复/新增错误（平均seed/轮换的访问数）',changes.groupby(['protocol','k','contrast'])[['repaired','introduced','changed']].mean().reset_index())]:
        appendix+='## '+title+'\n\n'+table(df)+'\n\n'
    (DOC/'business-budget-results.md').write_text(appendix,encoding='utf-8')
    write(OUT/'statistics-complete.json',{'passed':True,'bootstrap_draws':2000,'unique_contents':30,'unique_visits':240,'oof_rows':51840,
        'model_cells':432,'averaging':'metrics across rotations/seeds, not probability ensembling','bootstrap':'stratified shared content clusters conditional on frozen models and C sets',
        'scoring_seal':sha(OUT/'scoring-seal.json'),'script_hash':sha(__file__)})
    print(table(summary),flush=True);print(table(contrast[contrast.metric.eq('F1')]),flush=True)

def figures(summary,rotation):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    dest=DOC/'figures';dest.mkdir(exist_ok=True,parents=True)
    colors=plt.get_cmap('tab10').colors
    for metric in METRICS:
        fig,axes=plt.subplots(1,2,figsize=(12,4),sharey=True)
        for ax,dep in zip(axes,sorted(summary.protocol.unique())):
            for i,(arm,g) in enumerate(summary[summary.protocol==dep].groupby('arm')):
                g=g.sort_values('k');r=rotation[(rotation.protocol==dep)&(rotation.arm==arm)].groupby('k')[metric]
                ax.plot(g.k,g[metric],marker='o',label=arm,color=colors[i]);ax.fill_between(g.k,r.min(),r.max(),alpha=.08,color=colors[i])
            ax.set_title(dep);ax.set_xticks([1,2,3],['6 / 24\n25%','12 / 48\n50%','18 / 72\n75%']);ax.set_xlabel('Calibration contents / paired visits\nshare of training contents');ax.grid(alpha=.2)
        axes[0].set_ylabel(metric);axes[1].legend(ncol=3);fig.suptitle('Fixed-budget comparison; bands: rotation-mean range (not CI)')
        fig.tight_layout();fig.savefig(dest/(metric+'-budget.png'),dpi=160);plt.close(fig)

if __name__=='__main__':main()
