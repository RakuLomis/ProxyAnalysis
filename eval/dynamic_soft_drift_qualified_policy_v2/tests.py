"""New outer-policy unit tests; not a repeat of the sealed LR/FD study."""
from common import *
import objective
import projected_step as PS
import line_search as LS
import quality

def run():
    configure();passed=[]
    def test(name,ok):require(ok,'Unit test failed: '+name);passed.append(name)
    def rejected(name,fn):
        try:fn()
        except RuntimeError:passed.append(name)
        else:raise RuntimeError('Negative accepted: '+name)
    q=tensor(np.ones(10));m=tensor([1,10000]*5);g=tensor([1,-2]*5)
    p,gamma=PS.direction(g,m);test('scaled_amplitude',float((m.sqrt()*p).abs().max())<=.1000000000000001)
    test('metric_direction',torch.allclose(p,-g/m*gamma))
    z,zero=PS.direction(torch.zeros_like(g),m);test('zero_direction',bool((z==0).all()) and zero==1)
    edge=tensor([0,2]*5);nq,delta=PS.candidate(edge,-g,1.)
    test('actual_projected_delta',torch.equal(nq,edge) and bool((delta==0).all()))
    test('boundary_stationarity',float(PS.projected_gradient(edge,g).abs().max())==0 and float(g.abs().max())>0)
    cur=dict(g_f=g,g_v=g,L_f=1.,L_v=1.)
    _,delta=PS.candidate(q,p,1.);sig=LS.signal(cur,delta);test('two_gradient_descent',sig['direction_pass'])
    test('uphill_rejected',not LS.accept(cur,dict(L_f=1.1,L_v=1.1),sig)['value_pass'])
    test('validated_uphill_rejected',not LS.accept(cur,dict(L_f=.9,L_v=1.1),sig)['value_pass'])
    test('rounding_only_rejected',not LS.accept(cur,dict(L_f=1.-1e-12,L_v=1.-1e-12),sig)['value_pass'])
    test('resolved_descent_accepted',LS.accept(cur,dict(L_f=.9,L_v=.9),sig)['value_pass'])
    test('zero_signal_rejected',not LS.signal(cur,torch.zeros_like(q))['direction_pass'])
    test('disagreeing_gradient_rejected',not LS.signal({**cur,'g_v':-g},delta)['direction_pass'])
    fb=dict(Q_f=1.,Q_v=1.,gradient_f=g,gradient_v=g)
    s=objective.evaluate(q,fb,None,'QT')
    moved=objective.evaluate(q+.1,fb,None,'QT')
    test('original_q_shrink',abs(moved['shrink']-.0001)<1e-15)
    test('not_u_regularization',abs(float(.01*(m.sqrt()*.1).square().mean())-moved['shrink'])>.1)
    c=dict(A=tensor([2.]*10),B=tensor([1.]*10),s=tensor([.5]*10))
    dp=objective.evaluate(q+.1,fb,c,'QP');expected=((q+.1-1)*(c['A']*(q+.1+1)-2*c['B'])/c['s']).clamp_min(0).square().sum()/20
    test('original_relation_scale',abs(dp['penalty']-float(expected))<1e-15)
    rejected('T_recovery_denied',lambda:objective.evaluate(q,fb,c,'QT'))
    rejected('unknown_arm_denied',lambda:kind_for('anything'))
    test('typed_G_backend',kind_for('QG')=='G' and kind_for('QT')=='P')
    end={**s,'g_f':g*.1,'g_v':g*.1,'L_f':.99,'L_v':.99}
    result=quality.conclude(s,end,m,'accepted_update_limit',20)
    test('finite_progress_only_normal_terminal',result['status']=='finite_progress')
    test('budget_not_relabelled',quality.conclude(s,end,m,'stop_budget',20)['status']=='stop_budget')
    test('line_stop_not_relabelled',quality.conclude(s,end,m,'stop_line_search',20)['status']=='stop_line_search')
    test('small_scaled_gradient_not_stationary',not quality.stationary({**s,'g_f':g*.01,'g_v':g*.01},tensor([1e12]*10)))
    test('caps_arithmetic',36*41*12==17712 and 36*21*12*2==18144)
    safe=payload.normalize(dict(x=np.float64(.1),nested=[np.int64(2),q]));payload.assert_identical(safe,payload.normalize(safe))
    test('safe_numpy_normalization',type(safe['x']) is float and type(safe['nested'][0]) is int)
    rejected('CPU_denied',lambda:cuda(torch.ones(10,dtype=torch.float64)))
    return dict(passed=True,count=len(passed),tests=passed,old_FD_rerun=False,new_business_fits=0)

