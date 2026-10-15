"""The original q objective, not an objective in whitened coordinates."""
from common import *

def evaluate(q,feedback,coeff,arm,need_gradient=True):
    cuda(q);require(q.shape==(10,) and bool(((q>=0)&(q<=2)).all()),'q feasibility')
    require((coeff is None)==(arm=='O-TP'),'Wrong relation arm')
    shrink=float(.01*(q-1).square().mean());gs=.002*(q-1)
    if coeff is None:
        gap=torch.zeros_like(q);penalty=0.;gp=torch.zeros_like(q);parts=torch.zeros_like(q)
    else:
        gap=(q-1)*(coeff['A']*(q+1)-2*coeff['B'])/coeff['s']
        pos=gap.clamp_min(0);parts=pos.square()/20;penalty=float(parts.sum())
        gp=pos*(2*coeff['A']*q-2*coeff['B'])/(10*coeff['s'])
    out=dict(q=q.detach().clone(),Q_f=feedback['Q_f'],Q_v=feedback['Q_v'],shrink=shrink,penalty=penalty,
             L_f=feedback['Q_f']+shrink+penalty,L_v=feedback['Q_v']+shrink+penalty,gap=gap,
             penalty_parts=parts,shrink_gradient=gs,penalty_gradient=gp,feedback=feedback)
    if need_gradient:
        out.update(g_f=feedback['gradient_f']+gs+gp,g_v=feedback['gradient_v']+gs+gp)
        require(torch.isfinite(out['g_f']).all() and torch.isfinite(out['g_v']).all(),'Nonfinite outer gradient')
    return out
