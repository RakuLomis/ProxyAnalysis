"""Worker reads ONLY scenario training bundles. Never imports trusted exporter."""
import time
from .common import *
from ..conditional_drift.model import fit_pool,decode,device,torch
from ..conditional_drift.common import illegal

def run_scenario(folder):
    bundle=TrainingBundle(folder);meta=bundle.manifest;name=meta['scenario'];dest=OUT/'generation'/name;dest.mkdir(parents=True,exist_ok=True)
    if (dest/'complete.json').exists():
        old=read(dest/'complete.json');assert old['bundle_hash']==sha(Path(folder)/'manifest.json')
        for path,h in old['files'].items():assert sha(path)==h
        return
    pre=bundle.get('C_pre');post=bundle.get('C_post');query=bundle.get('U_pre')
    assert set(pre.session_id)==set(meta['C_sessions'])==set(post.session_id)
    assert set(query.session_id)==set(meta['U_sessions']) and not set(pre.content_id)&set(query.content_id)
    keys=IDENTITY+['F'];train=pre.merge(post,on=keys,suffixes=('_pre','_post'),validate='one_to_one')
    assert 'label_id' not in train and 'label_id' not in query
    started=time.perf_counter();models={};pools={};audits={}
    for kind,wrong in [('true',False),('wrong',True)]:models[kind],pools[kind],audits[kind]=fit_pool(train,wrong)
    for kind,rows in audits.items():
        for row in rows:assert row['held_content'] not in row['fit_contents'] and set(row['fit_contents']).issubset(set(meta['C_contents']))
    torch.save({kind:m.state() for kind,m in models.items()},dest/'centers.pt')
    for kind,p in pools.items():p.to_parquet(dest/(kind+'-pool.parquet'),index=False)
    write(dest/'residual-folds.json',audits)
    a=query[FEATURES].to_numpy(float);F=query.F.to_numpy(float);true=models['true']
    means={kind:m.predict(a,F) for kind,m in models.items()}
    center=true.center;mean=true.mean.cpu().numpy();scale=true.scale.cpu().numpy()
    source=(np.log1p(pre[NUMERIC].to_numpy(float))-mean)/scale;qc=(np.log1p(query[NUMERIC].to_numpy(float))-mean)/scale
    assert pre.session_id.tolist()==train.session_id.tolist()
    contents=sorted(pre.content_id.unique());indices={c:np.flatnonzero(pre.content_id.to_numpy()==c) for c in contents}
    centroids=np.stack([source[indices[c]].mean(0) for c in contents])
    values={'B3':pools['true'][['drift_'+k for k in FEATURES]].to_numpy(),
            'B4':pools['true'][['residual_'+k for k in FEATURES]].to_numpy(),
            'B5':pools['wrong'][['residual_'+k for k in FEATURES]].to_numpy()}
    for seed in config()['seeds']:
      rows=[]
      for i,r in enumerate(query.to_dict('records')):
        distances=np.linalg.norm(centroids-qc[i],axis=1);near=np.argsort(distances,kind='stable')[:min(8,len(contents))]
        for view in range(8):
          for arm in ['B2','B3','B4','B5']:
            rng=np.random.default_rng(int(objhash([seed,name,r['session_id'],view])[:16],16));donor=None;reasons=[]
            for attempt in range(1 if arm=='B2' else 33):
                if arm=='B2':z=np.log1p(a[i])+center
                else:
                    c=int(rng.choice(np.arange(len(contents)) if arm=='B3' else near));donor=int(rng.choice(indices[contents[c]]))
                    base=np.log1p(a[i]) if arm=='B3' else means['wrong' if arm=='B5' else 'true'][i]
                    z=base+values[arm][donor]
                raw,rounded,reason=decode(z,F[i]);reasons.append(reason or 'valid')
                if attempt==0:first_raw=raw.copy();first_reason=reason
                if not reason:break
            result=a[i] if reason else rounded;assert not illegal(result,F[i])
            pool=pools['wrong' if arm=='B5' else 'true'];d=None if donor is None else pool.iloc[donor]
            row={**r,'scenario':name,'fold':meta['fold'],'k':meta['k'],'rotation':meta['rotation'],'arm':arm,'seed':seed,'view':view,
                'C_hash':meta['C_hash'],'first_invalid':bool(first_reason),'first_reason':first_reason,'fallback':bool(reason),'attempts':len(reasons),
                'attempt_reasons_json':json.dumps(reasons),'donor_session':None if d is None else d.session_id,
                'donor_content':None if d is None else d.content_id,'target_donor_session':None if d is None else d.target_session_id}
            if d is not None:assert d.session_id in meta['C_sessions'] and d.content_id not in meta['U_contents']
            for j,k in enumerate(FEATURES):row[k]=int(result[j]);row['first_raw_'+k]=float(first_raw[j]);row['last_raw_'+k]=float(raw[j])
            rows.append(row)
      pd.DataFrame(rows).to_parquet(dest/f'samples-{seed}.parquet',index=False,compression='zstd')
    assert set(bundle.access)=={'C_pre','C_post','U_pre'}
    write(dest/'complete.json',{'scenario':name,'bundle_hash':sha(Path(folder)/'manifest.json'),'C_hash':meta['C_hash'],
        'seconds':time.perf_counter()-started,'cuda':True,'ridge_fits':2*(len(contents)+1),'read_roles':bundle.access,
        'files':{str(p):sha(p) for p in dest.iterdir() if p.is_file()}})
    print(name,'generated',flush=True)

