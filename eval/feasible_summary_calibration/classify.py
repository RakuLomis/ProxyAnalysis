"""CUDA-only independent classifiers; reference and inference run as separate stages."""
import sys,time,argparse,importlib.util
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'src'))
from proxy_analysis.feasible_summary_calibration.common import *
from proxy_analysis.conditional_drift.model import device,torch
HEAD_PATH=ROOT/'eval/paired_calibration_budget/train.py'
spec=importlib.util.spec_from_file_location('frozen_heads',HEAD_PATH);headmod=importlib.util.module_from_spec(spec);spec.loader.exec_module(headmod);Heads=headmod.Heads
ARMS=['raw','center','marginal','paired','cyclic','group']

def freeze():
    assert read(OUT/'generation-gate.json')['passed'] and read(OUT/'generation-audit.json')['passed']
    for p,h in read(OUT/'contract.json')['files'].items():assert sha(p)==h
    files=[Path(__file__),Path(__file__).with_name('score.py'),HEAD_PATH,CONFIG,OUT/'contract.json',OUT/'generation-gate.json',OUT/'generation-audit.json',*list((OUT/'generation').glob('*/*/complete.json'))]
    c={'files':{str(p):sha(p) for p in files},'restricted_tasks':4320,'reference_tasks':720,'steps':1000,'cuda':True,'independent_parameters':True}
    if (OUT/'classification-contract.json').exists():assert read(OUT/'classification-contract.json')==c
    else:write(OUT/'classification-contract.json',c)

def prepare(folder,reference=False):
    if reference:assert read(OUT/'restricted-prediction-seal.json')['passed']
    b=Bundle(folder,'paired');meta=b.manifest;C=b.get('C_pre');Cp=b.get('C_post');U=b.get('U_pre');labels=b.get('labels')
    source=pd.concat([C,U]).sort_values('session_id').reset_index(drop=True).merge(labels,on='session_id',validate='one_to_one');assert len(source)==96
    classes=sorted(source.label_id.unique());assert len(classes)==6 and not set(C.session_id)&set(U.session_id)
    mean=np.log1p(C[NUMERIC].to_numpy(float)).mean(0);scale=np.log1p(C[NUMERIC].to_numpy(float)).std(0);scale[scale<1e-10]=1
    cpost=Cp.set_index('session_id');lookup={s:i for i,s in enumerate(source.session_id)};ref=None
    if reference:ref=pd.read_parquet(SOURCE/'reference'/folder.name/'U_post.parquet').set_index('session_id');assert set(ref.index)==set(U.session_id)
    states=[];arrays=[];indices=[];views=[];jobs=[];dev=device();target=np.array([classes.index(l) for l in source.label_id])
    for seed in config()['seeds']:
        torch.manual_seed(seed);base=torch.nn.Sequential(torch.nn.Linear(7,32),torch.nn.ReLU(),torch.nn.Linear(32,6)).to(dev);initial=base.state_dict();rng=np.random.default_rng(seed)
        groups={l:sorted(g.content_id.unique()) for l,g in source.groupby('label_id')}
        for g in groups.values():assert len(g)==4;rng.shuffle(g)
        ids={c:np.flatnonzero(source.content_id.to_numpy()==c) for g in groups.values() for c in g}
        schedule=np.stack([np.concatenate([ids[groups[l][step%4]] for l in classes]) for step in range(1000)])
        assert np.bincount(schedule.ravel(),minlength=96).tolist()==[250]*96
        draw=rng.integers(0,8,(1000,24));samples=None
        if not reference:
            frames=[]
            for kind in ['paired','group']:
                path=OUT/'generation'/kind/folder.name/f'samples-{seed}.parquet';done=read(path.parent/'complete.json');assert sha(path)==done['files'][str(path)]
                frames.append(pd.read_parquet(path))
            samples=pd.concat(frames).set_index(['arm','session_id','view']).sort_index()
        for arm in (['reference'] if reference else ARMS):
            arr=np.empty((96,8,7),float)
            for r in source.to_dict('records'):
                sid=r['session_id'];i=lookup[sid]
                if sid in meta['C_sessions']:arr[i]=cpost.loc[sid,NUMERIC].to_numpy(float)
                elif reference:arr[i]=ref.loc[sid,NUMERIC].to_numpy(float)
                elif arm=='raw':arr[i]=[r[k] for k in NUMERIC]
                else:arr[i]=samples.loc[(arm,sid)][NUMERIC].to_numpy(float)
            states.append({k:v.clone() for k,v in initial.items()});arrays.append((np.log1p(arr)-mean)/scale);indices.append(schedule);views.append(draw)
            jobs.append({k:meta[k] for k in ['scenario','protocol','fold','business_group','rotation']}|{'seed':seed,'arm':arm,
                'initial_hash':objhash({k:v.cpu().tolist() for k,v in initial.items()}),'schedule_hash':objhash([schedule.tolist(),draw.tolist()])})
    return Heads(states).to(dev),torch.tensor(np.stack(arrays),device=dev,dtype=torch.float32),torch.tensor(target,device=dev),torch.tensor(np.stack(indices),device=dev),torch.tensor(np.stack(views),device=dev),jobs,mean,scale,classes,meta,b.access

