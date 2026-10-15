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
    s=objective.evaluate(q,fb,None,'O-TP')
    moved=objective.evaluate(q+.1,fb,None,'O-TP')
    test('original_q_shrink',abs(moved['shrink']-.0001)<1e-15)
    test('not_u_regularization',abs(float(.01*(m.sqrt()*.1).square().mean())-moved['shrink'])>.1)
    c=dict(A=tensor([2.]*10),B=tensor([1.]*10),s=tensor([.5]*10))
    dp=objective.evaluate(q+.1,fb,c,'O-DP');expected=((q+.1-1)*(c['A']*(q+.1+1)-2*c['B'])/c['s']).clamp_min(0).square().sum()/20
    test('original_relation_scale',abs(dp['penalty']-float(expected))<1e-15)
    rejected('T_recovery_denied',lambda:objective.evaluate(q,fb,c,'O-TP'))
    rejected('unknown_arm_denied',lambda:kind_for('anything'))
    test('typed_G_backend',kind_for('O-DG')=='G' and kind_for('O-TP')=='P')
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
    rejects('T_full_coefficients',lambda:parent_asset(PARENT/'C-coefficients'/r['id']/'P.pt','coefficients','P',r['id'],'O-TP'))
    rejects('G_P_task',lambda:parent_asset(PARENT/'tasks'/i['id']/'P.pt','task','P',i['id'],'O-DG'))
    rejects('P_G_initial',lambda:parent_asset(PARENT/'feedback-cache'/'G'/i['id']/(one+'.pt'),'initial','G',i['id'],'O-DP'))
    rejects('outer_task_forbidden',lambda:parent_asset(PARENT/'tasks'/r['id']/'P.pt','task','P',r['id'],'O-DP'))
    rejects('old_learned_q_forbidden',lambda:parent_asset(PARENT/'q'/r['id']/'D-P.pt','initial','P',r['id'],'O-DP'))
    rejects('H_scores_forbidden',lambda:parent_asset(PARENT/'scores/metrics.parquet','task','P',r['id'],'O-DP'))
    rejects('unregistered_pcap_forbidden',lambda:parent_asset(ROOT/'Datasets/forbidden.pcap','task','P',r['id'],'O-DP'))
    return dict(passed=True,count=len(passed),tests=passed,H_U_numeric_reads=0)

def replay_initial():
    import feedback
    import scales
    rows=[];q=tensor(np.ones(10))
    # Each P/G task once. T reuses P values and the same metric, never full coefficients.
    for r in contract()['roles']:
        rs=[e for e in contract()['inner_roles'] if (e['target'],e['group'])==(r['target'],r['group'])]
        for arm in ['O-DP','O-DG']:
            kind=kind_for(arm);install_tasks({(e['id'],kind):feedback.validate_task(e,kind,arm) for e in rs})
            values=[feedback.initial(e,kind,q,arm) for e in rs]
            fb,_=feedback.aggregate(rs,kind,q,arm,True,values);coeff=scales.coefficients(r,arm)
            st=objective.evaluate(q,fb,coeff,arm)
            oldarm={'O-DP':'D-P','O-DG':'D-G'}[arm]
            old=parent_asset(PARENT/'trajectories'/r['id']/(oldarm+'.parquet'),'old-source-trajectory',kind,r['id'],'initial-audit')
            a=old.iloc[0];err=abs(st['L_f']-a.total)
            require(err<1e-12 and np.max(np.abs(st['g_f'].cpu().numpy()-np.asarray(a.total_gradient)))<1e-12,'Original q=1 objective/gradient replay')
            m=scales.load(r,arm);require(torch.equal(m,1+coeff['A']/coeff['s']),'Frozen metric replay')
            rows.append(dict(role_id=r['id'],kind=kind,Q=fb['Q_f'],objective_error=err,mean_gradient_difference=fb['mean_gradient_max_difference'],max_original_gradient=fb['max_original_gradient']))
    require(len(rows)==24,'Initial replay count');save(pd.DataFrame(rows),OUT/'tables/initial-replay.parquet')
    write(OUT/'initial-replay.json',dict(passed=True,role_kind_batches=24,source_initial_endpoints=288,new_fits=0,H_U_reads=0))
