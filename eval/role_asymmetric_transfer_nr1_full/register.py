"""Frozen resume contract and source lineage; no H probability/label reads."""
from common import *
from weight_schedule import registry

def run():
    with stage('R0'):
        old=read(OLD/'manifests/contract.json');nr=read(NR/'manifests/contract.json');comp=read(NR/'completion.json')
        require(sha(OLD/'manifests/contract.json')==read(OLD/'manifests/seal.json')['sha256'],'Old contract seal')
        require(sha(NR/'manifests/contract.json')==read(NR/'manifests/seal.json')['sha256'],'NR1 contract seal')
        require(comp['pilot_program_complete'] and comp['ready_for_full_resume_review'] and read(NR/'verification.json')['passed'],'NR1 not qualified')
        require((OLD/'failure.json').exists() and not (OLD/'completion.json').exists(),'Preserve original stop')
        require(sha(Path(inspect.getfile(torch.optim.LBFGS)))==old['environment']['installed_LBFGS_sha256'],'Installed LBFGS changed')
        require(sha(ROOT/'docs/role-asymmetric-transfer-v1-20261017/numeric-pilot-report-20261018.md')==comp['report_sha256'],'NR1 report seal')
        fixed=dict(old['fixed']);arts=dict(old['artifacts']);sources={}
        def fix(p,expected=None):
            h=sha(p);require(expected is None or h==expected,'Changed source '+rel(p));fixed[rel(p)]=h;checked(p,h,'resume-registration');return h
        def art(p,expected=None):
            meta=read(p.with_suffix('.json'));h=fix(p,expected);require(h==meta['sha256'],'Artifact checksum');arts[rel(p)]=h;fix(p.with_suffix('.json'));return meta
        for p,h in old['code'].items():fix(ROOT/p,h)
        for p,h in nr['code'].items():fix(ROOT/p,h)
        for p,h in nr['preserve'].items():fix(ROOT/p,h)
        for p in [OLD/'manifests/contract.json',OLD/'manifests/seal.json',OLD/'failure.json',OLD/'cost-ledger.json',
                  NR/'manifests/contract.json',NR/'manifests/seal.json',NR/'completion.json',NR/'verification.json',NR/'cost-ledger.json',
                  NR/'audits/old-stop-reproduction.json',NR/'audits/prefix-comparison.json',NR/'audits/deterministic-repeats.json',
                  NR/'analysis/summary.json',ROOT/'outputs/role-asymmetric-transfer-v1-20261017/closeout-20261018/stop-analysis.json']:
            fix(p)
        for r in old['roles']:
            p=trainpath(r);art(p)
        for p in (NR/'endpoints').rglob('*.json'):
            e=read(p);key=(e['role_id'],e['policy_id']);path=ROOT/e['root']/'model.pt';meta=art(path)
            source_policy=ROOT/e['root']/'manifests/numeric-policy.json'
            fix(source_policy,meta['optimizer']['numeric_policy_sha256']);require(read(source_policy)==POLICY,'NR1 source policy differs')
            slot=NR/'slots'/e['role_id']/(e['policy_id']+'.pt');art(slot)
            sources[key]=dict(role_id=e['role_id'],policy_id=e['policy_id'],path=rel(path),sha256=arts[rel(path)],slot_path=rel(slot),source='NR1-pilot',source_max_iter=4000,source_max_eval=20000,
                source_policy_sha256=meta['optimizer']['numeric_policy_sha256'],source_run=rel(NR))
            fix(p)
        require(len(sources)==42,'42 NR1 endpoints')
        for e in nr['accepted_old']:
            key=(e['role_id'],e['policy_id'])
            if key in sources:continue
            path=ROOT/e['path'];meta=art(path,e['sha256']);slot=OLD/'numeric-slots'/e['role_id']/(e['policy_id']+'.pt');art(slot)
            require(meta['optimizer']['numeric_policy_sha256']==sha(OLD/'manifests/numeric-policy.json'),'Old accepted source policy')
            sources[key]=dict(role_id=e['role_id'],policy_id=e['policy_id'],path=rel(path),sha256=e['sha256'],slot_path=rel(slot),source='old-accepted-budget-compatible',source_max_iter=2000,source_max_eval=10000,
                source_policy_sha256=meta['optimizer']['numeric_policy_sha256'],source_run=rel(OLD))
        require(len(sources)==166,'Scientific adoption union')
        aliases={p['alias']:p for p in registry() if p['alias']}
        for e in old['historical_endpoints']:
            path=ROOT/e['path'];meta=art(path,e['sha256']);key=(e['role_id'],aliases[e['alias']]['id'])
            require(meta['optimizer']['numeric_policy_sha256']==sha(OLD/'manifests/numeric-policy.json'),'Historical reference source policy')
            require(key not in sources,'Alias/scientific collision')
            sources[key]=dict(role_id=e['role_id'],policy_id=key[1],path=rel(path),sha256=e['sha256'],slot_path=None,source='historical-reference',source_max_iter=2000,source_max_eval=10000,
                source_policy_sha256=meta['optimizer']['numeric_policy_sha256'],source_run=str(Path(e['path']).parent),historical_alias=e['alias'])
        require(len(sources)==586,'Total adoption count')
        for parent in [TI,SA]:
            fix(parent/'predictions/complete.json')
            fixed[rel(parent/'predictions/visits.parquet')]=read(parent/'predictions/complete.json')['sha256']
        own={rel(p):sha(p) for p in Path(__file__).parent.glob('*.py')}
        require(ast.dump(ast.parse((OLD_CODE/'score.py').read_text()))==ast.dump(ast.parse(Path(__file__).with_name('score.py').read_text())),'Scoring algorithm changed')
        require(ast.dump(ast.parse((OLD_CODE/'predict.py').read_text()))==ast.dump(ast.parse(Path(__file__).with_name('predict.py').read_text())),'Inference algorithm changed')
        write(OUT/'manifests/numeric-policy.json',POLICY)
        totalkeys={(r['id'],p['id']) for r in old['roles'] for p in registry()};pending=sorted(totalkeys-set(sources))
        require(len(totalkeys)==2340 and len(pending)==1754,'Full matrix coverage')
        c=dict(version='RA1-full-NR1-resume',authorization='User approved resume with NR1, uniform 4000/20000, original 8h cumulative cap',registered_unix=time.time(),
            plan_sha256=sha(PLAN),roles=old['roles'],policies=registry(),primary=old['primary'],references=old['references'],packages=old['packages'],
            fixed=fixed,artifacts=arts,code=own,environment=dict(old['environment'],resume_torch=str(torch.__version__),resume_numpy=np.__version__),
            adopted=list(sources.values()),pending=[dict(role_id=a,policy_id=b) for a,b in pending],original_failure_sha256=sha(OLD/'failure.json'),
            new_fit_count=1754,adopted_scientific=166,historical_aliases=420,prior_activity_components=read(OUT/'manifests/prior-activity.json'),
            cumulative_cap_seconds=28800,prior_fit_attempts=200,total_fit_cap=2348,source_model_logs_never_rewritten=True,source_historical_H_read_before_selection=False)
        write(OUT/'manifests/contract.json',c);write(OUT/'manifests/seal.json',dict(sha256=sha(OUT/'manifests/contract.json')))
        save(pd.DataFrame(c['adopted']),OUT/'manifests/adoption-candidates.parquet');save(pd.DataFrame(c['pending']),OUT/'manifests/pending-initial.parquet')
        textfile(DOC/'resume-contract.md',PLAN.read_text(encoding='utf-8'))
        progress('resume_contract_sealed',adoption_candidates=586,new_pending=1754)