def engineering():
    m,x,y,ix,v,*_=prepare(sorted((SOURCE/'bundles/paired').iterdir())[0]);n=len(x);sel=torch.arange(n,device=device());batch=x[sel[:,None],ix[:,0],v[:,0]];yy=y[ix[:,0]]
    refs=[]
    for i in range(n):
        h=torch.nn.Sequential(torch.nn.Linear(7,32),torch.nn.ReLU(),torch.nn.Linear(32,6)).to(device());h.load_state_dict(m.one(i));refs.append(h)
    opt=torch.optim.Adam(m.parameters(),lr=.001,foreach=False);opts=[torch.optim.Adam(h.parameters(),lr=.001,foreach=False) for h in refs];delta=0.
    for step in range(5):
        opt.zero_grad(set_to_none=True);loss,_=m.loss(batch,yy);loss.sum().backward();opt.step()
        for i,(h,o) in enumerate(zip(refs,opts)):
            o.zero_grad(set_to_none=True);l=torch.nn.functional.cross_entropy(h(batch[i]),yy[i])+.5e-4*sum(p.square().sum() for k,p in h.named_parameters() if k.endswith('weight'));l.backward();o.step()
        with torch.no_grad():
            expected=torch.stack([h(batch[i]) for i,h in enumerate(refs)]);actual=m(batch);torch.testing.assert_close(actual,expected,atol=2e-5,rtol=2e-4);delta=max(delta,float((actual-expected).abs().max()))
    with torch.no_grad():
        changed=batch.clone();changed[1:]+=10;assert torch.equal(m(changed)[0],m(batch)[0])
    start=time.perf_counter()
    for step in range(100):opt.zero_grad(set_to_none=True);loss,_=m.loss(batch,yy);loss.sum().backward();opt.step()
    torch.cuda.synchronize();elapsed=time.perf_counter()-start
    write(OUT/'classification-engineering.json',{'passed':True,'cuda':True,'max_logit_difference':delta,'model_axis_isolated':True,'seconds_per_18head_step':elapsed/100,'test_data_read':False})
    print(read(OUT/'classification-engineering.json'),flush=True)

def train(reference=False):
    assert read(OUT/'classification-engineering.json')['passed'];mode='reference' if reference else 'restricted';total=720 if reference else 4320;finished=0
    if reference:assert read(OUT/'restricted-prediction-seal.json')['passed']
    for folder in sorted((SOURCE/'bundles/paired').iterdir()):
        dest=OUT/'classifiers'/mode/folder.name;dest.mkdir(parents=True,exist_ok=True)
        if (dest/'complete.json').exists():
            done=read(dest/'complete.json');assert done['contract']==sha(OUT/'classification-contract.json')
            for p,h in done['files'].items():assert sha(p)==h
            finished+=done['models'];continue
        model,x,y,ix,views,jobs,mean,scale,classes,meta,access=prepare(folder,reference);n=len(jobs);sel=torch.arange(n,device=device());opt=torch.optim.Adam(model.parameters(),lr=.001,foreach=False);history=[];start=time.perf_counter()
        for step in range(1000):
            opt.zero_grad(set_to_none=True);batch=x[sel[:,None],ix[:,step],views[:,step]];loss,ce=model.loss(batch,y[ix[:,step]]);loss.sum().backward();opt.step();history.append(torch.stack([loss.detach(),ce.detach()],-1))
            if step%100==0:assert torch.isfinite(loss).all()
        torch.cuda.synchronize();history=torch.stack(history).cpu().numpy();assert np.isfinite(history).all();log=[]
        for i,job in enumerate(jobs):
            torch.save({'head':model.one(i),'mean':mean,'scale':scale,'job':job,'classes':classes,'C_hash':meta['C_hash'],'scaler_fit_sessions':meta['C_sessions'],
                'contract':sha(OUT/'classification-contract.json')},dest/f"s{job['seed']}-{job['arm']}.pt")
            log.extend({**job,'step':j+1,'loss':float(history[j,i,0]),'ce_nats':float(history[j,i,1])} for j in range(1000))
        pd.DataFrame(log).to_parquet(dest/'training-log.parquet',index=False)
        write(dest/'complete.json',{'contract':sha(OUT/'classification-contract.json'),'models':n,'cuda':True,'steps':1000,'mode':mode,'read_roles':access,
            'U_post_read':reference,'H_read':False,'seconds':time.perf_counter()-start,'files':{str(p):sha(p) for p in dest.iterdir() if p.is_file()}})
        finished+=n;write(OUT/(mode+'-training-progress.json'),{'completed':finished,'total':total,'status':'running'})
        if finished%(n*20)==0:print(mode,finished,'/',total,flush=True)
        del model,x,opt,ix,views;torch.cuda.empty_cache()
    write(OUT/(mode+'-training-progress.json'),{'completed':total,'total':total,'status':'complete'})

