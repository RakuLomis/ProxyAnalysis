"""Frozen pre-optimization pool, only for engineering equivalence/throughput checks."""
import numpy as np
import torch
from torch import nn

class ReferenceSequenceEncoder(nn.Module):
    def __init__(self,channels,chunk=2048):
        super().__init__();self.c1=nn.Conv1d(channels,32,3,padding=1);self.c2=nn.Conv1d(32,32,3,padding=1);self.chunk=chunk

    def forward(self,sequences):
        device=self.c1.weight.device;pieces=[];groups={}
        for seq_id,seq in enumerate(sequences):
            n=len(seq)
            for a in range(0,n,self.chunk):
                b=min(n,a+self.chunk);lo=max(0,a-2);hi=min(n,b+2)
                item=(seq_id,seq[lo:hi],a-lo,b-lo);idx=len(pieces);pieces.append(item)
                groups.setdefault((len(item[1])-1).bit_length(),[]).append(idx)
        sums=[None]*len(pieces);maxima=[None]*len(pieces);counts=[None]*len(pieces)
        for indices in groups.values():
            for pos in range(0,len(indices),64):
                batch=indices[pos:pos+64];width=max(len(pieces[i][1]) for i in batch)
                data=np.zeros((len(batch),sequences[0].shape[1],width),np.float32)
                valid=np.zeros((len(batch),1,width),np.float32);central=np.zeros_like(valid)
                for j,i in enumerate(batch):
                    _,seq,a,b=pieces[i];data[j,:,:len(seq)]=seq.T;valid[j,0,:len(seq)]=1;central[j,0,a:b]=1
                x=torch.from_numpy(data).to(device);mask=torch.from_numpy(valid).to(device);keep=torch.from_numpy(central).to(device)
                h=torch.relu(self.c1(x))*mask;h=torch.relu(self.c2(h))*mask
                su=(h*keep).sum(-1);ma=h.masked_fill(keep==0,-torch.inf).max(-1).values
                for j,i in enumerate(batch):sums[i]=su[j];maxima[i]=ma[j];counts[i]=int(central[j].sum())
        byseq=[[] for _ in sequences]
        for i,p in enumerate(pieces):byseq[p[0]].append(i)
        output=[]
        for ids in byseq:
            mean=torch.stack([sums[i] for i in ids]).sum(0)/sum(counts[i] for i in ids)
            maximum=torch.stack([maxima[i] for i in ids]).max(0).values
            output.append(torch.cat([mean,maximum]))
        return torch.stack(output)
