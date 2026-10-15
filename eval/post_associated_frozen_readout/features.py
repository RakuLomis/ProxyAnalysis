from common import *

def load_train(r):
    s=source_tensor(ROOT/r['classification'],r['id']);m=source_tensor(ROOT/r['base'],r['id'])
    require(s['x'].shape==(480,96) and s['real_x'].shape==(192,96),'Frozen source sizes')
    require(torch.equal(s['mu'],m['mu']) and torch.equal(s['scale'],m['scale']),'Frozen scale')
    require(abs(float(s['mass'].sum())-1)<1e-12,'Classification mass')
    cm=F.one_hot(s['y'],6).double().T@s['mass'];require(float((cm-1/6).abs().max())<1e-12,'Class mass')
    return s,m
def g_forward(g,x):return F.linear(F.relu(F.linear(x.float(),g['w0'],g['b0'])),g['w1'],g['b1'])
def ensure_g(r,arm,seed):
    if arm=='X':return None
    path=gpath(r,arm,seed)
    if path.exists():return own(path)
    a=source_tensor(ROOT/r['g_assets'][f'{arm}-{seed}'],r['id'],arm)
    state=a if arm=='R' else a['state']
    g={k:state[k].detach().clone() for k in ['w0','b0','w1','b1']}
    require(all(v.dtype==torch.float32 and v.is_cuda and not v.requires_grad for v in g.values()),'Frozen G only')
    put(path,g,role_id=r['id'],arm=arm,seed=seed,frozen=True,source=r['g_assets'][f'{arm}-{seed}'])
    return g
def feature(x,g):
    xf=x.float();return xf.double() if g is None else torch.cat([xf,g_forward(g,xf)],1).double()
def offset(x,m):return x@m['weight'].T+m['bias']
