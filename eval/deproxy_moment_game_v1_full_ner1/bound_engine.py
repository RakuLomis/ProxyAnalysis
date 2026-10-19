"""Uniform-lr CUDA Graph qualification; legacy states are read-only references."""
from common import *
from engine import Engine
from problems import load,initial_head,modelroot
from classifier import basis
from moment_features import grouping,moments
from models import KEYS

class BoundEngine(Engine):
    def __init__(self,data,jobs,heads,streams=True):
        require(len(data)==len(jobs)==len(heads),'Engine exact cardinality')
        keys=[(j['role_id'],j['arm'],j['recipe']['id'],j['seed']) for j in jobs]
        require(len(set(keys))==len(keys),'Duplicate engine job')
        require(len({capfor(j['arm']) for j in jobs})==1 or all(d.get('synthetic') for d in data),'Capability bucket')
        for d,j,h in zip(data,jobs,heads):
            require(d['binding']==(j['role_id'],j['arm']),'Engine data binding')
            require(h['binding']==(j['role_id'],'post' if j['arm']=='E-post' else 'pre',j['recipe']['gamma']),'Engine head binding')
        super().__init__(data,jobs,heads,streams=streams)

def bind(d,j,h):
    return dict(d,binding=(j['role_id'],j['arm'])),dict(h,binding=(j['role_id'],'post' if j['arm']=='E-post' else 'pre',j['recipe']['gamma']))
