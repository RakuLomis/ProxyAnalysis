"""Read-only adoption, bounded tests and sealed v4 solver contract."""
import shutil
from common import *
from optimizer_preconditioning import (coordinates, decode, transformed_objective, gates,
    fit_preconditioned, install_local_step, reference_metadata, stop_action)

FIRST='main/f0/shadowsocks/G0/i1/vless'
SECOND='main/f0/shadowsocks/G0/i2/vless'

def pilot_ids(c):
    ids=[]
    for i,target in enumerate(PROTOCOLS):
        for g,group in enumerate(MASKS):
            outer=(i+g)%5;inner=min(j for j in range(5) if j!=outer)
            calibration=[p for p in PROTOCOLS if p!=target][g]
            ids.append(f'main/f{outer}/{target}/{group}/i{inner}/{calibration}')
    ids += [SECOND,'main/f0/shadowsocks/G1/i1/trojan','main/f0/shadowsocks/G2/i1/vmess']
    require(len(ids)==len(set(ids))==15,'Pilot count')
    registry={r['id']:r for r in c['main']}
    for rid in ids:
        require(rid in registry,'Missing pilot role')
        r=registry[rid]
        require(r['inner'] is not None and r['target'] not in r['sources']+[r['calibration']],'Pilot permissions')
    require({registry[rid]['outer'] for rid in ids}==set(range(5)),'Pilot five-fold coverage')
    return [FIRST,SECOND]+sorted(set(ids)-{FIRST,SECOND})

