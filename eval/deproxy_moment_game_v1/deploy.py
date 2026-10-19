"""Closed post-only inference: no IO, labels, protocol, visit keys or pre inputs."""
import torch
import torch.nn.functional as F
from simplex import project_blocks
from ridge_anchor import forward

def base_logp(raw,base):
    z=(raw-base['mu'])/base['scale']
    return F.log_softmax(F.linear(z,base['weight'],base['bias']),1)

def branch_logp(raw,export):
    z=(raw-export['mu_B'])/export['scale_B']
    anchor=raw if export['anchor'] is None else forward(z,export['anchor'])
    s=export['residual']
    residual=0 if s is None else F.linear(F.relu(F.linear(z,s['U1'],s['d1'])),s['U2'])
    a=project_blocks(anchor+residual);x=(a-export['mu_A'])/export['scale_A']
    return F.log_softmax(F.linear(x,export['head']['W'],export['head']['c']),1)

def mixture(base,branch,beta):
    if beta==0:return base
    if beta==1:return branch
    return torch.logaddexp(base+__import__('math').log1p(-beta),branch+__import__('math').log(beta))
