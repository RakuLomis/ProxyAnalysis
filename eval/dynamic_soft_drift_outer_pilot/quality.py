"""Original-coordinate stationarity; no re-labelling budget/line stops."""
from common import *
from projected_step import projected_gradient

def residual(state,m):
    return dict(PG_f=float(projected_gradient(state['q'],state['g_f']).abs().max()),
                PG_v=float(projected_gradient(state['q'],state['g_v']).abs().max()),
                scaled_PG_f=float(projected_gradient(state['q'],state['g_f'],m).abs().max()),
                scaled_PG_v=float(projected_gradient(state['q'],state['g_v'],m).abs().max()))

def stationary(state,m):
    x=residual(state,m);return max(x['PG_f'],x['PG_v'])<=1e-3

def conclude(origin,end,m,status,accepted,dual_descent=True):
    a=residual(origin,m);b=residual(end,m)
    improve=min(origin['L_f'],origin['L_v'])-max(end['L_f'],end['L_v'])
    ratios={k:None if a[k]==0 else b[k]/a[k] for k in ['PG_f','PG_v']}
    progress_ok=dual_descent and improve>=1e-4*max(1.,abs(origin['L_f'])) and b['PG_f']<=.2*a['PG_f'] and b['PG_v']<=.2*a['PG_v']
    if status=='accepted_update_limit':status='finite_progress' if accepted==20 and progress_ok else 'qualified_descent_only'
    return dict(status=status,passed=status in ['stationary','stationary_at_origin','finite_progress'],
                accepted_updates=accepted,origin_residual=a,terminal_residual=b,residual_ratios=ratios,
                improvement=improve,finite_progress_conditions=bool(progress_ok),dual_descent=dual_descent)
