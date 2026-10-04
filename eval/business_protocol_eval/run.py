"""Budget-gated production worker. Engineering alone never authorizes a run."""
import argparse
import pandas as pd
import time
from common import *
from packages import Bundle
from generation import generate_query,sample_query,allowed_generator_jobs,torch
from learning import Heads,network,scaler,schedule,independent_pre_schedule

ARMS={'M2':'paired','M3':'group','M4':'cyclic'}


def authorize():
    contract=read(OUT/'contract.json')
    auth=OUT/'authorization.json'
    if not auth.exists():raise PermissionError('Gate B requires explicit user approval before production')
    record=read(auth)
    assert record['formal_training_allowed'] is True
    assert record['contract_sha256']==file_hash(OUT/'contract.json')
    assert record['classifier_budget']==525
    check_files(contract['code_hashes'])
    check_files(contract['artifact_hashes'])
    device();torch.backends.cuda.matmul.allow_tf32=False
    torch.backends.cudnn.allow_tf32=False
    return contract


def completed(folder):
    path=folder/'complete.json'
    if not path.exists():return False
    done=read(path);assert done['contract_sha256']==file_hash(OUT/'contract.json')
    for name,h in done['files'].items():assert file_hash(folder/name)==h
    return True


def seal(folder,metadata):
    write(folder/'complete.json',{**metadata,'contract_sha256':file_hash(OUT/'contract.json'),
         'files':{p.name:file_hash(p) for p in folder.iterdir() if p.is_file() and p.name!='complete.json'}})


def generate():
    authorize();count=0
    for path in sorted((OUT/'generator-roles').glob('*.json')):
        job=read(path)
        for kind in ARMS.values():
            dest=OUT/'generation'/job['job']/kind
            if not completed(dest):
                dest.mkdir(parents=True,exist_ok=True)
                result=generate_query(job,kind,SEEDS[0]);query=result['query']
                torch.save(result['model'].state(),dest/'model.pt')
                np.save(dest/'residual-pool.npy',result['pool'].cpu().numpy())
                write(dest/'loco.json',result['loco'])
                effects=[]
                for seed in SEEDS:
                    values,audit,draw=sample_query(result['model'],result['pool'],query,job['job'],seed)
                    np.savez_compressed(dest/f'samples-{seed}.npz',values=values,
                                        session_ids=query.session_id.to_numpy(dtype=str),donor_indices=draw)
                    effects.append({'seed':seed,**audit})
                write(dest/'decoder-effects.json',effects)
                seal(dest,{'job':job['job'],'kind':kind,'cuda':True,'ridge_fits':19,'reads':result['access'],
                           'fit_sessions':job['fit_sessions'],'query_sessions':job['query_sessions'],
                           'test_reads':0,'redraws':0})
            count+=1
            write(OUT/'generation-progress.json',{'complete':count,'total':300})
            print(f'Generation {count}/300',flush=True)


def generated_for(role,arm,seed,session_ids):
    data={}
    for name in allowed_generator_jobs(role):
        dest=OUT/'generation'/name/ARMS[arm];assert completed(dest)
        done=read(dest/'complete.json')
        assert set(done['fit_sessions'])|set(done['query_sessions']) <= set(role['train'])
        with np.load(dest/f'samples-{seed}.npz',allow_pickle=False) as f:
            for sid,values in zip(f['session_ids'],f['values']):
                assert str(sid) not in data;data[str(sid)]=values
    assert set(data)==set(session_ids)
    return np.stack([data[sid] for sid in session_ids])


def prepare_classifiers(role):
    name=role['scenario'];only=role['experiment']=='I0'
    bundle=Bundle(OUT/'packages/training'/name,'I0' if only else 'M1')
    post=bundle.get('post');assert set(post.session_id)==set(role['train'])
    pre=None if only else bundle.get('pre_unpaired')
    mu,sd=scaler(post);classes=sorted(post.label_id.unique());y=np.array([classes.index(v) for v in post.label_id])
    a=post[FEATURES].to_numpy(float);states=[];arrays=[];indices=[];ys=[];draws=[];jobs=[]
    for seed in SEEDS:
        torch.manual_seed(seed);state=network().state_dict()
        ix=schedule(post,seed);px=ix if only else independent_pre_schedule(post,pre,ix)
        rng=np.random.default_rng(seed);view=rng.integers(0,8,ix.shape)
        for arm in (['I0'] if only else ['M0','M1','M2','M3','M4']):
            real=np.repeat(a[:,None,:],8,axis=1)
            if arm in ['M0','I0']:aux=real;ax=ix;ay=y
            elif arm=='M1':
                aux=np.repeat(pre[FEATURES].to_numpy(float)[:,None,:],8,axis=1);ax=px
                ay=np.array([classes.index(v) for v in pre.label_id])
            else:aux=generated_for(role,arm,seed,post.session_id.tolist());ax=ix;ay=y
            arr=np.concatenate([real,aux],axis=0)
            arrays.append((np.log1p(arr)-mu)/sd)
            indices.append(np.concatenate([ix,ax+len(post)],axis=1))
            draws.append(np.concatenate([view,view],axis=1));ys.append(np.concatenate([y,ay]))
            states.append({k:v.clone() for k,v in state.items()})
            jobs.append({'seed':seed,'arm':arm,'scenario':name,'initial_hash':digest({k:v.cpu().tolist() for k,v in state.items()}),
                         'main_schedule_hash':digest(ix.tolist()),'view_schedule_hash':digest(view.tolist())})
    return (Heads(states).to(device()),torch.tensor(np.stack(arrays),device=device(),dtype=torch.float32),
            torch.tensor(np.stack(indices),device=device()),torch.tensor(np.stack(draws),device=device()),
            torch.tensor(np.stack(ys),device=device()),jobs,mu,sd,classes)