def unit_tests():
    checks=[];errors=[];synthetic_fits=0
    def check(name,value):
        require(value,name);checks.append({'name':name,'passed':True})
    torch.manual_seed(20261006)
    x=torch.randn((60,96),device=device(),dtype=torch.float64);x[:,0]=0
    y=torch.arange(6,device=device()).repeat(10)
    mass=torch.full((60,),1/60,device=device(),dtype=torch.float64)
    normal={'x':x,'y':y,'mass':mass}
    actual=[torch.load(PREP/'slots'/rid/'CT1.pt',map_location=device(),weights_only=True) for rid in [FIRST,SECOND]]
    for name,source in [('synthetic',normal),('original_failure',actual[0]),('v2_failure',actual[1])]:
        for t in TS:
            xx,yy,mm=source['x'],source['y'],source['mass'];a,l,ax=coordinates(xx,mm,t)
            v=(torch.randn((6,97),device=device(),dtype=torch.float64)*.01).requires_grad_()
            theta=decode(v,l);w=theta[:,:96].detach().requires_grad_();b=theta[:,96].detach().requires_grad_()
            orig=objective(w,b,xx,yy,mm,t);other=transformed_objective(v,l,ax,yy,mm,t)
            gw,gb=torch.autograd.grad(orig,(w,b));gv,=torch.autograd.grad(other,(v,))
            row={'case':name,'t':t,'objective':abs(float(orig.detach()-other.detach())),
                 'logits':float((xx@w.T+b-ax@v.T).detach().abs().max()),
                 'gradient':float((torch.cat([gw,gb[:,None]],1)-gv@l.T).abs().max()),
                 'roundtrip':float((v.detach()-theta.detach()@l).abs().max())}
            errors.append(row);check(name+' equivalence '+str(t),max(row[k] for k in ['objective','logits','gradient','roundtrip'])<1e-10)
    a,l,ax=coordinates(x,mass,0)
    theta=torch.zeros((6,97),device=device(),dtype=torch.float64);theta[:,96]=torch.arange(6,device=device())
    v=theta@l;ce=(F.cross_entropy(x@theta[:,:96].T+theta[:,96],y,reduction='none')*mass).sum()
    check('Bias not penalized',abs(float(transformed_objective(v,l,ax,y,mass,0)-ce))<1e-10)
    check('Wrong V penalty detected',float(.0005*v.square().sum())>1e-6)
    check('Original gate cannot use tiny V gradient',not gates(1,2,.002,20,0,0)['original_coordinate_gradient'])
    check('Old 500 boundary is not new cap',gates(1,2,0,500,0,0)['iteration_budget'])
    check('1999 budget eligible',gates(1,2,0,POLICY['max_iter']-1,0,0)['iteration_budget'])
    check('2000 rejected',not gates(1,2,0,POLICY['max_iter'],0,0)['iteration_budget'])
    check('625 no longer evaluation ceiling',stop_action(.002,evaluations=625)=='continue')
    check('9999 still below evaluation ceiling',stop_action(.002,evaluations=POLICY['max_eval']-1)=='continue')
    check('Overshoot stops without another update',stop_action(.002,evaluations=POLICY['max_eval']+3)=='evaluation_budget')
    check('Replay mismatch rejected',not gates(1,2,0,20,1e-8,0)['objective_replay'])
    scenarios=[('Flat loss does not stop',dict(small_change=True),'continue'),
        ('Small transformed step does not stop',dict(small_step=True),'continue'),
        ('Negative tiny directional derivative continues',dict(gtd=-1e-15),'continue'),
        ('Nonnegative directional derivative fails',dict(gtd=0),'non_descent_failure'),
        ('Three identical updates fail',dict(unchanged=3),'unchanged_parameter_failure'),
        ('Two identical updates remain bounded',dict(unchanged=2),'continue'),
        ('Iteration ceiling stops',dict(iterations=POLICY['max_iter']),'iteration_budget'),
        ('Evaluation ceiling stops',dict(evaluations=POLICY['max_eval']),'evaluation_budget'),
        ('Nonfinite fails',dict(finite=False),'nonfinite_failure')]
    for name,kwargs,expected in scenarios:check(name,stop_action(.002,**kwargs)==expected)
    check('Original gradient candidate',stop_action(1e-7)=='original_gradient_candidate')
    # Exactly two original-mode fits, on identical data and zero initialization.
    from optimizer_preconditioning import SETTINGS
    results=[];traces=[]
    for local in [False,True]:
        v=torch.nn.Parameter(torch.zeros((6,97),device=device(),dtype=torch.float64))
        opt=torch.optim.LBFGS([v],**SETTINGS);record={};trace=[]
        if local:install_local_step(opt,record,original_mode=True)
        def closure():
            opt.zero_grad();loss=transformed_objective(v,l,ax,y,mass,0)
            loss.backward();trace.append(float(loss.detach()));return loss
        opt.step(closure);results.append(v.detach().clone());traces.append(trace);synthetic_fits+=1
        write(OUT/'manifests'/f'synthetic-reference-{int(local)}.json',
              {'iterations':int(opt.state[v]['n_iter']),'evaluations':int(opt.state[v]['func_evals']),
               'closure_values':trace,'local_observed':local})
    check('Original-mode parameters bitwise equal',torch.equal(*results))
    check('Original-mode closure trajectory equal',traces[0]==traces[1])
    # Two new-mode fits: normal and a fixed 300x scale condition stress.
    for name,xx in [('normal',x),('conditioned',x.clone())]:
        if name=='conditioned':xx[:,1]*=300
        _,log=fit_preconditioned(xx,y,mass,0,{'role_id':'tests/'+name,'arm':'synthetic',
            't':0,'input_sha256':'synthetic'},diagnostic=True)
        synthetic_fits+=1;check(name+' fit passes original gates',log['accepted'])
        check(name+' adopted-point gradient verified',log['gradient_replay_error']<1e-10)
    # Invalid input attempts no optimizer iteration, saved outside formal models.
    try:fit_preconditioned(x,y,mass*2,0,{'role_id':'tests/invalid-mass','arm':'synthetic',
        't':0,'input_sha256':'synthetic'},diagnostic=True)
    except RuntimeError:pass
    else:raise RuntimeError('Invalid mass accepted')
    failure=OUT/'diagnostic-failures/tests/invalid-mass/synthetic-t0.json'
    check('Invalid input logged',failure.exists() and not read(failure)['accepted'])
    check('Invalid state stored',failure.with_suffix('.pt').exists())
    check('No invalid formal model',(not (OUT/'models/tests').exists()))
    import copy
    for name in ['normal','conditioned']:
        log=read(OUT/'diagnostic-fit-logs/tests'/name/'synthetic-t0.json')
        validate_new_log(log)
        bad=copy.deepcopy(log);bad['numeric_policy_sha256']='wrong'
        try:validate_new_log(bad)
        except RuntimeError:check(name+' wrong policy rejected',True)
        else:raise RuntimeError('Wrong policy accepted')
    check('Historical policy kept distinct',base.read(PREP/'manifests/experiment-contract-amended-io-v1.json')['optimizer']['max_iter']==500)
    require(synthetic_fits==4,'Four synthetic fits only')
    write(OUT/'manifests/objective-equivalence.json',{'passed':True,'cases':errors,
        'max_absolute_error':max(row[k] for row in errors for k in ['objective','logits','gradient','roundtrip'])})
    write(OUT/'manifests/optimizer-unit-tests.json',{'passed':True,'checks':checks,'count':len(checks),
        'synthetic_fits':4,'invalid_input_attempts_without_steps':1,'CUDA_float64':True,
        'target_U_or_test_data_read':False})
    return len(checks)

