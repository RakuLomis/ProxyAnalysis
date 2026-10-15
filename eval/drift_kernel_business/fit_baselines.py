"""CUDA fixed LR and MLP; reads training post visits only."""
import torch.nn.functional as F
from common import *

def lr_fit(x,y):
    w=torch.nn.Parameter(torch.zeros((6,96),device=cuda(),dtype=torch.float64))
    b=torch.nn.Parameter(torch.zeros(6,device=cuda(),dtype=torch.float64))
    opt=torch.optim.LBFGS([w,b],max_iter=500,tolerance_grad=1e-9,tolerance_change=1e-12,line_search_fn='strong_wolfe')
    evaluations=0
    def closure():
        nonlocal evaluations
        evaluations+=1
        opt.zero_grad()
        loss=F.cross_entropy(x@w.T+b,y)+.0005*w.square().sum()
        loss.backward()
        return loss
    opt.step(closure)
    final=float(closure().detach())
    gradient=max(float(w.grad.abs().max()),float(b.grad.abs().max()))
    state=opt.state[w]
    return {'weight':w.detach(),'bias':b.detach()}, {'iterations':int(state.get('n_iter',0)),
           'closure_evaluations':evaluations,'objective':final,'max_gradient':gradient,
           'hit_iteration_budget':int(state.get('n_iter',0))>=500}

def mlp_fit(x,y,seed):
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    net=torch.nn.Sequential(torch.nn.Linear(96,32),torch.nn.ReLU(),torch.nn.Linear(32,6)).to(cuda())
    opt=torch.optim.AdamW(net.parameters(),lr=1e-3,weight_decay=1e-4)
    for step in range(1000):
        opt.zero_grad(set_to_none=True)
        loss=F.cross_entropy(net(x),y)
        loss.backward()
        opt.step()
    return {'w1':net[0].weight.detach(),'b1':net[0].bias.detach(),
            'w2':net[2].weight.detach(),'b2':net[2].bias.detach()}, {'updates':1000,'final_training_CE':float(F.cross_entropy(net(x),y).detach())}

def run():
    c=start('baseline_fit')
    torch.set_num_threads(1)
    torch.backends.cuda.matmul.allow_tf32=False
    torch.backends.cudnn.allow_tf32=False
    torch.use_deterministic_algorithms(True)
    times=[]
    for role in c['roles']:
        fold,p=role['fold'],role['protocol']
        folder=modelfolder(fold,p)
        done=folder/'complete.json'
        if done.exists():
            for name,h in read(done)['sha256'].items():
                require(sha(folder/name)==h,'Saved model changed')
            print('resume complete',p,fold,flush=True)
            continue
        frame=load_package(rolefolder(fold,p)/'fit-post-hist.parquet','baseline_fit')
        raw=tensor(frame[HIST])
        mu=raw.mean(0)
        scale=raw.std(0,unbiased=False)
        scale=torch.where(scale>0,scale,torch.ones_like(scale))
        x=(raw-mu)/scale
        y=tensor(frame.label_id.map({v:i for i,v in enumerate(LABELS)}),torch.int64)
        started=time.perf_counter()
        state,log=lr_fit(x,y)
        torch.cuda.synchronize()
        log.update({'fold':fold,'protocol':p,'arm':'G1','seconds':time.perf_counter()-started,'device':'cuda:0'})
        torch.save({'mu':mu,'scale':scale,**state},folder/'G1.pt')
        logs=[log]
        for seed in SEEDS:
            started=time.perf_counter()
            state,log=mlp_fit(x.float(),y,seed)
            torch.cuda.synchronize()
            log.update({'fold':fold,'protocol':p,'arm':'G2','seed':seed,'seconds':time.perf_counter()-started,'device':'cuda:0'})
            torch.save({'mu':mu,'scale':scale,**state},folder/f'G2-{seed}.pt')
            logs.append(log)
        hashes={q.name:sha(q) for q in folder.glob('*.pt')}
        write(done,{'sha256':hashes,'fits':logs,'source_sha256':c['source_sha256']})
        times.extend(logs)
        print('CUDA LR + three 1000-update MLPs',p,fold,flush=True)
    # Read completion records for resumed tasks as well, rather than lose their ledger.
    allfits=[fit for r in c['roles'] for fit in read(modelfolder(r['fold'],r['protocol'])/'complete.json')['fits']]
    finish('baseline_fit',fits=allfits,LR_models=20,MLP_models=60,test_files_opened=0)

if __name__=='__main__':
    run()
