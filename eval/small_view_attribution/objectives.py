"""Exactly the frozen CE/L2; small means 10% of auxiliary mass."""
from common import *

def slot(v,x,y,mass,beta=.1):
    require(0<=beta<=1,'Beta')
    xs=[v['main_x']];ys=[v['main_y']];ms=[v['main_mass']]
    if beta<1:xs.append(v['S_x']);ys.append(v['S_y']);ms.append(v['S_mass']*(1-beta))
    if beta>0:xs.append(x);ys.append(y);ms.append(mass*beta)
    xs.append(v['C_x']);ys.append(v['C_y']);ms.append(v['C_mass'])
    s={'x':torch.cat(xs),'y':torch.cat(ys),'mass':torch.cat(ms),'mu':v['mu'],'scale':v['scale']}
    require(abs(float(s['mass'].sum())-1)<1e-12 and (s['mass']>0).all(),'Total CE mass')
    require(float((weighted(s['y'],s['mass'],6)-1/6).abs().max())<1e-12,'Class quality changed')
    return s

def reference(v,a):
    return slot(v,v[a[0]+'_x'] if a!='S' else v['S_x'],v[a[0]+'_y'] if a!='S' else v['S_y'],
                v[a[0]+'_mass'] if a!='S' else v['S_mass'],0. if a=='S' else .1)

def loss(m,s,t):
    z=s['x']@m['weight'].T+m['bias']
    return (s['mass']*(torch.logsumexp(z,1)-z.gather(1,s['y'][:,None]).squeeze(1))).sum()+.0005*(1+t)*m['weight'].square().sum()

def gradient(m,s,t):
    error=(torch.softmax(s['x']@m['weight'].T+m['bias'],1)-F.one_hot(s['y'],6))*s['mass'][:,None]
    return error.T@s['x']+.001*(1+t)*m['weight'],error.sum(0)

def audit(m,s,t,log):
    require(torch.equal(m['mu'],s['mu']) and torch.equal(m['scale'],s['scale']),'Coordinate mismatch')
    value=float(loss(m,s,t));gw,gb=gradient(m,s,t);maximum=max(float(gw.abs().max()),float(gb.abs().max()))
    require(maximum<=1e-5 and abs(value-log['objective'])<1e-10 and abs(maximum-log['max_gradient'])<1e-10,'Independent precision replay')
    return {'objective':value,'gradient_inf':maximum,'objective_replay_error':abs(value-log['objective']),
            'gradient_replay_error':abs(maximum-log['max_gradient'])}
