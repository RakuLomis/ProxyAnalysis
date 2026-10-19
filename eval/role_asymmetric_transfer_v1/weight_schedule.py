"""Independent label-indexed loss-mass splitting; no source-side row join."""
from common import *

def registry():
    rows=[]
    for source in ['P','G','RawPre','RawPost']:
        for m in [.1,.25,.5]:
            for allocation in ['SYM','UPR','CPR']:
                rc,ru={'SYM':(m,m),'UPR':(0.,2*m),'CPR':(2*m,0.)}[allocation]
                alias=source+'-small' if m==.1 and allocation=='SYM' else None
                rows.append(dict(id=f'{source}__m{int(m*100):03d}__{allocation}',source=source,m=m,allocation=allocation,rho_C=rc,rho_U=ru,alias=alias))
    for name,source,rho in [('S','P',0.),('P-full','P',1.),('G-full','G',1.)]:
        rows.append(dict(id=name,source=source,m=rho,allocation='endpoint',rho_C=rho,rho_U=rho,alias=name))
    require(len(rows)==39,'Policy count');return rows

PRIMARY='P__m025__UPR'
REFERENCES=['P__m010__SYM','P__m025__SYM','G__m025__UPR','RawPre__m025__UPR','RawPost__m025__UPR','S']

def selection(v,p):
    a=p['source']
    if a=='RawPre':return v['rawpre_x'],v['P_y'],v['P_mass']
    if a=='RawPost':return v['main_x'],v['main_y'],v['main_mass']
    return v[a+'_x'],v[a+'_y'],v[a+'_mass']

def slot(v,p,missing,ledger=False):
    rc,ru=p['rho_C'],p['rho_U'];x,y,m=selection(v,p)
    rs=torch.where(torch.isin(v['S_y'],tensor(missing,torch.long)),tensor(ru),tensor(rc))
    rx=torch.where(torch.isin(y,tensor(missing,torch.long)),tensor(ru),tensor(rc))
    xs=[v['main_x'],v['S_x'],x,v['C_x']];ys=[v['main_y'],v['S_y'],y,v['C_y']]
    ms=[v['main_mass'],v['S_mass']*(1-rs),m*rx,v['C_mass']]
    xx,yy,mm=torch.cat(xs),torch.cat(ys),torch.cat(ms)
    require(torch.isfinite(xx).all() and torch.isfinite(mm).all() and (mm>=0).all(),'Invalid training coordinates/mass')
    require(abs(float(mm.sum())-1)<1e-12 and float((weighted(yy,mm,6)-1/6).abs().max())<1e-12,'Class/total mass')
    require(abs(float(ms[1].sum())-(1/3-(rc+ru)/6))<1e-12 and abs(float(ms[2].sum())-(rc+ru)/6)<1e-12,'Subslot mass')
    for group in [False,True]:
        take_s=torch.isin(ys[1],tensor(missing,torch.long))==group
        take_x=torch.isin(ys[2],tensor(missing,torch.long))==group
        require(abs(float(ms[1][take_s].sum()+ms[2][take_x].sum())-1/6)<1e-12,'C/U auxiliary mass')
    keep=mm>0
    out=dict(x=xx[keep],y=yy[keep],mass=mm[keep],mu=v['mu'],scale=v['scale'])
    if ledger:
        rows=[]
        for name,yy_,mm_ in zip(['source-post','CORAL',p['source'],'C-post'],ys,ms):
            rows.extend(dict(slot_type=name,row_index=j,label=int(yi),sample_mass=float(wi),retained=bool(wi>0),role='U' if int(yi) in missing else 'C') for j,(yi,wi) in enumerate(zip(yy_.cpu().tolist(),mm_.cpu().tolist())))
        return out,rows
    return out

def audit(model,s,t,log=None):
    require(torch.equal(model['mu'],s['mu']) and torch.equal(model['scale'],s['scale']),'Model coordinates')
    z=s['x']@model['weight'].T+model['bias'];error=(z.softmax(1)-F.one_hot(s['y'],6))*s['mass'][:,None]
    value=(s['mass']*(z.logsumexp(1)-z.gather(1,s['y'][:,None]).squeeze(1))).sum()+.0005*(1+t)*model['weight'].square().sum()
    gw=error.T@s['x']+.001*(1+t)*model['weight'];gb=error.sum(0)
    maximum=max(float(gw.abs().max()),float(gb.abs().max()))
    out=dict(objective=float(value),gradient_inf=maximum)
    require(np.isfinite(float(value)) and maximum<=1e-5,'Original gradient gate')
    if log is not None:
        oe=abs(float(value)-log['objective']);ge=abs(maximum-log['max_gradient'])
        require(log['accepted'] and log['solver']==SOLVER and oe<1e-10 and ge<1e-10,'Independent objective/gradient replay')
        require(all(acceptance_gates(log['objective'],log['initial_objective'],log['max_gradient'],log['iterations'],log['objective_replay_error'],log['gradient_replay_error']).values()),'Historical numerical gates')
        require(log['settings']['max_iter']==2000 and log['settings']['max_eval']==10000,'Historical budget')
        out.update(objective_replay_error=oe,gradient_replay_error=ge)
    return out
