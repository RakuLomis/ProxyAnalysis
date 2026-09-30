"""CUDA-only, independently parameterized heads. No scoring labels during fits/inference."""
import argparse,time
from formal_common import *
Heads=module('extend_frozen_heads',ROOT/'eval/paired_calibration_budget/train.py').Heads

def prepare(folder,reference=False):
    b=Bundle(folder,'paired');meta=b.meta;jobmeta=metadata(folder.name);features=NUMERIC[jobmeta['track']]
    C=b.get('C_pre');Cp=b.get('C_post');U=b.get('U_pre');labels=b.get('labels')
    source=pd.concat([C,U]).sort_values('session_id').reset_index(drop=True).merge(labels,on='session_id',validate='one_to_one')
    assert len(source)==96 and not set(C.content_id)&set(U.content_id)
    classes=sorted(source.label_id.unique());assert len(classes)==6
    mean=np.log1p(C[features].to_numpy(float)).mean(0);scale=np.log1p(C[features].to_numpy(float)).std(0);scale[scale<1e-10]=1
    cpost=Cp.set_index('session_id');ref=later_package(folder.name,'reference','U_post').set_index('session_id') if reference else None
    if reference:assert set(ref.index)==set(U.session_id)
    target=np.array([classes.index(v) for v in source.label_id]);states=[];arrays=[];indices=[];views=[];jobs=[]
    for seed in SEEDS:
        torch.manual_seed(seed);base=torch.nn.Sequential(torch.nn.Linear(len(features),32),torch.nn.ReLU(),torch.nn.Linear(32,6)).to(device());initial=base.state_dict()
        rng=np.random.default_rng(seed);groups={l:sorted(g.content_id.unique()) for l,g in source.groupby('label_id')}
        for group in groups.values():assert len(group)==4;rng.shuffle(group)
        ids={c:np.flatnonzero(source.content_id.to_numpy()==c) for group in groups.values() for c in group}
        assert all(len(v)==4 for v in ids.values())
        schedule=np.stack([np.concatenate([ids[groups[l][step%4]] for l in classes]) for step in range(1000)])
        assert np.bincount(schedule.ravel(),minlength=96).tolist()==[250]*96
        draw=rng.integers(0,8,(1000,24));samples=None
        if not reference:
            frames=[]
            for kind in ['paired','group']:
                dest=OUT/'generation'/kind/folder.name;done=read(dest/'complete.json');path=dest/f'samples-{seed}.parquet'
                assert_artifact_contract(done,dest/'complete.json')
                assert sha(path)==done['files'][str(path)]
                frames.append(pd.read_parquet(path))
            samples=pd.concat(frames).set_index(['arm','session_id','view']).sort_index()
        for arm in (['reference'] if reference else ARMS):
            arr=np.empty((96,8,len(features)),float)
            for i,r in enumerate(source.to_dict('records')):
                sid=r['session_id']
                if sid in meta['C_sessions']:arr[i]=cpost.loc[sid,features].to_numpy(float)
                elif reference:arr[i]=ref.loc[sid,features].to_numpy(float)
                elif arm=='raw':arr[i]=[r[k] for k in features]
                else:arr[i]=samples.loc[(arm,sid)][features].to_numpy(float)
            assert np.isfinite(arr).all() and (arr>=0).all()
            states.append({k:v.clone() for k,v in initial.items()});arrays.append((np.log1p(arr)-mean)/scale);indices.append(schedule);views.append(draw)
            jobs.append({**jobmeta,'seed':seed,'arm':arm,'initial_hash':digest({k:v.cpu().tolist() for k,v in initial.items()}),
                         'schedule_hash':digest([schedule.tolist(),draw.tolist()])})
    return (Heads(states).to(device()),torch.tensor(np.stack(arrays),device=device(),dtype=torch.float32),
            torch.tensor(target,device=device()),torch.tensor(np.stack(indices),device=device()),torch.tensor(np.stack(views),device=device()),
            jobs,mean,scale,classes,meta,b.access)

def engineering():
    records=[]
    for track in ['W','T']:
        m,x,y,ix,v,*_=prepare(PREP/'packages/paired'/f'{track}-shadowsocks-f0-g0-r0')
        sel=torch.arange(len(x),device=device());batch=x[sel[:,None],ix[:,0],v[:,0]];yy=y[ix[:,0]];refs=[]
        for i in range(len(x)):
            h=torch.nn.Sequential(torch.nn.Linear(len(NUMERIC[track]),32),torch.nn.ReLU(),torch.nn.Linear(32,6)).to(device());h.load_state_dict(m.one(i));refs.append(h)
        opt=torch.optim.Adam(m.parameters(),lr=.001,foreach=False);opts=[torch.optim.Adam(h.parameters(),lr=.001,foreach=False) for h in refs];delta=0.
        for step in range(5):
            opt.zero_grad(set_to_none=True);loss,_=m.loss(batch,yy);loss.sum().backward();opt.step()
            for i,(h,o) in enumerate(zip(refs,opts)):
                o.zero_grad(set_to_none=True);l=torch.nn.functional.cross_entropy(h(batch[i]),yy[i])+.5e-4*sum(p.square().sum() for k,p in h.named_parameters() if k.endswith('weight'));l.backward();o.step()
            with torch.no_grad():
                expected=torch.stack([h(batch[i]) for h,i in zip(refs,range(len(refs)))]);actual=m(batch)
                torch.testing.assert_close(actual,expected,atol=2e-5,rtol=2e-4);delta=max(delta,float((actual-expected).abs().max()))
        with torch.no_grad():
            changed=batch.clone();changed[1:]+=10;assert torch.equal(m(changed)[0],m(batch)[0])
        records.append({'track':track,'max_logit_difference':delta,'independent_heads':18,'model_axis_isolated':True})
    write(OUT/'classification-engineering.json',{'passed':True,'cuda':True,'records':records,'test_data_read':False})
    print('Classification engineering passed',records,flush=True)

