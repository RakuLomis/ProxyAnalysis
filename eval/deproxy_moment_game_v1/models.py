"""Float64 low-rank raw residual, fixed anchor and task/moment objective."""
from common import *
from classifier import basis
from simplex import project_blocks
from moment_features import losses
KEYS=['U1','d1','U2','A','c']

def initial(head,seed):
    gen=torch.Generator(device='cuda').manual_seed(seed);q=basis()
    return dict(U1=torch.randn((8,96),device='cuda',dtype=torch.float64,generator=gen)/np.sqrt(96),
        d1=torch.zeros(8,device='cuda',dtype=torch.float64),U2=torch.zeros((96,8),device='cuda',dtype=torch.float64),
        A=q.T@head['W'],c=q.T@head['c'])
def generate(s,d):
    residual=F.linear(F.relu(F.linear(d['z'],s['U1'],s['d1'])),s['U2'])
    return project_blocks(d['anchor']+residual),residual
def head_logits(x,s,q):return F.linear(x,s['A'],s['c'])@q.T
def objective(s,d,arm,recipe,q):
    ahat,residual=generate(s,d);xh=(ahat-d['mu_A'])/d['scale_A']
    zg=head_logits(xh,s,q);zr=head_logits(d['real_x'],s,q)
    cg=(F.cross_entropy(zg,d['y'],reduction='none')*d['w']).sum()
    cr=(F.cross_entropy(zr,d['y_pre'],reduction='none')*d['w_pre']).sum();task=(cg+cr)/2
    rec=((ahat-d['target']).square().sum(1)*d['w']).sum()/10 if arm!='E-post' else torch.zeros_like(task)
    f1=f2=g1=g2=torch.zeros_like(task)
    if arm in ['F-P','F-G']:f1,f2,g1,g2=losses(ahat,d)
    dev=(residual.square().sum(1)*d['w']).sum()/10
    reg=recipe['gamma']*sum(s[k].square().sum() for k in ['U1','U2','A'])
    full=task+rec+f1+f2+g1+g2+.1*dev+reg
    return full,torch.stack([cg,cr,task,rec,f1,f2,g1,g2,dev,reg]),ahat,residual
