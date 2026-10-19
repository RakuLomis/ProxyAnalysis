"""CUDA graph-capable exact Adam state and model-wise clipping; no data loaders."""
from common import *
from models import Tensorized,Independent
from types import SimpleNamespace

class Engine:
    def __init__(self,data,jobs,backend='tensorized',states=None,adam=None,update_G=True,update_head=True):
        require(jobs and len({j['recipe']['lr'] for j in jobs})==1,'Each numerical bucket has one lr')
        require(backend in {'tensorized','independent','streams'},'Unknown numerical backend')
        cls=Tensorized if backend=='tensorized' else Independent
        self.net=cls(data,jobs,states,update_G,update_head);self.backend=backend;self.jobs=jobs
        settings=dict(lr=jobs[0]['recipe']['lr'],betas=(.9,.999),eps=1e-8,weight_decay=0,foreach=False,capturable=True)
        if backend=='streams':
            self.streams=[torch.cuda.Stream() for _ in range(min(8,len(jobs)))]
            self.optimizers=[torch.optim.Adam([p for p in self.net.state_head(i).values() if p.requires_grad],**settings) for i in range(len(jobs))]
            self.opt=SimpleNamespace(state={})
        else:self.opt=torch.optim.Adam([p for p in self.net.parameters() if p.requires_grad],**settings)
        # Preallocate state and gradients to avoid allocation/lazy H2D inside capture.
        for name,p in self.net.named_parameters():
            if p.requires_grad:
                if backend=='streams':
                    i=int(name.split('_')[0][1:]);state=self.optimizers[i].state[p];self.opt.state[p]=state
                else:state=self.opt.state[p]
                state['step']=torch.zeros((),device='cuda',dtype=torch.float32)
                state['exp_avg']=torch.zeros_like(p);state['exp_avg_sq']=torch.zeros_like(p);p.grad=torch.zeros_like(p)
        self.graph=None;self.steps=0;self.values=None;self.parts=None;self.norms=None
        self.clip_count=torch.zeros(len(jobs),device='cuda',dtype=torch.int64)
        self.frozen_adam=[{} for _ in jobs]
        if adam is not None:self.restore_adam(adam)
    def step(self):
        if self.backend=='streams':return self.stream_step()
        self.opt.zero_grad(set_to_none=False)
        if self.backend=='independent':values,parts=self.net.backward_step()
        else:
            values,parts=self.net.objective();values.sum().backward()
        norms=self.net.clip();self.opt.step()
        self.net.bad.logical_or_(~torch.isfinite(values))
        self.values=values.detach();self.parts=parts.detach();self.norms=norms.detach()
        self.clip_count.add_((self.norms>5).long())
    def stream_step(self):
        # Same per-model F.linear, backward, clip and Adam arithmetic as reference;
        # only independent model work is scheduled concurrently. Fork and join are
        # inside capture, making the graph's stream dependencies explicit.
        root=torch.cuda.current_stream();values=[];parts=[];norms=[]
        for stream in self.streams:stream.wait_stream(root)
        from models import loss_one
        for i,(d,j,opt) in enumerate(zip(self.net.data,self.jobs,self.optimizers)):
            with torch.cuda.stream(self.streams[i%len(self.streams)]):
                opt.zero_grad(set_to_none=False);s=self.net.state_head(i)
                value,part=loss_one(s,d,j['recipe']);value.backward()
                ps=[p for p in s.values() if p.requires_grad]
                norm=sum(p.grad.double().square().sum() for p in ps).sqrt()
                factor=(5/norm.clamp_min(1e-30)).clamp_max(1)
                for p in ps:p.grad.mul_(factor.to(p.dtype))
                opt.step();self.net.bad[i].logical_or_(~torch.isfinite(norm)|~torch.isfinite(value))
                values.append(value.detach());parts.append(torch.stack(part).detach());norms.append(norm.detach())
        for stream in self.streams:root.wait_stream(stream)
        self.values=torch.stack(values);self.parts=torch.stack(parts);self.norms=torch.stack(norms)
        self.clip_count.add_((self.norms>5).long())
    def healthy(self):
        require(not bool(self.net.bad.any()),'Nonfinite loss/gradient recorded; no automatic retry')
        require(all(bool(torch.isfinite(p).all()) for p in self.net.parameters()),'Nonfinite parameters')
    def adam_head(self,i):
        out={}
        for k in KEYS:
            p=getattr(self.net,k) if self.backend=='tensorized' else getattr(self.net,f'h{i}_{k}')
            if p not in self.opt.state:
                if k in self.frozen_adam[i]:out[k]={name:value.detach().clone() for name,value in self.frozen_adam[i][k].items()}
                continue
            z=self.opt.state[p]
            out[k]={name:(value.detach().clone() if name=='step' or self.backend!='tensorized' else value[i].detach().clone()) for name,value in z.items()}
        return out
    def restore_adam(self,heads):
        for i,head in enumerate(heads):
            for k,s in head.items():
                p=getattr(self.net,k) if self.backend=='tensorized' else getattr(self.net,f'h{i}_{k}')
                if not p.requires_grad:
                    self.frozen_adam[i][k]={name:value.detach().clone() for name,value in s.items()}
                    continue
                dest=self.opt.state[p]
                for name,val in s.items():
                    if self.backend=='tensorized' and name!='step':dest[name][i].copy_(val)
                    else:
                        if self.backend=='tensorized' and i>0:require(torch.equal(dest[name],val),'Mixed Adam ages')
                        dest[name].copy_(val)
        self.steps=max(int(float(v['step'])) for head in heads for v in head.values())
    def snapshot_all(self):return [self.net.snapshot(i) for i in range(self.net.count)]
    def capture(self):
        require(self.graph is None,'Already captured')
        params={n:p.detach().clone() for n,p in self.net.named_parameters()}
        opts={n:{k:v.detach().clone() for k,v in self.opt.state[p].items()} for n,p in self.net.named_parameters() if p.requires_grad}
        clip_initial=self.clip_count.clone()
        def reset():
            with torch.no_grad():
                for n,p in self.net.named_parameters():
                    p.copy_(params[n])
                    if p.requires_grad:
                        p.grad.zero_()
                        for k,v in opts[n].items():self.opt.state[p][k].copy_(v)
                self.net.bad.zero_()
                self.clip_count.copy_(clip_initial)
        stream=torch.cuda.Stream();stream.wait_stream(torch.cuda.current_stream())
        with torch.cuda.stream(stream):
            for _ in range(3):self.step()
        torch.cuda.current_stream().wait_stream(stream);torch.cuda.synchronize();reset()
        g=torch.cuda.CUDAGraph()
        with torch.cuda.graph(g):self.step()
        torch.cuda.synchronize();reset();self.graph=g
    def advance(self,n,check_every=50):
        for j in range(n):
            if self.graph is None:self.step()
            else:self.graph.replay()
            self.steps+=1
            if check_every and (j+1)%check_every==0:self.healthy()
        self.healthy()
    def checkpoint(self):
        return dict(parameters=self.snapshot_all(),adam=[self.adam_head(i) for i in range(self.net.count)],steps=self.steps)

def fit_train_only(data,jobs,backend='independent',cuda_graph=True,steps=2000,midpoint=1000,states=None,adam=None,
                   update_G=True,update_head=True,progress_callback=None):
    """No query argument, no validation risk, same selected endpoint after fixed steps."""
    engine=Engine(data,jobs,backend,states,adam,update_G,update_head)
    if cuda_graph:engine.capture()
    initial=engine.steps;trace=[];middle=None
    stops=sorted(set([s for s in [1,10,100,500,midpoint,1500,2000] if initial<s<=initial+steps]+[initial+steps]))
    for endpoint in stops:
        engine.advance(endpoint-engine.steps)
        with torch.no_grad():loss,parts=engine.net.objective()
        trace.append(dict(step=endpoint,objective=cpu(loss).tolist(),parts=cpu(parts).tolist(),
                          gradient_norm=cpu(engine.norms).tolist()))
        if endpoint==midpoint:middle=engine.checkpoint()
        if progress_callback:progress_callback(endpoint)
    return dict(midpoint=middle,terminal=engine.checkpoint(),trace=trace)
