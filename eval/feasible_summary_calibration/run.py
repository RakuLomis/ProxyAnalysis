import sys,argparse,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'src'))
from proxy_analysis.feasible_summary_calibration.common import *
from proxy_analysis.feasible_summary_calibration.model import *
from proxy_analysis.conditional_drift.common import illegal

def prepare():
    OUT.mkdir(parents=True,exist_ok=True);DOC.mkdir(parents=True,exist_ok=True)
    for p,h in read(SOURCE/'worker-contract.json')['files'].items():assert sha(p)==h
    for p,h in read(SOURCE/'contract.json')['inputs'].items():assert sha(p)==h
    assert read(SOURCE/'permission-gate.json')['passed']
    files=[CONFIG,ROOT/'plan/feasible-summary-calibration-plan-20260928.md',SOURCE/'roles.parquet',SOURCE/'business-groups.json',SOURCE/'permission-gate.json',SOURCE/'generation-gate.json',
        *list((SOURCE/'bundles').glob('*/*/manifest.json')),*Path(ROOT/'src/proxy_analysis/feasible_summary_calibration').glob('*.py'),Path(__file__)]
    contract={'files':{str(p):sha(p) for p in files},'source':str(SOURCE),'classification_tasks':5040,'old_failure_retained':True,'config':config()}
    if (OUT/'contract.json').exists():assert read(OUT/'contract.json')==contract
    else:write(OUT/'contract.json',contract)
    save('roles',pd.read_parquet(SOURCE/'roles.parquet'));write(OUT/'business-groups.json',read(SOURCE/'business-groups.json'))
    write(OUT/'permission-gate.json',{'passed':True,'inherited_scenarios':240,'source_permission_hash':sha(SOURCE/'permission-gate.json'),'group_post_F_forbidden':True})

