"""Resumable sealed P3 production. Frozen inference has post-only capability."""
import argparse
import json
import time
from p3_common import *
from p3_model import fit, sample


def generate():
    authorize();count=0;start=time.perf_counter()
    for jp in sorted((OUT/'generator-roles').glob('*.json')):
        job=read(jp)
        for arm,(method,kind) in GENERATORS.items():
            dest=OUT/'generation'/job['job']/arm
            if not completed(dest):
                dest.mkdir(parents=True,exist_ok=True)
                pre,post,query,reads=generator_frames(job,method,kind)
                model,pool,logs,canon,oof=fit(pre,post,kind,method)
                torch.save(model.state(),dest/'model.pt');np.save(dest/'residual-pool.npy',pool.cpu().numpy())
                write(dest/'loco.json',logs)
                np.savez_compressed(dest/'loco-latent.npz',
                    predictions=np.concatenate([v['prediction'] for v in oof]),
                    targets=np.concatenate([v['target'] for v in oof]),
                    content_ids=np.concatenate([np.repeat(v['content_id'],4) for v in oof]))
                effects=[]
                for seed in SEEDS:
                    values,eff,draw=sample(model,pool,query,job['job'],seed)
                    if arm=='D0_pair':
                        with np.load(LATEST/'generation'/job['job']/'paired'/f'samples-{seed}.npz',allow_pickle=False) as prior:
                            np.testing.assert_array_equal(values,prior['values']);np.testing.assert_array_equal(draw,prior['donor_indices'])
                    np.savez_compressed(dest/f'samples-{seed}.npz',values=values,session_ids=query.session_id.to_numpy(dtype=str),donor_indices=draw)
                    effects.append({'seed':seed,**eff})
                if arm=='D0_pair':
                    np.testing.assert_array_equal(pool.cpu().numpy(),np.load(LATEST/'generation'/job['job']/'paired/residual-pool.npy'))
                # Frozen distribution diagnostic only, no new classifier views.
                a=query[W].to_numpy(float);aux=query[AUX].to_numpy(float) if method!='D0' else None
                latent=model.predict(a,aux);raw,_=wm.decode(latent)
                allraw,_=wm.decode(latent[:,None,:]+pool[None,:,:])
                q=torch.quantile(allraw.to(torch.float64),torch.tensor([.025,.975],device=latent.device,dtype=torch.float64),dim=1)
                np.savez_compressed(dest/'distribution.npz',session_ids=query.session_id.to_numpy(dtype=str),
                    latent_center=latent.cpu().numpy(),raw_center=raw.cpu().numpy(),raw_low=q[0].cpu().numpy(),raw_high=q[1].cpu().numpy())
                write(dest/'decoder-effects.json',effects)
                complete(dest,{'job':job['job'],'arm':arm,'method':method,'kind':kind,'cuda':True,'Ridge_fits':19,
                    'reads':reads,'fit_sessions':job['fit_sessions'],'query_sessions':job['query_sessions'],'query_post_reads':0,
                    'test_reads':0,'redraws':0,'beta':model.beta.cpu().tolist(),
                    'center_column_space_relative_error':model.center_column_space_relative_error,
                    'D0_exact_replay':arm=='D0_pair'})
            count+=1
            if count%25==0:
                print('generation',count,'/500 elapsed',round(time.perf_counter()-start,1),flush=True)
                write(OUT/'generation-progress.json',{'complete':count,'total':500})
    assert count==500
    write(OUT/'generation-complete.json',{'complete':500,'Ridge_fits':9500,'D0_all100_replayed':True,'seal_sha256':file_hash(OUT/'seal.json')})


def generated(role,arm,seed,ids):
    data={}
    for jp in sorted((OUT/'generator-roles').glob('*.json')):
        job=read(jp)
        if job['fold']!=role['fold']:continue
        assert set(job['fit_sessions'])|set(job['query_sessions'])<=set(role['train'])
        dest=OUT/'generation'/job['job']/arm;assert completed(dest)
        with np.load(dest/f'samples-{seed}.npz',allow_pickle=False) as f:
            for sid,value in zip(f['session_ids'],f['values']):
                assert str(sid) not in data;data[str(sid)]=value
    assert set(data)==set(ids);return np.stack([data[sid] for sid in ids])