def run():
    configure();require(not (OUT/'manifests/contract-seal.json').exists(),'V4 already sealed')
    require(not (PREP/'runner.lock').exists() and not (PREVIOUS/'runner.lock').exists(),'Prior runner active')
    c=base.contract();priorpath=PREVIOUS/'manifests/experiment-contract-v3.json';prior=read(priorpath)
    require(sha(priorpath)==read(priorpath.with_name('contract-seal.json'))['sha256'],'V3 contract seal')
    for p,h in {**c['source_sha256'],**prior['previous_source_sha256'],**prior['source_sha256']}.items():require(sha(ROOT/p)==h,'Old source changed')
    require(sha(PLAN)==c['plan_sha256'],'Original plan changed')
    for p,h in c['baseline_sha256'].items():require(sha(ROOT/p)==h,'Historical input changed')
    for p,info in c['packages'].items():require(sha(ROOT/p)==info['sha256'],'Package changed')
    adoption=read(PREVIOUS/'manifests/adopted-artifacts.json')
    require(sha(PREVIOUS/'manifests/adopted-artifacts.json')==prior['adopted_artifacts_sha256'],'Prior adoption inventory')
    files=dict(adoption['files'])
    for p,h in files.items():require(sha(ROOT/p)==h,'Adopted input changed')
    snapshots=dict(prior['original_snapshots'])
    for folder in ['models','pilot','failures','diagnostic-failures','fit-logs']:
        for p in (PREVIOUS/folder).rglob('*'):
            if p.is_file():files[rel(p)]=sha(p)
    for root in [PREP,ROOT/'outputs/calibrated-deployment-business-transfer-20261006/run-02',PREVIOUS]:
        for name in ['failure.json','progress.json','runner.stdout.log','runner.stderr.log']:
            p=root/name
            if p.exists():snapshots[rel(p)]=sha(p)
        for p in (root/'manifests/stages').glob('*.json'):snapshots[rel(p)]=sha(p)
    for p in (ROOT/'docs/calibrated-deployment-business-transfer').rglob('*'):
        if p.is_file() and not p.is_relative_to(DOC):snapshots[rel(p)]=sha(p)
    slotcount=0
    for r in c['main']:
        for arm in ARMS:
            p=PREP/'slots'/r['id']/(arm+'.pt')
            s=torch.load(p,map_location=device(),weights_only=True)
            require(torch.isfinite(s['x']).all() and (s['mass']>0).all(),'Invalid slot')
            require(float((weighted(s['y'],s['mass'],6)-1/6).abs().max())<1e-12,'Slot class mass')
            require(s['x'].shape in [(336,96),(640,96)],'Slot shape');slotcount+=1
        if slotcount%500==0:progress('GS01_slot_audit',slots=slotcount,total=3900)
    require(slotcount==3900,'Slot count')
    ids=pilot_ids(c)
    require(ids==read(PREVIOUS/'manifests/pilot-role-registry.json')['ids'],'V3 pilot registry changed')
    write(OUT/'manifests/numeric-policy.json',POLICY)
    write(OUT/'manifests/pilot-role-registry.json',{'ids':ids,'roles':15,'candidates':300})
    write(OUT/'manifests/recovery-input-inventory.json',{'snapshots':snapshots,'old_runs_read_only':True,
        'v1_diagnostic_models':680,'v1_main_models':4,'v2_accepted_main_models':104,'v3_unpromoted_pilot_models':24})
    write(OUT/'manifests/adopted-artifacts.json',{'files':files,'training_slots_verified':slotcount,'old_only_read':True})
    write(OUT/'manifests/path-contract.json',{'input_root':rel(PREP),'output_root':rel(OUT),'report_root':rel(DOC),
        'old_main_model_reuse':0,'main_candidates':14700})
    for name in ['content-folds.parquet','cohort-visits.parquet','reused-post-models.json']:
        src=PREP/'manifests'/name;dst=writable(OUT/'manifests'/name);dst.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(src,dst);require(sha(src)==sha(dst),'Copied manifest changed')
    for name in ['classification-summary.parquet','kernel-feature-summary.parquet']:
        src=PREP/'diagnostics'/name;dst=writable(OUT/'diagnostics'/name);dst.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(src,dst);require(sha(src)==sha(dst),'Copied diagnostics changed')
    reference=reference_metadata();write(OUT/'manifests/reference-source-and-solver-diff.json',reference)
    checks=unit_tests()
    sources={rel(p):sha(p) for p in Path(__file__).parent.iterdir() if p.suffix=='.py' or p.name=='README.md'}
    v={'version':'v4-original-gradient-aware-lbfgs','original_contract_sha256':sha(PREP/'manifests/experiment-contract-amended-io-v1.json'),
       'original_plan_sha256':sha(PLAN),'repair_plan_sha256':sha(REPAIR_PLAN),'source_sha256':sources,
       'previous_contracts':{**prior['previous_contracts'],rel(priorpath):sha(priorpath)},
       'previous_source_sha256':{**prior['previous_source_sha256'],**prior['source_sha256']},
       'adopted_artifacts_sha256':sha(OUT/'manifests/adopted-artifacts.json'),'original_snapshots':snapshots,
       'pilot_roles':ids,'formal_main_inner_fits':14400,'formal_main_outer_fits':300,'synthetic_fits':4,
       'reused_diagnostic_models':680,'deterministic_diagnostic_fits':2,'old_main_refits':108,'old_unpromoted_pilot_not_reused':24,
       'numeric_policy_sha256':sha(OUT/'manifests/numeric-policy.json'),
       'objective_equivalence_sha256':sha(OUT/'manifests/objective-equivalence.json'),
       'unit_tests_sha256':sha(OUT/'manifests/optimizer-unit-tests.json'),
       'installed_LBFGS_sha256':reference['installed_file_sha256'],
       'reference_and_diff_sha256':sha(OUT/'manifests/reference-source-and-solver-diff.json'),
       'methods_labels_coordinates_permissions_changed':False,'stopping_rule_changed':False,
       'iteration_budget_gate_changed':True,'precision_gates_changed':False,
       'max_iter':POLICY['max_iter'],'max_eval':POLICY['max_eval']}
    write(OUT/'manifests/experiment-contract-v4.json',v)
    complete(OUT/'manifests/contract-seal.json',sha256=sha(OUT/'manifests/experiment-contract-v4.json'))
    progress('GS06_v4_contract_sealed',unit_checks=checks,adopted_files=len(files),pilot_models=300)

if __name__=='__main__':
    import traceback
    try:run()
    except BaseException as exc:
        write(OUT/'preparation-failure.json',{'exception':str(exc),'traceback':traceback.format_exc()})
        progress('engineering_stop_before_contract',error=str(exc));raise
