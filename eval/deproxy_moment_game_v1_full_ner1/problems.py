"""Fixed train-only convex problems, original initializations, and source binding."""
from common import *
import common
from classifier import basis,validate_old_head
from simplex import project_blocks
from ridge_anchor import forward
from moment_features import grouping

def headpath(r,side,g):return OUT/'initial-classifiers'/r['id']/side/f'g{g:g}.pt'
def modelroot(r,arm,candidate):return OUT/'models'/r['id']/arm/candidate/str(SEEDS[0])

def initial_head(r,side,g,new=False):
    p=headpath(r,side,g)
    h=own(p,r['id'])
    x,y,w=initial_arrays(r,side);validate_old_head(h,x,y,w,g)
    return h

def initial_arrays(r,side):
    p=OLD/'packages'/r['id'];s=own(p/f'scales/{side}.pt',r['id'])
    # P replays pre equations from its own paired bag, not the G-only
    # independently permuted margin. G retains its original anonymous order.
    name=('paired/train.pt' if common.CAP=='P' else 'group/pre.pt') if side=='pre' else 'post/train.pt'
    d=own(p/name,r['id'])
    return (d['a' if side=='pre' else 'b']-s['mu'])/s['scale'],d['y'],d['w']

def load(r,arm,anchor=True):
    rid=r['id'];p=OLD/'packages'/rid;cap=capfor(arm);require(cap==common.CAP,'Arm capability mismatch')
    sb=own(p/'scales/post.pt',rid)
    if cap=='E':
        d=own(p/'post/train.pt',rid);d.update(a=d['b'],y_pre=d['y'],w_pre=d['w'],mu_A=sb['mu'],scale_A=sb['scale'])
    elif cap=='G':
        d=own(p/'group/post.pt',rid);pre=own(p/'group/pre.pt',rid);t=own(p/'group/targets.pt',rid);sa=own(p/'scales/pre.pt',rid)
        d.update(a=pre['a'],y_pre=pre['y'],w_pre=pre['w'],target=t['target'],mu_A=sa['mu'],scale_A=sa['scale'])
        d.update({k:t[k] for k in ['mom1','mom2','pi','gap']})
    else:
        d=own(p/'paired/train.pt',rid);sa=own(p/'scales/pre.pt',rid)
        d.update(y_pre=d['y'],w_pre=d['w'],target=d['a'],mu_A=sa['mu'],scale_A=sa['scale'])
        if arm=='F-P':d.update(own(p/'paired/moments.pt',rid))
    d.update(mu_B=sb['mu'],scale_B=sb['scale']);d['z']=(d['b']-sb['mu'])/sb['scale']
    d['real_x']=(d['a']-d['mu_A'])/d['scale_A']
    if arm in ['F-P','F-G']:
        d['condition_rows'],d['conditional_w'],pi=grouping(d['ci'],d['w'])
        require(torch.allclose(pi,d['pi'],atol=1e-14,rtol=1e-14),'Conditional masses')
    if not anchor:return d
    if cap=='E':d['anchor']=d['b']
    else:
        anchor=own(OUT/'anchors'/rid/f'{cap}.pt',rid);d['anchor']=forward(d['z'],anchor)
        # Reuse only after independent blockwise normal-equation replay.
        for j in range(10):
            z=d['z'][:,block(j)];t=d['target'][:,block(j)];w=d['w'];xm=(z*w[:,None]).sum(0);tm=(t*w[:,None]).sum(0)
            cov=(z-xm).T@((z-xm)*w[:,None])+torch.eye(SIZES[j],device='cuda',dtype=torch.float64)
            cross=(t-tm).T@((z-xm)*w[:,None]);M=anchor[f'M{j}'];c=anchor[f'c{j}']
            require(float((M@cov-cross).norm()/cross.norm().clamp_min(1))<=1e-10 and float((c-(tm-M@xm)).abs().max())<=1e-10,'Inverse anchor independent replay')
    return d

def arrays(d,hat):
    return torch.cat([(hat-d['mu_A'])/d['scale_A'],d['real_x']]),torch.cat([d['y'],d['y_pre']]),torch.cat([d['w'],d['w_pre']])/2


def spec_cap(s):return ('G' if s['arm']=='pre' else 'E') if s['kind']=='initial' else capfor(s['arm'])

def fit_anchor(r,cap):
    from ridge_anchor import fit_inverse
    p=OUT/'anchors'/r['id']/f'{cap}.pt'
    if p.exists():
        # load() independently replays normal equations before an existing anchor
        # is consumed; never recompute an accepted anchor over its path.
        d=load(r,'R-'+cap);return own(p,r['id'])
    d=load(r,'R-'+cap,anchor=False);state,quality=fit_inverse(d['z'],d['target'],d['w'])
    put(p,state,role_id=r['id'],capability=cap,alpha=1.,quality=quality)
    return state
