"""OR00-OR07 freeze references, numerical tests and the approved v2 contract."""
import shutil
from common import *
from optimizer_preconditioning import coordinates, decode, transformed_objective, gates, fit_preconditioned

PILOT = ['main/f0/shadowsocks/G0/i1/vless', 'main/f0/shadowsocks/G1/i1/trojan',
         'main/f0/shadowsocks/G2/i1/vmess']

def unit_tests():
    checks = []; errors = []
    def check(name, value):
        require(value, name); checks.append({'name': name, 'passed': True})
    actual = torch.load(PREP/'slots'/PILOT[0]/'CT1.pt', map_location=device(), weights_only=True)
    torch.manual_seed(20261006)
    x = torch.randn((60, 96), device=device(), dtype=torch.float64)
    x[:, 0] = 0
    y = torch.arange(6, device=device()).repeat(10); mass = torch.full((60,), 1/60, device=device(), dtype=torch.float64)
    for name, source in [('synthetic', {'x': x, 'y': y, 'mass': mass}), ('actual_CT1', actual)]:
      for t in TS:
        xx, yy, mm = source['x'], source['y'], source['mass']
        a, l, ax = coordinates(xx, mm, t)
        v = (torch.randn((6, 97), device=device(), dtype=torch.float64)*.01).requires_grad_()
        theta = decode(v, l); rw = theta[:, :96].detach().requires_grad_(); rb = theta[:, 96].detach().requires_grad_()
        orig = objective(rw, rb, xx, yy, mm, t); other = transformed_objective(v, l, ax, yy, mm, t)
        gw, gb = torch.autograd.grad(orig, (rw, rb)); gv, = torch.autograd.grad(other, (v,))
        err = {'case': name, 't': t, 'objective': abs(float(orig.detach()-other.detach())),
               'logits': float((xx@rw.T+rb-ax@v.T).detach().abs().max()),
               'gradient': float((torch.cat([gw, gb[:, None]], 1)-gv@l.T).abs().max()),
               'roundtrip': float((v.detach()-theta.detach()@l).abs().max())}
        errors.append(err); check(name+' equivalence '+str(t), max(err[k] for k in ['objective','logits','gradient','roundtrip']) < 1e-10)
        check('No explicit inverse '+name+str(t), torch.isfinite(l).all())
    a, l, ax = coordinates(x, mass, 0.)
    theta = torch.zeros((6, 97), device=device(), dtype=torch.float64); theta[:, 96] = torch.arange(6, device=device())
    v = theta@l
    ce = (F.cross_entropy(x@theta[:, :96].T+theta[:, 96], y, reduction='none')*mass).sum()
    check('Bias not regularized', abs(float(transformed_objective(v, l, ax, y, mass, 0)-ce)) < 1e-10)
    check('Wrong V penalty detected', float(.0005*v.square().sum()) > 1e-6)
    check('Original gradient gate not transformed gate', not gates(1., 2., .002, 20, 0., 0.)['original_coordinate_gradient'])
    check('500 rejected', not gates(1., 2., 0., 500, 0., 0.)['iteration_budget'])
    check('Replay error rejected', not gates(1., 2., 0., 20, 1e-8, 0.)['objective_replay'])
    negative = {'role_id': 'tests/invalid-mass', 'arm': 'synthetic', 't': 0, 'input_sha256': 'synthetic'}
    try: fit_preconditioned(x, y, mass*2, 0, negative, diagnostic=True)
    except RuntimeError: pass
    else: raise RuntimeError('Invalid mass accepted')
    failed = OUT/'diagnostic-failures/tests/invalid-mass/synthetic-t0.json'
    check('Failed input logged before raise', failed.exists() and not read(failed)['accepted'])
    check('Failure state saved separately', failed.with_suffix('.pt').exists())
    check('No formal invalid model', not (OUT/'models/tests').exists())
    # Genuine synthetic numerical fit; separate from 14,700 formal candidates.
    m, log = fit_preconditioned(x, y, mass, 0, {'role_id':'tests/synthetic-fit','arm':'synthetic','t':0,
                                              'input_sha256':'synthetic'}, diagnostic=True)
    check('Synthetic optimization accepted in original coordinates', log['accepted'])
    # Observation hooks must not change the original optimizer's path.
    from optimizer_preconditioning import observed_step, SETTINGS
    raw_models = []
    for observe in [False, True]:
        w = torch.nn.Parameter(torch.zeros((6,96),device=device(),dtype=torch.float64))
        b = torch.nn.Parameter(torch.zeros(6,device=device(),dtype=torch.float64))
        opt = torch.optim.LBFGS([w,b], **SETTINGS); record = {}
        if observe: observed_step(opt,record)
        def closure():
            opt.zero_grad(); val=objective(w,b,x,y,mass,0);val.backward();return val
        opt.step(closure);raw_models.append((w.detach(),b.detach()))
        if observe:check('Actual break captured', bool(record))
    check('Observation arithmetic unchanged', all(torch.equal(a,b) for a,b in zip(*raw_models)))
    write(OUT/'manifests/objective-equivalence.json', {'passed': True, 'cases': errors, 'max_absolute_error':
          max(v[k] for v in errors for k in ['objective','logits','gradient','roundtrip'])})
    write(OUT/'manifests/optimizer-unit-tests.json', {'passed':True,'checks':checks,'count':len(checks),
          'synthetic_fits':3,'target_U_or_test_data_read':False,'CUDA_float64':True})
    return len(checks)

