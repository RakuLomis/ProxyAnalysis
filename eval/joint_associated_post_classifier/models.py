"""Complete post-only classifiers: independent and tensorized leading model axis."""
from common import *

def initial(data,seed):
    s={}
    for index,(ni,no) in enumerate([(96,16),(16,8)]):
        gen=torch.Generator(device='cuda').manual_seed(seed+index*100003)
        w=torch.empty((no,ni),device='cuda',dtype=torch.float32);b=torch.empty(no,device='cuda',dtype=torch.float32)
        w.uniform_(-ni**-.5,ni**-.5,generator=gen);b.uniform_(-ni**-.5,ni**-.5,generator=gen)
        s['a'+str(index)]=w;s['d'+str(index)]=b
    s.update(W=data['W'].detach().clone(),V=torch.zeros((6,8),device='cuda',dtype=torch.float64),c=data['c'].detach().clone())
    require(sum(p.numel() for p in s.values())==2318,'Parameter count')
    return s

def forward_post(x,s):
    g=F.linear(F.relu(F.linear(x.float(),s['a0'],s['d0'])),s['a1'],s['d1'])
    return F.linear(x,s['W'],s['c'])+F.linear(g.double(),s['V']),g

def loss_one(s,d,recipe):
    z,g=forward_post(d['x'],s)
    ce=(F.cross_entropy(z,d['y'],reduction='none')*d['mass']).sum()
    if recipe['lam']>0:
        mse=((g[d['real_index']].double()-d['target'].double()).square().mean(-1)*d['real_mass']).sum()
    else:mse=torch.zeros((),device='cuda',dtype=torch.float64)
    reg=sum(s[k].double().square().sum() for k in ['W','V','a0','a1'])*recipe['gamma']
    return ce+recipe['lam']*mse+reg,(ce,mse,reg)

def loss_independent(s,d,recipe):
    # Independent CE and analytic head gradients, with no functional CE call.
    # Keep the exact FP32 G evaluation; independently replay head/CE/L2 algebra.
    # A different FP32 matmul/bias fusion would test a different floating-point G.
    x=d['x'];h=F.relu(F.linear(x.float(),s['a0'],s['d0']));g=F.linear(h,s['a1'],s['d1'])
    z=x@s['W'].T+g.double()@s['V'].T+s['c'];lp=z-z.logsumexp(1)[:,None]
    ce=-(lp.gather(1,d['y'][:,None]).squeeze(1)*d['mass']).sum()
    err=(lp.exp()-F.one_hot(d['y'],6))*d['mass'][:,None]
    gradW=err.T@x+2*recipe['gamma']*s['W'];gradV=err.T@g.double()+2*recipe['gamma']*s['V'];gradc=err.sum(0)
    mse=(((g[d['real_index']].double()-d['target'].double()).square().sum(1)/8)*d['real_mass']).sum() if recipe['lam'] else torch.zeros_like(ce)
    reg=recipe['gamma']*sum((s[k].double()*s[k].double()).sum() for k in ['W','V','a0','a1'])
    return ce+recipe['lam']*mse+reg,dict(W=gradW,V=gradV,c=gradc)