def gate():
    files=sorted((OUT/'generation').glob('*/samples-*.parquet'));assert len(files)==360
    frames=[pd.read_parquet(p) for p in files];x=save('generated-U',pd.concat(frames,ignore_index=True))
    assert len(x)==552960 and not x.duplicated(['scenario','seed','arm','session_id','view']).any()
    s=save('legality-summary',x.groupby(['protocol','k','arm']).agg(source_views=('session_id','size'),first_invalid_rate=('first_invalid','mean'),fallback_rate=('fallback','mean'),mean_attempts=('attempts','mean')).reset_index())
    s['passed']=(s.first_invalid_rate<=.1)&(s.fallback_rate<=.01);save('legality-summary',s)
    save('legality-by-scenario',x.groupby(['scenario','protocol','k','rotation','seed','arm']).agg(first_invalid_rate=('first_invalid','mean'),fallback_rate=('fallback','mean')).reset_index())
    reasons=save('first-invalid-reasons',x[x.first_invalid].groupby(['protocol','k','arm','first_reason']).size().rename('source_views').reset_index())
    passed=bool(s.passed.all());write(OUT/'generation-gate.json',{'stage':'CB4','passed':passed,'classification_started':False,
        'U_post_read':False,'views':len(x),'failed':s[~s.passed].to_dict('records')})
    (DOC/'generation-legality.md').write_text('# CB3–CB4 小预算生成合法性\n\n120个scenario完成，生成器仅从其C拟合；U_pre只查询，不开放U_post或H_pre。生成、重抽及整数规则保持冻结。\n\n'+table(s)+'\n\n门限在读取结果前固定：每部署×预算×臂首次非法≤10%，fallback≤1%；不按预算合并。\n\n'+table(reasons)+'\n\n'+('全部通过，允许正式分类。' if passed else '**门限未全部通过：按计划暂停正式分类，保留全部预算和臂，不自行调参。需要用户决定下一步。**')+'\n\n视图计数不是独立内容数；同一原内容会出现在不同外折/轮换/seed中。必要摘要约束通过不代表协议或语义保真。\n',encoding='utf-8')
    print(s.to_string(index=False),flush=True)
    if not passed:raise StageGate('CB4 failed: user confirmation required before changing design or running classifiers')

def run():
    assert read(OUT/'permission-gate.json')['passed'];device()
    for i,path in enumerate(sorted((OUT/'bundles').iterdir())):
        run_scenario(path);write(OUT/'progress.json',{'stage':'CB4','completed':i+1,'total':120,'classifiers_started':False})
    gate()