def train(reference=False):
    assert read(OUT/'classification-engineering.json')['passed'];mode='reference' if reference else 'restricted';total=3240 if reference else 19440;finished=0
    for folder in folders():
        dest=OUT/'classifiers'/mode/folder.name;dest.mkdir(parents=True,exist_ok=True)
        if (dest/'complete.json').exists():
            done=checkseal(dest/'complete.json');finished+=done['models'];continue
        model,x,y,ix,views,jobs,mean,scale,classes,meta,access=prepare(folder,reference)
        n=len(jobs);sel=torch.arange(n,device=device());opt=torch.optim.Adam(model.parameters(),lr=.001,foreach=False);history=[];start=time.perf_counter()
        for step in range(1000):
            opt.zero_grad(set_to_none=True);batch=x[sel[:,None],ix[:,step],views[:,step]];loss,ce=model.loss(batch,y[ix[:,step]]);loss.sum().backward();opt.step()
            history.append(torch.stack([loss.detach(),ce.detach()],-1))
            if step%100==0:assert torch.isfinite(loss).all()
        torch.cuda.synchronize();history=torch.stack(history).cpu().numpy();assert np.isfinite(history).all()
        # One tensor bundle per scenario avoids 18 tiny file writes; heads remain independent.
        torch.save({'heads':[model.one(i) for i in range(n)],'jobs':jobs,'mean':mean,'scale':scale,'classes':classes,
                    'scaler_fit_sessions':meta['C_sessions'],'contract':contract_hash()},dest/'models.pt')
        np.savez_compressed(dest/'training-history.npz',loss=history[:,:,0],ce_nats=history[:,:,1])
        checkpoint(dest,{'models':n,'cuda':True,'steps':1000,'mode':mode,'read_roles':access,'U_post_read':reference,'H_read':False,'seconds':time.perf_counter()-start})
        finished+=n;write(OUT/(mode+'-training-progress.json'),{'completed':finished,'total':total,'status':'running'})
        if finished%(n*10)==0:print(mode,finished,'/',total,flush=True)
    assert finished==total
    write(OUT/(mode+'-training-progress.json'),{'completed':total,'total':total,'status':'complete'})

def infer(reference=False):
    mode='reference' if reference else 'restricted';total=3240 if reference else 19440
    assert read(OUT/(mode+'-training-progress.json'))=={'completed':total,'total':total,'status':'complete'}
    rows=[];inputs={};maxdiff=0.
    for folder in folders():
        dest=OUT/'classifiers'/mode/folder.name;done=checkseal(dest/'complete.json');assert not done['H_read'] and done['U_post_read']==reference
        meta=read(folder/'manifest.json');frame=later_package(folder.name,'scoring','H_post');features=NUMERIC[metadata(folder.name)['track']]
        assert list(frame)==['session_id',*features] and set(frame.session_id)==set(meta['H_sessions'])
        assert not set(frame.session_id)&(set(meta['C_sessions'])|set(meta['U_sessions']))
        ck=torch.load(dest/'models.pt',map_location=device(),weights_only=False)
        assert ck['contract']==contract_hash() and set(ck['scaler_fit_sessions'])==set(meta['C_sessions'])
        x=torch.tensor((np.log1p(frame[features].to_numpy(float))-ck['mean'])/ck['scale'],device=device(),dtype=torch.float32)
        h=Heads(ck['heads']).to(device());h.eval()
        with torch.no_grad():
            batch=x[None].expand(len(ck['jobs']),-1,-1);p=h(batch).softmax(-1)
            q=torch.cat([h(b).softmax(-1) for b in batch.split(6,dim=1)],dim=1)
            torch.testing.assert_close(p,q,atol=2e-6,rtol=2e-5);assert torch.equal(p.argmax(-1),q.argmax(-1));maxdiff=max(maxdiff,float((p-q).abs().max()))
        for i,job in enumerate(ck['jobs']):
            prob=p[i].cpu().numpy()
            rows.extend({'session_id':sid,**job,'classes_json':json.dumps(ck['classes']),**{f'p{j}':float(prob[r,j]) for j in range(6)}} for r,sid in enumerate(frame.session_id))
        jobs=pd.DataFrame(ck['jobs'])
        for _,g in jobs.groupby('seed'):assert g.initial_hash.nunique()==g.schedule_hash.nunique()==1
        path=PREP/'packages/scoring'/folder.name/'H_post.parquet';inputs[str(path)]=sha(path)
    p=pd.DataFrame(rows);assert len(p)==total*24 and not p.duplicated(['scenario','seed','arm','session_id']).any()
    path=OUT/(mode+'-predictions.parquet');p.to_parquet(path,index=False)
    write(OUT/(mode+'-prediction-seal.json'),{'passed':True,'rows':len(p),'models':total,'cuda':True,'labels_read':False,'test_pre_read':False,
         'max_replay_difference':maxdiff,'predictions_hash':sha(path),'H_post_inputs':inputs,'contract':contract_hash()})
    print(mode,'predictions sealed',len(p),flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--stage',choices=['engineering','restricted','infer','reference','infer-reference'],required=True);a=p.parse_args();freeze()
    assert read(OUT/'generation-gate.json')['passed']
    if a.stage=='engineering':engineering()
    elif a.stage in ['restricted','reference']:train(a.stage=='reference')
    else:infer(a.stage=='infer-reference')
