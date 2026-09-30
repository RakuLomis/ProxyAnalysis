"""CUDA batched independent heads. No evaluation package or exporter imports."""
import sys,time,argparse
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'src'))
from proxy_analysis.calibration_budget.common import *
from proxy_analysis.conditional_drift.model import device,torch

ARMS=[f'B{i}' for i in range(6)]

class Heads(torch.nn.Module):
    def __init__(self,states):
        super().__init__()
        self.w1=torch.nn.Parameter(torch.stack([s['0.weight'] for s in states]));self.b1=torch.nn.Parameter(torch.stack([s['0.bias'] for s in states]))
        self.w2=torch.nn.Parameter(torch.stack([s['2.weight'] for s in states]));self.b2=torch.nn.Parameter(torch.stack([s['2.bias'] for s in states]))
    def forward(self,x):return torch.bmm(torch.relu(torch.bmm(x,self.w1.transpose(1,2))+self.b1[:,None,:]),self.w2.transpose(1,2))+self.b2[:,None,:]
    def loss(self,x,y):
        logits=self(x);ce=-torch.log_softmax(logits,-1).gather(-1,y[:,:,None]).squeeze(-1).mean(1)
        loss=ce+.5*1e-4*(self.w1.square().sum((1,2))+self.w2.square().sum((1,2)))
        return loss,ce
    def one(self,index):return {'0.weight':self.w1[index].detach().clone(),'0.bias':self.b1[index].detach().clone(),'2.weight':self.w2[index].detach().clone(),'2.bias':self.b2[index].detach().clone()}

def freeze():
    assert read(OUT/'permission-gate.json')['passed'] and read(OUT/'generation-gate.json')['passed']
    assert read(OUT/'generation-permission-audit.json')['passed']
    for path,h in read(OUT/'worker-contract.json')['inputs'].items():assert sha(path)==h
    files=[Path(__file__),CONFIG,OUT/'worker-contract.json',OUT/'generation-gate.json',
       *list((OUT/'generation').glob('*/complete.json'))]
    contract={'files':{str(p):sha(p) for p in files},'tasks':2160,'independent_batch_heads':18,'shared_parameters':False,
        'steps':1000,'device':'cuda','dtype':'float32','scale':'C_pre_only','test_packages_available_to_loader':False}
    path=OUT/'training-contract.json'
    if path.exists():assert read(path)==contract
    else:write(path,contract)

