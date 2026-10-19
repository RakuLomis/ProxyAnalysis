"""Capability-specific train-only arrays. G never loads a P package."""
from common import *
from moment_features import grouping
from ridge_anchor import forward

def root(r):return OUT/'packages'/r['id']
def headpath(r,side,gamma):return OUT/'initial-classifiers'/r['id']/side/(gamma_tag(gamma)+'.pt')
def anchorpath(r,cap):return OUT/'anchors'/r['id']/(cap+'.pt')
def load(r,arm,anchor=True):
    rid=r['id'];p=root(r);cap=capfor(arm)
    sb=own(p/'scales/post.pt',rid)
    if cap=='E':
        d=own(p/'post/train.pt',rid);d.update(a=d['b'],y_pre=d['y'],w_pre=d['w'],mu_A=sb['mu'],scale_A=sb['scale'])
    elif cap=='G':
        d=own(p/'group/post.pt',rid);pre=own(p/'group/pre.pt',rid);targets=own(p/'group/targets.pt',rid)
        sa=own(p/'scales/pre.pt',rid)
        d.update(a=pre['a'],y_pre=pre['y'],w_pre=pre['w'],target=targets['target'],mu_A=sa['mu'],scale_A=sa['scale'])
        d.update({k:targets[k] for k in ['mom1','mom2','pi','gap']})
    else:
        d=own(p/'paired/train.pt',rid);sa=own(p/'scales/pre.pt',rid)
        d.update(y_pre=d['y'],w_pre=d['w'],target=d['a'],mu_A=sa['mu'],scale_A=sa['scale'])
        if arm=='F-P':d.update(own(p/'paired/moments.pt',rid))
    d['mu_B']=sb['mu'];d['scale_B']=sb['scale'];d['z']=(d['b']-sb['mu'])/sb['scale']
    d['real_x']=(d['a']-d['mu_A'])/d['scale_A']
    if arm in ['F-P','F-G']:
        d['condition_rows'],d['conditional_w'],pi=grouping(d['ci'],d['w'])
        require(torch.allclose(pi,d['pi'],atol=1e-14,rtol=1e-14),'Conditional masses differ')
    if anchor:d['anchor']=d['b'] if cap=='E' else forward(d['z'],own(anchorpath(r,cap),rid))
    return d

def fit_initial(r,side,gamma):
    from classifier import fit
    p=root(r);rid=r['id']
    if side=='pre':
        d=own(p/'group/pre.pt',rid);s=own(p/'scales/pre.pt',rid);raw=d['a']
    else:
        d=own(p/'post/train.pt',rid);s=own(p/'scales/post.pt',rid);raw=d['b']
    return fit((raw-s['mu'])/s['scale'],d['y'],d['w'],gamma,headpath(r,side,gamma),dict(role_id=rid,capability=side,kind='real-'+side+'-initial'))

def fit_anchor(r,cap):
    from ridge_anchor import fit_inverse
    p=anchorpath(r,cap)
    if p.exists():return own(p,r['id'])
    d=load(r,'R-P' if cap=='P' else 'R-G',anchor=False)
    with compute('inverse-anchor',role_id=r['id'],capability=cap,bundles=1):s,errors=fit_inverse(d['z'],d['target'],d['w'])
    put(p,s,role_id=r['id'],capability=cap,alpha=1.,parameters=1020,quality=errors);return s
