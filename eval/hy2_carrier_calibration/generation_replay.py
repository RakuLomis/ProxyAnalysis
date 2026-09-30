"""Reconstruct every generated integer summary from saved CUDA state and donors."""
from window_model import *

def main():
    assert read(OUT/'generation-gate.json')['passed']
    checked=0;rows=[]
    for kind in ['paired','group']:
      for folder in sorted((OUT/'bundles'/kind).iterdir()):
        bundle=Bundle(folder,kind);a=bundle.get('C_pre');post=bundle.get('C_post');u=bundle.get('U_pre').sort_values('session_id').reset_index(drop=True)
        dest=OUT/'generation'/kind/folder.name;models={};pools={}
        for arm in (['group'] if kind=='group' else ['paired','cyclic']):
            ck=torch.load(dest/(arm+'.pt'),map_location=device(),weights_only=False)
            m=Ridge.__new__(Ridge)
            for k,v in ck['model'].items():setattr(m,k,v)
            models[arm]=m;pools[arm]=ck['residuals']
            for log in ck['loco']:
                assert log['held_content'] not in log['fit_contents'] and len(log['fit_contents'])==5
        if kind=='paired':
            a=a.sort_values(['content_id','repetition']);post=post.set_index('session_id').loc[a.session_id]
            drift=encode(post[FEATURES].to_numpy(float))-encode(a[FEATURES].to_numpy(float))
        for seed in SEEDS:
            sample=pd.read_parquet(dest/f'samples-{seed}.parquet')
            for arm,f in sample.groupby('arm'):
                f=f.sort_values(['session_id','view']);assert f.session_id.unique().tolist()==u.session_id.tolist()
                donor=f.donor_index.to_numpy().reshape(len(u),8)
                if arm in models:z=models[arm].predict(u[FEATURES].to_numpy())[:,None,:]+pools[arm][donor]
                elif arm=='center':z=encode(u[FEATURES].to_numpy())[:,None,:]+torch.quantile(drift,.5,dim=0)[None,None,:].expand(len(u),8,6)
                else:z=encode(u[FEATURES].to_numpy())[:,None,:]+drift[donor]
                got,_=decode(z);np.testing.assert_array_equal(got.cpu().numpy().reshape(-1,6),f[FEATURES].to_numpy())
                checked+=len(f)
        rows.append({'kind':kind,'scenario':folder.name,'passed':True,'access':json.dumps(bundle.access)})
    assert checked==2016000
    save('generation-replay-audit',rows)
    write(OUT/'generation-replay.json',{'passed':True,'replayed_views':checked,'cuda':True,'script_hash':sha(__file__),
                                      'U_post_read':False,'H_read':False})
    print('all generated views replayed',checked,flush=True)
if __name__=='__main__':main()