def prepare(folder):
    bundle=TrainingBundle(folder);meta=bundle.manifest;C=bundle.get('C_pre');Cp=bundle.get('C_post');U=bundle.get('U_pre');labels=bundle.get('labels')
    source=pd.concat([C,U]).sort_values('session_id').reset_index(drop=True).merge(labels,on='session_id',validate='one_to_one')
    assert len(source)==96 and set(source.session_id)==set(meta['C_sessions'])|set(meta['U_sessions'])
    classes=sorted(source.label_id.unique());assert len(classes)==6
    mean=np.log1p(C[NUMERIC].to_numpy(float)).mean(0);scale=np.log1p(C[NUMERIC].to_numpy(float)).std(0);scale[scale<1e-10]=1
    cpost=Cp.set_index('session_id');lookup={s:i for i,s in enumerate(source.session_id)}
    states=[];arrays=[];all_indices=[];all_views=[];jobs=[];y=np.array([classes.index(v) for v in source.label_id]);cfg=config();dev=device()
    for seed in cfg['seeds']:
        torch.manual_seed(seed);base=torch.nn.Sequential(torch.nn.Linear(7,32),torch.nn.ReLU(),torch.nn.Linear(32,6)).to(dev)
        initial=base.state_dict();rng=np.random.default_rng(seed)
        groups={label:sorted(g.content_id.unique()) for label,g in source.groupby('label_id')}
        for group in groups.values():rng.shuffle(group)
        cgroups={label:[c for c in group if c in meta['C_contents']] for label,group in groups.items()}
        assert all(len(v)==meta['k'] for v in cgroups.values())
        ids={c:np.flatnonzero(source.content_id.to_numpy()==c) for group in groups.values() for c in group}
        shared=np.stack([np.concatenate([ids[groups[label][step%4]] for label in classes]) for step in range(1000)])
        c_only=np.stack([np.concatenate([ids[cgroups[label][step%meta['k']]] for label in classes]) for step in range(1000)])
        assert np.bincount(shared.ravel(),minlength=96).tolist()==[250]*96
        counts=np.bincount(c_only.ravel(),minlength=96);mask=source.session_id.isin(meta['C_sessions']).to_numpy()
        assert (counts[~mask]==0).all() and counts[mask].max()-counts[mask].min()<=1
        draws=rng.integers(0,8,(1000,24))
        path=OUT/'generation'/meta['scenario']/f'samples-{seed}.parquet'
        generation_done=read(path.parent/'complete.json');assert sha(path)==generation_done['files'][str(path)]
        samples=pd.read_parquet(path).set_index(['arm','session_id','view'])
        for arm in ARMS:
            arr=np.zeros((96,8,7),float)
            for r in source.to_dict('records'):
                sid=r['session_id'];i=lookup[sid]
                if sid in meta['C_sessions']:arr[i]=cpost.loc[sid,NUMERIC].to_numpy(float)
                elif arm=='B1':arr[i]=np.array([r[c] for c in NUMERIC])
                elif arm!='B0':arr[i]=samples.loc[(arm,sid)].sort_index()[NUMERIC].to_numpy(float)
            index=c_only if arm=='B0' else shared
            states.append({k:v.clone() for k,v in initial.items()});arrays.append((np.log1p(arr)-mean)/scale)
            all_indices.append(index);all_views.append(draws)
            jobs.append({'scenario':meta['scenario'],'protocol':meta['protocol'],'fold':meta['fold'],'k':meta['k'],'rotation':meta['rotation'],
                'seed':seed,'arm':arm,'initial_hash':objhash({k:v.cpu().tolist() for k,v in initial.items()}),
                'schedule_hash':objhash([index.tolist(),draws.tolist()])})
    model=Heads(states).to(dev)
    return model,torch.tensor(np.stack(arrays),device=dev,dtype=torch.float32),torch.tensor(y,device=dev),torch.tensor(np.stack(all_indices),device=dev),torch.tensor(np.stack(all_views),device=dev),jobs,mean,scale,classes,meta,bundle.access

def engineering():
    values=prepare(sorted((OUT/'bundles').iterdir())[0]);model,x,y,index,view,*_=values
    selected=torch.arange(18,device=device());batch=x[selected[:,None],index[:,0],view[:,0]];target=y[index[:,0]]
    refs=[]
    for i in range(18):
        h=torch.nn.Sequential(torch.nn.Linear(7,32),torch.nn.ReLU(),torch.nn.Linear(32,6)).to(device());h.load_state_dict(model.one(i));refs.append(h)
    opt=torch.optim.Adam(model.parameters(),lr=.001,foreach=False);opts=[torch.optim.Adam(h.parameters(),lr=.001,foreach=False) for h in refs]
    maxlogit=0.;maxweight=0.
    for step in range(5):
        opt.zero_grad(set_to_none=True);loss,_=model.loss(batch,target);loss.sum().backward();opt.step()
        for i,(h,o) in enumerate(zip(refs,opts)):
            o.zero_grad(set_to_none=True);l=torch.nn.functional.cross_entropy(h(batch[i]),target[i])+.5e-4*sum(p.square().sum() for n,p in h.named_parameters() if n.endswith('weight'))
            l.backward();o.step()
        with torch.no_grad():
            expected=torch.stack([h(batch[i]) for i,h in enumerate(refs)]);actual=model(batch)
            torch.testing.assert_close(actual,expected,atol=2e-5,rtol=2e-4);maxlogit=max(maxlogit,float((actual-expected).abs().max()))
            for i,h in enumerate(refs):
                for key,v in model.one(i).items():
                    torch.testing.assert_close(v,h.state_dict()[key],atol=2e-5,rtol=2e-4);maxweight=max(maxweight,float((v-h.state_dict()[key]).abs().max()))
    # Model axis isolation: altering another model's inputs cannot affect model 0.
    with torch.no_grad():
        changed=batch.clone();changed[1:]+=100
        assert torch.equal(model(batch)[0],model(changed)[0])
    started=time.perf_counter()
    for step in range(100):
        opt.zero_grad(set_to_none=True);loss,_=model.loss(batch,target);loss.sum().backward();opt.step()
    torch.cuda.synchronize();elapsed=time.perf_counter()-started
    write(OUT/'cuda-engineering.json',{'passed':True,'cuda':True,'independent_heads':18,'comparison_steps':5,'max_logit_delta':maxlogit,'max_weight_delta':maxweight,
        'model_axis_isolated':True,'seconds_per_18head_step':elapsed/100,'estimated_training_seconds':elapsed/100*1000*120,'test_data_read':False})
    print(read(OUT/'cuda-engineering.json'),flush=True)

