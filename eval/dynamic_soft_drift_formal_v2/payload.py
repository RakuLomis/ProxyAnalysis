"""No pickle allowlisting: checkpoints contain only builtins and Torch tensors."""
import numpy as np
import torch


def normalize(value, path='$'):
    """Convert metadata scalars, preserve tensor data; reject all unknown objects."""
    if isinstance(value, np.generic):
        converted=value.item()
        if isinstance(converted, np.generic):
            raise TypeError('Scalar has no exact Python builtin conversion at '+path)
        return normalize(converted,path)
    if isinstance(value,torch.Tensor):return value
    if type(value) in (type(None),bool,int,float,str):return value
    if isinstance(value,dict):
        result={}
        for key,item in value.items():
            k=normalize(key,path+'.<key>')
            if type(k) not in (type(None),bool,int,float,str,tuple):
                raise TypeError('Unsupported dictionary key at '+path)
            result[k]=normalize(item,path+'.'+str(k))
        return result
    if isinstance(value,list):return [normalize(v,path+f'[{i}]') for i,v in enumerate(value)]
    if isinstance(value,tuple):return tuple(normalize(v,path+f'[{i}]') for i,v in enumerate(value))
    raise TypeError('Unsupported checkpoint object at '+path+': '+type(value).__module__+'.'+type(value).__name__)


def assert_identical(a,b,path='$'):
    """Independent readback including tensor bytes, scalar types and signed zeros."""
    if isinstance(a,torch.Tensor):
        if not isinstance(b,torch.Tensor) or a.dtype!=b.dtype or a.shape!=b.shape:
            raise RuntimeError('Tensor schema mismatch at '+path)
        # map_location can move optimizer counters; it must never change their bytes.
        aa=a.detach().contiguous().reshape(-1).view(torch.uint8)
        bb=b.detach().to(a.device).contiguous().reshape(-1).view(torch.uint8)
        if not torch.equal(aa,bb):raise RuntimeError('Tensor bytes changed at '+path)
        return
    if type(a)!=type(b):raise RuntimeError('Checkpoint type mismatch at '+path)
    if isinstance(a,dict):
        if list(a)!=list(b):raise RuntimeError('Dictionary keys/order changed at '+path)
        for key in a:assert_identical(a[key],b[key],path+'.'+str(key))
    elif isinstance(a,(list,tuple)):
        if len(a)!=len(b):raise RuntimeError('Sequence size changed at '+path)
        for i,(x,y) in enumerate(zip(a,b)):assert_identical(x,y,path+f'[{i}]')
    elif isinstance(a,float):
        if a.hex()!=b.hex():raise RuntimeError('Float value changed at '+path)
    elif a!=b:raise RuntimeError('Checkpoint value changed at '+path)


def numpy_paths(value,path='$'):
    if isinstance(value,np.generic):return [path+':'+type(value).__name__]
    if isinstance(value,dict):
        result=[]
        for k,v in value.items():result+=numpy_paths(k,path+'.<key>')+numpy_paths(v,path+'.'+str(k))
        return result
    if isinstance(value,(list,tuple)):
        return [p for i,x in enumerate(value) for p in numpy_paths(x,path+f'[{i}]')]
    return []