def classifiers(role):
    post=Bundle(OUT/'packages/training'/role['scenario'],'classifier').get('post')
    assert set(post.session_id)==set(role['train'])
    mu,sd=LE.scaler(post);classes=sorted(post.label_id.unique());y=np.array([classes.index(v) for v in post.label_id])
    a=post[W].to_numpy(float);states=[];arrays=[];indices=[];ys=[];draws=[];jobs=[]
    for seed in SEEDS:
        torch.manual_seed(seed);state=LE.network().state_dict();ix=LE.schedule(post,seed)
        view=np.random.default_rng(seed).integers(0,8,ix.shape)
        for arm in ARMS:
            real=np.repeat(a[:,None,:],8,axis=1)
            aux=real if arm=='M0' else generated(role,arm,seed,post.session_id.tolist())
            arrays.append((np.log1p(np.concatenate([real,aux],axis=0))-mu)/sd)
            indices.append(np.concatenate([ix,ix+len(post)],axis=1));draws.append(np.concatenate([view,view],axis=1))
            ys.append(np.concatenate([y,y]));states.append({k:v.clone() for k,v in state.items()})
            jobs.append({'seed':seed,'arm':arm,'scenario':role['scenario'],
                'initial_hash':LC.digest({k:v.cpu().tolist() for k,v in state.items()}),
                'main_schedule_hash':LC.digest(ix.tolist()),'view_schedule_hash':LC.digest(view.tolist())})
    return LE.Heads(states).to(LC.device()),torch.tensor(np.stack(arrays),device=LC.device(),dtype=torch.float32),\
        torch.tensor(np.stack(indices),device=LC.device()),torch.tensor(np.stack(draws),device=LC.device()),\
        torch.tensor(np.stack(ys),device=LC.device()),jobs,mu,sd,classes


def train():
    authorize();assert read(OUT/'generation-complete.json')['complete']==500;count=0
    for rp in sorted((OUT/'roles').glob('*.json')):
        role=read(rp);dest=OUT/'models'/role['scenario']
        if not completed(dest):
            dest.mkdir(parents=True,exist_ok=True);h,x,ix,v,y,jobs,mu,sd,classes=classifiers(role)
            heads=torch.arange(18,device=LC.device());opt=torch.optim.Adam(h.parameters(),lr=.001,foreach=False)
            losses=[];start=time.perf_counter()
            for step in range(1000):
                opt.zero_grad(set_to_none=True);batch=x[heads[:,None],ix[:,step],v[:,step]]
                target=y[heads[:,None],ix[:,step]];loss=h.loss(batch,target);assert torch.isfinite(loss).all()
                loss.sum().backward();opt.step();losses.append(loss.detach())
            torch.cuda.synchronize()
            torch.save({'states':[h.one(i) for i in range(18)],'jobs':jobs,'mean':mu,'scale':sd,'classes':classes,
                        'scaler_fit_sessions':role['train']},dest/'models.pt')
            np.save(dest/'losses.npy',torch.stack(losses).cpu().numpy())
            complete(dest,{'classifiers':18,'cuda':True,'steps':1000,'test_reads':0,'train_sessions':role['train'],
                           'seconds':time.perf_counter()-start,'peak_cuda_bytes':torch.cuda.max_memory_allocated()})
        count+=18;write(OUT/'training-progress.json',{'complete':count,'total':90});print('classifiers',count,'/90',flush=True)
    write(OUT/'training-complete.json',{'classifiers':count,'seal_sha256':file_hash(OUT/'seal.json')})


def infer():
    authorize();assert read(OUT/'training-complete.json')['classifiers']==90
    assert not (OUT/'prediction-seal.json').exists();rows=[]
    for rp in sorted((OUT/'roles').glob('*.json')):
        role=read(rp);dest=OUT/'models'/role['scenario'];assert completed(dest)
        ck=torch.load(dest/'models.pt',map_location=LC.device(),weights_only=False)
        assert set(ck['scaler_fit_sessions'])==set(role['train'])
        test=Bundle(OUT/'packages/inference'/role['scenario'],'inference').get('test_post')
        assert set(test)=={'session_id',*W} and set(test.session_id)==set(role['test'])
        x=torch.tensor((np.log1p(test[W].to_numpy(float))-ck['mean'])/ck['scale'],device=LC.device(),dtype=torch.float32)
        h=LE.Heads(ck['states']).to(LC.device()).eval()
        with torch.no_grad():p=h(x[None].expand(18,-1,-1)).softmax(-1).cpu().numpy()
        for i,job in enumerate(ck['jobs']):
            rows.extend({'session_id':sid,**job,'fold':role['fold'],'classes_json':json.dumps(ck['classes']),
                **{f'p{k}':float(p[i,j,k]) for k in range(6)}} for j,sid in enumerate(test.session_id))
    result=pd.DataFrame(rows);assert len(result)==10800
    assert not result.duplicated(['arm','seed','session_id']).any()
    result.to_parquet(OUT/'predictions.parquet',index=False)
    write(OUT/'prediction-seal.json',{'rows':10800,'cuda':True,'labels_read':False,'test_pre_read':False,
        'sha256':file_hash(OUT/'predictions.parquet'),'seal_sha256':file_hash(OUT/'seal.json')})
    print('post-only CUDA inference complete',flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('stage',choices=['generate','train','infer'])
    {'generate':generate,'train':train,'infer':infer}[parser.parse_args().stage]()
