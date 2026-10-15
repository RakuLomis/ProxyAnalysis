"""Actual C: outer-coordinate OOF errors, independent P/G namespaces."""
from common import *

def replay_map(model,x,y,eta,constant,meta):
    n=len(x);mx=x.mean(0);my=y.mean(0);xc=x-mx;yc=y-my
    xx=xc.T@xc/n;yx=yc.T@xc/n;tau=max(float(xx.trace())/96,1e-12);alpha=eta*tau
    m=model['matrix'];b=model['bias'];eye=torch.eye(96,device=device(),dtype=torch.float64)
    rec=(x@m.T+b-y).square().mean()+constant/96
    reg=alpha*(m-eye).square().sum()/96
    grad=2*(m@xx-yx+alpha*(m-eye))/96
    bias=2*(m@mx+b-my)/96
    error=abs(float(rec+reg)-meta['mapping']['objective'])
    require(meta['mapping']['accepted'] and meta['mapping']['eta']==eta and meta['mapping']['parameters']==9312,'OOF family mismatch')
    require(abs(meta['mapping']['alpha']-alpha)<1e-9*max(1,alpha) and float(grad.abs().max())<=1e-8 and float(bias.abs().max())<=1e-8 and error<1e-10,'OOF objective replay failed')
    return error

def one(r,kind,mu,scale,s,rawvar):
    arm='D-G' if kind=='G' else 'D-P';a,u,_,rec=production()
    aa=[];bb0=[];bb=[];post_blocks=[];alltokens=[];audits=[]
    for i in range(4):
        root=AG/'packages'/r['id']/f'i{i}';dest=AG/'diagnostics'/r['id']/f'i{i}'
        pred=artifact(dest/f'{kind}-predictions.pt',kind,arm,r)
        model=artifact(dest/f'{kind}-map.pt',kind,arm,r)
        sc=artifact(root/'scaler.pt','shared',arm,r);mn=sc['mu'];sd=sc['scale']
        info=read((dest/f'{kind}-map.pt').with_suffix('.json'))
        require(info['role_id']==r['id'] and info['inner']==i and info['arm']==kind,'OOF identity')
        if kind=='P':
            fit=package(root/'P-fit.parquet','C-P-fit',arm,r)
            query=package(root/'P-query.parquet','C-P-query',arm,r)
            score=package(root/'P-score.parquet','C-P-score',arm,r)
            require(query.query_key.is_unique and set(query.query_key)==set(score.query_key),'P score join')
            score=score.set_index('query_key').loc[query.query_key].reset_index()
            require(list(score.content_token)==list(query.content_token),'P content join')
            x=(tensor(fit[['pre_'+h for h in HIST]])-mn)/sd
            y=(tensor(fit[['post_'+h for h in HIST]])-mn)/sd
            constant=0.;target=(tensor(score[HIST])-mu)/scale
        else:
            fit=package(root/'G-pre-fit.parquet','C-G-fit',arm,r)
            fitpost=package(root/'G-post-fit.parquet','C-G-fit',arm,r)
            query=package(root/'G-pre-validation.parquet','C-G-query',arm,r)
            score=package(root/'G-post-validation.parquet','C-G-score',arm,r)
            require(not set(query.query_key)&set(score.query_key),'Group identities accidentally paired')
            x=(tensor(fit[HIST])-mn)/sd
            yf=(tensor(fitpost[HIST])-mn)/sd
            centers={t:yf[tensor(fitpost.content_token.eq(t).to_numpy(),torch.bool)].mean(0) for t in set(fit.content_token)}
            y=torch.stack([centers[t] for t in fit.content_token])
            constant=sum(float((yf[tensor(fitpost.content_token.eq(t).to_numpy(),torch.bool)]-centers[t]).square().mean(0).sum())/12 for t in centers)
            post=(tensor(score[HIST])-mu)/scale
            means={t:post[tensor(score.content_token.eq(t).to_numpy(),torch.bool)].mean(0) for t in set(query.content_token)}
            target=torch.stack([means[t] for t in query.content_token]);post_blocks.append((list(query.content_token),list(score.content_token),post))
        require(len(fit)==48 and len(query)==16 and len(score)==16,'OOF row counts')
        require(not set(fit.content_token)&set(query.content_token),'OOF content leakage')
        expected={hashlib.sha256(('ja-content:'+t).encode()).hexdigest() for t in r['C_diagnostic_contents'][i]}
        require(set(query.content_token)==expected and set(score.content_token)==expected,'OOF held members mismatch')
        require(torch.equal(pred['a'],tensor(query[HIST])) and list(pred['content_tokens'])==list(query.content_token) and list(pred['query_keys'])==list(query.query_key),'OOF query replay')
        require(torch.equal(pred['scale'],sd),'OOF inner scale mismatch')
        b0=(((tensor(query[HIST])-mn)/sd)@model['matrix'].T+model['bias'])*sd+mn
        pe=float((b0-pred['b0']).abs().max());require(pe<1e-12,'OOF raw prediction replay')
        je=replay_map(model,x,y,r['eta'],constant,info)
        aa.append((pred['a']-mu)/scale);bb0.append((pred['b0']-mu)/scale);bb.append(target);alltokens.extend(query.content_token)
        audits.append(dict(role_id=r['id'],kind=kind,inner=i,eta=r['eta'],rows=16,raw_prediction_error=pe,objective_error=je,fit_query_content_disjoint=True,outer_scale_used=True))
    require(len(set(alltokens))==16 and pd.Series(alltokens).value_counts().eq(4).all(),'OOF coverage')
    aa=torch.cat(aa);bb0=torch.cat(bb0);bb=torch.cat(bb);w=torch.full((64,),1/64,device=device(),dtype=torch.float64)
    variance=None
    if kind=='G':
        variance=torch.zeros(10,device=device(),dtype=torch.float64)
        for pt,bt,pz in post_blocks:
            for t in set(pt):
                z=pz[tensor(np.array(bt)==t,torch.bool)];center=z.mean(0)
                for j in range(10):variance[j]+=(z[:,block(j)]-center[block(j)]).square().mean()/16
    c=rec.coefficients(aa,bb0,bb,w,variance);c.update(s=s,raw_variance=rawvar)
    q=tensor([.9,1.1]*5);explicit=rec.explicit_error(aa,bb0,bb,w,q)
    if kind=='G':
        # All 16x(4x4) anonymous pairs, not a chosen donor permutation.
        explicit=torch.zeros_like(s)
        offset=0
        for pt,bt,pz in post_blocks:
            pp=a.adjust(aa[offset:offset+16],bb0[offset:offset+16],q)
            for t in set(pt):
                xx=pp[tensor(np.array(pt)==t,torch.bool)];yy=pz[tensor(np.array(bt)==t,torch.bool)]
                for j in range(10):explicit[j]+=(xx[:,None,block(j)]-yy[None,:,block(j)]).square().mean()/16
            offset+=16
    err=float((explicit-rec.error(q,c)).abs().max());require(err<1e-10,'OOF quadratic vs explicit error')
    require(bool((rec.gap(torch.ones_like(q),c)==0).all()),'q=1 gap not zero')
    put(c,OUT/'C-coefficients'/r['id']/(kind+'.pt'),role_id=r['id'],kind=kind,actual_C_OOF=True,source_pilot_coefficients_reused=False,outer_coordinates=True,explicit_error=err)
    return audits,err

def run():
    with stage('OOF_coefficients'):
        audits=[];errs=[];a,u,_,rec=production()
        for k,r in enumerate(contract()['roles']):
            # Training-only anonymous scaler shared by both workers; no P targets in G.
            sc=artifact(PREP/'slots'/r['id']/'CT2.pt','shared','D-P',r);mu=sc['mu'];scale=sc['scale']
            d=package(AG/'packages'/r['id']/'full/G-post.parquet','C-anonymous-post','D-P',r)
            z=(tensor(d[HIST])-mu)/scale;s,rv=rec.anonymous_variance(z,tensor(d.fit_mass))
            for kind in ['P','G']:
                rows,err=one(r,kind,mu,scale,s,rv);audits.extend(rows);errs.append(err)
            if (k+1)%12==0:progress('OOF_coefficients_prepared',roles=k+1,total=60)
        save(pd.DataFrame(audits),OUT/'audits/OOF-provenance.parquet')
        write(OUT/'audits/OOF-replay.json',dict(passed=True,predictions=480,coefficient_sets=120,max_explicit_error=max(errs),group_all_combinations=True,H_reads=0,U_reads=0,new_mapping_fits=0))

if __name__=='__main__':run()

