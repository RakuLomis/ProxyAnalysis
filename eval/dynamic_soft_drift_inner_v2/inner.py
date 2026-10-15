"""Full q=1 training coordinates, fixed global spectral bound, original W L2."""
from common import *
TRAIN_KEYS=['main_x','main_y','main_mass','S_x','S_y','S_mass','pre_x','pre_y','pre_mass','mapped_x','C_x','C_y','C_mass']
def initialize(train,t,U):
    require(set(train)==set(TRAIN_KEYS),'Conditioning may receive training fields only')
    s=U.pack(train,'unused',tensor(np.ones(10)));x=s['x'];mass=s['mass']
    require(x.is_cuda and x.dtype==torch.float64,'CUDA float64 only')
    aug=torch.cat([x,torch.ones_like(x[:,:1])],1);alpha=.0005*(1+t)
    H=aug.T@(aug*mass[:,None])/6+torch.diag(tensor([2*alpha]*96+[0.]))
    L=torch.linalg.cholesky(H);inv=torch.linalg.solve_triangular(L,torch.eye(97,device=device(),dtype=torch.float64),upper=False)
    Z=aug@inv.T;sqrtmass=mass.sqrt()[:,None];safety=1+1e-12
    c0=torch.linalg.matrix_norm(sqrtmass*Z,ord=2)*safety;parts=[];deltas=[]
    n=len(train['main_x'])+len(train['S_x']);m=len(train['pre_x'])
    for j in range(10):
        raw=torch.zeros_like(x);raw[n:n+m,block(j)]=train['mapped_x'][:,block(j)]-train['pre_x'][:,block(j)]
        D=torch.cat([raw,torch.zeros_like(raw[:,:1])],1)@inv.T;deltas.append(D)
        parts.append(torch.linalg.matrix_norm(sqrtmass*D,ord=2)*safety)
    B=inv[:,:96];reg=2*alpha*(torch.linalg.matrix_norm(B,ord=2)*safety).square()
    bound=.5*(c0+torch.stack(parts).sum()).square()+reg;step=.9/bound
    require(torch.isfinite(step) and step>0 and not inv.requires_grad,'Invalid frozen coordinates')
    # Independent Gram-eigen spectral witnesses and reconstruction at the fixed perturbation.
    zalt=Z.clone()
    for j,D in enumerate(deltas):zalt=zalt+(-.1 if j%2==0 else .1)*D
    alt=U.pack(train,'unused',tensor(np.array([.9,1.1]*5)))
    za=torch.cat([alt['x'],torch.ones_like(alt['x'][:,:1])],1)@inv.T
    reconstruct=float((zalt-za).abs().max());witness=[]
    for z in [Z,za]:
        G=(z*sqrtmass).T@(z*sqrtmass)
        local=.5*torch.linalg.eigvalsh(G).max()+reg
        require(float(local)<=float(bound)*(1+1e-10),'Spectral upper-bound witness')
        witness.append(float(local))
    require(reconstruct<1e-10,'Block reconstruction')
    factor=float((H-L@L.T).abs().max())/max(1.,float(H.abs().max()))
    require(factor<1e-10,'Cholesky factor replay')
    V=(torch.arange(582,device=device(),dtype=torch.float64).reshape(6,97)/10000).requires_grad_()
    theta=V@inv;original=U.original_objective(theta,s,t)
    logits=Z@V.T;transformed=(F.cross_entropy(logits,s['y'],reduction='none')*mass).sum()+alpha*(V@B).square().sum()
    error=abs(float(original.detach()-transformed.detach()))
    ga=torch.autograd.grad(original,V)[0];gb=torch.autograd.grad(transformed,V)[0]
    gradient_error=float((ga-gb).abs().max());require(error<1e-10 and gradient_error<1e-10,'Original W regularization coordinate equivalence')
    audit=dict(step=float(step),c0=float(c0),c_blocks=[float(v) for v in parts],curvature_upper=float(bound),
               local_witnesses=witness,regularizer_bound=float(reg),factor_error=factor,
               objective_error=error,gradient_error=gradient_error,reconstruction_error=reconstruct,
               matrix_from_training_only=True,bias_regularized=False,frozen=True)
    return dict(inv=inv.detach(),step=step.detach(),t=t),audit
def run(b,q,K,U):
    require(K in [64,128,256] and q.is_cuda and q.dtype==torch.float64,'Unregistered K or CPU')
    x,y,mass,ax=U.inputs(b,q);V=torch.zeros((len(x),6,97),device=device(),dtype=torch.float64)
    B=b['inv'][:,:,:96];onehot=F.one_hot(y,6).to(torch.float64);reg=.001*(1+b['t'])
    for _ in range(K):
        z=ax@V.transpose(1,2);e=(torch.softmax(z,2)-onehot)*mass[:,:,None]
        grad=e.transpose(1,2)@ax+reg[:,None,None]*((V@B)@B.transpose(1,2))
        V=V-b['step'][:,None,None]*grad
    theta=V@b['inv'];z=b['query_x']@theta[:,:,:96].transpose(1,2)+theta[:,:,96].unsqueeze(1)
    ce=torch.logsumexp(z,2)-z.gather(2,b['query_y'][:,:,None]).squeeze(2)
    return (ce*b['query_mass']).sum(1),theta