def infer(reference=False):
    mode='reference' if reference else 'restricted';total=720 if reference else 4320
    assert read(OUT/(mode+'-training-progress.json'))=={'completed':total,'total':total,'status':'complete'}
    rows=[];maxdiff=0.;inputs={};checks=[]
    for folder in sorted((OUT/'classifiers'/mode).iterdir()):
        done=read(folder/'complete.json');assert not done['H_read'] and done['U_post_read']==reference
        for p,h in done['files'].items():assert sha(p)==h
        meta=read(SOURCE/'bundles/paired'/folder.name/'manifest.json');path=SOURCE/'evaluation'/folder.name/'H_post.parquet';inputs[str(path)]=sha(path);frame=pd.read_parquet(path)
        assert 'label_id' not in frame and len(frame)==24
        assert not set(frame.content_id)&(set(meta['C_contents'])|set(meta['U_contents']))
        jobs=[]
        for path in folder.glob('*.pt'):
            ck=torch.load(path,map_location=device(),weights_only=False);jobs.append(ck['job']);assert set(ck['scaler_fit_sessions'])==set(meta['C_sessions'])
            h=torch.nn.Sequential(torch.nn.Linear(7,32),torch.nn.ReLU(),torch.nn.Linear(32,6)).to(device());h.load_state_dict(ck['head']);h.eval()
            x=torch.tensor((np.log1p(frame[NUMERIC].to_numpy(float))-ck['mean'])/ck['scale'],device=device(),dtype=torch.float32)
            with torch.no_grad():
                p=torch.softmax(h(x),-1);h.load_state_dict(torch.load(path,map_location=device(),weights_only=False)['head']);q=torch.cat([torch.softmax(h(b),-1) for b in x.split(6)])
                torch.testing.assert_close(p,q,atol=2e-6,rtol=2e-5);assert torch.equal(p.argmax(1),q.argmax(1));maxdiff=max(maxdiff,float((p-q).abs().max()))
            prob=p.cpu().numpy()
            for i,r in enumerate(frame[IDENTITY].to_dict('records')):rows.append({**r,**ck['job'],'classes_json':json.dumps(ck['classes']),**{f'p{j}':float(prob[i,j]) for j in range(6)}})
        jobs=pd.DataFrame(jobs)
        for _,g in jobs.groupby('seed'):assert g.initial_hash.nunique()==1 and g.schedule_hash.nunique()==1
        checks.append({'scenario':folder.name,'mode':mode,'passed':True,'models':len(jobs)})
    p=save(mode+'-predictions',rows);assert len(p)==total*24 and not p.duplicated(['scenario','seed','arm','session_id']).any()
    save(mode+'-classifier-audit',checks)
    write(OUT/(mode+'-prediction-seal.json'),{'passed':True,'rows':len(p),'models':total,'cuda':True,'labels_read':False,'test_pre_read':False,'max_replay_difference':maxdiff,
        'predictions_hash':sha(OUT/(mode+'-predictions.parquet')),'H_post_inputs':inputs})
    print(mode,'predictions sealed',len(p),flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--stage',choices=['engineering','restricted','infer','reference','infer-reference'],required=True);a=p.parse_args();freeze()
    if a.stage=='engineering':engineering()
    elif a.stage in ['restricted','reference']:train(a.stage=='reference')
    else:infer(a.stage=='infer-reference')
