"""Register all allowed assets without opening any numeric H/U data."""
from common import *

def run():
    configure();require(not (OUT/'manifests/seal.json').exists(),'Formal run already registered')
    ds=read(DS/'manifests/experiment-contract.json');jc=read(JA/'manifests/experiment-contract.json')
    sc=read(SA/'manifests/experiment-contract.json');ac=read(AG/'manifests/experiment-contract.json')
    ix=read(AG/'packages/index.json');roles=ds['roles'];inners=ds['inner_roles']
    require(len(roles)==60 and len(inners)==720,'Role counts')
    result=read(V2/'completion.json')
    require(result['numeric_qualified'] and result['status']=='qualified_solution_feedback_v2','Numerical prerequisite')
    require(sha(V2/'verification.json')==result['verification_sha256'],'V2 verification seal')
    fixed={};artifacts={};packages={};membership=[];refs=[]
    failed_root=ROOT/'outputs/dynamic-soft-drift-business-formal-20261012/run-01'
    old=read(failed_root/'completion.json')
    require(old['status']=='stop_formal_gate_failure' and not old['H_scored'],'Preserve first failure')
    old_contract=read(failed_root/'manifests/experiment-contract.json')
    require(sha(failed_root/'manifests/experiment-contract.json')==read(failed_root/'manifests/seal.json')['contract_sha256'],'Old formal seal')
    for path,h in old_contract['code'].items():require(sha(ROOT/path)==h,'Old formal source modified')
    def fix(p):fixed[rel(p)]=sha(p)
    for root in [DS,JA,TI,SA,AG,CJ]:
        p=root/'manifests/experiment-contract.json';require(sha(p)==read(p.with_name('seal.json'))['contract_sha256'],'Parent contract seal');fix(p);fix(p.with_name('seal.json'))
    for p in [V2/'completion.json',V2/'verification.json',V2/'manifests/contract.json',V2/'manifests/seal.json',
              AG/'packages/index.json',AG/'packages/complete.json',AG/'diagnostics/predictions-complete.json',
              SA/'manifests/models-complete.json',SA/'manifests/new-endpoints.parquet',CJ/'completion.json',
              TI/'manifests/views-complete.json']:
        fix(p)
    vv=read(V2/'verification.json')
    for p,h in vv['files'].items():require(sha(ROOT/p)==h,'V2 artifact changed');fixed[p]=h
    require(sha(AG/'packages/index.json')==read(AG/'packages/complete.json')['index_sha256'],'C index changed')
    def art(p,kind,r):
        info=read(p.with_suffix('.json'));require(sha(p)==info['sha256'],'Artifact SHA changed')
        artifacts[rel(p)]=dict(sha256=info['sha256'],kind=kind,role_id=r['id']);fix(p.with_suffix('.json'))
    def pkg(p,r,origin):
        info=dict(origin[rel(p)]);require(sha(p)==info['sha256'],'Package SHA changed')
        info['role_id']=r['id'];packages[rel(p)]=info
    agroles={r['id']:r for r in ac['roles']}
    views={m['role_id']:m for m in read(TI/'manifests/views-complete.json')['metadata']}
    for r in roles+inners:
        role_permission(r,r['inner'] is not None)
        for fn in ['source-pre.parquet','source-post.parquet','C-post.parquet','query.parquet','labels.parquet']:pkg(PREP/'packages'/r['id']/fn,r,jc['packages'])
        for arm in ['CT1','CT2']:art(PREP/'slots'/r['id']/(arm+'.pt'),'shared',r)
        if r['inner'] is not None:
            for kind,j in [('P',1),('G',2)]:
                mp=JA/'maps'/r['id']/f'JA{j}-eta{r["eta"]:g}.pt';info=read(mp.with_suffix('.json'))
                require(info['eta']==r['eta'] and info['mapping']['accepted'],'Source map family/eta')
                art(mp,kind,r);art(JA/'slots'/r['id']/f'JA{j}-eta{r["eta"]:g}.pt',kind,r)
            outer=next(o for o in roles if (o['outer'],o['target'],o['group'])==(r['outer'],r['target'],r['group']))
            require(set(r['sources']+[r['calibration']])==set(outer['sources']) and set(r['train_contents'])|set(r['validation_contents'])==set(outer['train_contents']),'Source episode exclusion')
        else:
            v=views[r['id']];r['reuse_views']=rel(TI/'slots'/r['id']/'views.pt');r['reuse_maps']=v['mappings']
            r['C_diagnostic_contents']=agroles[r['id']]['C_diagnostic_contents']
            require(v['eta']==r['eta'] and v['t']==r['t'],'Outer fixed settings')
            art(ROOT/r['reuse_views'],'shared',r)
            for kind in ['P','G']:art(ROOT/r['reuse_maps'][kind],kind,r)
            for i in range(4):
                root=AG/'packages'/r['id']/f'i{i}'
                for fn in ['P-fit.parquet','P-query.parquet','P-score.parquet','G-pre-fit.parquet','G-post-fit.parquet','G-pre-validation.parquet','G-post-validation.parquet']:pkg(root/fn,r,ix)
                art(root/'scaler.pt','shared',r)
                for kind in ['P','G']:
                    for fn in [f'{kind}-map.pt',f'{kind}-predictions.pt']:art(AG/'diagnostics'/r['id']/f'i{i}'/fn,kind,r)
            pkg(AG/'packages'/r['id']/'full/G-post.parquet',r,ix)
        membership.append(dict(role_id=r['id'],inner=r['inner'],target=r['target'],calibration=r['calibration'],sources=r['sources'],train_contents=r['train_contents'],validation_contents=r['validation_contents'],C_contents=r['C_contents'],U_contents=r['U_contents'],passed=True))
    raw=pd.read_parquet(SA/'manifests/new-endpoints.parquet')
    refidx={(a['role_id'],a['arm']):a for a in sc['references']}
    for row in raw.to_dict('records'):refidx[(row['role_id'],row['arm'])]=row
    for r in roles:
        for a in REFERENCES:
            if a=='M-S':p=CJ/'models/outer'/r['id']/'M-S.pt'
            else:p=ROOT/refidx[(r['id'],a)]['model_path']
            info=read(p.with_suffix('.json'));opt=info['optimizer']
            require(opt['accepted'] and opt['solver']==SOLVER and opt['settings']['max_iter']==2000 and opt['settings']['max_eval']==10000,'Old model policy incompatible')
            require(all(acceptance_gates(opt['objective'],opt['initial_objective'],opt['max_gradient'],opt['iterations'],opt['objective_replay_error'],opt['gradient_replay_error']).values()),'Old model numerical gates')
            require(info.get('role_id')==r['id'],'Old model role')
            art(p,'shared',r);refs.append(dict(role_id=r['id'],arm=a,model_path=rel(p),model_sha256=sha(p),t=info.get('t',r['t']),new_fit=False))
    for p in [ROOT/'eval/calibrated_deployment_transfer/common.py',ROOT/'eval/calibrated_deployment_transfer_v4/numeric_policy.py',ROOT/'eval/calibrated_deployment_transfer_v4/optimizer_preconditioning.py',
              *list((ROOT/'eval/dynamic_soft_drift_implicit_pilot').glob('*.py')),
              *list((ROOT/'eval/dynamic_soft_drift_calibration').glob('*.py')),
              *list((ROOT/'eval/anchor_guard_drift').glob('*.py'))]:fix(p)
    env=dict(ds['environment']);require(env['torch']==torch.__version__ and env['gpu']==torch.cuda.get_device_name(0),'Environment changed')
    c=dict(version='BF-solution-business-v2-safe-payload',registered_unix=time.time(),plan_sha256=sha(PLAN),roles=roles,inner_roles=inners,references=refs,
           packages=packages,artifacts=artifacts,fixed_files=fixed,code={rel(p):sha(p) for p in Path(__file__).parent.glob('*.py')},environment=env,
           updates=20,terminal_audit=True,lr=.05,betas=[.9,.999],adam_eps=1e-8,q_range=[0.,2.],rho=.01,nu=1.,variance_floor=1e-6,
           primary=PRIMARY,bootstrap=10000,bootstrap_seed=20261012,confidence=1-.05/7,formal_authorized=True,
           caps=dict(logical_forward=45360,new_source_LR=45360,new_final_LR=180,implicit=90720,validation=45360,refinement=1360800),
           numerical=dict(fine_gradient=1e-9,Newton_max=30,Armijo_trials=25,validation_steps=1,validation_step=1.,H_error=1e-10,linear_residual=1e-10,hyper_atol=1e-6,hyper_rtol=1e-3),
           H_U_fit_forbidden=True,test_pre_forbidden=True,PCAP_forbidden=True,CPU_fallback=False,old_runs_read_only=True)
    science_fields=['plan_sha256','roles','inner_roles','references','packages','artifacts','environment',
                    'updates','terminal_audit','lr','betas','adam_eps','q_range','rho','nu','variance_floor',
                    'primary','bootstrap','bootstrap_seed','confidence','formal_authorized','caps','numerical',
                    'H_U_fit_forbidden','test_pre_forbidden','PCAP_forbidden','CPU_fallback','old_runs_read_only']
    require(all(c[k]==old_contract[k] for k in science_fields),'Scientific contract changed')
    for p in failed_root.rglob('*'):
        if p.is_file():fixed[rel(p)]=sha(p)
    for p in (ROOT/'eval/dynamic_soft_drift_formal').glob('*.py'):fixed[rel(p)]=sha(p)
    old_report=ROOT/'docs/dynamic-soft-drift-calibration/formal-20261012/execution-report-20261012.md'
    if old_report.exists():fixed[rel(old_report)]=sha(old_report)
    c['repair']=dict(parent_failure=rel(failed_root/'completion.json'),old_stop_preserved=True,
                     scope='serialization-only',payload_schema='builtin-and-tensor-v2',
                     weights_only=True,unsafe_globals_allowlisted=False,readback_before_accept=True,
                     old_q_or_models_imported=False,old_forward_cache_imported=False,
                     science_equal_fields=science_fields)
    write(OUT/'manifests/repair-contract.json',c['repair'])
    write(OUT/'manifests/experiment-contract.json',c);write(OUT/'manifests/seal.json',dict(contract_sha256=sha(OUT/'manifests/experiment-contract.json')))
    write(OUT/'manifests/numeric-policy.json',POLICY);write(OUT/'environment.json',env)
    write(OUT/'ledger.json',dict(logical_forward=0,new_source_LR=0,new_final_LR=0,implicit=0,validation=0,refinement=0,cache_hits=0,q_updates=0))
    save(pd.DataFrame(membership),OUT/'audits/membership.parquet');save(pd.DataFrame(refs),OUT/'manifests/baseline-index.parquet')
    write(OUT/'registration.json',dict(passed=True,roles=60,source_episodes=720,old_models=420,OOF_predictions=480,source_maps=1440,numeric_H_reads=0,numeric_U_reads=0,resource=disk_gate()))
    progress('formal_registered',roles=60,source_episodes=720,old_models=420)

if __name__=='__main__':run()

