"""Reconstruct first proposals from saved CUDA centers and frozen residual pools."""
from phase2 import *

def verify():
    paired=paired_table().set_index('session_id');checks=[]
    for task in read(OUT/'generation-tasks.json'):
        name=f"{task['protocol']}-f{task['fold']}-i{task['inner_fold']}";folder=OUT/'generation'/name
        state=torch.load(folder/'centers.pt',map_location=device(),weights_only=False)
        models={}
        for kind in ['true','wrong']:
            model=Ridge.__new__(Ridge)
            for attr in ['mean','scale','weight','center']:setattr(model,attr,state[kind][attr])
            assert model.weight.is_cuda;models[kind]=model
        train=paired.loc[task['fit_sessions']].reset_index();query=paired.loc[task['query_sessions']].reset_index()
        a=query[[k+'_pre' for k in FEATURES]].to_numpy(float);F=query.F.to_numpy(float)
        centers={k:m.predict(a,F) for k,m in models.items()};true=models['true']
        mean=true.mean.cpu().numpy();scale=true.scale.cpu().numpy()
        coords=(np.log1p(train[[k+'_pre' for k in FEATURES]+['F']].to_numpy(float))-mean)/scale
        qc=(np.log1p(np.column_stack([a,F]))-mean)/scale
        contents=sorted(train.content_id.unique());ix={c:np.flatnonzero(train.content_id.to_numpy()==c) for c in contents};centroids=np.stack([coords[ix[c]].mean(0) for c in contents])
        pools={kind:pd.read_parquet(folder/(kind+'-pool.parquet')) for kind in ['true','wrong']}
        seed=config()['seeds'][0];actual=pd.read_parquet(folder/f'generated-{seed}.parquet');actual=actual[actual.view==0].set_index(['session_id','arm'])
        maxdiff=0.
        for i,r in enumerate(query.to_dict('records')):
            near=np.argsort(np.linalg.norm(centroids-qc[i],axis=1),kind='stable')[:8]
            for arm in ['T1','T2','T3','T4','T5']:
                rng=np.random.default_rng(int(object_hash([seed,name,r['session_id'],0])[:16],16))
                if arm=='T1':z=np.log1p(a[i])+true.center
                elif arm=='T3':z=centers['true'][i]
                else:
                    k=int(rng.choice(np.arange(len(contents)) if arm=='T2' else near));donor=int(rng.choice(ix[contents[k]]))
                    pool=pools['wrong' if arm=='T5' else 'true'];cols=[('drift_' if arm=='T2' else 'residual_')+f for f in FEATURES]
                    base=np.log1p(a[i]) if arm=='T2' else centers['wrong' if arm=='T5' else 'true'][i]
                    z=base+pool.iloc[donor][cols].to_numpy(float)
                raw,_,_=decode(z,F[i]);expected=actual.loc[(r['session_id'],arm),['first_raw_'+k for k in FEATURES]].to_numpy(float)
                np.testing.assert_allclose(raw,expected,atol=1e-7,rtol=1e-12);maxdiff=max(maxdiff,float(np.abs(raw-expected).max()))
        checks.append({'task':name,'proposals_replayed':120,'cuda':True,'max_raw_difference':maxdiff})
    save('generator-replay-audit',pd.DataFrame(checks));js('generator-replay-audit.json',{'tasks':40,'first_proposals':4800,'all_passed':True,'cuda':True,'max_raw_difference':max(r['max_raw_difference'] for r in checks)})
    print(read(OUT/'generator-replay-audit.json'),flush=True)

if __name__=='__main__':verify()
