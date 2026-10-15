"""Single-side numeric-only representation. No metadata or opposite side accepted."""
from common import *

def schema(x):
    require(isinstance(x,pd.DataFrame) and list(x)==FEATURES,'Single-side numeric whitelist')
    a=x.to_numpy()
    require(np.isfinite(a).all() and (a>=0).all() and (a==np.floor(a)).all(),'Invalid native integer')
    for d in ['up','down']:
        u,e,w,p=[x[f'{v}_{d}'].to_numpy() for v in ['U','E','W','P']]
        require((u<=w).all() and (e<=p).all() and (e<=u).all(),'Native physical inequalities')
        require(np.array_equal(u==0,e==0),'Empty unique direction inconsistency')
    require((x.U_up+x.U_down>0).all(),'Empty flow forbidden')
    require((x.FR_packet_runs>=1).all() and (x.R_unique_zero_runs>=1).all(),'Invalid direction run')
    require((x.FR_packet_runs<=x.P_up+x.P_down).all(),'Packet run exceeds packets')
    require((x.R_unique_zero_runs<=x.E_up+x.E_down).all(),'Unique run exceeds events')

def states(x):
    schema(x); a=[]
    for d in ['up','down']:
        u=x['U_'+d].to_numpy(); e=x['E_'+d].to_numpy()
        code=1+4*np.searchsorted([1024,16384,262144],u,side='right')+np.searchsorted([4,16,64],e,side='right')
        code[u==0]=0; a.append(code)
    u=x.U_up.to_numpy()+x.U_down.to_numpy()
    for f in ['R_unique_zero_runs','FR_packet_runs']:
        a.append(4*np.searchsorted([2048,32768,524288],u,side='right')+
                 np.searchsorted([4,16,64],x[f].to_numpy(),side='right'))
    return np.stack(a,1).astype('int64')

def summarize(x):
    s=states(x); m=[]; j=[]; independent=[]
    for n,f in enumerate(FEATURES):
        edges=base.BYTE_EDGES if n<4 else base.COUNT_EDGES
        m.extend(np.bincount(np.searchsorted(edges,x[f],side='right'),minlength=len(edges)+1)/len(x))
    for g,k in enumerate(SIZES):
        h=np.bincount(s[:,g],minlength=k)/len(x); j.extend(h)
        if k==17:
            positive=h[1:].reshape(4,4); weight=positive.sum()
            v=np.outer(positive.sum(1),positive.sum(0))/weight if weight>0 else np.zeros((4,4))
            independent.extend(np.r_[h[0],v.ravel()])
        else:
            v=h.reshape(4,4); independent.extend(np.outer(v.sum(1),v.sum(0)).ravel())
    return {'M':np.asarray(m),'J':np.r_[m,j],'I':np.r_[m,independent]},s

def predict(model,q,representation):
    columns=INPUTS[representation]
    require(set(q)=={'visit_id',*columns} and q.visit_id.is_unique,'Unsafe post-only query schema')
    with torch.no_grad():
        x=(tensor(q[columns])-model['mu'])/model['scale']
        p=torch.softmax(x@model['weight'].T+model['bias'],1)
    require(torch.isfinite(p).all() and (p>0).all(),'Invalid CUDA prediction')
    d=pd.DataFrame(p.cpu().numpy(),columns=[f'p{i}' for i in range(6)])
    d['visit_id']=q.visit_id.to_numpy(); d['prediction']=p.argmax(1).cpu().numpy(); return d
