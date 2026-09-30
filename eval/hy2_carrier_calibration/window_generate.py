"""Separate paired/group CUDA generation workers; no evaluation input access."""
import argparse
from window_model import *

def engineering():
    folder=sorted((OUT/'bundles/paired').iterdir())[0];b=Bundle(folder,'paired');a=b.get('C_pre');post=b.get('C_post')
    x=np.vstack([a[FEATURES],post[FEATURES],[[1,0,1,0,1,0],[0,65527,0,1,0,1],[65527,65527,1,1,1,1]]])
    y,_=decode(encode(x));assert np.array_equal(y.cpu().numpy(),x)
    rng=np.random.default_rng(20260928);z=rng.normal(0,3,(5000,6));out,_=decode(z);validate(out)
    assert np.array_equal(decode(encode(out))[0].cpu().numpy(),out.cpu().numpy())
    for val in [float('inf'),float('nan'),1000.]:
        bad=np.zeros((1,6));bad[0,0]=val
        try:decode(bad)
        except FloatingPointError:pass
        else:raise AssertionError('overflow accepted')
    gb=Bundle(OUT/'bundles/group'/folder.name,'group');ga=gb.get('C_pre');gp=gb.get('C_post')
    m,r,_,_,_=fit(ga,gp,'group');m2,r2,_,_,_=fit(ga.sample(frac=1,random_state=1),gp.sample(frac=1,random_state=2),'group')
    torch.testing.assert_close(m.weight,m2.weight,rtol=0,atol=0);torch.testing.assert_close(r,r2,rtol=0,atol=0)
    # Explicit Cartesian loss and mean-target solve share normalized regularization.
    aa=ga.sort_values(['content_id',*FEATURES]);pp=gp.sort_values(['content_id',*FEATURES]);aa4=np.repeat(aa[FEATURES].to_numpy(),4,axis=0)
    bb=torch.cat([encode(pp[pp.content_id==c][FEATURES].to_numpy()).repeat(4,1) for c in sorted(aa.content_id.unique())])
    expanded=Ridge(aa4,bb);torch.testing.assert_close(expanded.weight,m.weight,atol=1e-9,rtol=1e-8)
    write(OUT/'generator-engineering.json',{'passed':True,'cuda':True,'random_cases':5000,'group_permutation':True,'cartesian_equivalence':True,'C_only_real_inputs':True})
    print('CUDA decoder and group engineering passed',flush=True)

def generate(kind):
    assert read(OUT/'generator-engineering.json')['passed']
    for p,h in read(OUT/'learning-contract.json')['files'].items():assert sha(p)==h
    for k,folder in enumerate(sorted((OUT/'bundles'/kind).iterdir())):
        dest=OUT/'generation'/kind/folder.name;dest.mkdir(parents=True,exist_ok=True)
        if (dest/'complete.json').exists():
            done=read(dest/'complete.json');assert done['contract']==sha(OUT/'learning-contract.json')
            for p,h in done['files'].items():assert sha(p)==h
            continue
        b=Bundle(folder,kind);a=b.get('C_pre');post=b.get('C_post');u=b.get('U_pre').sort_values('session_id').reset_index(drop=True)
        fitted={};logs=[]
        for arm in (['group'] if kind=='group' else ['paired','cyclic']):
            m,res,log,pre,drift=fit(a,post,arm);fitted[arm]=(m,res,drift)
            torch.save({'model':m.state(),'residuals':res,'loco':log},dest/(arm+'.pt'));logs+=log
        uz=encode(u[FEATURES].to_numpy(float));audit=[]
        for seed in SEEDS:
            rng=np.random.default_rng(seed);rows=[]
            draw=rng.integers(0,24,(len(u),8));gdraw=rng.integers(0,96,(len(u),8))
            for arm in (['group'] if kind=='group' else ['center','marginal','paired','cyclic']):
                if arm in fitted:
                    m,res,_=fitted[arm];donor=gdraw if arm=='group' else draw
                    z=m.predict(u[FEATURES].to_numpy(float))[:,None,:]+res[donor]
                else:
                    drift=fitted['paired'][2];donor=draw
                    z=uz[:,None,:]+(torch.quantile(drift,.5,dim=0)[None,None,:].expand(len(u),8,6) if arm=='center' else drift[draw])
                values,effects=decode(z);arr=values.cpu().numpy()
                # Independent integer-domain check, not relying on decode assertions.
                w,p,r=arr[...,:2],arr[...,2:4],arr[...,4:]
                assert (r<=p).all() and (p<=w).all() and (w<=65527*p).all() and (np.abs(r[...,0]-r[...,1])<=1).all()
                assert ((r==0)==(p==0)).all() and ((p==0)==(w==0)).all()
                for i,sid in enumerate(u.session_id):
                    for view in range(8):rows.append({'arm':arm,'session_id':sid,'view':view,'donor_index':int(donor[i,view]) if arm!='center' else -1,**dict(zip(FEATURES,map(int,arr[i,view])))})
                audit.append({'arm':arm,'seed':seed,'views':len(u)*8,**{name:int(v.sum()) for name,v in effects.items()},'unique_views_mean':float(np.mean([len(np.unique(x,axis=0)) for x in arr]))})
            pd.DataFrame(rows).to_parquet(dest/f'samples-{seed}.parquet',index=False)
        pd.DataFrame(audit).to_parquet(dest/'audit.parquet',index=False)
        write(dest/'complete.json',{'contract':sha(OUT/'learning-contract.json'),'read_roles':b.access,'cuda':True,'redraws':0,'fallbacks':0,
                                    'files':{str(p):sha(p) for p in dest.iterdir() if p.is_file()}})
        if (k+1)%30==0:print(kind,k+1,'/300',flush=True)

def gate():
    rows=[]
    for kind in ['paired','group']:
        folders=sorted((OUT/'generation'/kind).iterdir());assert len(folders)==300
        for f in folders:
            done=read(f/'complete.json');assert set(done['read_roles'])=={'C_pre','C_post','U_pre'}
            for p,h in done['files'].items():assert sha(p)==h
            df=pd.read_parquet(f/'audit.parquet');df['scenario']=f.name;rows.append(df)
    audits=save('generation-audit',pd.concat(rows));assert audits.views.sum()==2016000
    write(OUT/'generation-gate.json',{'passed':True,'generated_views':2016000,'ridge_fits':6300,'redraws':0,'fallbacks':0,'cuda':True})
    print('generation gate passed',flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('stage',choices=['engineering','paired','group','gate']);a=p.parse_args()
    if a.stage=='engineering':engineering()
    elif a.stage=='gate':gate()
    else:generate(a.stage)
