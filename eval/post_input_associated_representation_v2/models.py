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
            self.register_parameter(f'w{j}',torch.nn.Parameter(torch.stack(ws)))
            self.register_parameter(f'b{j}',torch.nn.Parameter(torch.stack(bs)))
    def latent(self,x):return torch.bmm(F.relu(torch.bmm(x,self.w0.transpose(1,2))+self.b0[:,None]),self.w1.transpose(1,2))+self.b1[:,None]
    def forward(self,x,logits0=None):
        g=self.latent(x)
        if self.teacher:return torch.bmm(g,self.w2.transpose(1,2))+self.b2[:,None]
        r=torch.bmm(torch.cat([x,g],-1),self.w2.transpose(1,2))+self.b2[:,None]
        r=r-r.mean(-1,keepdim=True)
        return logits0+.1*r.to(torch.float64)
    def regularizer(self):return .01*sum(getattr(self,f'w{j}').square().flatten(1).sum(1) for j in range(3))
    def snapshot(self,i):return {k:v[i].detach().clone() for k,v in self.state_dict().items()}
    def clip(self):
        norm=torch.sqrt(sum(p.grad.square().flatten(1).sum(1) for p in self.parameters()))
        scale=(5/norm.clamp_min(1e-30)).clamp_max(1)
        for p in self.parameters():p.grad.mul_(scale.reshape((self.count,)+((1,)*(p.ndim-1))))

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
