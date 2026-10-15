"""DS01--DS05: hash/metadata inventory; no target numeric tensors loaded."""
from common import *

def run():
    configure();require(not (OUT/'manifests/seal.json').exists(),'Run already registered')
    tc=read(TI/'manifests/experiment-contract.json');jc=read(JA/'manifests/experiment-contract.json')
    fixed={};artifacts={};packages={};pilot_packages={};audits=[];membership=[]
    def fix(p):fixed[rel(p)]=sha(p)
    for root in [TI,JA]:
        p=root/'manifests/experiment-contract.json'
        require(sha(p)==read(p.with_name('seal.json'))['contract_sha256'],'Parent contract hash')
        fix(p);fix(p.with_name('seal.json'))
    for root in [AG,AC]:
        comp=read(root/'completion.json');require(comp['passed'],'Parent incomplete')
        verification=root/('stage-1-verification.json' if root==AG else 'verification.json')
        require(sha(verification)==comp['verification_sha256'],'Parent verification hash')
        fix(root/'completion.json');fix(verification)
    require(read(AG/'completion.json')['status']=='stop_no_supported_protection_target','Hard branch stop changed')
    require(read(AC/'completion.json')['parent_stop_preserved'],'Closeout changed stop')
    for p in [JA/'failure.json',JA/'closeout-20261009/completion.json',
              JA/'closeout-20261009/verification.json',TI/'manifests/views-complete.json']:
        fix(p)
    close=read(JA/'closeout-20261009/completion.json')
    require(close['passed'] and sha(JA/'failure.json')==close['original_failure_sha256'],'Preserve JA failure')
    roles=tc['roles'];inners=[]
    require(len(roles)==60,'Outer role count')
    for outer in roles:
        role_permission(outer)
        subset=[dict(r,eta=outer['eta'],t=outer['t']) for r in jc['roles'] if r['inner'] is not None and
                (r['outer'],r['target'],r['group'])==(outer['outer'],outer['target'],outer['group'])]
        require(len(subset)==12,'Twelve episodes per role')
        for r in subset:
            role_permission(r,True);require(set(r['sources']+[r['calibration']])==set(outer['sources']), 'Pseudo deployment set')
            require(set(r['train_contents'])|set(r['validation_contents'])==set(outer['train_contents']), 'Pseudo content split')
            require(len(r['train_contents'])==18 and len(r['validation_contents'])==6 and len(r['C_contents'])==12,'Episode content counts')
            membership.append(dict(role_id=r['id'],outer_role=outer['id'],source_protocols=r['sources'],
                                   calibration=r['calibration'],target_excluded=r['target'],
                                   train_contents=r['train_contents'],validation_contents=r['validation_contents'],
                                   C_contents=r['C_contents'],U_contents=r['U_contents'],passed=True))
            for kind in ['P','G']:
                p=oldmap(r,kind);exists=p.exists() and p.with_suffix('.json').exists()
                info=read(p.with_suffix('.json')) if exists else {}
                accepted=exists and info.get('mapping',{}).get('accepted',False)
                if exists:
                    require(info['eta']==r['eta'] and info['role_id']==r['id'],'Map role/eta mismatch')
                    require(sha(p)==info['sha256'],'Cached mapping hash changed');fix(p.with_suffix('.json'))
                    artifacts[rel(p)]=info['sha256']
                audits.append(dict(category='source-map',role_id=r['id'],arm=kind,path=rel(p),
                                   exists=exists,compatible=bool(accepted),status='reuse' if accepted else 'missing'))
            inners.append(r)
    require(len(inners)==720,'Inner role count')
    pilots=[]
    for r in roles:
        if r['outer']==0:
            matches=[v for v in inners if (v['outer'],v['target'],v['group'])==(r['outer'],r['target'],r['group'])]
            pilots.append(min(matches,key=lambda a:(a['calibration'],a['inner'])))
    require(len(pilots)==12 and all(r['inner']==1 for r in pilots),'Pilot identities')
    def art(p):
        info=read(p.with_suffix('.json'));require(sha(p)==info['sha256'],'Artifact hash changed')
        artifacts[rel(p)]=info['sha256'];fix(p.with_suffix('.json'))
    for r in pilots:
        pk=[]
        for p in [*[PREP/'packages'/r['id']/fn for fn in ['source-pre.parquet','source-post.parquet','C-post.parquet','query.parquet','labels.parquet']],
                  *[ROOT/r[k] for k in ['C_paired','C_group_pre','C_group_post']]]:
            info=jc['packages'][rel(p)];require(sha(p)==info['sha256'],'Pilot package changed')
            packages[rel(p)]=info;pk.append(rel(p))
        pilot_packages[r['id']]=pk
        for p in [PREP/'slots'/r['id']/'CT2.pt',PREP/'slots'/r['id']/'CT1.pt',
                  oldmap(r,'P'),oldmap(r,'G'),oldslot(r,'P'),oldslot(r,'G')]:art(p)
    preds=list((AG/'diagnostics').rglob('*-predictions.pt'))
    require(len(preds)==480,'Actual C OOF count')
    for p in preds:
        info=read(p.with_suffix('.json'));ok=sha(p)==info['sha256'];require(ok,'C OOF hash changed')
        fix(p.with_suffix('.json'));artifacts[rel(p)]=info['sha256']
        audits.append(dict(category='C-OOF',role_id=info.get('role_id',rel(p.parent)),
                           arm='P' if p.name.startswith('P') else 'G',path=rel(p),exists=True,compatible=True,status='hash-compatible_pending_formal_numeric_audit'))
    own={rel(p):sha(p) for p in Path(__file__).parent.glob('*.py')}
    inherited={**tc['historical_source_sha256'],**tc['source_sha256']}
    for p,h in inherited.items():require(sha(ROOT/p)==h,'Inherited source changed '+p);fixed[p]=h
    gpu=torch.cuda.get_device_properties(0)
    z=torch.arange(16,device=device(),dtype=torch.float64).reshape(4,4)
    require(torch.isfinite(z@z.T).all(),'CUDA float64 test')
    env=dict(python=sys.executable,torch=torch.__version__,cuda=torch.version.cuda,gpu=gpu.name,
             VRAM_MiB=gpu.total_memory/1048576,device='cuda:0',dtype='float64',CPU_fallback=False,
             installed_LBFGS_path=inspect.getfile(torch.optim.LBFGS),
             installed_LBFGS_sha256=sha(Path(inspect.getfile(torch.optim.LBFGS))))
    write(OUT/'environment.json',env);write(OUT/'manifests/numeric-policy.json',POLICY)
    c=dict(version='DS-v1-numeric-pilot',registered_unix=time.time(),plan_sha256=sha(PLAN),
           roles=roles,inner_roles=inners,pilot_roles=pilots,pilot_packages_by_role=pilot_packages,
           packages=packages,artifacts=artifacts,fixed_files=fixed,source_sha256=own,environment=env,
           K=64,q_updates=20,q_lr=.05,rho=.01,nu=1.,variance_floor=1e-6,
           pilot_classifier_cap=24,formal_classifier_cap=180,formal_meta_authorized=False,
           influence_function=False,target_numeric_reads=0,test_pre_read=False,
           parent_hard_anchor_stop='stop_no_supported_protection_target',physical_post_input_qualified=False)
    write(OUT/'manifests/experiment-contract.json',c)
    write(OUT/'manifests/seal.json',dict(contract_sha256=sha(OUT/'manifests/experiment-contract.json')))
    write(OUT/'manifests/input-sha256.json',dict(artifacts=artifacts,fixed_files=fixed))
    save(pd.DataFrame(membership),OUT/'audits/role-membership.parquet')
    save(pd.DataFrame(audits),OUT/'audits/reuse-audit.parquet')
    write(OUT/'inventory-complete.json',dict(passed=True,outer_roles=60,inner_roles=720,pilot_roles=12,
          C_OOF=480,source_map_references=1440,source_map_missing=sum(v['status']=='missing' for v in audits),
          target_numeric_reads=0,new_mapping_fits=0,new_classifier_fits=0))
    progress('inventory_complete',roles=60,episodes=720,pilots=12,source_maps_missing=sum(v['status']=='missing' for v in audits))

if __name__=='__main__':run()
