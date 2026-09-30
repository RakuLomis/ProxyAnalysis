"""Independent scoring after both permission regimes seal post-only predictions."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'src'))
from experiment import *
SOURCE=OUT
KEY=['protocol','business_group','rotation','seed','arm']
METRICS=['F1_new','F1_all','BA_all','CE_all_bits','Brier_all','CE_new_bits','Brier_new']

def measures(cm,ce,br,cen,brn,newmask):
    tp=np.diagonal(cm,axis1=-2,axis2=-1);support=cm.sum(-1);pred=cm.sum(-2)
    f1=np.divide(2*tp,support+pred,out=np.zeros_like(tp,dtype=float),where=(support+pred)>0)
    recall=np.divide(tp,support,out=np.zeros_like(tp,dtype=float),where=support>0)
    count=cm.sum((-2,-1));newcount=(support*newmask).sum(-1)
    return np.stack([(f1*newmask).sum(-1)/2,f1.mean(-1),recall.mean(-1),ce/count,br/count,cen/newcount,brn/newcount],-1)

def main():
    frames=[]
    for mode in ['restricted','reference']:
        seal=read(OUT/(mode+'-prediction-seal.json'));assert seal['passed'] and sha(OUT/(mode+'-predictions.parquet'))==seal['predictions_hash']
        frames.append(pd.read_parquet(OUT/(mode+'-predictions.parquet')))
    p=pd.concat(frames,ignore_index=True);labels=[]
    for folder in sorted((SOURCE/'evaluation').iterdir()):
        f=pd.read_parquet(folder/'H_labels.parquet');f['scenario']=folder.name;labels.append(f)
    p=p.merge(pd.concat(labels),on=['scenario','session_id','content_id'],validate='many_to_one');assert len(p)==126000
    classes=json.loads(p.classes_json.iloc[0]);assert p.classes_json.nunique()==1
    p['target']=p.label_id.map({c:i for i,c in enumerate(classes)});assert p.target.notna().all()
    p['prediction']=p[[f'p{i}' for i in range(5)]].to_numpy().argmax(1);save('scored-predictions',p)
    groups=read(OUT/'business-groups.json')['groups'];contents=sorted(p.content_id.unique());assert len(contents)==25;ci={c:i for i,c in enumerate(contents)}
    rows=[];cms=[];ces=[];brs=[];newm=[];cnm=[];recalls=[]
    for key,g in p.groupby(KEY,sort=True):
        assert len(g)==100 and g.session_id.nunique()==100
        cm=np.zeros((25,5,5));ce=np.zeros(25);br=np.zeros(25);mask=np.array([c in groups[key[1]] for c in classes]);cn=np.zeros(25)
        for c,h in g.groupby('content_id'):
            idx=ci[c];assert len(h)==4 and h.target.nunique()==1
            y=h.target.to_numpy(int);prob=h[[f'p{i}' for i in range(5)]].to_numpy();pred=h.prediction.to_numpy()
            np.add.at(cm[idx],(y,pred),1);ce[idx]=-np.log2(np.maximum(prob[np.arange(4),y],1e-30)).sum();br[idx]=np.square(prob-np.eye(5)[y]).sum();cn[idx]=mask[y[0]]
        whole=cm.sum(0);tp=np.diag(whole);den=whole.sum(0)+whole.sum(1)
        for j,c in enumerate(classes):recalls.append({**dict(zip(KEY,key)),'label_id':c,'is_new':bool(mask[j]),'F1':float(2*tp[j]/den[j]) if den[j] else 0.,'recall':float(tp[j]/whole[j].sum())})
        rows.append(key);cms.append(cm);ces.append(ce);brs.append(br);newm.append(mask);cnm.append(cn)
    keyframe=pd.DataFrame(rows,columns=KEY);cms=np.stack(cms);ces=np.stack(ces);brs=np.stack(brs);newm=np.stack(newm);cnm=np.stack(cnm)
    values=measures(cms.sum(1),ces.sum(1),brs.sum(1),(ces*cnm).sum(1),(brs*cnm).sum(1),newm)
    metrics=pd.concat([keyframe,pd.DataFrame(values,columns=METRICS)],axis=1);save('metrics-seed-rotation',metrics)
    summary=metrics.groupby(['protocol','arm'])[METRICS].mean().reset_index();save('metrics-summary',summary)
    grouped=metrics.groupby(['protocol','business_group','arm'])[METRICS].mean().reset_index();save('metrics-by-group',grouped)
    save('metrics-by-seed',metrics.groupby(['protocol','arm','seed'])[METRICS].mean().reset_index())
    save('metrics-by-rotation',metrics.groupby(['protocol','business_group','arm','rotation'])[METRICS].mean().reset_index())
    save('business-metrics',recalls);save('business-summary',pd.DataFrame(recalls).groupby(['protocol','business_group','arm','label_id','is_new'])[['F1','recall']].mean().reset_index())
    rng=np.random.default_rng(20260928);weights=np.zeros((10000,25),int);lab=p[['content_id','label_id']].drop_duplicates();assert len(lab)==25
    for _,g in lab.groupby('label_id'):
        ids=np.array([ci[c] for c in sorted(g.content_id)]);assert len(ids)==5;draw=rng.choice(ids,(10000,5),replace=True)
        for i in range(10000):np.add.at(weights[i],draw[i],1)
    np.savez_compressed(OUT/'bootstrap-content-draws.npz',weights=weights,contents=np.array(contents))
    contrasts=[];specs=[]
    for dep in sorted(p.protocol.unique()):
      for bg in [-1,*range(10)]:
        base=(keyframe.protocol==dep)&((keyframe.business_group==bg) if bg>=0 else True)
        for ref in ['raw','group','cyclic','center','marginal','reference']:
            ma=base&(keyframe.arm=='paired');mb=base&(keyframe.arm==ref)
            specs.append((dep,bg,ref,ma,mb));contrasts.append([])
    for start in range(0,10000,40):
        w=weights[start:start+40];cm=np.einsum('bc,mcij->bmij',w,cms,optimize=True)
        ce=w@ces.T;br=w@brs.T;cen=w@(ces*cnm).T;brn=w@(brs*cnm).T
        vals=measures(cm,ce,br,cen,brn,newm)
        for j,(_,_,_,ma,mb) in enumerate(specs):contrasts[j].append(vals[:,ma].mean(1)-vals[:,mb].mean(1))
    table_rows=[];boot_rows=[]
    for spec,parts in zip(specs,contrasts):
        dep,bg,ref,ma,mb=spec;v=np.concatenate(parts);point=values[ma].mean(0)-values[mb].mean(0)
        for j,m in enumerate(METRICS):
            lo,hi=np.quantile(v[:,j],[.025,.975]);family=2 if bg==-1 else 20
            adjlo,adjhi=np.quantile(v[:,j],[.05/(2*family),1-.05/(2*family)])
            table_rows.append({'protocol':dep,'business_group':bg,'contrast':'paired-'+ref,'metric':m,'delta':point[j],'low95':lo,'high95':hi,
                'adjusted_low':adjlo,'adjusted_high':adjhi,'family_size':family,'primary':bg==-1 and ref in ['raw','group'] and m=='F1_new'})
        boot_rows.extend({'protocol':dep,'business_group':bg,'contrast':'paired-'+ref,'draw':i,**dict(zip(METRICS,vv))} for i,vv in enumerate(v))
    c=save('contrasts',table_rows);save('bootstrap-contrasts',boot_rows)
    # Paired decisions and error changes retain every visit, not just net changes.
    ids=['scenario','protocol','business_group','rotation','seed','session_id','content_id','label_id','target'];a=p[p.arm=='paired'][ids+['prediction']];errors=[]
    for ref in ['raw','group','cyclic','center','marginal','reference']:
        g=a.merge(p[p.arm==ref][ids+['prediction']],on=ids,suffixes=('_paired','_ref'),validate='one_to_one');g['contrast']='paired-'+ref
        g['is_new']=[l in groups[bg] for l,bg in zip(g.label_id,g.business_group)]
        g['repaired']=(g.prediction_paired==g.target)&(g.prediction_ref!=g.target);g['introduced']=(g.prediction_paired!=g.target)&(g.prediction_ref==g.target);g['changed']=g.prediction_paired!=g.prediction_ref;errors.append(g)
    errors=save('error-ledger',pd.concat(errors));counts=errors.groupby(['protocol','business_group','rotation','seed','contrast','is_new'])[['repaired','introduced','changed']].sum().reset_index();save('error-counts',counts)
    appendix='# 可行摘要增广：完整统计表\n\nF1_new从完整五类混淆矩阵取目标两类F1均值；先计算各OOF指标，再平均组/轮换/seed，没有概率集成。\n\n'
    for title,df in [('总体',summary),('业务组',grouped),('全部对照区间',c),('逐seed',pd.read_parquet(OUT/'metrics-by-seed.parquet')),('逐轮换',pd.read_parquet(OUT/'metrics-by-rotation.parquet')),('业务',pd.read_parquet(OUT/'business-summary.parquet'))]:appendix+='## '+title+'\n\n'+table(df)+'\n\n'
    (DOC/'results-tables.md').write_text(appendix,encoding='utf-8')
    write(OUT/'statistics-complete.json',{'passed':True,'rows':len(p),'cells':len(metrics),'bootstrap_draws':10000,'primary_family_size':2,'unique_contents':25,'unique_visits':100,
        'script_hash':sha(__file__),'scored_hash':sha(OUT/'scored-predictions.parquet'),'conditional_on_frozen_models_and_calibration_sets':True})
    print(table(summary),flush=True);print(table(c[c.primary]),flush=True)

if __name__=='__main__':main()
