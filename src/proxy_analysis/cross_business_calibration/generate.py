"""Separate paired/group worker invocations; labels only used in later gate reporting."""
import time
from .common import *
from ..conditional_drift.model import fit_pool,decode,device,torch
from ..conditional_drift.common import illegal

def run_one(folder,kind):
    bundle=Bundle(folder,kind);meta=bundle.manifest;name=meta['scenario'];dest=OUT/'generation'/kind/name;dest.mkdir(parents=True,exist_ok=True)
    if (dest/'complete.json').exists():
        old=read(dest/'complete.json');assert old['bundle_hash']==sha(folder/'manifest.json')
        for p,h in old['files'].items():assert sha(p)==h
        return
    started=time.perf_counter();query=bundle.get('U_pre');models={};pools={};audits={}
    if kind=='paired':
        pre=bundle.get('C_pre');post=bundle.get('C_post')
        train=pre.merge(post,on=IDENTITY+['F'],suffixes=('_pre','_post'),validate='one_to_one');assert 'label_id' not in train
        for arm,wrong in [('X4',False),('X5',True)]:models[arm],pools[arm],audits[arm]=fit_pool(train,wrong)
        arms=['X2','X3','X4','X5'];basis=models['X4']
    else:
        from .group import fit_group,canonical
        pre,post=canonical(bundle.get('G_pre'),bundle.get('G_post'))
        models['X6'],pools['X6'],audits['X6']=fit_group(pre,post);basis=models['X6'];arms=['X6']
    assert set(pre.content_id)==set(meta['C_contents']) and not set(query.content_id)&set(pre.content_id)
    for arm,rows in audits.items():
        for r in rows:assert r['held_content'] not in r['fit_contents'] and set(r['fit_contents'])==set(meta['C_contents'])-{r['held_content']}
        pools[arm].to_parquet(dest/(arm+'-pool.parquet'),index=False)
    write(dest/'loco-audit.json',audits);torch.save({arm:m.state() for arm,m in models.items()},dest/'models.pt')
    a=query[FEATURES].to_numpy(float);F=query.F.to_numpy(float);pred={arm:m.predict(a,F) for arm,m in models.items()}
    mean=basis.mean.cpu().numpy();scale=basis.scale.cpu().numpy()
    source=(np.log1p(pre[NUMERIC].to_numpy(float))-mean)/scale;q=(np.log1p(query[NUMERIC].to_numpy(float))-mean)/scale
    contents=sorted(pre.content_id.unique());centroids=np.stack([source[pre.content_id.to_numpy()==c].mean(0) for c in contents]);support=[]
    for i,r in enumerate(query.to_dict('records')):
        support.append({'session_id':r['session_id'],'content_id':r['content_id'],'scenario':name,
            'outside_C_range_dimensions':int(((q[i]<source.min(0))|(q[i]>source.max(0))).sum()),'nearest_C_centroid_distance':float(np.linalg.norm(centroids-q[i],axis=1).min())})
    pd.DataFrame(support).to_parquet(dest/'query-support.parquet',index=False)
    pool_values={arm:p[['residual_'+k for k in FEATURES]].to_numpy() for arm,p in pools.items()}
    if kind=='paired':pool_values['X3']=pools['X4'][['drift_'+k for k in FEATURES]].to_numpy()
    # Indexing of candidate contents matches the frozen implementation even when all six are candidates.
    for seed in config()['seeds']:
      rows=[]
      for i,r in enumerate(query.to_dict('records')):
        near=np.argsort(np.linalg.norm(centroids-q[i],axis=1),kind='stable')[:min(8,len(contents))]
        for view in range(8):
          for arm in arms:
            rng=np.random.default_rng(int(objhash([seed,name,r['session_id'],view])[:16],16));reasons=[];donor=None
            pool=pools['X4' if arm in ['X2','X3'] else arm]
            for attempt in range(1 if arm=='X2' else 33):
                if arm=='X2':z=np.log1p(a[i])+basis.center
                else:
                    c=contents[int(rng.choice(np.arange(len(contents)) if arm=='X3' else near))]
                    candidates=np.flatnonzero(pool.content_id.to_numpy()==c)
                    if arm=='X6':
                        # Cartesian pool is canonical r-major/s-minor. Independent uniform r,s.
                        donor=int(candidates[int(rng.integers(0,4))*4+int(rng.integers(0,4))])
                    else:donor=int(rng.choice(candidates))
                    z=(np.log1p(a[i]) if arm=='X3' else pred[arm][i])+pool_values[arm][donor]
                raw,rounded,reason=decode(z,F[i]);reasons.append(reason or 'valid')
                if attempt==0:first_raw=raw.copy();first_reason=reason
                if not reason:break
            result=a[i] if reason else rounded;assert not illegal(result,F[i]);d=None if donor is None else pool.iloc[donor]
            row={**r,'scenario':name,'fold':meta['fold'],'business_group':meta['business_group'],'rotation':meta['rotation'],'arm':arm,'seed':seed,'view':view,
                'C_hash':meta['C_hash'],'first_invalid':bool(first_reason),'first_reason':first_reason,'fallback':bool(reason),'attempts':len(reasons),
                'attempt_reasons_json':json.dumps(reasons),'donor_content':None if d is None else d.content_id,'donor_pool_index':donor}
            if d is not None:assert d.content_id in meta['C_contents']
            for j,k in enumerate(FEATURES):row[k]=int(result[j]);row['first_raw_'+k]=float(first_raw[j]);row['last_raw_'+k]=float(raw[j])
            rows.append(row)
      pd.DataFrame(rows).to_parquet(dest/f'samples-{seed}.parquet',index=False,compression='zstd')
    write(dest/'complete.json',{'scenario':name,'kind':kind,'bundle_hash':sha(folder/'manifest.json'),'cuda':True,'ridge_fits':7*len(models),
        'seconds':time.perf_counter()-started,'read_roles':bundle.access,'files':{str(p):sha(p) for p in dest.iterdir() if p.is_file()}})

