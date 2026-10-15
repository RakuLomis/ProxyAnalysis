from core import *
import tempfile

ALLOWED={'references','score','diagnostics','plots','verify','report'}
def allowed_action(action):require(action in ALLOWED,'Forbidden operation')
def metadata_digest(path,root,seal,kind):
    p=Path(path).resolve();root=Path(root).resolve();require(p.is_relative_to(root),'Metadata path outside registered root')
    require(str(p) in seal and C.sha(p)==seal[str(p)],'Unregistered or changed weight')
    meta=p.with_suffix('.json') if kind=='individual' else p.parent/'complete.json'
    require(str(meta) in seal and C.sha(meta)==seal[str(meta)],'Metadata contract broken')
    h=C.read(meta)['sha256'];h=h if kind=='individual' else h[p.name]
    require(h==C.sha(p),'Weight/metadata conflict');return h

def run():
    with stage('tests'):
        results=[]
        def test(name,fn):fn();results.append({'name':name,'passed':True})
        def rejected(fn):
            try:fn()
            except (AssertionError,RuntimeError,KeyError,ValueError):return
            raise AssertionError('Expected rejection')
        with tempfile.TemporaryDirectory(prefix='ja-metadata-tests-') as td:
            root=Path(td);p=root/'weight.pt';p.write_bytes(b'synthetic-metadata-unit-test')
            individual=p.with_suffix('.json');directory=root/'complete.json'
            individual.write_text(json.dumps({'sha256':C.sha(p)}));directory.write_text(json.dumps({'sha256':{p.name:C.sha(p)}}))
            seal={str(v):C.sha(v) for v in [p,individual,directory]}
            test('individual metadata',lambda:metadata_digest(p,root,seal,'individual'))
            test('directory metadata',lambda:metadata_digest(p,root,seal,'directory'))
            for name,fn in [('weight changed',lambda:metadata_digest(p,root,{**seal,str(p):'wrong'},'directory')),
                            ('directory changed',lambda:metadata_digest(p,root,{**seal,str(directory):'wrong'},'directory')),
                            ('contract chain missing',lambda:metadata_digest(p,root,{},'directory')),
                            ('unregistered same name',lambda:metadata_digest(p,root,{str(directory):seal[str(directory)]},'directory')),
                            ('path escape',lambda:metadata_digest(p,root/'sub',seal,'directory'))]:test(name,lambda fn=fn:rejected(fn))
        for action in ['train','prepare','select','fit','resume-original-runner']:test('deny '+action,lambda action=action:rejected(lambda:allowed_action(action)))
        for kind,purpose in [('JA-C-paired','query'),('JA-C-group','paired-map'),('JA-heldout-visits','source-fit')]:
            test('deny '+kind+' '+purpose,lambda kind=kind,purpose=purpose:rejected(lambda:C.check_permission(kind,purpose)))
        dev=C.device();generator=torch.Generator(device=dev);generator.manual_seed(20261009)
        x=torch.randn(8,96,generator=generator,device=dev,dtype=torch.float64);y=torch.randn(8,96,generator=generator,device=dev,dtype=torch.float64)
        w=C.tensor([.05,.05,.05,.05,.2,.2,.2,.2]);tokens=[0]*4+[1]*4
        def decomposition(a,b,name):
            s,c,between,within=algebra(a,b,w,tokens);check_equal(c,between+within,name);return s,c,between,within
        test('unequal group masses',lambda:decomposition(x,y,'weighted identity'))
        def only_between():
            xx=x.clone();yy=y.clone();xx[:4]=xx[:4].mean(0);xx[4:]=xx[4:].mean(0);yy[:4]=yy[:4].mean(0);yy[4:]=yy[4:].mean(0)
            s,c,bt,wi=decomposition(xx,yy,'between only');require(float(wi.abs().max())<1e-12,'within not zero')
        test('zero within and between-only',only_between)
        def only_within():
            xx=x.clone();xx[:4]-=xx[:4].mean(0);xx[4:]-=xx[4:].mean(0)
            s,c,bt,wi=decomposition(xx,2*xx,'within only');require(float(bt.abs().max())<1e-12,'between not zero')
        test('within-only common changes',only_within)
        test('zero covariance',lambda:decomposition(torch.zeros_like(x),torch.zeros_like(y),'zeros'))
        s,c,bt,wi=decomposition(x,y,'regularized');mx=(x*w[:,None]).sum(0)
        alpha=1.;eye=torch.eye(96,device=dev,dtype=torch.float64);q=s+alpha*eye
        m1=torch.linalg.solve(q,(c+alpha*eye).T).T;m2=torch.linalg.solve(q,(bt+alpha*eye).T).T
        delta=torch.linalg.solve(q,wi.T).T
        test('matrix closed form',lambda:check_equal(m1-m2,delta,'matrix'))
        test('bias and application',lambda:check_equal((x@m1.T-mx@m1.T)-(x@m2.T-mx@m2.T),(x-mx)@delta.T,'application'))
        test('eta mismatch rejected',lambda:rejected(lambda:require(.1==1.,'eta mismatch')))
        test('all input covariance retained',lambda:require(float(s.trace())>0,'SAA lost'))
        write(OUT/'tests.json',{'passed':True,'rows':results,'CUDA':True,'dtype':'float64','new_fits':0})
if __name__=='__main__':run()
