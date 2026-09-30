"""Small full-sequence hierarchy. Padding and halo never contribute to pooling."""
import numpy as np
import torch
from torch import nn
from .cuda_packing import PackedSequences,PreparedFlows,pack_sequences,pooled_forward

class SequenceEncoder(nn.Module):
    def __init__(self,channels,chunk=2048):
        super().__init__();self.c1=nn.Conv1d(channels,32,3,padding=1);self.c2=nn.Conv1d(32,32,3,padding=1);self.chunk=chunk

    def forward(self,sequences):
        packed=sequences if isinstance(sequences,PackedSequences) else pack_sequences(sequences,self.c1.weight.device,self.chunk)
        return pooled_forward(self,packed)

class Hierarchy(nn.Module):
    def __init__(self,chunk=2048):
        super().__init__();self.structure=SequenceEncoder(7,chunk);self.temporal=SequenceEncoder(4,chunk)
        self.sproj=nn.Linear(128,32);self.tproj=nn.Linear(64,32);self.fusion=nn.Linear(64,32)
        self.head=nn.Sequential(nn.Linear(65,32),nn.ReLU(),nn.Linear(32,6))
        self.projector=nn.Sequential(nn.Linear(32,32),nn.ReLU(),nn.Linear(32,32))

    def flows(self,inputs,arm):
        ready=isinstance(inputs,PreparedFlows)
        n=inputs.n if ready else len(inputs)
        time=self.tproj(self.temporal(inputs.temporal if ready else [x['T'] for x in inputs]))
        if arm=='S0':static=torch.zeros((n,32),device=time.device)
        else:
            encoded=self.structure(inputs.structure if ready else [x['up'] for x in inputs]+[x['down'] for x in inputs])
            static=self.sproj(torch.cat([encoded[:n],encoded[n:]],dim=1))
        return torch.relu(self.fusion(torch.cat([static,time],dim=1)))

    def visits(self,inputs,sizes,arm):
        h=self.flows(inputs,arm);rows=[];start=0
        for count in sizes:
            a=h[start:start+count];start+=count
            rows.append(torch.cat([a.mean(0),a.max(0).values,a.new_tensor([np.log1p(count)])]))
        assert start==len(inputs)
        return self.head(torch.stack(rows))

def transformed(store,uid,side,rep,state,mask_rng=None,mask_rate=.05,no_type=False):
    data=store.data[uid,side];result={}
    for out,key,scale_key in [('T','T','T'),('up',rep+'_up',rep),('down',rep+'_down',rep)]:
        st=state[scale_key];x=((data[key]-np.asarray(st['mean'],np.float32))/np.asarray(st['scale'],np.float32)).astype(np.float32)
        if no_type and out!='T':x[:,3:]=0
        if mask_rng is not None:x=x*(mask_rng.random(x.shape)>=mask_rate)
        result[out]=x
    return result

def vicreg(a,b):
    invariance=(a-b).square().mean()
    std=lambda x:torch.sqrt(x.var(0,unbiased=True)+1e-4)
    variance=(torch.relu(1-std(a)).mean()+torch.relu(1-std(b)).mean())/2
    def cov(x):
        x=x-x.mean(0);c=x.T@x/(len(x)-1);mask=~torch.eye(c.shape[0],dtype=torch.bool,device=c.device)
        return c[mask].square().sum()/c.shape[0]
    covariance=cov(a)+cov(b)
    return 25*invariance+25*variance+covariance,{'invariance':float(invariance.detach()),'variance':float(variance.detach()),'covariance':float(covariance.detach())}