def train():
    assert read(OUT/'cuda-engineering.json')['passed'];folders=sorted((OUT/'bundles').iterdir());finished=0
    for folder in folders:
        name=folder.name;dest=OUT/'classifiers'/name;dest.mkdir(parents=True,exist_ok=True)
        if (dest/'complete.json').exists():
            saved=read(dest/'complete.json');assert saved['contract']==sha(OUT/'training-contract.json')
            for path,h in saved['files'].items():assert sha(path)==h
            finished+=18;continue
        model,x,y,index,views,jobs,mean,scale,classes,meta,access=prepare(folder)
        opt=torch.optim.Adam(model.parameters(),lr=.001,foreach=False);model.train();selector=torch.arange(18,device=device());losses=[];ces=[];started=time.perf_counter()
        for step in range(1000):
            opt.zero_grad(set_to_none=True);batch=x[selector[:,None],index[:,step],views[:,step]];target=y[index[:,step]]
            loss,ce=model.loss(batch,target);loss.sum().backward();opt.step();losses.append(loss.detach());ces.append(ce.detach())
            if (step+1)%100==0:assert torch.isfinite(loss).all()
        torch.cuda.synchronize();losses=torch.stack(losses).cpu().numpy();ces=torch.stack(ces).cpu().numpy();assert np.isfinite(losses).all()
        for i,job in enumerate(jobs):
            path=dest/f"s{job['seed']}-{job['arm']}.pt"
            torch.save({'head':model.one(i),'mean':mean,'scale':scale,'job':job,'classes':classes,
                'scaler_fit_sessions':meta['C_sessions'],'C_hash':meta['C_hash'],'contract':sha(OUT/'training-contract.json')},path)
        log=[]
        for i,job in enumerate(jobs):
            log.extend({**job,'step':s+1,'loss':float(losses[s,i]),'ce_nats':float(ces[s,i])} for s in range(1000))
        pd.DataFrame(log).to_parquet(dest/'training-log.parquet',index=False)
        write(dest/'complete.json',{'scenario':name,'contract':sha(OUT/'training-contract.json'),'cuda':True,'models':18,'steps_per_model':1000,
            'training_seconds':time.perf_counter()-started,'read_roles':access,'H_read':False,'U_post_read':False,
            'files':{str(p):sha(p) for p in dest.iterdir() if p.is_file()}})
        finished+=18;write(OUT/'training-progress.json',{'completed':finished,'total':2160,'status':'running'})
        print(name,finished,'/2160',flush=True)
        del model,opt,x,index,views;torch.cuda.empty_cache()
    write(OUT/'training-progress.json',{'completed':2160,'total':2160,'status':'complete'})

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--stage',choices=['engineering','train'],required=True);a=p.parse_args();freeze()
    if a.stage=='engineering':engineering()
    else:train()
