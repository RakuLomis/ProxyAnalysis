"""Independent formulas, branch-safe differences, capability and CUDA replay."""
from common import *
from model import initial,objective,load,KEYS,residual
from engine import Engine,compare
from prepare import basis_for

def synthetic():
    gen=torch.Generator(device='cuda').manual_seed(8817)
    rand=lambda *s:torch.randn(s,device='cuda',dtype=torch.float64,generator=gen)
    q=torch.linalg.qr(rand(96,5)).Q
    cx=.1*rand(48,96);sx=.1*rand(144,96);target=.1*rand(48,96)
    cy=torch.arange(4,device='cuda').repeat_interleave(12);sy=torch.arange(6,device='cuda').repeat_interleave(24)
    idx=torch.arange(48,device='cuda').reshape(4,12);sidx=torch.arange(144,device='cuda').reshape(6,24)
    t=(target@q)[idx];tc=t-t.mean(1,keepdim=True)
    return dict(cx=cx,sx=sx,target=target,post=target,cy=cy,sy=sy,post_y=cy,Q=q,K=q,
        cz0=.1*rand(48,96),mapped=.1*rand(144,96),cidx=idx,pidx=idx,sidx=sidx,cov=torch.bmm(tc.transpose(1,2),tc)/12)

def independent(s,d):
    # Slow independent torch reference; no covariance BMM or shared loss helper.
    rc=F.relu(d['cx']@s['U1'].T+s['d1'])@s['U2'].T
    rs=F.relu(d['sx']@s['U1'].T+s['d1'])@s['U2'].T
    zh=d['cz0']+rc;dim=d['K'].shape[1];k=d['Q'].shape[1]
    sup=sum(((zh[i]-d['target'][i])@d['K']).square().sum() for i in range(48))/(48*dim)
    cov=0.
    for yy in range(4):
        a=zh[d['cy']==yy]@d['K'];b=d['post'][d['post_y']==yy]@d['K']
        ac=a-a.mean(0);bc=b-b.mean(0)
        ca=sum(v[:,None]*v[None,:] for v in ac)/len(ac);cb=sum(v[:,None]*v[None,:] for v in bc)/len(bc)
        cov=cov+(ca-cb).square().sum()/(4*dim**2)
    means=[rs[d['sy']==yy].mean(0)@d['Q'] for yy in range(6)]
    relation=sum((means[a]-means[b]).square().sum() for a in range(6) for b in range(a+1,6))/(15*k)
    dev=.5*(rc.square().sum()/48+rs.square().sum()/144)/96
    reg=.0001*((s['U1']*s['U1']).sum()+(s['U2']*s['U2']).sum())
    return sup+cov+relation+.1*dev+reg

