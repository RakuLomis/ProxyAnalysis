from common import *
from features import load_train,ensure_g,g_forward,feature,offset
from head import basis,logits,objective,independent,projected
from solve import fit

def pilot():
    with stage('P1_interface_pilot'):
        r=contract()['roles'][0];s,m=load_train(r);q=basis();checks={}
        checks['orthonormal_basis']=bool(torch.allclose(q.T@q,torch.eye(5,device=device(),dtype=torch.float64),atol=1e-12,rtol=0))
        checks['zero_common_class']=float(q.sum(0).abs().max())<1e-12
        checks['projection']=float((q@q.T-(torch.eye(6,device=device(),dtype=torch.float64)-torch.ones((6,6),device=device(),dtype=torch.float64)/6)).abs().max())<1e-12
        g=ensure_g(r,'P',SEEDS[0]);phi=feature(s['x'],g);z0=offset(s['x'],m)
        a=torch.zeros((5,104),device=device(),dtype=torch.float64);b=torch.zeros(5,device=device(),dtype=torch.float64)
        zz=logits(a,b,phi,z0,q)
        checks['zero_logits_exact']=torch.equal(zz,z0);checks['zero_prob_exact']=torch.equal(zz.softmax(1),z0.softmax(1))
        checks['zero_class_exact']=torch.equal(zz.argmax(1),z0.argmax(1));checks['G_frozen']=all(not v.requires_grad for v in g.values())
        gen=torch.Generator(device=device()).manual_seed(20261014)
        a=(torch.randn((5,104),generator=gen,device=device(),dtype=torch.float64)*.001).requires_grad_()
        b=(torch.randn((5,),generator=gen,device=device(),dtype=torch.float64)*.001).requires_grad_()
        ja=objective(a,b,phi,z0,s['y'],s['mass'],.01,q);ga,gb=torch.autograd.grad(ja,(a,b))
        check=independent(a,b,phi,z0,s['y'],s['mass'],.01,q)
        objective_error=abs(float(ja.detach())-float(check['objective'].detach()))
        grad_error=max(float((ga-check['ga']).abs().max()),float((gb-check['gb']).abs().max()))
        checks['objective_manual_replay']=objective_error<=1e-10;checks['gradient_manual_replay']=grad_error<=1e-10
        zeros=torch.zeros_like(a);biased=independent(zeros,b,phi,z0,s['y'],s['mass'],1.,q)
        checks['bias_unpenalized']=float(biased['L2'])==0
        da=torch.randn(a.shape,generator=gen,device=device(),dtype=torch.float64);db=torch.randn(b.shape,generator=gen,device=device(),dtype=torch.float64)
        size=torch.sqrt(da.square().sum()+db.square().sum());da=da/size;db=db/size
        analytic=float((ga*da).sum()+(gb*db).sum());fd=[]
        for h in [1e-4,1e-5]:
            jplus=objective(a.detach()+h*da,b.detach()+h*db,phi,z0,s['y'],s['mass'],.01,q)
            jminus=objective(a.detach()-h*da,b.detach()-h*db,phi,z0,s['y'],s['mass'],.01,q)
            value=float((jplus-jminus)/(2*h));err=abs(value-analytic)
            fd.append(dict(h=h,analytic=analytic,finite_difference=value,error=err));require(err<=1e-7+1e-4*abs(analytic),'Smooth readout finite difference')
        checks['smooth_finite_difference']=True
        conversion=[]
        for arm in ['G','P']:
            for seed in SEEDS:
                old=source_tensor(ROOT/r['g_assets'][f'{arm}-{seed}'],r['id'],purpose='conversion')['state']
                gg={k:old[k] for k in ['w0','b0','w1','b1']};ff=feature(s['x'],gg)
                v=old['w2'].double();cc=old['b2'].double();d=.1*(v-v.mean(0));e=.1*(cc-cc.mean())
                math_r=ff@v.T+cc;math_delta=.1*(math_r-math_r.mean(1,keepdim=True));new_delta=ff@d.T+e
                native=F.linear(ff.float(),old['w2'],old['b2']);native_delta=(.1*(native-native.mean(1,keepdim=True))).double()
                aa=q.T@d;bb=q.T@e;normerr=abs(float(aa.square().sum())-float(d.square().sum()))
                common=v-v.mean(0);unused=v-common
                regerr=abs(float(.01*v.square().sum())-float(d.square().sum()+.01*unused.square().sum()))
                matherr=float((math_delta-new_delta).abs().max())
                require(matherr<=1e-10 and regerr<=1e-10 and normerr<=1e-10,'Output coordinates or L2 geometry')
                conversion.append(dict(arm=arm,seed=seed,math_logit_error=matherr,orthonormal_norm_error=normerr,
                    L2_geometry_error=regerr,native_float32_rounding_logit_error=float((native_delta-new_delta).abs().max())))
        checks['old_output_coordinate_conversion']=True
        negative=[]
        probes=[lambda:package(r,'predict'),lambda:package(r,'score'),
            lambda:check_source(PARENT/'packages'/r['id']/'teacher/fit.pt','train',r['id']),
            lambda:check_source(ROOT/r['g_assets'][f'P-{SEEDS[0]}'],'train',r['id'],'G'),
            lambda:check_source(ROOT/r['g_assets'][f'R-{SEEDS[0]}'],'train',r['id'],'X'),
            lambda:check_source(ROOT/'outputs/calibrated-deployment-business-transfer-20261006/run-01/packages/main/f0/shadowsocks/G0/outer/query.parquet','predict')]
        for f in probes:
            try:f()
            except RuntimeError:negative.append(True)
            else:negative.append(False)
        checks['permission_negative_cases']=all(negative)
        require(all(checks.values()),'Interface gate')
        write(OUT/'audits/unit-tests.json',dict(passed=True,checks=checks,objective_error=objective_error,
            gradient_error=grad_error,finite_difference=fd,conversions=conversion,new_G_fits=0,H_reads=0))
        logs=[]
        for arm in ARMS:
            for eta in ETAS:logs.append(fit(r,arm,eta,SEEDS[0]))
        upper=max(v['seconds'] for v in logs);used=read(OUT/'ledger.json')['fit_seconds']
        projected_seconds=used+(240-8)*upper
        require(projected_seconds<=2880,'Pilot projected fit budget >48 minutes; confirmation required')
        write(OUT/'audits/pilot.json',dict(passed=True,fits=8,projected_fit_seconds=projected_seconds,
            seconds_per_fit_upper=upper,fit_seconds_used=used,within_preflight=True,no_query_or_label_reads=True))

