"""N0 registration and canonical train-only inputs; all old outputs read-only."""
from common import *
from backend_loader import weight_functions,policy

def run():
    with phase('N0'):
        require(not (OUT/'manifests/seal.json').exists(),'Already registered')
        old=read(OLD/'manifests/contract.json');require(sha(OLD/'manifests/contract.json')==read(OLD/'manifests/seal.json')['sha256'],'Parent contract')
        require((OLD/'failure.json').exists() and not (OLD/'completion.json').exists(),'Preserve original stop')
        design=read(CASES);require(len(design['cases'])==42 and design['max_new_fit_attempts']==45 and not design['full_matrix_auto_start'],'Fixed design')
        allowed={};preserve={};accepted=[]
        def bind(p,expected=None,artifact=False):
            h=sha(p);require(expected is None or h==expected,'Parent hash mismatch '+rel(p));preserve[rel(p)]=h;checked(p,h,'registration-hash')
            if artifact:allowed[rel(p)]=h
            return h
        for p in [OLD/'manifests/contract.json',OLD/'manifests/seal.json',OLD/'failure.json',OLD/'cost-ledger.json',
                  OLD/'stages/P0.json',OLD/'stages/P1.json',OLD/'stages/P2.json',OLD/'audits/P1-complete.json']:
            bind(p)
        for p,h in old['code'].items():bind(ROOT/p,h)
        for p in (OLD/'models').rglob('*.pt'):
            info=read(p.with_suffix('.json'));bind(p,info['sha256'],True);bind(p.with_suffix('.json'))
            require(info['optimizer']['accepted'],'Old accepted model metadata')
            accepted.append(dict(role_id=info['role_id'],policy_id=info['policy_id'],path=rel(p),sha256=info['sha256'],metadata_sha256=sha(p.with_suffix('.json'))))
        require(len(accepted)==151,'Old model count')
        fp=OLD/'failures'/FAIL_ROLE/(FAIL_POLICY+'-t4.pt')
        bind(fp,artifact=True);bind(fp.with_suffix('.json'))
        require(read(fp.with_suffix('.json'))['optimizer_exit_reason']=='iteration_budget','Known old stop')
        roles={r['id']:r for r in old['roles']};weights=weight_functions();policies={p['id']:p for p in weights.registry()}
        for rid in sorted({x['role_id'] for x in design['cases']}):
            p=OLD/'packages'/rid/'training.pt';bind(p,read(p.with_suffix('.json'))['sha256'],True);bind(p.with_suffix('.json'))
        # Canonical slot audit for every accepted old endpoint supports later
        # read-only compatibility review, without making them formal NR1 models.
        for item in accepted:
            p=OLD/'numeric-slots'/item['role_id']/(item['policy_id']+'.pt');bind(p,read(p.with_suffix('.json'))['sha256'],True);bind(p.with_suffix('.json'))
        for case in design['cases']:
            p=OLD/'numeric-slots'/case['role_id']/(case['policy_id']+'.pt')
            if p.exists():bind(p,read(p.with_suffix('.json'))['sha256'],True);bind(p.with_suffix('.json'))
        own={rel(p):sha(p) for p in Path(__file__).parent.glob('*.py')}
        env=dict(python=sys.executable,torch=str(torch.__version__),numpy=np.__version__,cuda=torch.version.cuda,gpu=torch.cuda.get_device_name(0),
                 CUBLAS_WORKSPACE_CONFIG=os.environ['CUBLAS_WORKSPACE_CONFIG'],installed_LBFGS=inspect.getfile(torch.optim.LBFGS),installed_LBFGS_sha256=sha(Path(inspect.getfile(torch.optim.LBFGS))))
        require(env['installed_LBFGS_sha256']==old['environment']['installed_LBFGS_sha256'],'Installed optimizer changed')
        c=dict(version='RA1-NR1-numeric-pilot',authorization='User approved 4000/20000, 30 minutes, no full restart',registered_unix=time.time(),
            plan_sha256=sha(PLAN),cases_sha256=sha(CASES),design=design,allowed_inputs=allowed,preserve=preserve,code=own,environment=env,
            roles={k:roles[k] for k in {x['role_id'] for x in design['cases']}},policies=policies,accepted_old=accepted,
            old_role_settings={k:dict(t=v['t'],eta=v['eta']) for k,v in roles.items()},
            old_failure_state=rel(fp),old_policy=policy(True).POLICY,new_policy=policy(False).POLICY,parent_active_seconds=read(OLD/'cost-ledger.json')['active_seconds'],
            activity_limit_seconds=1800,compute_reserve_seconds=60,max_attempts=45,full_matrix_auto_start=False,H_query_reads=0,H_label_reads=0,actual_target_U_reads=0)
        write(OUT/'manifests/contract.json',c);write(OUT/'manifests/seal.json',dict(sha256=sha(OUT/'manifests/contract.json')))
        write(OUT/'manifests/fixed-cases.json',design)
        fingerprints=[]
        for case in design['cases']:
            r=roles[case['role_id']];p=policies[case['policy_id']];v=old_artifact(OLD/'packages'/r['id']/'training.pt');s=weights.slot(v,p,r['missing'])
            oldslot=OLD/'numeric-slots'/r['id']/(p['id']+'.pt')
            if oldslot.exists():
                existing=old_artifact(oldslot);require(all(torch.equal(s[k],existing[k]) for k in s),'Original slot row content changed')
            sig=signature(s);dst=OUT/'slots'/r['id']/(p['id']+'.pt');put(dst,s,role_id=r['id'],policy_id=p['id'],content_fingerprint=sig['sha256'])
            fingerprints.append(dict(role_id=r['id'],policy_id=p['id'],**sig))
        write(OUT/'manifests/input-fingerprints.json',fingerprints)
        write(OUT/'audits/N0.json',dict(passed=True,cases=42,old_accepted_models=151,new_maps=0,H_reads=0,U_reads=0))
