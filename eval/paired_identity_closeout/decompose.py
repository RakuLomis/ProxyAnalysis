from core import *

def one(r,eta):
    m1=C.get(C.mappath(r,'JA1',eta));m2=C.get(C.mappath(r,'JA2',eta))
    checks={}
    for name in ['mu','scale','sxx','pre_mean','post_mean','alpha','tau']:
        checks[name]=check_equal(m1[name],m2[name],'Common '+name)
    x,y,w,mx,my,sxx,cba,cb,cw,constant=tensors(r,m1['mu'],m1['scale'])
    for name,a,b in [('sxx',sxx,m1['sxx']),('paired_syx',cba,m1['syx']),('group_syx',cb,m2['syx']),
                     ('covariance_identity',cba,cb+cw),('pre_mean',mx,m1['pre_mean']),('post_mean',my,m1['post_mean'])]:
        checks[name]=check_equal(a,b,name)
    require(float(m1['alpha'])==eta*float(m1['tau']),'Regularization scale mismatch')
    q=sxx+float(m1['alpha'])*torch.eye(96,device=C.device(),dtype=torch.float64)
    delta=torch.cholesky_solve(cw.T,torch.linalg.cholesky(q)).T
    checks['matrix_identity']=check_equal(m1['matrix']-m2['matrix'],delta,'Map difference')
    checks['bias_identity']=check_equal(m1['bias']-m2['bias'],-delta@mx,'Bias difference')
    effect=(x-mx)@delta.T
    checks['application_identity']=check_equal(affine.apply(m1,x)-affine.apply(m2,x),effect,'Application difference')
    eig=torch.linalg.eigvalsh(q);singular=torch.linalg.svdvals(delta)
    squares=singular.square();total=float(squares.sum())
    stable=total/float(squares.max()) if float(squares.max())>0 else None
    row={'role_id':r['id'],'inner':r['inner'],'outer':r['outer'],'target':r['target'],'calibration':r['calibration'],
         'group':r['group'],'eta':eta,'alpha':float(m1['alpha']),'tau':float(m1['tau']),
         'C_rows':len(x),'C_groups':len(set(C.package(ROOT/r['C_paired'],'paired-map').content_token)),
         'within_norm':float(cw.norm()),'between_norm':float(cb.norm()),'cross_norm':float(cba.norm()),
         'within_between_inner_product':float((cw*cb).sum()),'delta_matrix_norm':float(delta.norm()),
         'delta_stable_rank':stable,'regularized_condition':float(eig.max()/eig.min()),
         'C_effect_MSE':float((w[:,None]*effect.square()).sum()/96),'group_target_variance_constant':constant,
         'maximum_normalized_residual':max(v['normalized'] for v in checks.values()),
         'maximum_absolute_residual':max(v['absolute'] for v in checks.values())}
    blocks=[]
    for j in range(10):
        for k in range(10):
            a,b=C.block(j),C.block(k);contribution=(x[:,b]-mx[b])@delta[a,b].T
            blocks.append({'role_id':r['id'],'inner':r['inner'],'calibration':r['calibration'],'target':r['target'],
                'group':r['group'],'eta':eta,'output_block':C.FEATURES[j],'input_block':C.FEATURES[k],
                'within_covariance_norm':float(cw[a,b].norm()),'delta_coefficient_norm':float(delta[a,b].norm()),
                'C_effect_energy':float((w[:,None]*contribution.square()).sum()),
                'additive_energy_fraction':False,'causal_effect':False})
    return row,checks,blocks,delta

def run():
    with stage('decompose'):
        require(C.read(CLOSE/'completion.json')['postprocess_complete'],'Closeout prerequisite')
        c=C.contract();allpairs=list(pairs(c));pilot=[];keys=set()
        for r in sorted((a for a in c['roles'] if a['inner'] is not None),key=lambda a:a['id']):
            key=(r['target'],r['group'])
            if key not in keys:keys.add(key);pilot.extend((r,e) for e in C.ETAS)
        require(len(pilot)==48,'Pilot role coverage')
        cache={}
        for r,e in pilot:cache[(r['id'],e)]=one(r,e)
        write(OUT/'pilot-algebra.json',{'passed':True,'roles':12,'pairs':48,'selection':'lexicographic role per target and group; all eta',
            'maximum_normalized_residual':max(v[0]['maximum_normalized_residual'] for v in cache.values())})
        rows=[];tests=[];blocks=[];deltas=[]
        for ix,(r,e) in enumerate(allpairs):
            row,checks,bb,delta=cache.get((r['id'],e),(None,None,None,None))
            if row is None:row,checks,bb,delta=one(r,e)
            rows.append(row);blocks.extend(bb);deltas.append(delta.cpu().numpy())
            for name,v in checks.items():tests.append({'role_id':r['id'],'eta':e,'check':name,**v})
            if (ix+1)%100==0:progress('decomposition',completed=ix+1,total=len(allpairs))
        frame=pd.DataFrame(rows);require(len(frame)==2929 and int(frame.inner.notna().sum())==2880,'Decomposition coverage')
        save(OUT/'moment-decomposition.parquet',frame);save(OUT/'identity-residuals.parquet',pd.DataFrame(tests))
        save(OUT/'block-effects.parquet',pd.DataFrame(blocks))
        np.savez_compressed(OUT/'delta-matrices.npz',role_id=frame.role_id.to_numpy(dtype=str),eta=frame.eta.to_numpy(),delta=np.stack(deltas))
        write(OUT/'algebra-verification.json',{'passed':True,'pairs':2929,'inner_pairs':2880,'outer_pairs':49,
            'absolute_max':float(frame.maximum_absolute_residual.max()),'normalized_max':float(frame.maximum_normalized_residual.max()),
            'threshold':1e-10,'new_mapping_fits':0,'all_arithmetic_CUDA_float64':True,
            'delta_matrices_sha256':C.sha(OUT/'delta-matrices.npz'),'different_eta_outer_roles_excluded_from_identity':11})
if __name__=='__main__':run()
