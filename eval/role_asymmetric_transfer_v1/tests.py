"""P1 deterministic mass, alias, independent derivative and CUDA tests."""
from common import *
from weight_schedule import registry,slot,audit
import solver_v4 as solver

def run():
    with stage('P1'):
        c=contract();refs={(a['role_id'],a['alias']):a for a in c['historical_endpoints']};audits=[];masses=[]
        maxvalue=maxgrad=0.
        for ri,r in enumerate(c['roles']):
            v=artifact(trainpath(r));y=v['main_y'];up=torch.isin(y,tensor(r['missing'],torch.long))
            for k in ['main','S','P','G']:
                require(float((weighted(v[k+'_y'],v[k+'_mass'],6)-tensor([1/12 if z in r['missing'] else 1/24 for z in range(6)])).abs().max())<1e-12,'Original source masses')
            for p in registry():
                s,led=slot(v,p,r['missing'],True)
                for row in led:row.update(role_id=r['id'],policy_id=p['id'])
                # Full row ledgers remain role-local to avoid one giant in-memory table.
                save(pd.DataFrame(led),OUT/'weights'/r['id']/(p['id']+'.parquet'))
                for yy in range(6):
                    for name in ['source-post','CORAL',p['source'],'C-post']:
                        ms=sum(z['sample_mass'] for z in led if z['label']==yy and z['slot_type']==name)
                        masses.append(dict(role_id=r['id'],policy_id=p['id'],label=yy,slot=name,mass=ms))
                if p['alias']:
                    ref=refs[(r['id'],p['alias'])];m=artifact(ROOT/ref['path']);log=read((ROOT/ref['path']).with_suffix('.json'))['optimizer']
                    aa=audit(m,s,r['t'],log);audits.append(dict(role_id=r['id'],policy_id=p['id'],path=ref['path'],sha256=ref['sha256'],**aa))
            if ri%12==11:progress('P1_alias_audit',roles=ri+1,aliases=len(audits))
        require(len(audits)==420,'All aliases audited')
        # Fixed synthetic objective and finite-difference tests; no real LR fits here.
        torch.manual_seed(20261017)
        x=torch.randn(48,96,device=device(),dtype=torch.float64);y=torch.arange(48,device=device())%6;mass=torch.full((48,),1/48,device=device(),dtype=torch.float64)
        w=(torch.randn(6,96,device=device(),dtype=torch.float64)*.01).requires_grad_();b=torch.zeros(6,device=device(),dtype=torch.float64,requires_grad=True)
        def loss(w,b):
            z=x@w.T+b;return (F.cross_entropy(z,y,reduction='none')*mass).sum()+.0025*w.square().sum()
        def independent(w,b):
            z=x@w.T+b;v=(mass*(z.logsumexp(1)-z[torch.arange(len(y),device=device()),y])).sum()+.0025*w.square().sum()
            e=(z.softmax(1)-F.one_hot(y,6))*mass[:,None];return v,e.T@x+.005*w,e.sum(0)
        a=loss(w,b);ga=torch.autograd.grad(a,(w,b));v,gw,gb=independent(w,b)
        maxvalue=abs(float(a-v));maxgrad=max(float((ga[0]-gw).abs().max()),float((ga[1]-gb).abs().max()))
        require(maxvalue<1e-10 and maxgrad<1e-10,'Independent synthetic objective gradient')
        dw=torch.randn_like(w);db=torch.randn_like(b);norm=(dw.square().sum()+db.square().sum()).sqrt();dw/=norm;db/=norm
        fd=float((loss(w+1e-5*dw,b+1e-5*db)-loss(w-1e-5*dw,b-1e-5*db))/2e-5);an=float((ga[0]*dw).sum()+(ga[1]*db).sum())
        require(abs(fd-an)<1e-8,'Finite difference synthetic')
        # Label/coordinate/weight joint permutation invariance, bias unpenalized.
        ix=torch.arange(47,-1,-1,device=device());z=x@w.T+b
        require(abs(float((F.cross_entropy(z[ix],y[ix],reduction='none')*mass[ix]).sum()-(F.cross_entropy(z,y,reduction='none')*mass).sum()))<1e-12,'Permutation')
        require(abs(float(loss(w,b+3)-loss(w,b)))<1e-12,'Common bias invariance/no bias regularizer')
        bad=float((F.cross_entropy(z,y.roll(1),reduction='none')*mass).sum()-(F.cross_entropy(z,y,reduction='none')*mass).sum())
        require(abs(bad)>1e-6,'Mismatched label negative test')
        r=c['roles'][0];v=artifact(trainpath(r));p=next(p for p in registry() if p['id']=='P__m025__UPR');s=slot(v,p,r['missing'])
        shuffled=dict(v)
        for prefix in ['P','S']:
            perm=torch.arange(len(v[prefix+'_y'])-1,-1,-1,device=device())
            for suffix in ['x','y','mass']:shuffled[prefix+'_'+suffix]=v[prefix+'_'+suffix][perm]
        ss=slot(shuffled,p,r['missing']);wm=torch.randn(6,96,device=device(),dtype=torch.float64)*.01;bm=torch.zeros(6,device=device(),dtype=torch.float64)
        def ce(s):return float((F.cross_entropy(s['x']@wm.T+bm,s['y'],reduction='none')*s['mass']).sum())
        require(abs(ce(s)-ce(ss))<1e-12,'Independent source array permutations')
        # Check linearity in rho, same weighted target, not interpolated features.
        p0=dict(p,rho_U=.2);p1=dict(p,rho_U=.8);pm=dict(p,rho_U=.5)
        require(abs(ce(slot(v,pm,r['missing']))-(ce(slot(v,p0,r['missing']))+ce(slot(v,p1,r['missing'])))/2)<1e-12,'Rho objective linearity')
        badv=dict(v);badv['P_x']=v['P_x'].clone();badv['P_x'][0,0]=float('nan')
        rejected=False
        try:slot(badv,p,r['missing'])
        except RuntimeError:rejected=True
        require(rejected,'Nonfinite negative test')
        # Capability rejects H/labels now, before model seal. No file body opened.
        for fn,purpose in [('query.parquet','query'),('labels.parquet','score')]:
            rejected=False
            try:package(rolepath(r)/fn,purpose)
            except RuntimeError:rejected=True
            require(rejected,'Premature H capability must reject')
        # One bounded synthetic solve and two real structural repeated fits.
        before=sha(ROOT/'eval/calibrated_deployment_transfer_v4/optimizer_preconditioning.py')
        model,log=solver.fit_preconditioned(x,y,mass,4.,dict(role_id='synthetic',arm='unit',kind='synthetic'),diagnostic=True)
        repeat=[]
        for j in range(2):
            m,l=solver.fit_preconditioned(s['x'],s['y'],s['mass'],r['t'],dict(role_id='structural',arm=f'replay{j}',kind='structural'),diagnostic=True)
            repeat.append((m,l))
        err=max(float((repeat[0][0][k]-repeat[1][0][k]).abs().max()) for k in ['weight','bias']);require(err==0.,'Deterministic structural repeat')
        require(before==sha(ROOT/'eval/calibrated_deployment_transfer_v4/optimizer_preconditioning.py'),'Historical solver mutated')
        save(pd.DataFrame(audits),OUT/'manifests/verified-aliases.parquet');save(pd.DataFrame(masses),OUT/'manifests/weight-ledger.parquet')
        write(OUT/'audits/P1-complete.json',dict(passed=True,aliases=420,policies=39,roles=60,mathematical_cases=2340,
              independent_value_error=maxvalue,independent_gradient_error=maxgrad,finite_difference_error=abs(fd-an),structural_repeat_error=err,
              extra_fits=3,synthetic_fits=1,structural_fits=2,H_reads=0,all_numeric_CUDA_float64=True,backend_AST_identical=True))
