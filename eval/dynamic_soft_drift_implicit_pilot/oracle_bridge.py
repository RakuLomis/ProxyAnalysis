"""Use unchanged independent polynomial oracle; never hide activation crossing."""
from common import *

def components(data,arm,q):
    a,u,o,rr=production(); c=data['coeff']; cc={k:c[k] for k in ['A','B','C','s']}
    qr=q.detach().clone().requires_grad_()
    pen=rr.soft(qr,cc)[0]; gp=torch.autograd.grad(pen,qr)[0]
    independent=tensor([o.derivative(float(q[j]),float(c['A'][j]),float(c['B'][j]),float(c['s'][j])) for j in range(10)])
    err=float((independent-gp).abs().max())
    require(err<1e-10,'Independent analytic soft penalty mismatch')
    shrink=a.regularizer(qr); gs=torch.autograd.grad(shrink,qr)[0]
    require(float((gs-.002*(q-1)).abs().max())<1e-10,'Independent shrinkage mismatch')
    return dict(penalty=pen.detach(),penalty_gradient=independent,shrink=shrink.detach(),shrink_gradient=gs.detach(),error=err)

def value(c,q,o):
    return sum(o.phi(float(q[j]),float(c['A'][j]),float(c['B'][j]),float(c['s'][j])) for j in range(10))

def direction(data,arm,q,d,h,task_gradient,D_h):
    a,u,o,rr=production(); c=data['coeff']; comp=components(data,arm,q)
    branches=[o.branch(float(q[j]),abs(h*float(d[j])),float(c['A'][j]),float(c['B'][j]),float(c['s'][j])) for j in range(10)]
    plus=q+h*d; minus=q-h*d
    shrinkfd=float((a.regularizer(plus)-a.regularizer(minus))/(2*h))
    penaltyfd=(value(c,plus,o)-value(c,minus,o))/(2*h)
    rows=[]
    for label in (['D-P','T-P'] if arm=='D-P' else ['D-G']):
        penalty=label!='T-P'; gradient=task_gradient+comp['shrink_gradient']+(comp['penalty_gradient'] if penalty else 0)
        direct=D_h+shrinkfd+(penaltyfd if penalty else 0)
        dg=float(gradient@d); error=abs(direct-dg); limit=1e-5+1e-3*abs(direct)
        full_required=not penalty or 'boundary' not in branches
        rows.append(dict(arm=label,branches=branches if penalty else ['no_penalty']*10,
               full_required=full_required,full_FD=direct,full_implicit=dg,full_error=error,full_limit=limit,
               penalty_FD=penaltyfd if penalty else 0.,penalty_direction=float(comp['penalty_gradient']@d) if penalty else 0.,
               boundary_truncation=penaltyfd-float(comp['penalty_gradient']@d) if penalty else 0.,
               oracle_error=comp['error'],passed=not full_required or error<=limit))
    return rows
