"""Immutable CUDA-ready batches. No labels, opposite-side fields or truncation."""
from dataclasses import dataclass
import numpy as np
import torch

@dataclass
class PackedSequences:
    batches: list
    order: torch.Tensor
    counts: torch.Tensor
    first: torch.Tensor
    multiple: list
    device: torch.device
    n: int

    @property
    def bytes(self):
        return sum(v.numel()*v.element_size() for batch in self.batches for v in batch)+sum(v.numel()*v.element_size() for v in [self.order,self.counts,self.first])

def pack_sequences(sequences,device,chunk=2048):
    device=torch.device(device);pieces=[];groups={};first=[];multiple=[];counts=[]
    for seq_id,seq in enumerate(sequences):
        n=len(seq);assert n>0;first.append(len(pieces));ids=[]
        for a in range(0,n,chunk):
            b=min(n,a+chunk);lo=max(0,a-2);hi=min(n,b+2);idx=len(pieces)
            pieces.append((seq[lo:hi],a-lo,b-lo));counts.append(b-a);ids.append(idx)
            groups.setdefault((hi-lo-1).bit_length(),[]).append(idx)
        if len(ids)>1:multiple.append((seq_id,ids))
    batches=[];ordered=[]
    for indices in groups.values():
        for pos in range(0,len(indices),64):
            batch=indices[pos:pos+64];width=max(len(pieces[i][0]) for i in batch)
            data=np.zeros((len(batch),sequences[0].shape[1],width),np.float32)
            valid=np.zeros((len(batch),1,width),np.float32);central=np.zeros_like(valid)
            for j,i in enumerate(batch):
                seq,a,b=pieces[i];data[j,:,:len(seq)]=seq.T;valid[j,0,:len(seq)]=1;central[j,0,a:b]=1
            batches.append(tuple(torch.from_numpy(x).to(device) for x in [data,valid,central]));ordered.extend(batch)
    return PackedSequences(batches,torch.as_tensor(np.argsort(ordered),device=device),
        torch.tensor(counts,dtype=torch.float32,device=device),torch.tensor(first,device=device),multiple,device,len(sequences))

def pooled_forward(encoder,packed):
    assert encoder.c1.weight.device==packed.device,'Cached inputs and model must share device'
    sums=[];maxima=[]
    for x,valid,central in packed.batches:
        h=torch.relu(encoder.c1(x))*valid;h=torch.relu(encoder.c2(h))*valid
        sums.append((h*central).sum(-1));maxima.append(h.masked_fill(central==0,-torch.inf).max(-1).values)
    sums=torch.cat(sums).index_select(0,packed.order);maxima=torch.cat(maxima).index_select(0,packed.order)
    result=torch.cat([sums/packed.counts[:,None],maxima],1).index_select(0,packed.first)
    # Most flows have a single chunk. Only truly long flows need this small loop.
    if packed.multiple:
        replacements=[];indices=[]
        for seq_id,ids in packed.multiple:
            index=torch.tensor(ids,device=packed.device);s=sums.index_select(0,index)
            mean=s.sum(0)/packed.counts.index_select(0,index).sum()
            maximum=maxima.index_select(0,index).max(0).values
            replacements.append(torch.cat([mean,maximum]));indices.append(seq_id)
        result=result.index_copy(0,torch.tensor(indices,device=packed.device),torch.stack(replacements))
    return result

@dataclass
class PreparedFlows:
    temporal: PackedSequences
    structure: object
    n: int

    def __len__(self):return self.n

    @property
    def bytes(self):return self.temporal.bytes+(self.structure.bytes if self.structure is not None else 0)

def prepare_flows(inputs,arm,device,chunk=2048):
    t=pack_sequences([x['T'] for x in inputs],device,chunk)
    s=None if arm=='S0' else pack_sequences([x['up'] for x in inputs]+[x['down'] for x in inputs],device,chunk)
    return PreparedFlows(t,s,len(inputs))

def state_key(state):
    return tuple((k,tuple(state[k]['mean']),tuple(state[k]['scale'])) for k in sorted(state))

def require_cuda(model):
    devices={p.device.type for p in model.parameters()}
    if devices!={'cuda'}:raise RuntimeError('Business training/inference requires CUDA; CPU fallback is forbidden')