def run(kind):
    assert read(OUT/'permission-gate.json')['passed'] and read(OUT/'group-engineering.json')['passed'];device()
    contract=read(OUT/'worker-contract.json')
    for p,h in contract['files'].items():assert sha(p)==h
    for i,path in enumerate(sorted((OUT/'bundles'/kind).iterdir())):
        run_one(path,kind);write(OUT/(kind+'-progress.json'),{'completed':i+1,'total':240,'classifiers_started':False})
        if (i+1)%10==0:print(kind,i+1,'/240',flush=True)

def gate():
    roles=pd.read_parquet(OUT/'roles.parquet');roles=roles[roles.role=='U'][['scenario','session_id','label_id','business_role']]
    frames=[];audit=[]
    for kind in ['paired','group']:
      folders=sorted((OUT/'generation'/kind).iterdir());assert len(folders)==240
      for folder in folders:
        done=read(folder/'complete.json');assert done['cuda']
        for path,h in done['files'].items():assert sha(path)==h
        assert set(done['read_roles'])==({'C_pre','C_post','U_pre'} if kind=='paired' else {'G_pre','G_post','U_pre'})
        audit.append({'scenario':folder.name,'kind':kind,'ridge_fits':done['ridge_fits'],'cuda':True,'seconds':done['seconds']})
        for path in sorted(folder.glob('samples-*.parquet')):
            f=pd.read_parquet(path);assert 'label_id' not in f
            frames.append(f.merge(roles,on=['scenario','session_id'],validate='many_to_one'))
    x=pd.concat(frames,ignore_index=True);assert len(x)==2073600
    assert not x.duplicated(['scenario','seed','arm','session_id','view']).any()
    save('generation-audit',audit)
    keys=['protocol','business_group','arm','business_role']
    summary=x.groupby(keys).agg(views=('session_id','size'),first_invalid_rate=('first_invalid','mean'),fallback_rate=('fallback','mean')).reset_index()
    summary['passed']=(summary.first_invalid_rate<=.1)&(summary.fallback_rate<=.01);save('legality-summary',summary)
    save('legality-by-scenario',x.groupby(['scenario','arm','seed','business_role']).agg(first_invalid_rate=('first_invalid','mean'),fallback_rate=('fallback','mean')).reset_index())
    save('legality-by-business',x.groupby(['protocol','business_group','arm','label_id']).agg(first_invalid_rate=('first_invalid','mean'),fallback_rate=('fallback','mean')).reset_index())
    save('first-invalid-reasons',x[x.first_invalid].groupby(keys+['first_reason']).size().rename('views').reset_index())
    passed=bool(summary.passed.all());write(OUT/'generation-gate.json',{'passed':passed,'generated_views':len(x),'classifiers_started':False,'failed':summary[~summary.passed].to_dict('records')})
    (DOC/'generation-legality.md').write_text('# XBC3–XBC5 生成合法性\n\n'+table(summary)+'\n\n门限：首次非法≤10%、回退≤1%，按部署/未覆盖业务组/臂/new或cal分别判断。必要数值约束不是协议合法性证明。\n\n'+('全部通过。' if passed else '**阶段门失败，停止正式分类，不调整阈值或删除困难设置。**')+'\n',encoding='utf-8')
    print(table(summary[~summary.passed] if not passed else summary),flush=True)
    if not passed:raise StageGate('XBC5 failed; user decision required before classification')