def train():
    with stage('P2_heads'):
        require(read(OUT/'audits/pilot.json')['passed'],'Pilot gate')
        roles=contract()['roles'];endpoints=[]
        for i,r in enumerate(roles):
            for arm in ARMS:
                for eta in ETAS:
                    for seed in ([SEEDS[0]] if arm=='X' else SEEDS):
                        p=modelpath(r,arm,eta,seed)
                        if not p.exists():fit(r,arm,eta,seed)
                    for seed in SEEDS:
                        endpoints.append(dict(role_id=r['id'],arm=arm,eta=eta,seed=seed,
                            model=rel(modelpath(r,arm,eta,seed)),base=r['base'],
                            G_path=None if arm=='X' else rel(gpath(r,arm,seed)),seed_alias=arm=='X'))
            progress('P2_role_complete',roles=i+1,total=12,accepted=read(OUT/'ledger.json')['accepted_fits'])
        require(len(endpoints)==288 and len({e['model'] for e in endpoints})==240,'Endpoint/unique model counts')
        require(read(OUT/'ledger.json')['accepted_fits']==240,'All new heads accepted')
        alias=0
        for r in roles:
            for eta in ETAS:
                group=[e for e in endpoints if e['role_id']==r['id'] and e['arm']=='X' and e['eta']==eta]
                require(len(group)==3 and len({e['model'] for e in group})==1 and all(e['G_path'] is None for e in group),'X seed alias')
                alias+=3
        # Historical training/base/G files unchanged; never open deferred query/labels here.
        for name,info in contract()['sources'].items():
            if info['kind'] not in ['query-post','query-label']:require(sha(ROOT/name)==info['sha256'],'Source mutated')
        write(OUT/'manifests/endpoints.json',endpoints);write(OUT/'audits/endpoint-alias-audit.json',dict(passed=True,X_logical=alias,X_unique=24))
        files=list((OUT/'models').rglob('*.pt'))+list((OUT/'models').rglob('*.json'))+list((OUT/'frozen-G').rglob('*.pt'))+list((OUT/'frozen-G').rglob('*.json'))
        files+=list((OUT/'fit-logs').rglob('*.json'))+[OUT/'manifests/endpoints.json',OUT/'manifests/experiment-contract.json',OUT/'manifests/code.json']
        files+=[ROOT/r['base'] for r in roles]
        seal(OUT/'manifests/models-complete.json',files,passed=True,unique_heads=240,endpoints=288,new_G_fits=0)

