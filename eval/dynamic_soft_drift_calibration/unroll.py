"""Fixed functional 64-step GD; exact differentiation through this program."""
from common import *
from amplitude import adjust

def pack(v,kind,q):
    xs=[v['main_x'],v['S_x'],adjust(v['pre_x'],v['mapped_x'],q),v['C_x']]
    ys=[v['main_y'],v['S_y'],v['pre_y'],v['C_y']]
    mass=[v['main_mass'],v['S_mass']*.9,v['pre_mass']*.1,v['C_mass']]
    return {'x':torch.cat(xs),'y':torch.cat(ys),'mass':torch.cat(mass)}

def initialize(v,t):
    sx=torch.cat([v['main_x'],v['S_x'],v['C_x']])
    sm=torch.cat([v['main_mass'],v['S_mass'],v['C_mass']])
    aug=torch.cat([sx,torch.ones_like(sx[:,:1])],1)
    h=aug.T@(aug*sm[:,None])/6+torch.diag(torch.cat([
        torch.full((96,),.001*(1+t),device=device(),dtype=torch.float64),tensor([0.])]))
    L=torch.linalg.cholesky(h);I=torch.eye(97,device=device(),dtype=torch.float64)
    inv=torch.linalg.solve_triangular(L,I,upper=False)
    slot=pack(v,'unused',torch.ones(10,device=device(),dtype=torch.float64))
    ax=torch.cat([slot['x'],torch.ones_like(slot['x'][:,:1])],1)@inv.T
    bounds=ax.norm(dim=1)
    n=len(v['main_x']);m=len(v['pre_x']);pre=torch.cat([v['pre_x'],torch.ones_like(v['pre_x'][:,:1])],1)@inv.T
    bound=pre.norm(dim=1)
    for j in range(10):
        delta=torch.zeros_like(v['pre_x']);delta[:,block(j)]=v['mapped_x'][:,block(j)]-v['pre_x'][:,block(j)]
        white=torch.cat([delta,torch.zeros_like(delta[:,:1])],1)@inv.T
        bound=bound+2*white.norm(dim=1)
    bounds[n+len(v['S_x']):n+len(v['S_x'])+m]=bound
    B=inv[:,:96]
    upper=.5*(slot['mass']*bounds.square()).sum()+.001*(1+t)*torch.linalg.matrix_norm(B,ord=2).square()
    step=.9/upper
    require(torch.isfinite(step) and step>0,'Invalid fixed step')
    return {'inv':inv,'step':step,'curvature_upper':upper,'t':t}

def batch(tasks):
    keys=['main_x','main_y','main_mass','S_x','S_y','S_mass','pre_x','pre_y','pre_mass',
          'mapped_x','C_x','C_y','C_mass','query_x','query_y','query_mass']
    v={k:torch.stack([d[k] for d in tasks]) for k in keys}
    v['inv']=torch.stack([d['conditioning']['inv'] for d in tasks])
    v['step']=torch.stack([d['conditioning']['step'] for d in tasks])
    v['t']=tensor([d['conditioning']['t'] for d in tasks])
    return v

def inputs(b,q):
    x=torch.cat([b['main_x'],b['S_x'],adjust(b['pre_x'],b['mapped_x'],q),b['C_x']],1)
    y=torch.cat([b['main_y'],b['S_y'],b['pre_y'],b['C_y']],1)
    mass=torch.cat([b['main_mass'],b['S_mass']*.9,b['pre_mass']*.1,b['C_mass']],1)
    aug=torch.cat([x,torch.ones_like(x[:,:,:1])],2)
    ax=aug@b['inv'].transpose(1,2)
    return x,y,mass,ax

def run(b,q):
    x,y,mass,ax=inputs(b,q)
    V=torch.zeros((len(x),6,97),device=device(),dtype=torch.float64)
    B=b['inv'][:,:,:96];onehot=F.one_hot(y,6).to(torch.float64)
    reg=.001*(1+b['t'])
    for _ in range(64):
        logits=ax@V.transpose(1,2)
        e=(torch.softmax(logits,2)-onehot)*mass[:,:,None]
        gradient=e.transpose(1,2)@ax+reg[:,None,None]*((V@B)@B.transpose(1,2))
        V=V-b['step'][:,None,None]*gradient
    theta=V@b['inv']
    z=b['query_x']@theta[:,:,:96].transpose(1,2)+theta[:,:,96].unsqueeze(1)
    ce=torch.logsumexp(z,2)-z.gather(2,b['query_y'][:,:,None]).squeeze(2)
    risk=(ce*b['query_mass']).sum(1)
    return risk,theta

def original_objective(theta,slot,t):
    z=slot['x']@theta[:,:96].T+theta[:,96]
    value=(slot['mass']*(torch.logsumexp(z,1)-z.gather(1,slot['y'][:,None]).squeeze(1))).sum()
    return value+.0005*(1+t)*theta[:,:96].square().sum()

def original_gradient(theta,slot,t):
    z=slot['x']@theta[:,:96].T+theta[:,96]
    e=(torch.softmax(z,1)-F.one_hot(slot['y'],6))*slot['mass'][:,None]
    return torch.cat([e.T@slot['x']+.001*(1+t)*theta[:,:96],e.sum(0)[:,None]],1)
