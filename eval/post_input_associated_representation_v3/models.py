"""Independent batched networks. No shared parameters between leading-axis heads."""
from common import *

class Heads(torch.nn.Module):
    def __init__(self,seeds,teacher=False):
        super().__init__();self.teacher=teacher;self.count=len(seeds)
        layers=[(96,16),(16,8),(8,6) if teacher else (104,6)]
        for j,(ni,no) in enumerate(layers):
            ws=[];bs=[]
            for seed in seeds:
                gen=torch.Generator(device=device()).manual_seed(seed+j*100003)
                w=torch.empty((no,ni),device=device(),dtype=torch.float32);b=torch.empty(no,device=device(),dtype=torch.float32)
                if j==2 and not teacher:w.zero_();b.zero_()
                else:w.uniform_(-ni**-.5,ni**-.5,generator=gen);b.uniform_(-ni**-.5,ni**-.5,generator=gen)
                ws.append(w);bs.append(b)
            for i,(w,b) in enumerate(zip(ws,bs)):
                self.register_parameter(f'h{i}_w{j}',torch.nn.Parameter(w))
                self.register_parameter(f'h{i}_b{j}',torch.nn.Parameter(b))
    def get(self,i,key):return getattr(self,f'h{i}_{key}')
    def parameters_head(self,i):return [self.get(i,f'{key}{j}') for j in range(3) for key in ['w','b']]
    def head_latent(self,i,x):
        return F.linear(F.relu(F.linear(x,self.get(i,'w0'),self.get(i,'b0'))),self.get(i,'w1'),self.get(i,'b1'))
    def latent(self,x):return torch.stack([self.head_latent(i,x[i]) for i in range(self.count)])
    def head_forward(self,i,x,logits0=None):
        g=self.head_latent(i,x)
        if self.teacher:return F.linear(g,self.get(i,'w2'),self.get(i,'b2'))
        r=F.linear(torch.cat([x,g],-1),self.get(i,'w2'),self.get(i,'b2'))
        return logits0+.1*(r-r.mean(-1,keepdim=True)).double()
    def forward(self,x,logits0=None):
        return torch.stack([self.head_forward(i,x[i],None if logits0 is None else logits0[i]) for i in range(self.count)])
    def head_regularizer(self,i):return .01*sum(self.get(i,f'w{j}').square().sum() for j in range(3))
    def regularizer(self):return torch.stack([self.head_regularizer(i) for i in range(self.count)])
    def snapshot(self,i):return {f'{key}{j}':self.get(i,f'{key}{j}').detach().clone() for j in range(3) for key in ['w','b']}
    def gradients(self):return {f'{key}{j}':torch.stack([self.get(i,f'{key}{j}').grad.detach().clone() for i in range(self.count)]) for j in range(3) for key in ['w','b']}
    def moments(self,opt):
        values={}
        for j in range(3):
            for key in ['w','b']:
                name=f'{key}{j}';states=[opt.state[self.get(i,name)] for i in range(self.count)]
                values[name]={k:torch.stack([s[k].detach().clone() for s in states]) for k in states[0]}
        return values
    def clip(self):
        for i in range(self.count):
            ps=self.parameters_head(i);norm=torch.sqrt(sum(p.grad.square().sum() for p in ps))
            scale=(5/norm.clamp_min(1e-30)).clamp_max(1)
            for p in ps:p.grad.mul_(scale)

def latent(state,x):return F.linear(F.relu(F.linear(x.float(),state['w0'],state['b0'])),state['w1'],state['b1'])
def logits(state,x,base):
    z=base_logits(base,x)
    if state is None:return z
    g=latent(state,x);r=F.linear(torch.cat([x.float(),g],-1),state['w2'],state['b2'])
    return z+.1*(r-r.mean(-1,keepdim=True)).double()
def pad(values):
    require(all(v.is_cuda for v in values),'All numerical arrays CUDA')
    n=max(len(v) for v in values);out=[]
    for v in values:
        z=torch.zeros((n,*v.shape[1:]),device=device(),dtype=v.dtype);z[:len(v)]=v;out.append(z)
    return torch.stack(out)
def finite(net):return all(bool(torch.isfinite(p).all()) for p in net.parameters())