def train():
    authorize();count=0
    for path in sorted((OUT/'roles').glob('*.json')):
        role=read(path);dest=OUT/'models'/role['scenario']
        if completed(dest):count+=read(dest/'complete.json')['classifiers'];continue
        dest.mkdir(parents=True,exist_ok=True)
        h,x,ix,v,y,jobs,mu,sd,classes=prepare_classifiers(role)
        heads=torch.arange(len(jobs),device=device());opt=torch.optim.Adam(h.parameters(),lr=.001,foreach=False)
        losses=[];started=time.perf_counter()
        for step in range(1000):
            opt.zero_grad(set_to_none=True)
            batch=x[heads[:,None],ix[:,step],v[:,step]];target=y[heads[:,None],ix[:,step]]
            loss=h.loss(batch,target);assert torch.isfinite(loss).all()
            loss.sum().backward();opt.step();losses.append(loss.detach())
        torch.cuda.synchronize()
        torch.save({'states':[h.one(i) for i in range(len(jobs))],'jobs':jobs,'mean':mu,'scale':sd,'classes':classes,
                    'scaler_fit_sessions':role['train']},dest/'models.pt')
        np.save(dest/'losses.npy',torch.stack(losses).cpu().numpy())
        seal(dest,{'classifiers':len(jobs),'cuda':True,'steps':1000,'test_reads':0,
                   'seconds':time.perf_counter()-started,'train_sessions':role['train']})
        count+=len(jobs);write(OUT/'training-progress.json',{'complete':count,'total':525})
        print(f'Classifiers {count}/525',flush=True)
    assert count==525
    write(OUT/'training-complete.json',{'classifiers':count,'contract_sha256':file_hash(OUT/'contract.json')})


def infer():
    authorize();assert read(OUT/'training-complete.json')['classifiers']==525
    assert not (OUT/'prediction-seal.json').exists()
    rows=[]
    for path in sorted((OUT/'roles').glob('*.json')):
        role=read(path);dest=OUT/'models'/role['scenario'];assert completed(dest)
        ck=torch.load(dest/'models.pt',map_location=device(),weights_only=False)
        assert set(ck['scaler_fit_sessions'])==set(role['train'])
        test=Bundle(OUT/'packages/inference'/role['scenario'],'inference').get('test_post')
        assert list(test)==['session_id',*FEATURES] and set(test.session_id)==set(role['test'])
        x=torch.tensor((np.log1p(test[FEATURES].to_numpy(float))-ck['mean'])/ck['scale'],device=device(),dtype=torch.float32)
        h=Heads(ck['states']).to(device()).eval()
        with torch.no_grad():p=h(x[None].expand(len(ck['jobs']),-1,-1)).softmax(-1).cpu().numpy()
        for i,job in enumerate(ck['jobs']):
            rows.extend({'session_id':sid,**job,'experiment':role['experiment'],'target':role['target'],
                         'fold':role['fold'],'classes_json':__import__('json').dumps(ck['classes']),
                         **{f'p{k}':float(p[i,j,k]) for k in range(6)}} for j,sid in enumerate(test.session_id))
    result=pd.DataFrame(rows);assert len(result)==19800
    assert not result.duplicated(['scenario','seed','arm','session_id']).any()
    path=OUT/'predictions.parquet';result.to_parquet(path,index=False)
    write(OUT/'prediction-seal.json',{'rows':len(result),'cuda':True,'labels_read':False,'test_pre_read':False,
          'sha256':file_hash(path),'contract_sha256':file_hash(OUT/'contract.json')})


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('stage',choices=['generate','train','infer'])
    {'generate':generate,'train':train,'infer':infer}[parser.parse_args().stage]()
