from common import *
from head import *

def run():
    with stage('tests'):
        q=basis();eye=torch.eye(5,device=device(),dtype=torch.float64)
        require(maxabs(q.T@q-eye)<1e-12 and maxabs(q.sum(0))<1e-12,'Q orthonormal')
        p6=torch.eye(6,device=device(),dtype=torch.float64)-torch.ones((6,6),device=device(),dtype=torch.float64)/6
        require(maxabs(q@q.T-p6)<1e-12,'Q contrast projector')
        gen=torch.Generator(device=device()).manual_seed(20261015)
        z0=torch.randn((20,6),generator=gen,device=device(),dtype=torch.float64)
        geo=geometry(z0,q);h=torch.randn((20,5),generator=gen,device=device(),dtype=torch.float64)
        a=apply(h,geo);require(maxabs(apply(a,geo)-a)<1e-12,'Idempotence')
        require(maxabs(apply(geo['u'],geo))<1e-12,'Radial annihilation')
        b=torch.randn(h.shape,generator=gen,device=device(),dtype=torch.float64)
        require(abs(float((h*apply(b,geo)).sum()-(apply(h,geo)*b).sum()))<1e-12,'Symmetric projection')
        geometry_errors(geo['s'],a@q.T,geo['mask'])
        # Exercise strict norm comparison in five coordinates without rounding
        # an exact threshold through a different, six-coordinate representation.
        boundary=torch.zeros((4,5),device=device(),dtype=torch.float64);boundary[:,0]=tensor([0.,.5e-12,1e-12,1.5e-12])
        mask=contrast_geometry(boundary,boundary@q.T)['mask']
        require(mask.tolist()==[False,False,False,True],'Strict tau norm mask')
        near=geometry(torch.zeros((4,6),device=device(),dtype=torch.float64),q)
        require(not bool(near['mask'].any()) and bool((apply(h[:4],near)==0).all()),'Zero rows retained')
        tiny=torch.zeros((3,5),device=device(),dtype=torch.float64);tiny[:,0]=tensor([.5e-12,1.5e-12,2e-12])
        require(geometry(tiny@q.T,q)['mask'].tolist()==[False,True,True],'Near-zero actual six-dimensional path')
        for bad in [float('nan'),float('inf')]:
            v=z0.clone();v[0,0]=bad
            try:geometry(v,q)
            except RuntimeError:pass
            else:raise RuntimeError('Nonfinite base was treated as near-zero')
        r=contract()['roles'][0];s,m,g=train(r,'OR-P',SEEDS[0]);phi=features(s['x'],g,'OR-P');base=offset(s['x'],m);geo=geometry(base,q)
        require(base.dtype==torch.float64 and phi.dtype==torch.float64 and all(not v.requires_grad for v in g.values()),'Frozen precision')
        w=torch.zeros((5,104),device=device(),dtype=torch.float64);b=torch.zeros(5,device=device(),dtype=torch.float64)
        zz,_,dd=logits(w,b,phi,base,q,geo)
        require(torch.equal(zz,base) and torch.equal(zz.softmax(1),base.softmax(1)) and torch.equal(zz.argmax(1),base.argmax(1)),'Zero head exact baseline')
        w=(torch.randn((5,104),generator=gen,device=device(),dtype=torch.float64)*.001).requires_grad_()
        b=(torch.randn((5,),generator=gen,device=device(),dtype=torch.float64)*.001).requires_grad_()
        loss=objective(w,b,phi,base,s['y'],s['mass'],q,geo);gw,gb=torch.autograd.grad(loss,(w,b))
        check=independent(w,b,phi,base,s['y'],s['mass'],q)
        je=abs(float(loss.detach()-check['objective'].detach()));ge=max(maxabs(gw-check['gw']),maxabs(gb-check['gb']))
        require(je<=1e-10 and ge<=1e-10,'Independent 6D objective/gradient')
        zz,_,delta=logits(w,b,phi,base,q,geo);geometry_errors(geo['s'],delta,geo['mask'])
        require(maxabs(zz-check['logits'])<=1e-12,'5D versus 6D logits')
        dw=torch.randn(w.shape,generator=gen,device=device(),dtype=torch.float64);db=torch.randn(b.shape,generator=gen,device=device(),dtype=torch.float64)
        norm=torch.sqrt(dw.square().sum()+db.square().sum());dw/=norm;db/=norm
        analytic=float((dw*gw).sum()+(db*gb).sum());fd=[]
        for step in [1e-4,1e-5]:
            plus=objective(w.detach()+step*dw,b.detach()+step*db,phi,base,s['y'],s['mass'],q,geo)
            minus=objective(w.detach()-step*dw,b.detach()-step*db,phi,base,s['y'],s['mass'],q,geo)
            value=float((plus-minus)/(2*step));error=abs(value-analytic)
            require(error<=1e-7+1e-4*abs(analytic),'Finite difference gate');fd.append(dict(step=step,error=error,analytic=analytic))
        require(abs(float((q@w).square().sum()-w.square().sum()))<1e-12,'Original weight L2')
        biased=independent(torch.zeros_like(w),b,phi,base,s['y'],s['mass'],q);require(float(biased['L2'])==0,'No bias penalty')
        empty=torch.empty((480,0),device=device(),dtype=torch.float64);ew=torch.empty((5,0),device=device(),dtype=torch.float64)
        require(bool(torch.isfinite(objective(ew,b,empty,base,s['y'],s['mass'],q,geo))),'BIAS empty input')
        negative=[]
        probes=[lambda:check_source(ROOT/r['query'],'predict',r['id']),lambda:check_source(ROOT/r['labels'],'labels',r['id']),
                lambda:check_source(ROOT/r['frozen_G'][f'OR-P-{SEEDS[0]}'],'train',r['id'],'OR-X'),
                lambda:check_source(ROOT/r['frozen_G'][f'OR-P-{SEEDS[0]}'],'train',r['id'],'OR-G'),
                lambda:check_source(ROOT/r['classification'],'train','different-role'),
                lambda:check_source(ROOT/'outputs/forbidden-actual-H/query.parquet','predict',r['id'])]
        for probe in probes:
            try:probe()
            except RuntimeError:negative.append(True)
            else:negative.append(False)
        require(all(negative),'Permission negative tests')
        # Metadatas never enter the numerical API; no parent-real-post direction.
        require(torch.equal(offset(s['x'],m),base),'View-specific baseline replay')
        xonly=features(s['x'],None,'OR-X');require(torch.equal(xonly,s['x'].float().double()),'Original x path')
        write(OUT/'audits/unit-tests.json',dict(passed=True,objective_error=je,gradient_error=ge,
              finite_differences=fd,permission_negative_tests=negative,synthetic_real_head_fits=0,
              train_geometry=geometry_errors(geo['s'],delta,geo['mask']),
              deterministic=True,device=torch.cuda.get_device_name(),dtype='float64',H_reads=0))
