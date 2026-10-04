"""Shared classifier and equal-visit schedules; no data reads on import."""
import torch
from common import *


class Heads(torch.nn.Module):
    def __init__(self,states):
        super().__init__()
        self.w1=torch.nn.Parameter(torch.stack([s['0.weight'] for s in states]))
        self.b1=torch.nn.Parameter(torch.stack([s['0.bias'] for s in states]))
        self.w2=torch.nn.Parameter(torch.stack([s['2.weight'] for s in states]))
        self.b2=torch.nn.Parameter(torch.stack([s['2.bias'] for s in states]))

    def forward(self,x):
        return torch.bmm(torch.relu(torch.bmm(x,self.w1.transpose(1,2))+self.b1[:,None]),self.w2.transpose(1,2))+self.b2[:,None]

    def loss(self,x,y):
        ce=-self(x).log_softmax(-1).gather(-1,y[...,None]).squeeze(-1).mean(1)
        return ce+.5e-4*(self.w1.square().sum((1,2))+self.w2.square().sum((1,2)))

    def one(self,i):
        return {'0.weight':self.w1[i].detach().clone(),'0.bias':self.b1[i].detach().clone(),
                '2.weight':self.w2[i].detach().clone(),'2.bias':self.b2[i].detach().clone()}


def network():return torch.nn.Sequential(torch.nn.Linear(6,32),torch.nn.ReLU(),torch.nn.Linear(32,6)).to(device())


def scaler(post):
    x=np.log1p(post[FEATURES].to_numpy(float));mean=x.mean(0);scale=x.std(0);scale[scale<1e-10]=1
    return mean,scale


def schedule(frame,seed,steps=1000):
    rng=np.random.default_rng(seed);groups={}
    for (p,y),g in frame.groupby(['protocol','label_id']):
        contents=sorted(g.content_id.unique());assert len(contents)==4;rng.shuffle(contents)
        groups[p,y]=[g.index[g.content_id.eq(c)].to_numpy() for c in contents]
        assert all(len(ids)==4 for ids in groups[p,y])
    result=np.stack([np.concatenate([groups[k][step%4] for k in sorted(groups)]) for step in range(steps)])
    assert np.bincount(result.ravel(),minlength=len(frame)).tolist()==[steps//4]*len(frame)
    return result


def independent_pre_schedule(post,pre,main):
    # All four repetitions of a content are included; no visit ID joins exist.
    groups={(p,c):g.index.to_numpy() for (p,c),g in pre.groupby(['protocol','content_id'])}
    rows=[]
    for ix in main:
        keys=list(dict.fromkeys(zip(post.loc[ix,'protocol'],post.loc[ix,'content_id'])))
        row=np.concatenate([groups[k] for k in keys]);assert len(row)==len(ix);rows.append(row)
    result=np.stack(rows)
    assert np.bincount(result.ravel(),minlength=len(pre)).tolist()==[len(main)//4]*len(pre)
    return result
