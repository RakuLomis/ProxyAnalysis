"""CUDA group-objective and ordering acceptance tests, training data only."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'src'))
from proxy_analysis.cross_business_calibration.common import *
from proxy_analysis.cross_business_calibration.group import GroupRidge,fit_group,canonical,torch,device

def main():
    folder=sorted((OUT/'bundles/group').iterdir())[0];bundle=Bundle(folder,'group')
    pre,post=canonical(bundle.get('G_pre'),bundle.get('G_post'));m,pool,audit=fit_group(pre,post)
    other,opool,_=fit_group(pre.sample(frac=1,random_state=21),post.sample(frac=1,random_state=77))
    torch.testing.assert_close(m.weight,other.weight,atol=0,rtol=0);pd.testing.assert_frame_equal(pool,opool)
    xraw=[];targets=[]
    for c,pa in pre.groupby('content_id'):
        pb=post[post.content_id==c]
        for _,a in pa.iterrows():
            for _,b in pb.iterrows():
                xraw.append(a[NUMERIC].to_numpy(float));targets.append(b[FEATURES].to_numpy(float))
    q=torch.tensor(np.log1p(np.stack(xraw)),device=device(),dtype=torch.float64)
    b=torch.tensor(np.log1p(np.stack(targets)),device=device(),dtype=torch.float64)
    x=torch.cat([(q-m.mean)/m.scale,torch.ones((96,1),device=device(),dtype=q.dtype)],1)
    y=(b-q[:,:6])/m.scale[:6];penalty=torch.eye(8,device=device(),dtype=q.dtype);penalty[-1,-1]=0
    expanded=torch.linalg.solve(x.T@x/96+penalty,x.T@y/96)
    torch.testing.assert_close(expanded,m.weight,rtol=1e-10,atol=1e-10)
    # Compare objective gradients at an arbitrary parameter, not just at the fitted solution.
    probe=m.weight.detach().clone().requires_grad_(True)
    le=((x@probe-y)**2).sum(1).mean()+probe[:-1].square().sum();ge=torch.autograd.grad(le,probe)[0]
    q0=torch.tensor(np.log1p(pre[NUMERIC].to_numpy(float)),device=device(),dtype=torch.float64)
    x0=torch.cat([(q0-m.mean)/m.scale,torch.ones((24,1),device=device(),dtype=q.dtype)],1)
    means={c:np.log1p(g[FEATURES].to_numpy(float)).mean(0) for c,g in post.groupby('content_id')}
    y0=(torch.tensor(np.stack([means[c] for c in pre.content_id]),device=device())-q0[:,:6])/m.scale[:6]
    lc=((x0@probe-y0)**2).sum(1).mean()+probe[:-1].square().sum();gc=torch.autograd.grad(lc,probe)[0]
    torch.testing.assert_close(ge,gc,rtol=1e-10,atol=1e-10)
    # Canonical ordering gives exactly repeatable samples under independent within-group permutation.
    query=bundle.get('U_pre');p=m.predict(query[FEATURES].to_numpy(float),query.F.to_numpy(float));op=other.predict(query[FEATURES].to_numpy(float),query.F.to_numpy(float))
    np.testing.assert_array_equal(p,op)
    for seed in config()['seeds']:
        ids=np.random.default_rng(seed).integers(0,len(pool),100)
        np.testing.assert_array_equal(p[:1]+pool.iloc[ids][['residual_'+k for k in FEATURES]].to_numpy(),op[:1]+opool.iloc[ids][['residual_'+k for k in FEATURES]].to_numpy())
    assert len(pool)==96 and all(len(r['fit_contents'])==5 and r['held_content'] not in r['fit_contents'] for r in audit)
    result={'passed':True,'cuda':True,'expanded_rows':96,'original_pre_rows':24,'group_residuals':96,
        'max_solution_difference':float((expanded-m.weight).abs().max()),'max_gradient_difference':float((ge-gc).abs().max()),
        'permutation_invariant':True,'generated_log_samples_invariant':True,'test_data_read':False}
    write(OUT/'group-engineering.json',result)
    files=[*Path(ROOT/'src/proxy_analysis/cross_business_calibration').glob('*.py'),*Path(__file__).parent.glob('*.py'),
        ROOT/'src/proxy_analysis/conditional_drift/model.py',ROOT/'src/proxy_analysis/conditional_drift/common.py',CONFIG,
        *list((OUT/'bundles').glob('*/*/manifest.json'))]
    contract={'files':{str(p):sha(p) for p in files},'export_contract':sha(OUT/'contract.json'),'CUDA':True}
    if (OUT/'worker-contract.json').exists():assert read(OUT/'worker-contract.json')==contract
    else:write(OUT/'worker-contract.json',contract)
    print(result,flush=True)

if __name__=='__main__':main()