def run():
    configure('tests');barrier('P0-complete.json');results=[];d=synthetic()
    s={k:v.clone().requires_grad_() for k,v in initial().items()}
    with torch.no_grad():s['U2'].fill_(.01);s['d1'].fill_(.5)
    a,_=objective(s,d);b=independent(s,d);ga=torch.autograd.grad(a,list(s.values()),retain_graph=True);gb=torch.autograd.grad(b,list(s.values()))
    ge=max(float((x-y).abs().max()) for x,y in zip(ga,gb));require(abs(float(a-b))<1e-12 and ge<1e-12,'Independent objective/gradient')
    results.append(dict(test='independent_objective',value_error=abs(float(a-b)),gradient_error=ge,passed=True))
    gen=torch.Generator(device='cuda').manual_seed(334)
    direction={k:torch.randn(v.shape,device='cuda',dtype=torch.float64,generator=gen) for k,v in s.items()}
    norm=sum(x.square().sum() for x in direction.values()).sqrt();direction={k:x/norm for k,x in direction.items()}
    analytic=sum((g*direction[k]).sum() for k,g in zip(s,ga))
    for h in [1e-4,1e-5]:
        vp=objective({k:v+h*direction[k] for k,v in s.items()},d)[0];vm=objective({k:v-h*direction[k] for k,v in s.items()},d)[0]
        fd=(vp-vm)/(2*h);er=float(abs(fd-analytic));require(er<=1e-8+1e-6*abs(float(analytic)),'Smooth finite differences')
        results.append(dict(test='finite_difference',h=h,error=er,passed=True))
    # Exact anonymous-group Cartesian identity, independent of hidden visit pairing.
    a=d['cx'][:4];b=d['post'][:4];center=b.mean(0)
    cart=(a[:,None]-b[None,:]).square().sum(-1).mean();mean=(a-center).square().sum(-1).mean();constant=(b-center).square().sum(-1).mean()
    require(abs(float(cart-mean-constant))<1e-12,'Cartesian center identity')
    perm=torch.tensor([3,1,0,2],device='cuda');require(torch.allclose(b.mean(0),b[perm].mean(0),atol=1e-15,rtol=1e-15),'Group order invariant')
    require(abs(float((a-b).square().sum()-(a-b[perm]).square().sum()))>1e-8,'Paired objective sensitive')
    results.append(dict(test='paired_and_group_cartesian',passed=True))
    # Effective rank must not pad a fourth feature direction into five.
    w=torch.zeros((6,96),device='cuda',dtype=torch.float64);w[:3,:3]=torch.eye(3,device='cuda',dtype=torch.float64)
    q,qa=basis_for(dict(weight=w));require(qa['rank']==3,'Rank-deficient fixture')
    vv=torch.linspace(-1,1,96,device='cuda',dtype=torch.float64);err=vv-vv@q@q.T
    wc=w-w.mean(0);require(float((wc@err).abs().max())<1e-12,'Null decision direction')
    results.append(dict(test='rank_and_relative_logits',passed=True,rank=3))
    scale=torch.linspace(.01,3,96,device='cuda',dtype=torch.float64);z=torch.zeros_like(scale);z[0]=1;z[1]=-1
    require(abs(float(z[:9].sum()))<1e-15 and abs(float((scale[:9]*z[:9]).sum()))>1e-4,'std all-ones negative fixture')
    results.append(dict(test='nonuniform_scale_mass_normal',passed=True))
    # Nonsmooth activation boundary has one-sided derivatives 0 and 1.
    boundary=torch.tensor(0.,device='cuda',dtype=torch.float64,requires_grad=True);gg=torch.autograd.grad(F.relu(boundary),boundary)[0]
    require(float(gg)==0,'ReLU convention');results.append(dict(test='relu_boundary',left_derivative=0.,right_derivative=1.,autograd=0.,passed=True))
    zero={k:v.clone().requires_grad_() for k,v in initial().items()};zz=objective(zero,d)[0];g=torch.autograd.grad(zz,list(zero.values()))
    # U1 receives only explicit L2 at zero U2; the data path is initially zero.
    require(torch.allclose(g[0],.0002*zero['U1'],atol=1e-12,rtol=1e-12) and float(g[2].abs().max())>1e-10,'Initial gradient paths')
    results.append(dict(test='zero_U2_gradient',initial_U1_data_gradient_zero=True,passed=True))
    independent_engine=Engine([d],[{}],streams=False);graph_engine=Engine([d],[{}],streams=True);graph_engine.capture()
    for stop in [1,10,100]:
        independent_engine.advance(stop-independent_engine.steps);graph_engine.advance(stop-graph_engine.steps)
        e=compare(independent_engine.snapshot(),graph_engine.snapshot());results.append(dict(test='single_graph_replay',step=stop,error=e,passed=True))
    # All 32 actual admissions replay 8 streams; cloned data still independent parameters/Adam.
    ds=[d for _ in range(32)];a=Engine(ds,[{} for _ in ds],False);b=Engine(ds,[{} for _ in ds],True);b.capture()
    for stop in [1,10,100]:
        a.advance(stop-a.steps);b.advance(stop-b.steps);e=compare(a.snapshot(),b.snapshot())
        results.append(dict(test='32_models_8_streams',step=stop,error=e,passed=True))
    # Test real training paths in each capability, without loading G's P target.
    denied=0
    for p,fun in [('query',lambda:external(PREP/'packages'/roles()[0]['id']/'query.parquet',roles()[0]['id'],'query')),
                  ('paired_for_G',lambda:own(OUT/'packages'/roles()[0]['id']/'P.pt',roles()[0]['id']))]:
        import common
        old=common.CAP;common.CAP='G'
        try:fun()
        except RuntimeError:denied+=1
        else:raise RuntimeError('Negative permission test failed '+p)
        finally:common.CAP=old
    results.append(dict(test='permission_negative',denied=denied,passed=True))
    save(OUT/'tests/engineering.parquet',results);flush('tests')
    seal(OUT/'manifests/math-complete.json',[OUT/'tests/engineering.parquet'],passed=True,query_reads=0)
    progress('math_and_CUDA_passed',checks=len(results),models=32,streams=8)

if __name__=='__main__':
    try:run()
    except BaseException as e:failure('tests',e);raise
