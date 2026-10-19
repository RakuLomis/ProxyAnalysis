"""Metadata registration only: never decode historical training tensors."""
from common import *

def register():
    require(not (OUT/'registration.json').exists(),'New registration only')
    pointer=read(OLD/'completion-current.json');require(sha(ROOT/pointer['path'])==pointer['sha256'],'Current revision hash')
    oldc=read(OLD/'manifests/contract.json')
    require(sha(OLD/'manifests/contract.json')==read(OLD/'manifests/contract.seal.json')['sha256'],'Original contract')
    prot=['shadowsocks','vless','trojan','vmess'];nxt={p:prot[(i+1)%4] for i,p in enumerate(prot)}
    rs=[r for r in oldc['inner_roles'] if r['outer']==0 and r['inner']==1 and r['calibration']==nxt[r['target']]]
    require(len(rs)==12,'Fixed twelve roles');assets={};heads=[];jobs=[];seals={}
    top=OLD/'manifests/P0-complete.json';topv=read(top)
    numeric=OLD/'manifests/P1-numeric-complete.json';nv=read(numeric)
    seals[rel(top)]=sha(top);seals[rel(numeric)]=sha(numeric)
    def bind(p,rid,expected=None):
        m=read(p.with_suffix('.json'));h=sha(p);mh=sha(p.with_suffix('.json'))
        require(m['role_id']==rid and h==m['sha256'],'Source sidecar/payload')
        if expected is not None:require(h==expected[rel(p)] and mh==expected[rel(p.with_suffix('.json'))],'Parent seal mismatch')
        assets[rel(p)]=dict(role_id=rid,capability=m['capability'],sha256=h,sidecar_sha256=mh,parent_seal_backed=expected is not None)
    for r in rs:
        rid=r['id'];pack=OLD/'packages'/rid/'complete.json'
        require(sha(pack)==topv['files'][rel(pack)],'P0 parent seal')
        pv=read(pack);seals[rel(pack)]=sha(pack)
        for path,h in pv['files'].items():
            if path.endswith('.pt'):bind(ROOT/path,rid,pv['files'])
        for side in ['pre','post']:
            for g in GAMMAS:
                p=OLD/'initial-classifiers'/rid/side/f'g{g:g}.pt'
                # Historical initial tensors have sidecars, not a top-level tensor seal.
                # Bind now; independently replay their original equations before using.
                bind(p,rid);q=p.with_suffix('.quality.json')
                require(sha(q)==nv['files'][rel(q)],'Initial quality parent binding')
                heads.append(dict(role_id=rid,arm=side,gamma=g,path=rel(p),kind='initial'))
        for cap in ['P','G']:bind(OLD/'anchors'/rid/f'{cap}.pt',rid,nv['files'])
        recipes=RECIPES if (r['target'],r['group']) in [('shadowsocks','G0'),('vmess','G2')] else RECIPES[:1]
        items=[(arm,f'g{g:g}',g) for arm in ['R-P','R-G'] for g in GAMMAS]
        items += [(arm,rec['id'],rec['gamma']) for rec in recipes for arm in DYNAMIC]
        for arm,candidate,g in items:
            p=OLD/'models'/rid/arm/candidate/str(SEEDS[0]);s=p/'complete.json'
            require(sha(s)==nv['files'][rel(s)],'Model parent seal');sv=read(s);seals[rel(s)]=sha(s)
            for path,h in sv['files'].items():
                if path.endswith('.pt'):bind(ROOT/path,rid,sv['files'])
            heads.append(dict(role_id=rid,arm=arm,candidate=candidate,gamma=g,path=rel(p/'head.pt'),kind='static' if arm.startswith('R-') else 'refit'))
            if not arm.startswith('R-'):
                jobs.append(dict(role_id=rid,arm=arm,recipe=next(x for x in RECIPES if x['id']==candidate),seed=SEEDS[0]))
    require(len(heads)==232 and len(jobs)==88,'Original exact inventories')
    b=read(OLD/'budget.json')
    value=dict(version='NER1',roles=rs,jobs=jobs,heads=heads,assets=assets,parent_seals=seals,
        parent_budget_sha256=sha(OLD/'budget.json'),parent_stop_sha256=pointer['sha256'],
        plan_sha256=sha(PLAN),original_contract_sha256=sha(OLD/'manifests/contract.json'),
        torch_lbfgs_sha256=sha(inspect.getfile(torch.optim.LBFGS)),query_read=False,H_scored=False,
        full_experiment_enabled=False,repair_cap_seconds=14400,activity_cap_seconds=86400,forecast_gate_seconds=69120,
        model_loss_permissions_thresholds_unchanged=True)
    write(OUT/'registration.json',value,True);write(OUT/'registration.seal.json',dict(sha256=sha(OUT/'registration.json')),True)
    write(OUT/'budget.json',dict(parent_seconds=b['used_seconds'],repair_seconds=0.,used_seconds=b['used_seconds'],items=[]),True)
    write(OUT/'environment.json',dict(python=sys.executable,torch=torch.__version__,cuda=torch.version.cuda,registration_only=True),True)
    progress('R0_registered',roles=12,heads=232,dynamic_jobs=88,full_experiment_enabled=False)

if __name__=='__main__':register()
