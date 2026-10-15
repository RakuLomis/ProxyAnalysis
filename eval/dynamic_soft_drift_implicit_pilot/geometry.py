"""Additive count correction and actual source-only Hessian geometry."""
from common import *
import gauge as G

def run():
    with stage('geometry'):
        quality=pd.read_parquet(sealed(V2/'q-one-quality.parquet','old-quality-booleans'))
        old=pd.read_parquet(sealed(V2/'failure-path.parquet','old-ambiguous-counts'))
        rows=[]
        for k,d in quality.groupby('K'):
            require(len(d)==24 and int(d['passed'].sum())==0,'Old stop changed')
            for gate in [x for x in d if x.endswith('_pass')]:
                n=int((~d[gate]).sum()); passed=int(d[gate].sum())
                require(n+passed==24 and n==int(old.loc[old.K==k,gate].iloc[0]),'Failure-count semantic replay')
                rows.append(dict(K=int(k),gate=gate.removesuffix('_pass'),original_column=gate,
                                 tested_count=24,passed_count=passed,failed_count=n,old_value_is_failure_count=True))
        save(pd.DataFrame(rows),OUT/'audits/failure-counts-corrected.parquet')
        saved=pd.read_parquet(sealed(V2/'audits/coordinates.parquet','saved-spectral-bounds'))
        a,u,o,rr=production()
        n=module('implicit_sealed_v2_coordinate_math',ROOT/'eval/dynamic_soft_drift_inner_v2/inner.py')
        quality_theta={}
        for arm in ['D-P','D-G']:
            p=sealed(V2/'quality-models'/f'{arm}-K256.pt','old-finite-endpoints')
            quality_theta[arm]=torch.load(p,map_location=device(),weights_only=True)['theta']
        e=G.basis(); identity=torch.eye(97,device=device(),dtype=torch.float64)
        geometry=[]; bounds=[]; equivalent=[]; auditrows=[]
        for i,r in enumerate(contract()['roles']):
            for arm in ['D-P','D-G']:
                data=task(r,arm); v=data['view']; co=coordinate(r,arm); m=reference(r,arm)
                s=u.pack(v,arm,tensor(np.ones(10)))
                require(s['x'].shape==(480,96) and abs(float(s['mass'].sum())-1)<1e-12,'Frozen training slot')
                require(float((weighted(s['y'],s['mass'],6)-1/6).abs().max())<1e-12,'Frozen class mass')
                require(torch.equal(v['mu'],m['mu']) and torch.equal(v['scale'],m['scale']),'Reference preprocessing')
                train={k:v[k] for k in n.TRAIN_KEYS}
                re,ba=n.initialize(train,r['t'],u)
                require(float((co['inv']-re['inv']).abs().max())<1e-10,'Frozen inverse mismatch')
                before=saved.loc[(saved.role_id==r['id'])&(saved.arm==arm)].iloc[0]
                for key in ['step','c0','curvature_upper','regularizer_bound']:
                    require(abs(float(before[key])-ba[key])<=1e-10*max(1,abs(ba[key])),'Bound replay '+key)
                bounds.append(dict(role_id=r['id'],arm=arm,**ba,old_step=float(v['conditioning']['step']),
                    q_one_design_upper=ba['local_witnesses'][0],q_alt_design_upper=ba['local_witnesses'][1],
                    global_over_q_one_design=ba['curvature_upper']/ba['local_witnesses'][0],
                    global_over_q_alt_design=ba['curvature_upper']/ba['local_witnesses'][1],not_exact_Hessian=True))
                inv=co['inv']; aa=G.augmented(s)
                oldref=torch.cat([m['weight'],m['bias'][:,None]],1)
                for point,theta in [('zero',torch.zeros_like(oldref)),('K256',quality_theta[arm][i]),('old_LR',oldref)]:
                    reduced=G.decode(G.encode(theta,e,identity),e,identity)
                    raw=G.hessian(reduced,s,r['t'],e,identity)
                    white=G.hessian(reduced,s,r['t'],e,inv)
                    item=dict(role_id=r['id'],arm=arm,point=point,dimension=485,common_W_analytically_eliminated=True,
                              original_gradient=float(u.original_gradient(theta,s,r['t']).abs().max()))
                    for name,h in [('raw_contrast',raw),('whitened_contrast',white)]:
                        eig=torch.linalg.eigvalsh(h); emin=float(eig.min()); emax=float(eig.max())
                        item.update({name+'_min':emin,name+'_max':emax,name+'_condition':emax/emin if emin>0 else None,
                                     name+'_symmetry':float((h-h.T).norm()/h.norm().clamp_min(1)),name+'_positive':emin>0})
                    geometry.append(item)
                    save(pd.DataFrame(geometry),OUT/'audits/hessian-geometry.parquet')
                # Explicit coordinate chain and exact common-component accounting.
                modelv=G.encode(oldref,e,inv); dec=G.decode(modelv,e,inv)
                common=.0005*(1+r['t'])*6*oldref[:,:96].mean(0).square().sum()
                probability_error=float((torch.softmax(aa@oldref.T,1)-torch.softmax(aa@dec.T,1)).abs().max())
                difference=float(u.original_objective(oldref,s,r['t'])-u.original_objective(dec,s,r['t']))
                eq=G.audit(dec,s,r['t'],e,inv)
                require(probability_error<1e-10 and abs(difference-float(common))<1e-10,'Exact gauge reduction')
                equivalent.append(dict(role_id=r['id'],arm=arm,probability_error=probability_error,
                                  common_W_L2=float(common),target_difference=difference,**eq,passed=True))
                oc=o.coefficients(data,arm)
                error=max(float((oc[k]-data['coeff'][k]).abs().max()) for k in ['A','B','C','s'])
                require(error<1e-10,'Frozen independent penalty coefficients changed')
                auditrows.append(dict(role_id=r['id'],arm=arm,coefficient_error=error,passed=True))
                progress('source_geometry',positions=len(geometry),total=72,role=r['id'],arm=arm)
        save(pd.DataFrame(bounds),OUT/'audits/geometry-bounds.parquet')
        save(pd.DataFrame(equivalent),OUT/'audits/gauge-equivalence.parquet')
        save(pd.DataFrame(auditrows),OUT/'audits/oracle-coefficients.parquet')
        save(pd.DataFrame(o.tests()),OUT/'audits/oracle-branch-tests.parquet')
        # IO negatives fail before loading any forbidden numeric object.
        for f in [lambda:asset(SOURCE/'pilot/tasks'/contract()['roles'][0]['id']/'D-P.pt','D-G','negative'),
                  lambda:writable(REF/'forbidden.json'),lambda:cuda(torch.ones(1))]:
            try:f()
            except RuntimeError:pass
            else:raise RuntimeError('Permission negative accepted')
        write(OUT/'geometry-complete.json',dict(passed=True,positions=len(geometry),source_problems=24,
             old_full_gate_count=0,negative_checks=3,new_LR_fits=0))
