"""Freeze source priority, old terminal records and all NR2 full inputs."""
from common import *
from weight_schedule import registry
from backend import modules

def run():
    with stage('R0'):
        parent=read(FULL1/'manifests/contract.json');nr=read(NR2/'manifests/contract.json');comp=read(NR2/'completion.json')
        require(sha(FULL1/'manifests/contract.json')==read(FULL1/'manifests/seal.json')['sha256'],'Full NR1 contract seal')
        require(sha(NR2/'manifests/contract.json')==read(NR2/'manifests/seal.json')['sha256'],'NR2 contract seal')
        require(comp['pilot_program_complete'] and read(NR2/'verification.json')['passed'] and comp['all_52_cases_accepted'],'NR2 not qualified')
        require(sha(ROOT/'docs/role-asymmetric-transfer-v1-20261017/nr2-run02/complete-report-20261018.md')==comp['report_sha256'],'NR2 report seal')
        require((OLD/'failure.json').exists() and (FULL1/'failure.json').exists() and not (FULL1/'completion.json').exists(),'Preserve old stops')
        require(sha(Path(inspect.getfile(torch.optim.LBFGS)))==nr['environment']['installed_LBFGS_sha256'],'Installed LBFGS changed')
        fixed=dict(parent['fixed']);arts=dict(parent['artifacts'])
        def fix(p,expected=None):
            budget_check();h=sha(p);require(expected is None or h==expected,'Changed source '+rel(p));fixed[rel(p)]=h;checked(p,h,'resume-registration');return h
        def art(p,expected=None):
            meta=read(p.with_suffix('.json'));h=fix(p,expected);require(meta['sha256']==h,'Artifact source checksum');arts[rel(p)]=h;fix(p.with_suffix('.json'));return meta
        for p,h in parent['code'].items():fix(ROOT/p,h)
        for p,h in nr['code'].items():fix(ROOT/p,h)
        for p,h in nr['protected'].items():fix(ROOT/p,h)
        for p in [FULL1/'manifests/contract.json',FULL1/'manifests/seal.json',FULL1/'failure.json',FULL1/'cost-final.json',
                  FULL1/'run-closeout.json',FULL1/'manifests/adopted-endpoints.parquet',NR2/'manifests/contract.json',NR2/'manifests/seal.json',
                  NR2/'completion.json',NR2/'verification.json',NR2/'cost-final.json',NR2/'analysis/interpretation.json',
                  NR2/'audits/prefix-comparison.json',NR2/'audits/deterministic-repeats.json',NR2/'audits/engineering.json',
                  NR2/'audits/old-endpoint-compatibility.json']:
            fix(p)
        old=pd.read_parquet(FULL1/'manifests/adopted-endpoints.parquet').replace({np.nan:None}).to_dict('records')
        old.extend(read(p) for p in (FULL1/'new-endpoints').rglob('*.json'));require(len(old)==1024,'Old available 1024')
        sources={}
        for e in old:
            path=ROOT/e['path'];meta=art(path,e['sha256']);key=(e['role_id'],e['policy_id']);log=meta['optimizer']
            slot=ROOT/e['slot_path'] if e.get('slot_path') else None
            if slot:art(slot)
            source_policy=(path.parent/'manifests/numeric-policy.json') if e['source']=='NR1-pilot' else ((FULL1 if e['source']=='NR1-full-new' else OLD)/'manifests/numeric-policy.json')
            fix(source_policy,log['numeric_policy_sha256'])
            sources[key]=dict(role_id=key[0],policy_id=key[1],path=rel(path),sha256=e['sha256'],slot_path=rel(slot) if slot else None,
                source=e['source'],source_kind='v4',source_policy_path=rel(source_policy),source_policy_sha256=log['numeric_policy_sha256'],
                source_max_iter=log['settings']['max_iter'],source_max_eval=log['settings']['max_eval'],result_path=None,result_sha256=None)
        previous=dict(sources);nrkeys=[]
        for p in (NR2/'endpoints').rglob('endpoint.json'):
            fix(p);e=read(p);key=(e['role_id'],e['policy_id']);path=ROOT/e['model_path'];art(path,e['model_sha256'])
            slot=NR2/'slots'/e['role_id']/(e['policy_id']+'.pt');art(slot)
            result=ROOT/e['result_path'];rh=fix(result)
            sources[key]=dict(role_id=key[0],policy_id=key[1],path=rel(path),sha256=e['model_sha256'],slot_path=rel(slot),
                source='NR2-pilot',source_kind='NR2',source_policy_path=rel(NR2/'manifests/contract.json'),
                source_policy_sha256=sha(NR2/'manifests/contract.json'),source_policy_kind='contract.design.solver_proposal',
                source_max_iter=4000,source_max_eval=20000,result_path=rel(result),result_sha256=rh)
            nrkeys.append(key)
        require(len(nrkeys)==len(set(nrkeys))==52 and len(set(nrkeys)&set(previous))==32,'NR2 source overlap')
        require(len(sources)==1044,'1044 adoption candidates')
        total={(r['id'],p['id']) for r in parent['roles'] for p in registry()};pending=sorted(total-set(sources))
        require(len(total)==2340 and len(pending)==1296,'Pending full coverage')
        own={rel(p):sha(p) for p in Path(__file__).parent.glob('*.py')}
        for name in ['predict.py','score.py']:
            require(ast.dump(ast.parse((OLD_CODE/name).read_text()))==ast.dump(ast.parse(Path(__file__).with_name(name).read_text())),'Prediction/scoring AST changed')
        n,l=modules()
        for name,m in [('numeric',n),('legacy_prefix',l)]:
            original=ast.parse((NR2_CODE/(name+'.py')).read_text())
            require(all(f.name in vars(m) for f in original.body if isinstance(f,ast.FunctionDef)),'Sealed NR2 functions not loaded')
        policy=nr['design']['solver_proposal']
        require(policy['lbfgs_phase_update_limit']==1024 and policy['newton_update_limit']==32 and policy['original_gradient_limit']==1e-5,'NR2 source numerical contract')
        write(OUT/'manifests/numeric-policy.json',dict(**POLICY,sealed_NR2_policy=policy,source_contract_sha256=sha(NR2/'manifests/contract.json')))
        fixed[rel(OUT/'manifests/numeric-policy.json')]=sha(OUT/'manifests/numeric-policy.json')
        c=dict(version='RA1-full-NR2-resume',roles=parent['roles'],policies=registry(),primary=parent['primary'],references=parent['references'],
            packages=parent['packages'],fixed=fixed,artifacts=arts,code=own,plan_sha256=sha(PLAN),
            adopted=list(sources.values()),pending=[dict(role_id=r,policy_id=p) for r,p in pending],
            protected_old_available=len(previous),NR2_scientific_priority_count=52,overlap32_preserved=True,
            adopted_scientific=624,historical_aliases=420,new_fit_count=1296,prior_optimization_attempts=697,total_optimization_cap=2348,
            original_failure_sha256=sha(OLD/'failure.json'),full_NR1_failure_sha256=sha(FULL1/'failure.json'),
            prior_activity_components=read(OUT/'manifests/prior-activity.json'),cumulative_cap_seconds=28800,
            environment=dict(nr['environment'],full_resume_torch=str(torch.__version__)),new_method_selected_after_H=False)
        write(OUT/'manifests/contract.json',c);write(OUT/'manifests/seal.json',dict(sha256=sha(OUT/'manifests/contract.json')))
        save(pd.DataFrame(c['adopted']),OUT/'manifests/adoption-candidates.parquet');save(pd.DataFrame(c['pending']),OUT/'manifests/pending-initial.parquet')
        textfile(DOC/'resume-contract.md',PLAN.read_text(encoding='utf-8'))
        write(OUT/'audits/backend-binding.json',dict(passed=True,source_numeric_sha256=sha(NR2_CODE/'numeric.py'),source_legacy_sha256=sha(NR2_CODE/'legacy_prefix.py'),
            functions_compiled_without_body_changes=True,runtime_changes=['IO paths','activity guard','sealed common runtime'],prediction_scoring_AST_identical=True))
        progress('NR2_full_contract_sealed',adoption_candidates=1044,new_pending=1296)