def engineering():
    b=Bundle(sorted((SOURCE/'bundles/group').iterdir())[0],'group');pre=b.get('G_pre');post=b.get('G_post')
    m,p,_,canonical_pre=fit(pre,post,'group');n,q,_,_=fit(pre.sample(frac=1,random_state=8),post.sample(frac=1,random_state=9),'group')
    torch.testing.assert_close(m.weight,n.weight,atol=0,rtol=0);pd.testing.assert_frame_equal(p,q)
    a=[];F=[];target=[]
    for c,g in canonical_pre.groupby('content_id'):
        zg=encode(post[post.content_id==c][FEATURES].to_numpy(float))
        for r in g.to_dict('records'):
            for zz in zg:a.append([r[k] for k in FEATURES]);F.append(r['F']);target.append(zz)
    expanded=Ridge(np.array(a),np.array(F),torch.stack(target));torch.testing.assert_close(m.weight,expanded.weight,atol=1e-10,rtol=1e-10)
    # Exact round-trip for synthetic integer boundaries, direction parity, zeros and large realistic counts.
    cases=[];fs=[]
    for ff in [1,2,3,10,100]:
      for NN in [ff,ff+1,ff+2,2*ff+7]:
       B=ff-(ff-NN)%2
       for dd in range(-B,B+1,2):
        R=np.array([(NN+dd)//2,(NN-dd)//2],dtype=np.int64)
        for gap in [0,1,100,10**9]:
            E=np.where(R==0,0,R+gap);U=np.where(R==0,0,E+gap*100)
            cases.append(np.r_[U,E,R]);fs.append(ff)
    recovered,_=decode(encode(np.array(cases)),np.array(fs));np.testing.assert_array_equal(recovered.cpu().numpy(),cases)
    rng=np.random.default_rng(77);z=rng.uniform(-40,25,(5000,6));F=rng.integers(1,200,5000);decoded,_=decode(z,F)
    for v,f in zip(decoded.cpu().numpy(),F):assert not illegal(v,f)
    try:decode(np.full((1,6),1000.),np.array([1]))
    except FloatingPointError:pass
    else:raise AssertionError('Overflow was silently accepted')
    result={'passed':True,'cuda':True,'group_permutation_invariant':True,'expanded_objective_difference':float((m.weight-expanded.weight).abs().max()),'roundtrip_cases':len(cases),'random_legal_cases':5000,'overflow_stops':True,'test_data_read':False}
    write(OUT/'engineering.json',result);print(result,flush=True)

def roundtrip(a,F):
    decoded,_=decode(encode(a),F);np.testing.assert_array_equal(decoded.cpu().numpy(),a)

def generate(kind):
    assert read(OUT/'engineering.json')['passed']
    for p,h in read(OUT/'contract.json')['files'].items():assert sha(p)==h
    for count,folder in enumerate(sorted((SOURCE/'bundles'/kind).iterdir())):
      bundle=Bundle(folder,kind);meta=bundle.manifest;name=folder.name;dest=OUT/'generation'/kind/name;dest.mkdir(parents=True,exist_ok=True)
      if (dest/'complete.json').exists():
        old=read(dest/'complete.json');assert old['contract']==sha(OUT/'contract.json')
        for p,h in old['files'].items():assert sha(p)==h
        continue
      started=time.perf_counter();query=bundle.get('U_pre');models={};pools={};audits={}
      try:
        if kind=='paired':
            pre=bundle.get('C_pre');post=bundle.get('C_post')
            for arm in ['paired','cyclic']:models[arm],pools[arm],audits[arm],_=fit(pre,post,arm)
            basis=models['paired'];arms=['center','marginal','paired','cyclic']
            roundtrip(post[FEATURES].to_numpy(float),post.F.to_numpy(float))
        else:
            models['group'],pools['group'],audits['group'],pre=fit(bundle.get('G_pre'),bundle.get('G_post'),'group')
            basis=models['group'];arms=['group']
        roundtrip(pre[FEATURES].to_numpy(float),pre.F.to_numpy(float));roundtrip(query[FEATURES].to_numpy(float),query.F.to_numpy(float))
        for arm,pool in pools.items():pool.to_parquet(dest/(arm+'-pool.parquet'),index=False)
        write(dest/'loco.json',audits);torch.save({a:m.state() for a,m in models.items()},dest/'models.pt')
        a=query[FEATURES].to_numpy(float);F=query.F.to_numpy(float);za=encode(a)
        pred={arm:m.predict(a,F) for arm,m in models.items()}
        if kind=='paired':
            drift=pools['paired'][[f'd{j}' for j in range(6)]].to_numpy();pred['center']=za+tensor(np.quantile(drift,.5,axis=0));pred['marginal']=za
        contents=sorted(pre.content_id.unique());source=((tensor(np.log1p(pre[NUMERIC].to_numpy(float)))-basis.mean)/basis.scale).cpu().numpy()
        qc=((tensor(np.log1p(query[NUMERIC].to_numpy(float)))-basis.mean)/basis.scale).cpu().numpy()
        centers=np.stack([source[pre.content_id.to_numpy()==c].mean(0) for c in contents])
        for seed in config()['seeds']:
            records=[];zs=[];ff=[]
            for i,r in enumerate(query.to_dict('records')):
                near=np.argsort(np.linalg.norm(centers-qc[i],axis=1),kind='stable')
                for view in range(8):
                    for arm in arms:
                        rng=np.random.default_rng(int(objhash([seed,name,r['session_id'],view])[:16],16));donor=None;c=None
                        z=pred[arm][i]
                        if arm!='center':
                            pool=pools['paired' if arm=='marginal' else arm]
                            c=contents[int(rng.choice(np.arange(6) if arm=='marginal' else near))];ix=np.flatnonzero(pool.content_id.to_numpy()==c)
                            donor=int(ix[int(rng.integers(4))*4+int(rng.integers(4))]) if arm=='group' else int(rng.choice(ix))
                            fields=[('d' if arm=='marginal' else 'e')+str(j) for j in range(6)]
                            z=z+tensor(pool.iloc[donor][fields].to_numpy(float))
                        records.append({**r,'scenario':name,'business_group':meta['business_group'],'fold':meta['fold'],'rotation':meta['rotation'],'seed':seed,'view':view,'arm':arm,'donor_content':c,'donor_pool_index':donor})
                        zs.append(z);ff.append(F[i])
            z=torch.stack(zs);decoded,change=decode(z,np.array(ff));df=pd.DataFrame(records)
            for j,k in enumerate(FEATURES):df[k]=decoded[:,j].cpu().numpy();df['z'+str(j)]=z[:,j].cpu().numpy()
            for k,v in change.items():df[k]=v.cpu().numpy()
            df.to_parquet(dest/f'samples-{seed}.parquet',index=False,compression='zstd')
        write(dest/'complete.json',{'scenario':name,'kind':kind,'contract':sha(OUT/'contract.json'),'cuda':True,'roundtrip_passed':True,'fits':7*len(models),'read_roles':bundle.access,
            'seconds':time.perf_counter()-started,'files':{str(p):sha(p) for p in dest.iterdir() if p.is_file()}})
      except Exception as e:
        write(OUT/'numeric-failure.json',{'scenario':name,'kind':kind,'error':repr(e),'classification_started':False});raise
      write(OUT/(kind+'-progress.json'),{'completed':count+1,'total':240})
      if (count+1)%20==0:print(kind,count+1,'/240',flush=True)

def gate():
    rows=[];summary=[];total=0
    roles=pd.read_parquet(SOURCE/'roles.parquet',filters=[('role','==','U')],columns=['scenario','session_id','label_id','business_role'])
    for kind in ['paired','group']:
      folders=sorted((OUT/'generation'/kind).iterdir());assert len(folders)==240
      for folder in folders:
        done=read(folder/'complete.json');assert done['roundtrip_passed'] and done['cuda']
        for p,h in done['files'].items():assert sha(p)==h
        rows.append({'scenario':folder.name,'kind':kind,'fits':done['fits'],'seconds':done['seconds']})
        for path in folder.glob('samples-*.parquet'):
            f=pd.read_parquet(path);assert 'label_id' not in f
            for v,ff in zip(f[FEATURES].to_numpy(),f.F):assert not illegal(v,ff)
            assert f.groupby(['session_id','arm']).view.nunique().eq(8).all();total+=len(f)
            f=f.merge(roles,on=['scenario','session_id'],validate='many_to_one')
            summary.append(f.groupby(['protocol','business_group','arm','business_role']).agg(views=('session_id','size'),N_active=('N_floor_active','sum'),D_active=('D_bound_active','sum'),zero_direction=('zero_direction','sum'),N_added=('N_added','sum'),D_latent_displacement=('D_latent_bound_displacement','sum'),D_quantization=('D_lattice_displacement','sum'),ignored_G=('ignored_G','sum'),ignored_H=('ignored_H','sum')).reset_index())
    assert total==2073600
    save('generation-runtime',rows);s=pd.concat(summary).groupby(['protocol','business_group','arm','business_role']).sum(numeric_only=True).reset_index()
    for k in ['N_active','D_active','zero_direction']:s[k+'_rate']=s[k]/s.views
    save('decoder-effects',s);write(OUT/'generation-gate.json',{'passed':True,'views':total,'invalid':0,'redraws':0,'fallbacks':0,'fits':5040,'CUDA':True,'classification_started':False})
    print('Generation gate passed',total,flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--stage',choices=['prepare','engineering','paired','group','gate'],required=True);a=p.parse_args()
    if a.stage=='prepare':prepare()
    elif a.stage=='engineering':engineering()
    elif a.stage=='gate':gate()
    else:generate(a.stage)