class Tensorized(torch.nn.Module):
    def __init__(self,data,jobs,states=None,update_G=True,update_head=True):
        super().__init__();self.count=len(jobs);self.jobs=jobs;self.update_G=update_G;self.update_head=update_head
        states=states or [initial(d,j['seed']) for d,j in zip(data,jobs)]
        for k in KEYS:self.register_parameter(k,torch.nn.Parameter(torch.stack([s[k] for s in states]),requires_grad=update_G if k in GKEYS else update_head))
        self.x=torch.stack([d['x'] for d in data]);self.xf=self.x.float()
        self.y=torch.stack([d['y'] for d in data]);self.mass=torch.stack([d['mass'] for d in data])
        self.target=torch.stack([d['target'].double() for d in data]);self.real_mass=torch.stack([d['real_mass'] for d in data])
        self.real_index=data[0]['real_index'];require(all(torch.equal(d['real_index'],self.real_index) for d in data),'Batch real order')
        self.lam=tensor([j['recipe']['lam'] for j in jobs]);self.gamma=tensor([j['recipe']['gamma'] for j in jobs])
        self.bad=torch.zeros(self.count,device='cuda',dtype=torch.bool)
    def forward(self):
        h=torch.relu(torch.bmm(self.xf,self.a0.transpose(1,2))+self.d0[:,None])
        g=torch.bmm(h,self.a1.transpose(1,2))+self.d1[:,None]
        z=torch.bmm(self.x,self.W.transpose(1,2))+self.c[:,None]+torch.bmm(g.double(),self.V.transpose(1,2))
        return z,g
    def objective(self):
        z,g=self.forward();ce=(F.cross_entropy(z.flatten(0,1),self.y.flatten(),reduction='none').reshape_as(self.y)*self.mass).sum(1)
        mse=((g[:,self.real_index].double()-self.target).square().mean(-1)*self.real_mass).sum(1)
        # Zero-lambda jobs receive zero targets; no paired target file was read.
        mse=torch.where(self.lam>0,mse,torch.zeros_like(mse))
        reg=self.gamma*sum(getattr(self,k).double().square().flatten(1).sum(1) for k in ['W','V','a0','a1'])
        return ce+self.lam*mse+reg,torch.stack([ce,mse,reg],1)
    def clip(self):
        active=[p for p in self.parameters() if p.requires_grad]
        norm=sum(p.grad.double().square().flatten(1).sum(1) for p in active).sqrt()
        factor=(5/norm.clamp_min(1e-30)).clamp_max(1)
        for p in active:p.grad.mul_(factor.to(p.dtype).reshape((self.count,)+((1,)*(p.ndim-1))))
        self.bad.logical_or_(~torch.isfinite(norm));return norm
    def snapshot(self,i):return {k:getattr(self,k)[i].detach().clone() for k in KEYS}

class Independent(torch.nn.Module):
    def __init__(self,data,jobs,states=None,update_G=True,update_head=True):
        super().__init__();self.count=len(jobs);self.data=data;self.jobs=jobs;self.update_G=update_G;self.update_head=update_head
        states=states or [initial(d,j['seed']) for d,j in zip(data,jobs)]
        for i,s in enumerate(states):
            for k in KEYS:self.register_parameter(f'h{i}_{k}',torch.nn.Parameter(s[k].detach().clone(),requires_grad=update_G if k in GKEYS else update_head))
        self.bad=torch.zeros(len(jobs),device='cuda',dtype=torch.bool)
    def state_head(self,i):return {k:getattr(self,f'h{i}_{k}') for k in KEYS}
    def objective(self):
        vals=[];parts=[]
        for i,(d,j) in enumerate(zip(self.data,self.jobs)):
            v,p=loss_one(self.state_head(i),d,j['recipe']);vals.append(v);parts.append(torch.stack(p))
        return torch.stack(vals),torch.stack(parts)
    def backward_step(self):
        vals=[];parts=[]
        for i,(d,j) in enumerate(zip(self.data,self.jobs)):
            v,p=loss_one(self.state_head(i),d,j['recipe']);v.backward();vals.append(v.detach());parts.append(torch.stack(p).detach())
        return torch.stack(vals),torch.stack(parts)
    def clip(self):
        norms=[]
        for i in range(self.count):
            ps=[p for p in self.state_head(i).values() if p.requires_grad]
            norm=sum(p.grad.double().square().sum() for p in ps).sqrt();norms.append(norm)
            factor=(5/norm.clamp_min(1e-30)).clamp_max(1)
            for p in ps:p.grad.mul_(factor.to(p.dtype))
        norms=torch.stack(norms);self.bad.logical_or_(~torch.isfinite(norms));return norms
    def snapshot(self,i):return {k:v.detach().clone() for k,v in self.state_head(i).items()}
