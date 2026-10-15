"""Same CE and original L2, only replace auxiliary loss mass."""
from common import *

def slot(v,arm,beta):
    require(arm in ['P','G'] and 0<=beta<=1,'Invalid fixed intervention')
    xs=[v['main_x']];ys=[v['main_y']];mass=[v['main_mass']]
    if beta<1:
        xs.append(v['S_x']);ys.append(v['S_y']);mass.append(v['S_mass']*(1-beta))
    if beta>0:
        xs.append(v[arm+'_x']);ys.append(v[arm+'_y']);mass.append(v[arm+'_mass']*beta)
    xs.append(v['C_x']);ys.append(v['C_y']);mass.append(v['C_mass'])
    x=torch.cat(xs);y=torch.cat(ys);m=torch.cat(mass)
    require(abs(float(m.sum())-1)<1e-12 and (m>0).all(),'CE mass')
    require(float((weighted(y,m,6)-1/6).abs().max())<1e-12,'Class prior changed')
    return {'x':x,'y':y,'mass':m,'mu':v['mu'],'scale':v['scale']}

def loss(model,s,t,regularize=True):
    logits=s['x']@model['weight'].T+model['bias']
    value=(s['mass']*(torch.logsumexp(logits,1)-logits.gather(1,s['y'][:,None]).squeeze(1))).sum()
    if regularize:value=value+.0005*(1+t)*model['weight'].square().sum()
    return value

def auxiliary(v,arm):return {'x':v[arm+'_x'],'y':v[arm+'_y'],'mass':v[arm+'_mass']}

def gradient(model,s,t,regularize=True):
    p=torch.softmax(s['x']@model['weight'].T+model['bias'],1)
    error=(p-F.one_hot(s['y'],6))*s['mass'][:,None]
    gw=error.T@s['x'];gb=error.sum(0)
    if regularize:gw=gw+.001*(1+t)*model['weight']
    return gw,gb

def normalized_model(model):
    return {'weight':model['weight'],'bias':model['bias']-model['bias'].mean()}
