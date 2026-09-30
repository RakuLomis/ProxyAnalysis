"""Extend adapter: original W/T coordinates and draws; repetitions 1--4, no new fit target."""
import argparse,time
from formal_common import *
sys.path.insert(0,str(ROOT/'eval/hy2_carrier_calibration'))
import window_model as wm
from proxy_analysis.feasible_summary_calibration import model as tm
from proxy_analysis.feasible_summary_calibration.common import objhash

def fit(pre,post,kind,track):
    mod=wm if track=='W' else tm;features=FEATURES[track];numeric=NUMERIC[track]
    if kind=='group':
        assert set(pre)=={'content_id',*numeric} and set(post)=={'content_id',*features}
        pre=pre.sort_values(['content_id',*numeric]).reset_index(drop=True)
        post=post.sort_values(['content_id',*features]).reset_index(drop=True)
    else:
        pre=(pre.sort_values(['content_id','repetition']) if track=='W' else pre).reset_index(drop=True)
        post=post.set_index('session_id').loc[pre.session_id].reset_index()
    assert len(pre)==len(post)==24 and pre.groupby('content_id').size().eq(4).all()
    a=pre[features].to_numpy(float);b=mod.encode(post[features].to_numpy(float));donor=np.arange(24)
    if kind=='cyclic':
        for _,g in pre.groupby('content_id'):
            ix=g.sort_values('repetition').index.to_numpy();assert pre.loc[ix,'repetition'].tolist()==[1,2,3,4]
            donor[ix]=np.roll(ix,-1)
        assert (donor!=np.arange(24)).all()
    if kind=='group':
        means={c:b[np.flatnonzero(post.content_id.eq(c))].mean(0) for c in post.content_id.unique()}
        targets=torch.stack([means[c] for c in pre.content_id])
    else:targets=b[donor]
    def build(mask):
        return mod.Ridge(a[mask],targets[mask]) if track=='W' else mod.Ridge(a[mask],pre.F.to_numpy(float)[mask],targets[mask])
    model=build(np.ones(24,bool));pools=[];logs=[]
    za=mod.encode(a)
    for c in sorted(pre.content_id.unique()):
        held=pre.content_id.eq(c).to_numpy();inner=build(~held)
        pred=inner.predict(a[held]) if track=='W' else inner.predict(a[held],pre.loc[held,'F'].to_numpy(float))
        if kind=='group':
            z=b[np.flatnonzero(post.content_id.eq(c))];err=(z[None,:,:]-pred[:,None,:]).reshape(-1,6)
            rows=[{'content_id':c,'pre_local_index':i//4,'post_local_index':i%4} for i in range(16)]
        else:
            err=targets[held]-pred;rows=[]
            for i in np.flatnonzero(held):
                rows.append({'content_id':c,'session_id':pre.iloc[i].session_id,'target_session_id':post.iloc[donor[i]].session_id,
                             **dict(zip([f'd{j}' for j in range(6)],(targets[i]-za[i]).cpu().numpy()))})
        ef=pd.DataFrame(rows)
        for j in range(6):ef[f'e{j}']=err[:,j].cpu().numpy()
        pools.append(ef);logs.append({'held_content':c,'fit_contents':sorted(pre.loc[~held,'content_id'].unique()),'normal_residual':inner.normal_residual})
    return model,pd.concat(pools,ignore_index=True),logs,pre,targets-za

def valid(x,track,F=None):
    x=np.asarray(x);u,e,r=x[:,:2],x[:,2:4],x[:,4:]
    assert np.isfinite(x).all() and (x>=0).all() and (x==np.floor(x)).all()
    assert (r<=e).all() and (e<=u).all() and ((r==0)==(e==0)).all() and ((e==0)==(u==0)).all()
    if track=='W':assert (u<=65527*e).all() and (r.sum(1)>=1).all() and (np.abs(r[:,0]-r[:,1])<=1).all()
    else:assert (r.sum(1)>=F).all() and (np.abs(r[:,0]-r[:,1])<=F).all()

def generate_one(folder,kind):
    name=folder.name;track=metadata(name)['track'];mod=wm if track=='W' else tm;features=FEATURES[track]
    dest=OUT/'generation'/kind/name;dest.mkdir(parents=True,exist_ok=True)
    if (dest/'complete.json').exists():
        checkseal(dest/'complete.json');return
    start=time.perf_counter();bundle=Bundle(PREP/'packages'/kind/name,kind);query=bundle.get('U_pre')
    if track=='W':query=query.sort_values('session_id').reset_index(drop=True)
    models={};pools={};logs={};drifts={}
    if kind=='paired':pre=bundle.get('C_pre');post=bundle.get('C_post');kinds=['paired','cyclic'];arms=['center','marginal','paired','cyclic']
    else:pre=bundle.get('G_pre');post=bundle.get('G_post');kinds=['group'];arms=['group']
    for arm in kinds:models[arm],pools[arm],logs[arm],canonical,drifts[arm]=fit(pre,post,arm,track)
    pre=canonical;basis=models[kinds[0]]
    for frame in [pre,query]+([post] if kind=='paired' else []):
        a=frame[features].to_numpy(float);f=frame.F.to_numpy(float) if track=='T' else None
        decoded,_=mod.decode(mod.encode(a),f) if track=='T' else mod.decode(mod.encode(a))
        np.testing.assert_array_equal(decoded.cpu().numpy(),a);valid(a,track,f)
    a=query[features].to_numpy(float);F=query.F.to_numpy(float) if track=='T' else None;za=mod.encode(a)
    pred={k:(m.predict(a,F) if track=='T' else m.predict(a)) for k,m in models.items()}
    if kind=='paired':
        drift=drifts['paired'] if track=='W' else tm.tensor(pools['paired'][[f'd{j}' for j in range(6)]].to_numpy(float))
        pred['center']=za+torch.quantile(drift,.5,dim=0);pred['marginal']=za
    if track=='T':
        contents=sorted(pre.content_id.unique());source=(np.log1p(pre[NUMERIC[track]].to_numpy(float))-basis.mean.cpu().numpy())/basis.scale.cpu().numpy()
        qc=(np.log1p(query[NUMERIC[track]].to_numpy(float))-basis.mean.cpu().numpy())/basis.scale.cpu().numpy()
        centers=np.stack([source[pre.content_id.eq(c)].mean(0) for c in contents])
    for arm,pool in pools.items():pool.to_parquet(dest/(arm+'-pool.parquet'),index=False)
    torch.save({k:m.state() for k,m in models.items()},dest/'models.pt');write(dest/'loco.json',logs)
    summaries=[]
    for seed in SEEDS:
        rows=[];zs=[];ff=[]
        if track=='W':
            rng=np.random.default_rng(seed);draw=rng.integers(0,24,(len(query),8));gdraw=rng.integers(0,96,(len(query),8))
        for i,r in enumerate(query.to_dict('records')):
            if track=='T':near=np.argsort(np.linalg.norm(centers-qc[i],axis=1),kind='stable')
            for view in range(8):
                for arm in arms:
                    z=pred[arm][i];donor=None
                    if arm!='center':
                        pool=pools['paired' if arm=='marginal' else arm]
                        if track=='W':
                            donor=int(gdraw[i,view] if arm=='group' else draw[i,view])
                            residual=drift[donor] if arm=='marginal' else wm.tensor(pool.iloc[donor][[f'e{j}' for j in range(6)]].to_numpy(float))
                        else:
                            rng=np.random.default_rng(int(objhash([seed,name,r['session_id'],view])[:16],16))
                            c=contents[int(rng.choice(np.arange(6) if arm=='marginal' else near))];ix=np.flatnonzero(pool.content_id.eq(c))
                            donor=int(ix[int(rng.integers(4))*4+int(rng.integers(4))]) if arm=='group' else int(rng.choice(ix))
                            residual=tm.tensor(pool.iloc[donor][[('d' if arm=='marginal' else 'e')+str(j) for j in range(6)]].to_numpy(float))
                        z=z+residual
                    rows.append({'session_id':r['session_id'],'arm':arm,'view':view,'donor_index':donor});zs.append(z)
                    if track=='T':ff.append(F[i])
        z=torch.stack(zs);decoded,audit=mod.decode(z,np.array(ff)) if track=='T' else mod.decode(z)
        x=decoded.cpu().numpy();valid(x,track,np.array(ff) if track=='T' else None)
        df=pd.DataFrame(rows)
        for j,k in enumerate(features):df[k]=x[:,j];df['z'+str(j)]=z[:,j].cpu().numpy()
        if track=='T':df['F']=ff
        for k,v in audit.items():df[k]=v.cpu().numpy()
        assert len(df)==72*8*len(arms) and not df.duplicated(['arm','session_id','view']).any()
        df.to_parquet(dest/f'samples-{seed}.parquet',index=False,compression='zstd')
        for arm,g in df.groupby('arm'):
            summaries.append({'seed':seed,'arm':arm,'views':len(g),**{k:float(g[k].sum()) for k in audit}})
    write(dest/'decoder-effects.json',summaries)
    checkpoint(dest,{'scenario':name,'kind':kind,'cuda':True,'roundtrip_passed':True,'read_roles':bundle.access,
                     'fits':7*len(models),'seconds':time.perf_counter()-start,'redraws':0,'fallbacks':0})

def engineering():
    rows=[]
    for track in ['W','T']:
        name=f'{track}-shadowsocks-f0-g0-r0';b=Bundle(PREP/'packages/group'/name,'group');a=b.get('G_pre');p=b.get('G_post')
        m,pool,_,canon,_=fit(a,p,'group',track)
        n,other,*_=fit(a.sample(frac=1,random_state=8),p.sample(frac=1,random_state=9),'group',track)
        torch.testing.assert_close(m.weight,n.weight,atol=0,rtol=0);pd.testing.assert_frame_equal(pool,other)
        mod=wm if track=='W' else tm;aa=[];ff=[];zz=[]
        for c,g in canon.groupby('content_id'):
            targets=mod.encode(p[p.content_id==c][FEATURES[track]].to_numpy(float))
            for r in g.to_dict('records'):
                for z in targets:
                    aa.append([r[k] for k in FEATURES[track]]);zz.append(z)
                    if track=='T':ff.append(r['F'])
        expanded=mod.Ridge(np.array(aa),torch.stack(zz)) if track=='W' else mod.Ridge(np.array(aa),np.array(ff),torch.stack(zz))
        torch.testing.assert_close(m.weight,expanded.weight,atol=1e-10,rtol=1e-10)
        # Replay original fitter with only the old repetition names restored; all numeric inputs identical.
        b=Bundle(PREP/'packages/paired'/name,'paired');pre=b.get('C_pre');post=b.get('C_post')
        for kind in ['paired','cyclic']:
            new,pool,*_=fit(pre,post,kind,track);oldpre=pre.copy();oldpost=post.copy()
            oldpre.repetition=oldpre.repetition.map({1:1,2:2,3:4,4:5});oldpost.repetition=oldpost.repetition.map({1:1,2:2,3:4,4:5})
            old=mod.fit(oldpre,oldpost,kind);torch.testing.assert_close(new.weight,old[0].weight,atol=1e-12,rtol=1e-12)
            actual=wm.tensor(pool[[f'e{j}' for j in range(6)]].to_numpy(float))
            expected=old[1] if track=='W' else tm.tensor(old[1][[f'e{j}' for j in range(6)]].to_numpy(float))
            torch.testing.assert_close(actual,expected,atol=1e-12,rtol=1e-12)
        for forbidden in ['U_post','H_post','H_pre']:
            try:b.get(forbidden)
            except PermissionError:pass
            else:raise AssertionError('Forbidden role accepted')
        rows.append({'track':track,'group_permutation_exact':True,'old_fit_numeric_replay_atol_rtol':1e-12,'Cartesian_objective_equivalent':True})
    write(OUT/'generation-engineering.json',{'passed':True,'cuda':True,'tracks':rows,'test_data_read':False})
    print('Generation engineering passed',flush=True)

def gate():
    effects=[];total=0
    for folder in folders():
        track=metadata(folder.name)['track']
        for kind in ['paired','group']:
            dest=OUT/'generation'/kind/folder.name;done=checkseal(dest/'complete.json')
            assert done['cuda'] and done['roundtrip_passed']
            for seed in SEEDS:
                f=pd.read_parquet(dest/f'samples-{seed}.parquet');valid(f[FEATURES[track]].to_numpy(),track,f.F.to_numpy() if track=='T' else None);total+=len(f)
            effects.extend([{**metadata(folder.name),**r} for r in read(dest/'decoder-effects.json')])
    assert total==1080*72*8*5*3
    pd.DataFrame(effects).to_parquet(OUT/'decoder-effects.parquet',index=False)
    write(OUT/'generation-gate.json',{'passed':True,'views':total,'invalid':0,'redraws':0,'fallbacks':0,'scenarios':1080,'cuda':True})
    print('Generation gate passed:',total,flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--stage',choices=['engineering','generate','gate'],required=True);args=p.parse_args();freeze()
    if args.stage=='engineering':engineering()
    elif args.stage=='gate':gate()
    else:
        assert read(OUT/'generation-engineering.json')['passed']
        for i,folder in enumerate(folders()):
            try:
                for kind in ['paired','group']:generate_one(folder,kind)
            except Exception as e:
                write(OUT/'generation-failure-revision-02.json',{'scenario':folder.name,'kind':kind,'error':repr(e),'classification_started':False});raise
            write(OUT/'generation-progress.json',{'completed_scenarios':i+1,'total':1080})
            if (i+1)%10==0:print('generated',i+1,'/1080',flush=True)
