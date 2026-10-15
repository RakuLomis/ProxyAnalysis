from common import *

def run():
    require(not OUT.exists(),'Refuse overwrite of readout run');configure()
    old=read(SOURCE/'manifests/experiment-contract.json')
    require(sha(SOURCE/'manifests/experiment-contract.json')==read(SOURCE/'manifests/seal.json')['sha256'],'Parent contract')
    verifyseal(SOURCE/'manifests/engineering-code.json');verifyseal(SOURCE/'selections/complete.json')
    close=SOURCE.parent/'run-03';done=read(close/'completion.json')
    require(done['passed'] and done['fallback_verified'] and done['verification_sha256']==sha(close/'verification.json'),'P3 closeout')
    order=['shadowsocks','vless','trojan','vmess'];wanted={f'main/f0/{p}/G{g}/i1/{order[(i+1)%4]}' for i,p in enumerate(order) for g in range(3)}
    roles=[dict(r) for r in old['inner_roles'] if r['id'] in wanted];require(len(roles)==12,'Structural source roles')
    sources={}
    def bind(p,kind,rid=None,expected=None,**kw):
        h=sha(p);require(expected is None or expected==h,'Existing registered binding changed')
        sources[rel(p)]=dict(kind=kind,role_id=rid,sha256=h,**kw)
    for p in [SOURCE/'completion.json',SOURCE/'ledger.json',SOURCE/'selections/decisions.json',
              SOURCE/'selections/candidate-metrics.json',SOURCE/'manifests/experiment-contract.json',
              close/'completion.json',close/'verification.json',close/'independent-audit.json']:
        bind(p,'historical')
    for r in roles:
        rid=r['id'];r['classification']=rel(PARENT/'packages'/rid/'classification.pt');r['base']=rel(PARENT/'base-models'/rid/'P-small.pt')
        for name,kind in [('classification','classification'),('base','base')]:
            p=ROOT/r[name];side=read(p.with_suffix('.json'));require(side['role_id']==rid,'Training/base identity')
            bind(p,kind,rid,side['sha256']);bind(p.with_suffix('.json'),'metadata',rid)
        r['g_assets']={}
        for seed in SEEDS:
            for arm,oldarm,filename in [('R','A1-lambda0','initial.pt'),('G','A2-lambda1','terminal.pt'),('P','A3-lambda1','terminal.pt')]:
                p=SOURCE/'inner-models'/rid/f'{oldarm}-seed{seed}'/filename
                h=read(p.with_suffix('.json'))['sha256'];bind(p,{'R':'g-random','G':'g-group','P':'g-paired'}[arm],rid,h)
                bind(p.with_suffix('.json'),'metadata',rid);r['g_assets'][f'{arm}-{seed}']=rel(p)
        prefix=f'outputs/calibrated-deployment-business-transfer-20261006/run-01/packages/{rid}'
        for filename,field,kind,oldkind in [('query.parquet','query','query-post','main-query'),('labels.parquet','labels','query-label','main-inner-labels')]:
            key=prefix+'/'+filename;info=old['packages'][key]
            require(info['role_id']==rid and info['kind']==oldkind and info['rows']==24,'Legal source package registration')
            # No package bytes or labels opened at registration; defer SHA verification to sealed prediction/scoring.
            sources[key]=dict(kind=kind,role_id=rid,sha256=info['sha256'],rows=info['rows'],columns=info['columns']);r[field]=key
    ledger0=dict(attempted_fits=0,accepted_fits=0,fit_seconds=0.,teacher_fits=0,G_fits=0,base_fits=0)
    c=dict(version='frozen-readout-v2',authorization='User authorized execution of v2 plan on 2026-10-14',
        plan_sha256=sha(PLAN),sources=sources,roles=roles,seeds=SEEDS,arms=ARMS,etas=ETAS,
        actual_fits=240,endpoints=288,query_rows=6912,fit_cap_seconds=3600,preflight_cap_seconds=2880,
        max_iter=2000,max_eval=10000,solver='CUDA float64 LBFGS strong_wolfe, zero initialization',
        tolerance_grad=1e-9,tolerance_change=1e-12,gradient_gate=1e-5,objective_replay_gate=1e-10,
        H_forbidden=True,actual_U_forbidden=True,teacher_and_G_updates_forbidden=True,
        primary_reference_eta=.01,advance_CE_margin=.002,advance_C_margin=-.01,advance_deployment_C_margin=-.02,
        statistic='Descriptive structural source subset; no H tests or confidence intervals',
        G_ablation='D_G zeroed without D_x/e refit; diagnostic only',classification_precision='Original double baseline; float32 direct/head G features lifted to double; no restandardization')
    write(OUT/'manifests/experiment-contract.json',c);write(OUT/'manifests/contract-seal.json',dict(sha256=sha(OUT/'manifests/experiment-contract.json')))
    write(OUT/'manifests/source-bindings.json',sources);write(OUT/'manifests/role-index.json',[r['id'] for r in roles])
    write(OUT/'manifests/permission-contract.json',dict(actual_H=False,actual_U=False,PCAP=False,
        read_source_labels_after_all_predictions=True,new_G_teacher_base_fit=False,source_query_before_models=False))
    seal(OUT/'manifests/code.json',list(CODE.glob('*.py')),passed=True)
    mutable(OUT/'ledger.json',ledger0)
    write(OUT/'stages/P0_register.json',dict(passed=True,roles=12,sources=len(sources),new_fits=0,labels_read=0,H_reads=0))
    progress('P0_registered',roles=12,unique_fits=240,endpoints=288)
