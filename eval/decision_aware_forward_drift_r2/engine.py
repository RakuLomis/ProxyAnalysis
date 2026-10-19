"""Independent Adam paths, fixed 2000 steps, replayable 32/8 CUDA graphs."""
from common import *
from model import initial,objective,KEYS

class Engine:
    def __init__(self,ds,jobs,streams=True):
        require(0<len(jobs)<=32 and len(ds)==len(jobs),'Independent batch size')
        self.ds=ds;self.jobs=jobs;self.steps=0;self.graph=None
        self.states=[{k:torch.nn.Parameter(v.clone()) for k,v in initial().items()} for _ in jobs]
        self.streams=[torch.cuda.Stream() for _ in range(min(8,len(jobs)))] if streams else []
        self.opts=[];self.bad=torch.zeros(len(jobs),device='cuda',dtype=torch.bool);self.clips=torch.zeros(len(jobs),device='cuda',dtype=torch.int64)
        for s in self.states:
            opt=torch.optim.Adam(list(s.values()),lr=.0003,betas=(.9,.999),eps=1e-8,foreach=False,capturable=True,weight_decay=0)
            for p in s.values():
                p.grad=torch.zeros_like(p);state=opt.state[p]
                state['step']=torch.zeros((),device='cuda',dtype=torch.float32);state['exp_avg']=torch.zeros_like(p);state['exp_avg_sq']=torch.zeros_like(p)
            self.opts.append(opt)
    def step(self):
        root=torch.cuda.current_stream()
        for st in self.streams:st.wait_stream(root)
        for i,(s,d,opt) in enumerate(zip(self.states,self.ds,self.opts)):
            stream=self.streams[i%len(self.streams)] if self.streams else root
            with torch.cuda.stream(stream):
                opt.zero_grad(set_to_none=False);v,parts=objective(s,d);v.backward()
                n=sum(p.grad.square().sum() for p in s.values()).sqrt();factor=(5/n.clamp_min(1e-30)).clamp_max(1)
                for p in s.values():p.grad.mul_(factor)
                self.bad[i].logical_or_(~torch.isfinite(v)|~torch.isfinite(n));self.clips[i].add_((n>5).long());opt.step()
        for st in self.streams:root.wait_stream(st)
    def snapshot(self):
        return dict(parameters=[{k:p.detach().clone() for k,p in s.items()} for s in self.states],
            gradients=[{k:p.grad.detach().clone() for k,p in s.items()} for s in self.states],
            adam=[{k:{a:v.detach().clone() for a,v in opt.state[p].items()} for k,p in s.items()} for s,opt in zip(self.states,self.opts)],
            clips=self.clips.clone(),steps=self.steps)
    def restore(self,ck):
        with torch.no_grad():
            for i,(s,opt) in enumerate(zip(self.states,self.opts)):
                for k,p in s.items():
                    p.copy_(ck['parameters'][i][k]);p.grad.copy_(ck['gradients'][i][k])
                    for a,v in ck['adam'][i][k].items():opt.state[p][a].copy_(v)
            self.clips.copy_(ck['clips']);self.bad.zero_();self.steps=ck['steps']
    def capture(self):
        ck=self.snapshot();st=torch.cuda.Stream();st.wait_stream(torch.cuda.current_stream())
        with torch.cuda.stream(st):
            for _ in range(3):self.step()
        torch.cuda.current_stream().wait_stream(st);torch.cuda.synchronize();self.restore(ck)
        g=torch.cuda.CUDAGraph()
        with torch.cuda.graph(g):self.step()
        torch.cuda.synchronize();self.restore(ck);self.graph=g
    def advance(self,n):
        for _ in range(n):
            if self.graph is None:self.step()
            else:self.graph.replay()
            self.steps+=1
        require(not bool(self.bad.any()),'Nonfinite generator objective/gradient')
        require(all(bool(torch.isfinite(p).all()) for s in self.states for p in s.values()),'Nonfinite parameter')

def compare(a,b):
    worst=0.
    for i in range(len(a['parameters'])):
        for kind in ['parameters','gradients']:
            for k in KEYS:
                x,y=a[kind][i][k],b[kind][i][k];worst=max(worst,float((x-y).abs().max()))
                require(torch.allclose(x,y,atol=1e-9,rtol=1e-8),'CUDA replay '+kind)
        for k in KEYS:
            for name,x in a['adam'][i][k].items():
                y=b['adam'][i][k][name];require(torch.allclose(x,y,atol=1e-9,rtol=1e-8),'Adam replay')
    require(a['steps']==b['steps'] and torch.equal(a['clips'],b['clips']),'Exact step/clip state');return worst