def predict():
    with stage('P3_predict'):
        verifyseal(OUT/'manifests/models-complete.json');eps=read(OUT/'manifests/endpoints.json');rows=[];base_rows=[];diag=[]
        for i,r in enumerate(contract()['roles']):
            q=package(r,'predict');m=source_tensor(ROOT/r['base'],r['id']);raw=torch.as_tensor(q[HIST].to_numpy(),device=device(),dtype=torch.float64)
            x=(raw-m['mu'])/m['scale'];z0=offset(x,m);lp0=F.log_softmax(z0,1);p0=lp0.exp()
            bd=pd.DataFrame(p0.cpu().numpy(),columns=[f'p{k}' for k in range(6)])
            for k in range(6):bd[f'l{k}']=lp0[:,k].cpu().numpy()
            bd['visit_id']=q.visit_id.to_numpy();bd['role_id']=r['id'];base_rows.append(bd)
            for e in [v for v in eps if v['role_id']==r['id']]:
                h=own(ROOT/e['model']);g=None if e['G_path'] is None else own(ROOT/e['G_path'])
                phi=feature(x,g);d=h['D'];b=h['e'];dx=phi[:,:96]@d[:,:96].T;dg=torch.zeros_like(dx) if g is None else phi[:,96:]@d[:,96:].T
                zz=z0+phi@d.T+b;lp=F.log_softmax(zz,1);pp=lp.exp();offlp=F.log_softmax(z0+dx+b,1)
                rec=pd.DataFrame(pp.cpu().numpy(),columns=[f'p{k}' for k in range(6)])
                for k in range(6):
                    for prefix,t in [('l',lp),('off_l',offlp),('dx',dx),('dg',dg),('bias',b[None,:].expand(len(x),-1))]:rec[f'{prefix}{k}']=t[:,k].cpu().numpy()
                rec['visit_id']=q.visit_id.to_numpy()
                for key in ['role_id','arm','eta','seed']:rec[key]=e[key]
                rec['actual_target']=r['target'];rec['calibration']=r['calibration'];rec['group']=r['group'];rows.append(rec)
                gap=z0.topk(2,1).values;gap=gap[:,0]-gap[:,1];delta=zz-z0
                diag.append(dict(role_id=r['id'],arm=e['arm'],eta=e['eta'],seed=e['seed'],
                    delta_RMS=float(delta.square().mean().sqrt()),x_RMS=float(dx.square().mean().sqrt()),G_RMS=float(dg.square().mean().sqrt()),
                    guaranteed_unchanged=int((gap>2*delta.abs().max(1).values).sum()),cases=len(q),
                    G_zero_class_changes=int((zz.argmax(1)!=(z0+dx+b).argmax(1)).sum()),
                    model=e['model'],seed_alias=e['seed_alias']))
            progress('P3_source_role_predicted',roles=i+1,total=12)
        d=pd.concat(rows,ignore_index=True);base=pd.concat(base_rows,ignore_index=True)
        require(len(d)==6912 and len(base)==288,'Prediction sizes')
        save(OUT/'predictions/visits.parquet',d);save(OUT/'predictions/base.parquet',base)
        write(OUT/'diagnostics/output-use.json',diag)
        seal(OUT/'predictions/complete.json',[OUT/'predictions/visits.parquet',OUT/'predictions/base.parquet',OUT/'diagnostics/output-use.json'],
             passed=True,rows=6912,baseline_rows=288,source_only=True,labels_read=0,H_reads=0)

def metrics(y,p,lp,missing):
    pred=p.argmax(1);cm=np.bincount(y*6+pred,minlength=36).reshape(6,6);den=cm.sum(0)+cm.sum(1)
    f1=np.divide(2*np.diag(cm),den,out=np.zeros(6),where=den>0);use=np.isin(y,missing)
    ce=-lp[np.arange(len(y)),y];brier=((p-np.eye(6)[y])**2).sum(1)
    return dict(F1_U=float(f1[missing].mean()),F1_C=float(np.delete(f1,missing).mean()),F1_all=float(f1.mean()),
        CE_U=float(ce[use].mean()),CE_C=float(ce[~use].mean()),CE_all=float(ce.mean()),
        Brier=float(brier.mean()),Brier_U=float(brier[use].mean()),Brier_C=float(brier[~use].mean()),
        accuracy=float((pred==y).mean()),cm=cm.tolist(),class_F1=f1.tolist())

