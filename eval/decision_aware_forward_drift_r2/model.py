"""Fixed-coordinate forward refinement, no classifier in generator training."""
from common import *
KEYS=['U1','d1','U2']

def initial():
    g=torch.Generator(device='cuda').manual_seed(20261017)
    return dict(U1=torch.randn((8,96),generator=g,device='cuda',dtype=torch.float64)/np.sqrt(96),
        d1=torch.zeros(8,device='cuda',dtype=torch.float64),U2=torch.zeros((96,8),device='cuda',dtype=torch.float64))
def residual(s,x):return F.linear(F.relu(F.linear(x,s['U1'],s['d1'])),s['U2'])
def load(r,arm):
    p=OUT/'packages'/r['id'];d=own(p/('G.pt' if arm=='DA-G' else 'P.pt'),r['id']);d.update(own(p/'shared.pt',r['id']))
    d['cz0']=d['cx']@d['M'].T+d['bias']; d['K']=torch.eye(96,device='cuda',dtype=torch.float64) if arm=='Full-P' else d['Q']
    # Rows are vectors: K is 96xd, Q is 96xk.
    d['cidx']=torch.stack([torch.nonzero(d['cy']==yy).flatten() for yy in range(6) if yy not in r['missing']])
    d['pidx']=torch.stack([torch.nonzero(d['post_y']==yy).flatten() for yy in range(6) if yy not in r['missing']])
    require(d['cidx'].shape==d['pidx'].shape==(4,12),'C conditional grid')
    d['sidx']=torch.stack([torch.nonzero(d['sy']==yy).flatten() for yy in range(6)]);require(d['sidx'].shape==(6,24),'Source class grid')
    t=d['post']@d['K'];t=t[d['pidx']];tc=t-t.mean(1,keepdim=True);d['cov']=torch.bmm(tc.transpose(1,2),tc)/12
    return d
def objective(s,d):
    rc=residual(s,d['cx']);rs=residual(s,d['sx']);zh=d['cz0']+rc;k=d['Q'].shape[1];dim=d['K'].shape[1]
    sup=((zh-d['target'])@d['K']).square().sum(1).mean()/dim
    t=(zh@d['K'])[d['cidx']];tc=t-t.mean(1,keepdim=True);cov=torch.bmm(tc.transpose(1,2),tc)/12
    covloss=(cov-d['cov']).square().sum((1,2)).mean()/dim**2
    means=rs[d['sidx']].mean(1)@d['Q'];a,b=torch.triu_indices(6,6,offset=1,device='cuda')
    relation=(means[a]-means[b]).square().sum()/ (15*k)
    dev=(rc.square().sum(1).mean()+rs.square().sum(1).mean())/(2*96)
    reg=.0001*(s['U1'].square().sum()+s['U2'].square().sum())
    parts=torch.stack([sup,covloss,relation,.1*dev,reg]);return parts.sum(),parts
def diagnostic(s,d):
    val,parts=objective(s,d); gs=[]
    for item in parts:
        g=torch.autograd.grad(item,list(s.values()),retain_graph=True,allow_unused=True)
        gs.append(torch.cat([torch.zeros_like(p).flatten() if a is None else a.flatten() for p,a in zip(s.values(),g)]))
    g=torch.stack(gs);n=g.norm(dim=1)
    with torch.no_grad():
        rc=residual(s,d['cx']);err=d['cz0']+rc-d['target'];rs=residual(s,d['sx'])
        return dict(objective=float(val),parts=cpu(parts).tolist(),gradient_norms=cpu(n).tolist(),
            gradient_cosines=cpu((g@g.T)/(n[:,None]*n[None,:]).clamp_min(1e-30)).tolist(),
            C_Q_error=float((err@d['Q']).square().sum(1).mean()/d['Q'].shape[1]),C_std_error=float(err.square().mean()),
            source_residual_rms=float(rs.square().mean().sqrt()),std_max=float((d['mapped']+rs).abs().max()))
