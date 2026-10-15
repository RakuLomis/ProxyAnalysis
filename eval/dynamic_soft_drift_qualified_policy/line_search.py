"""Two-endpoint descent envelopes with fixed empirical precision margins."""
from common import *

def signal(current,delta):
    f=float(current['g_f']@delta);v=float(current['g_v']@delta)
    tau=float(((current['g_f']-current['g_v']).abs()*delta.abs()).sum())+1e-12*max(1.,abs(f),abs(v))
    return dict(direction_f=f,direction_v=v,tau_dir=tau,direction_pass=max(f,v)<-tau)

def accept(current,trial,signal):
    tau=1e-8*max(1.,abs(current['L_f']),abs(trial['L_f']))
    bound=min(current['L_f'],current['L_v'])+1e-4*min(signal['direction_f'],signal['direction_v'])-tau
    upper=max(trial['L_f'],trial['L_v'])
    return dict(tau_L=tau,acceptance_bound=bound,candidate_upper=upper,value_pass=signal['direction_pass'] and upper<=bound)