def score():
    with stage('P3_source_score'):
        verifyseal(OUT/'predictions/complete.json');d=pd.read_parquet(OUT/'predictions/visits.parquet');base=pd.read_parquet(OUT/'predictions/base.parquet')
        pcs=[f'p{k}' for k in range(6)];lcs=[f'l{k}' for k in range(6)];offcs=[f'off_l{k}' for k in range(6)];rows=[];bases=[]
        for r in contract()['roles']:
            labels=package(r,'score');lookup=dict(zip(labels.visit_id,labels.label_id.map(dict(zip(LABELS,range(6))))))
            require(all(v in range(6) for v in lookup.values()),'Known business classes')
            bb=base[base.role_id.eq(r['id'])].set_index('visit_id');sub=d[d.role_id.eq(r['id'])]
            ybase=np.array([lookup[v] for v in bb.index],int);mb=metrics(ybase,bb[pcs].to_numpy(),bb[lcs].to_numpy(),r['missing'])
            bases.append(dict(role_id=r['id'],actual_target=r['target'],calibration=r['calibration'],group=r['group'],**mb))
            for (arm,eta,seed),z in sub.groupby(['arm','eta','seed'],sort=False):
                zz=z.set_index('visit_id');yb=np.array([lookup[v] for v in zz.index],int);p=zz[pcs].to_numpy();lp=zz[lcs].to_numpy();basep=bb.loc[zz.index,pcs].to_numpy()
                m=metrics(yb,p,lp,r['missing']);offlp=zz[offcs].to_numpy();offm=metrics(yb,np.exp(offlp),offlp,r['missing'])
                pred=p.argmax(1);bp=basep.argmax(1);use=np.isin(yb,r['missing'])
                row=dict(role_id=r['id'],arm=arm,eta=float(eta),seed=int(seed),actual_target=r['target'],calibration=r['calibration'],group=r['group'],**m,
                    off_G_CE_U=offm['CE_U'],off_G_F1_U=offm['F1_U'])
                for name,mask in [('all',np.ones(len(yb),bool)),('U',use),('C',~use)]:
                    row['repaired_'+name]=int(((pred==yb)&(bp!=yb)&mask).sum());row['added_errors_'+name]=int(((pred!=yb)&(bp==yb)&mask).sum())
                rows.append(row)
        numbers=['F1_U','F1_C','F1_all','CE_U','CE_C','CE_all','Brier','Brier_U','Brier_C','accuracy']
        results=[]
        for arm in ARMS:
            for eta in ETAS:
                z=[r for r in rows if r['arm']==arm and r['eta']==eta]
                results.append(dict(arm=arm,eta=eta,tasks=12,logical_seed_endpoints=len(z),
                    **{k:float(np.mean([r[k] for r in z])) for k in numbers},
                    by_actual_target={p:{k:float(np.mean([r[k] for r in z if r['actual_target']==p])) for k in numbers} for p in ['shadowsocks','vless','trojan','vmess']},
                    repaired_all=sum(r['repaired_all'] for r in z),added_errors_all=sum(r['added_errors_all'] for r in z)))
        comparisons=[];bs={r['role_id']:r for r in bases}
        for eta in ETAS:
            paired=[r for r in rows if r['arm']=='P' and r['eta']==eta]
            for control in ['P-small','X','R','G']:
                lookup={(r['role_id'],r['seed']):r for r in rows if r['arm']==control and r['eta']==eta}
                deltas=[]
                for p in paired:
                    other=bs[p['role_id']] if control=='P-small' else lookup[(p['role_id'],p['seed'])]
                    deltas.append(dict(role_id=p['role_id'],calibration=p['calibration'],**{k:p[k]-other[k] for k in numbers}))
                comparisons.append(dict(eta=eta,control=control,**{f'delta_{k}':float(np.mean([r[k] for r in deltas])) for k in numbers},
                    worst_deployment_delta_F1_C=min(float(np.mean([r['F1_C'] for r in deltas if r['calibration']==cal])) for cal in ['shadowsocks','vless','trojan','vmess'])))
        ref=[v for v in comparisons if v['eta']==.01];bp=next(v for v in ref if v['control']=='P-small')
        gates=dict(source_CE_base=bp['delta_CE_U']<=-.002,source_F1_base=bp['delta_F1_U']>=0,
            C_overall=bp['delta_F1_C']>=-.01,C_deployment=bp['worst_deployment_delta_F1_C']>=-.02,
            same_eta_controls_CE=all(v['delta_CE_U']<=-.002 for v in ref if v['control']!='P-small'),
            same_eta_controls_F1=all(v['delta_F1_U']>=0 for v in ref if v['control']!='P-small'))
        summary=dict(cells=results,baseline={k:float(np.mean([r[k] for r in bases])) for k in numbers},
            comparisons=comparisons,advancement_gates=gates,advance_discussion=all(gates.values()),
            actual_roles_enabled=0,H_scored=False,statistical_inference='descriptive only; task/seed predictions are overlapping')
        write(OUT/'scores/role-results.json',rows);write(OUT/'scores/base-results.json',bases);write(OUT/'scores/summary.json',summary)
        seal(OUT/'scores/complete.json',[OUT/'scores/role-results.json',OUT/'scores/base-results.json',OUT/'scores/summary.json'],passed=True,source_only=True)

