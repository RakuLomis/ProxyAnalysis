"""Full-six-class endpoints, content-cluster bootstrap; never used for selection."""
from formal_common import *
KEY=['track','protocol','business_group','rotation','seed','arm']
METRICS=['F1_new','F1_all','BA_all','CE_all_bits','Brier_all','CE_new_bits','Brier_new']

def measures(cm,ce,br,cen,brn,mask):
    tp=np.diagonal(cm,axis1=-2,axis2=-1);support=cm.sum(-1);pred=cm.sum(-2)
    f1=np.divide(2*tp,support+pred,out=np.zeros_like(tp,dtype=float),where=(support+pred)>0)
    recall=np.divide(tp,support,out=np.zeros_like(tp,dtype=float),where=support>0)
    count=cm.sum((-2,-1));newcount=(support*mask).sum(-1)
    return np.stack([(f1*mask).sum(-1)/2,f1.mean(-1),recall.mean(-1),ce/count,br/count,cen/newcount,brn/newcount],-1)

def save(name,f):
    f=f if isinstance(f,pd.DataFrame) else pd.DataFrame(f);f.to_parquet(OUT/(name+'.parquet'),index=False);return f

def main():
    freeze();frames=[]
    for mode in ['restricted','reference']:
        seal=read(OUT/(mode+'-prediction-seal.json'));assert seal['passed'] and sha(OUT/(mode+'-predictions.parquet'))==seal['predictions_hash']
        frames.append(pd.read_parquet(OUT/(mode+'-predictions.parquet')))
    labels=[]
    for folder in folders():
        f=later_package(folder.name,'scoring','H_labels');f['scenario']=folder.name;labels.append(f)
    p=pd.concat(frames).merge(pd.concat(labels),on=['scenario','session_id'],validate='many_to_one');assert len(p)==544320
    assert p.classes_json.nunique()==1;classes=json.loads(p.classes_json.iloc[0]);p['target']=p.label_id.map({c:i for i,c in enumerate(classes)});assert p.target.notna().all()
    probs=p[[f'p{i}' for i in range(6)]].to_numpy();assert np.isfinite(probs).all() and (probs>=0).all();np.testing.assert_allclose(probs.sum(1),1,atol=2e-6)
    p['prediction']=probs.argmax(1);save('scored-predictions',p)
    contents=sorted(p.content_id.unique());assert len(contents)==30;ci={c:i for i,c in enumerate(contents)}
    lab=p[['content_id','label_id']].drop_duplicates();assert len(lab)==30
    weights=np.zeros((10000,30),int);rng=np.random.default_rng(20260928)
    for _,g in lab.groupby('label_id'):
        ids=np.array([ci[c] for c in sorted(g.content_id)]);assert len(ids)==5;draw=rng.choice(ids,(10000,5),replace=True)
        for i in range(10000):np.add.at(weights[i],draw[i],1)
    np.savez_compressed(OUT/'bootstrap-content-draws.npz',weights=weights,contents=np.array(contents))
    allmetrics=[];allcontrasts=[];business=[]
    # Per deployment to bound RAM; identical content draws preserve cross-deployment dependence.
    for (track,dep),frame in p.groupby(['track','protocol']):
        keys=[];cms=[];ces=[];brs=[];masks=[];contentmasks=[]
        for key,g in frame.groupby(KEY,sort=True):
            assert len(g)==g.session_id.nunique()==120
            newclasses=set(g.loc[g.business_role=='new','label_id']);assert len(newclasses)==2
            mask=np.array([c in newclasses for c in classes]);cm=np.zeros((30,6,6));ce=np.zeros(30);br=np.zeros(30);cn=np.zeros(30)
            for c,h in g.groupby('content_id'):
                assert len(h)==4 and h.target.nunique()==1;idx=ci[c];y=h.target.to_numpy(int);prob=h[[f'p{i}' for i in range(6)]].to_numpy()
                np.add.at(cm[idx],(y,h.prediction.to_numpy()),1);ce[idx]=-np.log2(np.maximum(prob[np.arange(4),y],1e-30)).sum();br[idx]=np.square(prob-np.eye(6)[y]).sum();cn[idx]=mask[y[0]]
            whole=cm.sum(0);tp=np.diag(whole);den=whole.sum(0)+whole.sum(1)
            for j,c in enumerate(classes):business.append({**dict(zip(KEY,key)),'label_id':c,'is_new':bool(mask[j]),'F1':float(2*tp[j]/den[j]) if den[j] else 0.,'recall':float(tp[j]/whole[j].sum())})
            keys.append(key);cms.append(cm);ces.append(ce);brs.append(br);masks.append(mask);contentmasks.append(cn)
        kf=pd.DataFrame(keys,columns=KEY);cms=np.stack(cms);ces=np.stack(ces);brs=np.stack(brs);masks=np.stack(masks);cn=np.stack(contentmasks)
        values=measures(cms.sum(1),ces.sum(1),brs.sum(1),(ces*cn).sum(1),(brs*cn).sum(1),masks)
        allmetrics.append(pd.concat([kf,pd.DataFrame(values,columns=METRICS)],axis=1));specs=[]
        for bg in [-1,0,1,2]:
            base=kf.business_group.eq(bg) if bg>=0 else np.ones(len(kf),bool)
            for ref in ['raw','group','cyclic','center','marginal','reference']:
                specs.append((bg,ref,base&kf.arm.eq('paired'),base&kf.arm.eq(ref)))
        boot=[[] for _ in specs]
        for start in range(0,10000,40):
            w=weights[start:start+40];cm=np.einsum('bc,mcij->bmij',w,cms,optimize=True)
            v=measures(cm,w@ces.T,w@brs.T,w@(ces*cn).T,w@(brs*cn).T,masks)
            for j,(_,_,ma,mb) in enumerate(specs):boot[j].append(v[:,ma].mean(1)-v[:,mb].mean(1))
        arrays={}
        for spec,parts in zip(specs,boot):
            bg,ref,ma,mb=spec;v=np.concatenate(parts);arrays[f'g{bg}_{ref}']=v;point=values[ma].mean(0)-values[mb].mean(0);family=10 if track=='W' else 8
            for j,metric in enumerate(METRICS):
                lo,hi=np.quantile(v[:,j],[.025,.975]);adjlo,adjhi=np.quantile(v[:,j],[.05/(2*family),1-.05/(2*family)])
                primary=bg==-1 and ref in ['raw','group'] and metric=='F1_new'
                allcontrasts.append(dict(track=track,protocol=dep,business_group=bg,contrast='paired-'+ref,metric=metric,delta=point[j],low95=lo,high95=hi,
                    adjusted_low=adjlo if primary else None,adjusted_high=adjhi if primary else None,family_size=family if primary else None,primary=primary))
        np.savez_compressed(OUT/f'bootstrap-contrasts-{track}-{dep}.npz',**arrays)
        print('Scored',track,dep,flush=True)
    metrics=save('metrics-seed-rotation',pd.concat(allmetrics));summary=save('metrics-summary',metrics.groupby(['track','protocol','arm'])[METRICS].mean().reset_index())
    for suffix,group in [('by-group',['track','protocol','business_group','arm']),('by-seed',['track','protocol','arm','seed']),('by-rotation',['track','protocol','business_group','arm','rotation'])]:
        save('metrics-'+suffix,metrics.groupby(group)[METRICS].mean().reset_index())
    save('business-metrics',business);contrasts=save('contrasts',allcontrasts)
    ids=['scenario','track','protocol','business_group','rotation','seed','session_id','content_id','label_id','target','business_role'];a=p[p.arm=='paired'][ids+['prediction']];errors=[]
    for ref in ['raw','group','cyclic','center','marginal','reference']:
        g=a.merge(p[p.arm==ref][ids+['prediction']],on=ids,suffixes=('_paired','_ref'),validate='one_to_one');g['contrast']='paired-'+ref
        g['repaired']=(g.prediction_paired==g.target)&(g.prediction_ref!=g.target);g['introduced']=(g.prediction_paired!=g.target)&(g.prediction_ref==g.target);g['changed']=g.prediction_paired!=g.prediction_ref;errors.append(g)
    e=save('error-ledger',pd.concat(errors));save('error-counts',e.groupby(['track','protocol','business_group','rotation','seed','contrast','business_role'])[['repaired','introduced','changed']].sum().reset_index())
    doc=ROOT/'docs/extend-calibration-20260930';doc.mkdir(exist_ok=True)
    text='# Extend v3 正式实验结果表\n\n全部使用 CUDA 拟合和推理。W 五部署主分析、T 四部署次分析；Hy2 未进入分类。\n\n'
    text+='F1_new 从完整六类混淆矩阵取两类均值，先汇合五折 OOF，再平均业务组、轮换与种子；不集成概率。\n\n'
    text+='区间为固定模型条件下的业务分层、内容簇 bootstrap（10000 次）；不是外部验证。主比较 W 家族 10 项，T 家族 8 项，分别校正；两项下界均大于零才通过对应部署双增量判据。\n\n'
    for title,f in [('总体',summary),('预定主对比',contrasts[contrasts.primary]),('逐 seed',pd.read_parquet(OUT/'metrics-by-seed.parquet')),('业务组',pd.read_parquet(OUT/'metrics-by-group.parquet'))]:
        text+='## '+title+'\n\n'+f.to_markdown(index=False,floatfmt='.6f')+'\n\n'
    (doc/'formal-v3-results.md').write_text(text,encoding='utf-8')
    write(OUT/'statistics-complete.json',{'passed':True,'rows':len(p),'bootstrap_draws':10000,'W_family':10,'T_family':8,'conditional_on_frozen_models':True,
        'scored_hash':sha(OUT/'scored-predictions.parquet'),'script_hash':sha(__file__)})
    print(contrasts[contrasts.primary].to_string(index=False),flush=True)

if __name__=='__main__':main()