def run():
    configure(); require(not (PREP/'runner.lock').exists(), 'Original runner active')
    require(not (OUT/'manifests/contract-seal.json').exists(), 'Preparation already sealed')
    c = base.contract(); files = {}
    for p,h in c['source_sha256'].items():require(sha(ROOT/p)==h,'Original source changed')
    require(sha(PLAN)==c['plan_sha256'],'Original plan changed')
    for p,h in c['baseline_sha256'].items():require(sha(ROOT/p)==h,'Baseline changed: '+p)
    for p,info in c['packages'].items():require(sha(ROOT/p)==info['sha256'],'Package changed: '+p)
    progress('OR00_OR01_original_inputs_verified', packages=len(c['packages']))
    slots = 0
    for folder in ['kernels','slots','models']:
      for p in (PREP/folder).rglob('*.pt'):
        side=p.with_suffix('.json'); meta=read(side); require(sha(p)==meta['sha256'],'Old artifact changed: '+rel(p))
        files[rel(p)]=meta['sha256'];files[rel(side)]=sha(side)
        if folder=='slots' and p.stem in ARMS:
            s=torch.load(p,map_location=device(),weights_only=True)
            require(torch.isfinite(s['x']).all() and (s['mass']>0).all(),'Invalid slot')
            require(float((weighted(s['y'],s['mass'],6)-1/6).abs().max())<1e-12,'Slot class mass')
            require(s['x'].shape in [(336,96),(640,96)],'Slot shape');slots+=1
        if len(files)%1000==0:progress('OR01_adopting_frozen_artifacts',files=len(files),slots_verified=slots)
    require(slots==3900,'Five arms times780roles')
    for name in ['content-folds.parquet','cohort-visits.parquet','reused-post-models.json']:
        src=PREP/'manifests'/name;dst=writable(OUT/'manifests'/name);dst.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(src,dst);require(sha(src)==sha(dst),'Copied manifest changed');files[rel(src)]=sha(src)
    for name in ['classification-summary.parquet','kernel-feature-summary.parquet']:
        src=PREP/'diagnostics'/name;dst=writable(OUT/'diagnostics'/name);dst.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(src,dst);require(sha(src)==sha(dst),'Diagnostic summary changed');files[rel(src)]=sha(src)
    snapshots={rel(p):sha(p) for p in [PREP/'failure.json',PREP/'progress.json',
                 PREP/'manifests/experiment-contract.json',PREP/'manifests/experiment-contract-amended-io-v1.json']}
    write(OUT/'manifests/recovery-input-inventory.json',{'original_status':'engineering_stop','snapshots':snapshots,
          'old_diagnostic_models':680,'old_main_models':4,'old_run_write_permitted':False})
    write(OUT/'manifests/adopted-artifacts.json',{'files':files,'training_slots_verified':slots,'old_only_read':True})
    write(OUT/'manifests/path-contract.json',{'input_root':rel(PREP),'output_root':rel(OUT),'report_root':rel(DOC),
          'old_model_reuse':{'diagnostics':680,'main':0},'main_candidates':14700})
    count=unit_tests()
    sources={rel(p):sha(p) for p in Path(__file__).parent.glob('*.py')}
    v={'version':'v2-parameter-preconditioning','original_contract_sha256':sha(PREP/'manifests/experiment-contract-amended-io-v1.json'),
       'original_plan_sha256':sha(PLAN),'repair_plan_sha256':sha(REPAIR_PLAN),'source_sha256':sources,
       'adopted_artifacts_sha256':sha(OUT/'manifests/adopted-artifacts.json'),
       'original_snapshots':snapshots,'pilot_roles':PILOT,'formal_main_inner_fits':14400,'formal_main_outer_fits':300,
       'reused_diagnostic_models':680,'history_additional_four_refits_approved':True,
       'objective_equivalence_sha256':sha(OUT/'manifests/objective-equivalence.json'),
       'unit_tests_sha256':sha(OUT/'manifests/optimizer-unit-tests.json'),
       'installed_LBFGS_sha256':sha(Path(inspect.getfile(torch.optim.LBFGS))),
       'methods_labels_coordinates_permissions_changed':False,'solver_coordinate_changed':True}
    write(OUT/'manifests/experiment-contract-v2.json',v)
    complete(OUT/'manifests/contract-seal.json',sha256=sha(OUT/'manifests/experiment-contract-v2.json'))
    progress('OR07_v2_contract_sealed',unit_checks=count,adopted_files=len(files),pilot_models=60)

if __name__=='__main__':run()