def verify():
    with stage('P4_verify'):
        verifyseal(OUT/'manifests/models-complete.json');verifyseal(OUT/'predictions/complete.json');verifyseal(OUT/'scores/complete.json')
        eps=read(OUT/'manifests/endpoints.json');d=pd.read_parquet(OUT/'predictions/visits.parquet');maxerr=0.;alias=0
        for r in contract()['roles']:
            query=package(r,'predict');m=source_tensor(ROOT/r['base'],r['id']);raw=torch.as_tensor(query[HIST].to_numpy(),device=device(),dtype=torch.float64)
            x=(raw-m['mu'])/m['scale'];z0=offset(x,m)
            for e in [t for t in eps if t['role_id']==r['id']]:
                h=own(ROOT/e['model']);g=None if e['G_path'] is None else own(ROOT/e['G_path']);phi=feature(x,g)
                lp=F.log_softmax(z0+phi@h['D'].T+h['e'],1)
                sub=d[d.role_id.eq(r['id'])&d.arm.eq(e['arm'])&d.eta.eq(e['eta'])&d.seed.eq(e['seed'])].set_index('visit_id').loc[query.visit_id]
                err=float(np.abs(lp.cpu().numpy()-sub[[f'l{k}' for k in range(6)]].to_numpy()).max());maxerr=max(maxerr,err);require(err==0,'Independent inference replay not exact')
                if e['arm']=='X':
                    other=d[d.role_id.eq(r['id'])&d.arm.eq('X')&d.eta.eq(e['eta'])&d.seed.eq(SEEDS[0])].set_index('visit_id').loc[query.visit_id]
                    require(np.array_equal(sub[[f'l{k}' for k in range(6)]].to_numpy(),other[[f'l{k}' for k in range(6)]].to_numpy()),'X seed predictions not exact aliases');alias+=1
        for name,info in contract()['sources'].items():require(sha(ROOT/name)==info['sha256'],'Historical/source package changed')
        require(read(OUT/'ledger.json')['accepted_fits']==240 and read(OUT/'ledger.json')['G_fits']==0,'Fit accounting')
        write(OUT/'audits/final-verification.json',dict(passed=True,unique_heads=240,endpoints=288,
            source_predictions=6912,independent_logprob_max_error=maxerr,X_seed_aliases=alias,
            historical_sources_unchanged=True,H_reads=0,actual_U_reads=0,new_G_fits=0,new_teacher_fits=0,
            inference_inputs='post numeric 96 only; frozen baseline and fixed G/head',no_H_intervals=True))

def finish():
    for name in ['P0_register','P1_interface_pilot','P2_heads','P3_predict','P3_source_score','P4_verify']:
        require(read(OUT/'stages'/f'{name}.json')['passed'],'All stages complete')
    summary=read(OUT/'scores/summary.json')
    write(OUT/'completion.json',dict(passed=True,status='source_frozen_readout_complete',source_experiment_complete=True,
        unique_head_fits=240,logical_endpoints=288,G_updated=False,formal_H_scored=False,
        advance_discussion=summary['advance_discussion'],actual_role_decisions_changed=False,
        verification_sha256=sha(OUT/'audits/final-verification.json')))
    progress('complete',unique_heads=240,endpoints=288,advance_discussion=summary['advance_discussion'],H_scored=False)
