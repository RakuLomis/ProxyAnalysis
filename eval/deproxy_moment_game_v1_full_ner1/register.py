"""Budget-only authorization amendment and sealed, parameter-identical pilot import."""
from common import *
import ast,platform

def run():
    started=time.perf_counter();require(not (OUT/'manifests/contract.json').exists(),'New full run only')
    old=read(OLD/'manifests/contract.json');require(sha(OLD/'manifests/contract.json')==read(OLD/'manifests/contract.seal.json')['sha256'],'Original scientific contract')
    pointer=read(PILOT/'completion-current.json');require(sha(ROOT/pointer['path'])==pointer['sha256'],'NER1 current state')
    stop=read(ROOT/pointer['path']);require(all(stop[k] for k in ['exit_policy_verified','uniform_lr_replay_verified','concurrent_heads_verified','integrated_pilot_verified']),'NER1 engineering acceptance')
    seal0=read(PILOT/'artifact-seal.json');require(sha(PILOT/'budget.json')==seal0['files'][rel(PILOT/'budget.json')],'Final pilot ledger seal')
    parent=read(PILOT/'budget.json')['used_seconds'];assets={};parents={};p0=read(OLD/'manifests/P0-complete.json')
    for r in old['inner_roles']+old['roles']:
        rid=r['id'];p=OLD/'packages'/rid/'complete.json';require(sha(p)==p0['files'][rel(p)],'Raw parent seal')
        v=read(p);parents[rel(p)]=sha(p)
        for path,h in v['files'].items():
            require(sha(ROOT/path)==h,'Raw sealed input changed '+path)
            if path.endswith('.pt'):
                m=read((ROOT/path).with_suffix('.json'))
                assets[path]=dict(role_id=rid,capability=m['capability'],sha256=h,sidecar_sha256=v['files'][rel((ROOT/path).with_suffix('.json'))])
    source=ROOT/'eval/deproxy_moment_game_v1_numeric_repair';bindings={}
    for name in ['classifier.py','lbfgs_local.py','models.py','simplex.py','moment_features.py','ridge_anchor.py','engine.py']:
        a=(CODE/name).read_text(encoding='utf-8');b=(source/name).read_text(encoding='utf-8')
        require(ast.dump(ast.parse(a))==ast.dump(ast.parse(b)),'NER1 numerical implementation changed '+name)
        bindings[name]=dict(source=rel(source/name),source_sha256=sha(source/name),copy_sha256=sha(CODE/name),AST_identical=True)
    f=read(PILOT/'cost-forecast-revision-02.json');newcost=f['conservative_seconds']+(parent-f['activity_used_before_forecast'])+(time.perf_counter()-started)
    require(newcost<=FORECAST_GATE,'32h conservative forecast gate not satisfied')
    c=dict(old,version='DP-GAN1-M-v1-Full-NER1',numeric_version='NER1',activity_cap=ACTIVITY_CAP,forecast_limit=FORECAST_GATE,
        assets=assets,raw_parent_seals=parents,pilot_budget_sha256=sha(PILOT/'budget.json'),pilot_state_sha256=pointer['sha256'],
        pilot_artifact_seal_sha256=sha(PILOT/'artifact-seal.json'),numerical_bindings=bindings,
        training_enabled=True,authorization='User approved full NER1; cumulative activity 40h, conservative gate 32h; all other model/loss/data/numeric gates unchanged',
        budget_amendment_only=True,old_stop_records_preserved=True,full_experiment_enabled=True,workers=4,models_per_bucket=32,streams=8)
    immutable(OUT/'manifests/contract.json',c);immutable(OUT/'manifests/contract.seal.json',dict(sha256=sha(OUT/'manifests/contract.json')))
    immutable(OUT/'manifests/budget-amendment.json',dict(inherited_seconds=parent,old_activity_cap=86400,activity_cap=ACTIVITY_CAP,
        old_forecast_gate=69120,forecast_gate=FORECAST_GATE,pilot_conservative_hours=f['conservative_hours'],
        amended_conservative_seconds=newcost,passed=newcost<=FORECAST_GATE,only_budget_changed=True,full_experiment_enabled=True))
    immutable(OUT/'budget.json',dict(cap_seconds=ACTIVITY_CAP,inherited_seconds=parent,new_seconds=0.,used_seconds=parent,items=[]))
    immutable(OUT/'environment.json',dict(python=sys.executable,python_version=platform.python_version(),torch=torch.__version__,cuda=torch.version.cuda,
        installed_LBFGS_sha256=sha(inspect.getfile(torch.optim.LBFGS)),numeric_version='NER1'))
    imported=[]
    def copy_tensor(src,dest,rid,cap,quality=False):
        require(sha(src)==seal0['files'][rel(src)] and sha(src.with_suffix('.json'))==seal0['files'][rel(src.with_suffix('.json'))],'Pilot payload/sidecar final seal')
        m=read(src.with_suffix('.json'));require(m['role_id']==rid,'Pilot role source')
        if quality:
            qsrc=src.with_suffix('.quality.json');q=read(qsrc);require(sha(qsrc)==seal0['files'][rel(qsrc)] and q['accepted'] and q['iterations']<2000 and q['evaluations']<10000,'Pilot head strict acceptance')
            shutil.copy2(qsrc,writable(dest.with_suffix('.quality.json')))
            ss=src.with_name(src.stem+'-solver.pt');dd=dest.with_name(dest.stem+'-solver.pt')
            require(sha(ss)==seal0['files'][rel(ss)],'Pilot solver state seal');shutil.copy2(ss,writable(dd))
            immutable(dd.with_suffix('.json'),dict(role_id=rid,capability=cap,numeric_version='NER1',sha256=sha(dd),imported_from_pilot=True,source=rel(ss)))
        shutil.copy2(src,writable(dest))
        immutable(dest.with_suffix('.json'),dict(role_id=rid,capability=cap,numeric_version='NER1',sha256=sha(dest),
            imported_from_pilot=True,source=rel(src),**({'accepted':True} if quality else {})))
        imported.append(dict(source=rel(src),destination=rel(dest),sha256=sha(dest),role_id=rid,capability=cap))
    # Accepted 232 heads and 88 paths only; no legacy run-01 classifier is reused.
    inventory=pd.read_parquet(PILOT/'tests/integrated-P1-inventory.parquet')
    require(len(inventory)==232 and sha(PILOT/'tests/integrated-P1-inventory.parquet')==seal0['files'][rel(PILOT/'tests/integrated-P1-inventory.parquet')],'Pilot inventory seal')
    for row in inventory.to_dict('records'):
        src=ROOT/row['output_path'];rid=row['role_id'];arm=row['arm']
        if row['kind']=='initial':dest=OUT/'initial-classifiers'/rid/arm/src.name;cap=arm
        else:dest=OUT/'models'/rid/arm/src.parent.name/str(SEEDS[0])/'head.pt';cap=capfor(arm)
        copy_tensor(src,dest,rid,cap,True)
        if row['kind']=='refit':
            for n in [0,1,100,500,1000,2000]:
                s=src.parent/f'step-{n:04}.pt';d=dest.parent/('terminal.pt' if n==2000 else f'trajectory/step-{n:04}.pt')
                copy_tensor(s,d,rid,cap)
            trace=src.parent/'trace.json';require(sha(trace)==seal0['files'][rel(trace)],'Pilot trace seal');shutil.copy2(trace,writable(dest.parent/'trace.json'))
    # Original 24 Ridge anchors were independently replayed by NER1; raw tensors
    # remain at their sealed parent location, but anchors become local assets.
    pilotreg=read(PILOT/'registration.json')
    for r in pilotreg['roles']:
        for cap in ['P','G']:
            src=OLD/'anchors'/r['id']/f'{cap}.pt';b=pilotreg['assets'][rel(src)]
            require(sha(src)==b['sha256'] and sha(src.with_suffix('.json'))==b['sidecar_sha256'],'Bound pilot anchor')
            dst=OUT/'anchors'/r['id']/f'{cap}.pt';shutil.copy2(src,writable(dst))
            immutable(dst.with_suffix('.json'),dict(role_id=r['id'],capability=cap,numeric_version='NER1',sha256=sha(dst),imported_from_pilot=True,source=rel(src)))
    save(OUT/'manifests/pilot-reuse.parquet',imported)
    immutable(OUT/'manifests/pilot-import.json',dict(heads=232,dynamic_paths=88,anchors=24,parameter_identical=True,import_is_not_new_fit=True,complete_equation_replay_before_use=True))
    b=read(OUT/'budget.json');seconds=time.perf_counter()-started;b['new_seconds']=seconds;b['used_seconds']=parent+seconds;b['items'].append(dict(stage='registration-and-pilot-import',seconds=seconds));write(OUT/'budget.json',b)
    progress('full_NER1_registered',roles=780,inherited_hours=parent/3600,imported_heads=232,activity_cap_hours=40,forecast_gate_hours=32)

if __name__=='__main__':run()