def permission_tests():
    r=contract()['roles'][0];i=contract()['inner_roles'][0];one=contract()['q_one_hash'];passed=[]
    def rejects(name,fn):
        try:fn()
        except RuntimeError:passed.append(name)
        else:raise RuntimeError('Permission negative accepted: '+name)
    rejects('T_full_coefficients',lambda:parent_asset(PARENT/'C-coefficients'/r['id']/'P.pt','coefficients','P',r['id'],'QT'))
    rejects('G_P_task',lambda:parent_asset(PARENT/'tasks'/i['id']/'P.pt','task','P',i['id'],'QG'))
    rejects('P_G_initial',lambda:parent_asset(PARENT/'feedback-cache'/'G'/i['id']/(one+'.pt'),'initial','G',i['id'],'QP'))
    rejects('outer_task_forbidden',lambda:parent_asset(PARENT/'tasks'/r['id']/'P.pt','task','P',r['id'],'QG'))
    rejects('old_learned_q_forbidden',lambda:parent_asset(PARENT/'q'/r['id']/'D-P.pt','initial','P',r['id'],'QP'))
    rejects('H_scores_forbidden',lambda:parent_asset(PARENT/'scores/metrics.parquet','task','P',r['id'],'QP'))
    rejects('unregistered_pcap_forbidden',lambda:parent_asset(ROOT/'Datasets/forbidden.pcap','task','P',r['id'],'QP'))
    return dict(passed=True,count=len(passed),tests=passed,H_U_numeric_reads=0)

def strategy_tests():
    from eligibility import choose
    configure();names=[];q=tensor([.9,1.1]*5)
    def check(name,yes):require(yes,'Strategy test failed '+name);names.append(name)
    def reject(name,fn):
        try:fn()
        except (RuntimeError,FileNotFoundError):names.append(name)
        else:raise RuntimeError('Strategy forbidden path accepted '+name)
    base=dict(origin_available=True,status='qualified_descent_only',passed=False,accepted_updates=20,trial_evaluations=20,terminal_residual={'PG_f':.1,'PG_v':.1},finite_progress_conditions=False,dual_descent=True)
    d=choose(base,q);check('descent_only_exact_identity',d['fallback'] and torch.equal(d['q'],torch.ones_like(q)))
    good={**base,'status':'finite_progress','passed':True,'finite_progress_conditions':True};d=choose(good,q)
    check('qualified_terminal_used',d['enabled'] and torch.equal(d['q'],q))
    reject('twentieth_state_without_gate',lambda:choose({**good,'finite_progress_conditions':False},q))
    reject('unexecuted_not_fallback',lambda:choose({**base,'origin_available':False},q))
    reject('integrity_not_fallback',lambda:choose(base,q,integrity=False))
    reject('global_stop_not_fallback',lambda:choose(base,q,global_stop=True))
    reject('backend_failure_not_fallback',lambda:choose({**base,'status':'stop_numeric_or_permission'},q))
    reject('incomplete_trial_budget_not_fallback',lambda:choose({**base,'status':'stop_budget','trial_evaluations':39},q))
    check('forty_trial_safe_fallback',choose({**base,'status':'stop_budget','trial_evaluations':40},q)['fallback'])
    stationary={**base,'status':'stationary_at_origin','passed':True,'accepted_updates':0,'terminal_residual':{'PG_f':1e-4,'PG_v':1e-4}}
    d=choose(stationary,torch.ones_like(q));check('stationary_identity_alias',d['enabled'] and d['identity'])
    check('remaining_budget_arithmetic',144*41*12==70848 and 144*21*12*2==72576 and 72000-8293.487963500433>0)
    if (OUT/'manifests/seal.json').exists():
        r=contract()['roles'][0]
        reject('H_query_before_all_models',lambda:package(PREP/'packages'/r['id']/'query.parquet','H-query','post-only-query',r))
        reject('H_labels_before_all_predictions',lambda:package(PREP/'packages'/r['id']/'labels.parquet','H-score','scorer',r))
    return dict(passed=True,count=len(names),tests=names,no_new_fits=True,no_H_U_numeric_reads=True)


