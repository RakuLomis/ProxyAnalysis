"""DSR scoped IO and deterministic CUDA float64 operations."""
from pathlib import Path
import hashlib
import json
import os
import time
os.environ.setdefault('CUBLAS_WORKSPACE_CONFIG', ':4096:8')
import numpy as np
import pandas as pd
import pyarrow.dataset
import pyarrow.parquet
import torch
import torch.nn.functional as F

ROOT=Path(__file__).resolve().parents[2]
OLD=ROOT/'outputs/kernel-sensitivity-regularization-20261005/run-01'
Q=ROOT/'outputs/protocol-probability-drift-20261004/run-01'
OUT=ROOT/'outputs/drift-state-group-risk-20261005/run-01'
DOC=ROOT/'docs/drift-state-group-risk'
PLAN=ROOT/'plan/drift-state-group-risk-classification-plan-20261005.md'
PROTOCOLS=['shadowsocks','vless','trojan','vmess']
LABELS=['bing.com::search_results_view','developer.mozilla.org::document_view',
        'github.com::repository_view','wikipedia.org::article_view',
        'youtube.com::search_results_view','youtube.com::video_playback']
FEATURES=['W_up','W_down','U_up','U_down','P_up','P_down','E_up','E_down','FR_packet_runs','R_unique_zero_runs']
WEIGHTS=[1/12]*8+[1/6]*2
BYTE_EDGES=[1,256,1024,4096,16384,65536,262144,1048576]
COUNT_EDGES=[1,2,3,4,8,16,32,64,128]
HIST=[f'h{j:02d}_{b:02d}' for j in range(10) for b in range(9 if j<4 else 10)]
ARMS=['DSR0','DSR1','DSR2','DSR3','DSR4']; ALPHAS=[0,.1,.25,.5]
TAU=1.; ETA=.1; ACCESS=[]

def require(ok,msg):
    if not ok: raise RuntimeError(msg)
def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,obj):
    p=Path(p); p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(obj,ensure_ascii=False,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf-8')
def sha(p):
    require(Path(p).suffix.lower() not in ['.pcap','.pcapng','.cap'],'No PCAP access')
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
    return h.hexdigest()
def rel(p): return Path(p).resolve().relative_to(ROOT).as_posix()
def save(df,p):
    Path(p).parent.mkdir(parents=True,exist_ok=True); df.to_parquet(p,index=False)
def device():
    require(torch.cuda.is_available(),'CUDA required, no CPU fallback'); return torch.device('cuda:0')
def configure():
    device(); torch.set_num_threads(1); torch.backends.cuda.matmul.allow_tf32=False
    torch.backends.cudnn.allow_tf32=False; torch.use_deterministic_algorithms(True)
    torch.cuda.reset_peak_memory_stats()
def tensor(x,dtype=torch.float64): return torch.as_tensor(np.asarray(x),device=device(),dtype=dtype)
def size(j): return 9 if j<4 else 10
def bins(x,j):
    z=tensor(x); require(torch.isfinite(z).all() and (z>=0).all() and (z==z.floor()).all(),'Invalid feature')
    return torch.bucketize(z,tensor(BYTE_EDGES if j<4 else COUNT_EDGES),right=True)
def weighted(i,w,n): return F.one_hot(i,n).to(torch.float64).T@w
def truths(df): return df.label_id.map(dict(zip(LABELS,range(6)))).to_numpy(int)
def visitid(session): return hashlib.sha256(('business-query-v1:'+session).encode()).hexdigest()
def rolekey(r): return f"f{r['outer']}/{r['protocol']}/"+('outer' if r['inner'] is None else f"i{r['inner']}")
def mainfolder(kind,r): return OUT/kind/'main'/rolekey(r)
def oldfolder(kind,r):
    p=OLD/kind/('outer' if r['inner'] is None else 'inner')/f"f{r['outer']}"/r['protocol']
    return p if r['inner'] is None else p/f"i{r['inner']}"
def sourcefolder(kind,source): return OUT/kind/'sources'/source['id']
def queryfolder(kind,query): return OUT/kind/'cf'/query['id']
def contract():
    original=OUT/'manifests/experiment-contract.json'
    amended=OUT/'manifests/experiment-contract-amended-v1.json'
    if amended.exists():
        seal=read(OUT/'manifests/engineering-repair-v1/amendment-seal.json')
        require(sha(amended)==seal['contract_sha256'],'Engineering amendment seal changed')
        c=read(amended)
        require(sha(original)==c['engineering_revision']['original_contract_sha256'],'Original contract changed')
        return c
    return read(original)
def start(stage):
    configure(); ACCESS.clear(); c=contract()
    for p,h in c['source_sha256'].items(): require(sha(ROOT/p)==h,'Sealed source changed')
    return c
def checked(p,mapping,role):
    h=sha(p); require(mapping.get(rel(p))==h,'Unsealed/changed '+rel(p))
    ACCESS.append({'role':role,'path':rel(p),'sha256':h})
def package(p,role):
    allowed={'kernel-fit':{'fit-paired','group-pre','group-post'},'lr-fit':{'train-post'},
      'true-state':{'query-paired'},'group-state':{'query-group-post','query-group-pre'},
      'difficulty-predict':{'query-post'},'difficulty-score':{'query-labels'},
      'state-grouping':{'train-post'},'risk-fit':{'train-post'},'class-predict':{'query-post'},
      'inner-select':{'score-labels'},'outer-score':{'score-labels'},'test-state':{'test-paired'},
      'verify':{'train-post','fit-paired','group-pre','group-post','query-paired','query-group-post',
                'query-group-pre','query-post','query-labels','score-labels','test-paired'}}
    p=Path(p); require(p.stem in allowed[role],'Forbidden package for '+role)
    if role=='inner-select': require('/i' in p.as_posix(),'Outer selection labels forbidden')
    if role in ['outer-score','test-state']:
        require((OUT/'predictions/complete.json').exists(),'Predictions must be sealed before test scoring')
    checked(p,contract()['packages_sha256'],role); df=pd.read_parquet(p)
    if role in ['class-predict','difficulty-predict']: validate_query(df)
    return df
def validate_query(q): require(set(q)=={'visit_id',*HIST},'Post-only query contains forbidden fields')
def validate_scope(source,query,parent):
    require(set(source).issubset(parent) and set(query).issubset(parent) and
            not set(source)&set(query) and set(source)|set(query)==set(parent),
            'Wrong CF scope/cache: source and query must partition parent training contents')
def complete(p,**extra):
    p=Path(p); write(p/'complete.json',{'time_unix':time.time(),
      'sha256':{x.name:sha(x) for x in p.iterdir() if x.suffix in ['.pt','.parquet']},**extra})
def artifact(p,role='artifact'):
    p=Path(p); require(read(p.parent/'complete.json')['sha256'].get(p.name)==sha(p),'Artifact seal mismatch')
    ACCESS.append({'role':role,'path':rel(p),'sha256':sha(p)})
    return torch.load(p,map_location=device(),weights_only=True)
def oldartifact(kind,r,name):
    p=oldfolder(kind,r)/(name+'.pt'); checked(p,contract()['baseline_sha256'],'old_'+kind)
    return artifact(p,'old_'+kind)
def finish(stage,**details):
    details['cuda_peak_allocated_MiB']=torch.cuda.max_memory_allocated()/1048576
    write(OUT/'manifests'/f'{stage}-ledger.json',{'reads':ACCESS,'completed_unix':time.time(),**details})
    write(OUT/'progress.json',{'stage':stage,'time_unix':time.time(),**details}); print(stage,details,flush=True)
def standardize(df):
    h=tensor(df[HIST]); mu=h.mean(0); scale=h.std(0,unbiased=False)
    scale=torch.where(scale>0,scale,torch.ones_like(scale)); return (h-mu)/scale,mu,scale
def probabilities(m,q):
    validate_query(q)
    with torch.no_grad():
        x=(tensor(q[HIST])-m['mu'])/m['scale']; p=torch.softmax(x@m['weight'].T+m['bias'],1)
    d=pd.DataFrame(p.cpu().numpy(),columns=[f'p{y}' for y in range(6)])
    d['visit_id']=q.visit_id.to_numpy(); d['prediction']=p.argmax(1).cpu().numpy(); return d
def metrics(y,p):
    y=np.asarray(y,int); z=p.argmax(1); cm=np.bincount(y*6+z,minlength=36).reshape(6,6)
    den=cm.sum(0)+cm.sum(1); f1=np.divide(2*np.diag(cm),den,out=np.zeros(6),where=den>0)
    return {'F1':float(f1.mean()),'accuracy':float((z==y).mean()),
      'CE':float(-np.log(p[np.arange(len(y)),y]).mean()),'Brier':float(((p-np.eye(6)[y])**2).sum(1).mean())},cm
def kernel(paired,gp,gb,j):
    require(set(gp)=={'content_id','fit_mass',*['pre_'+f for f in FEATURES]},'Anonymous pre identity leak')
    require(set(gb)=={'content_id','fit_mass',*['post_'+f for f in FEATURES]},'Anonymous post identity leak')
    k=size(j); a=bins(paired['pre_'+FEATURES[j]],j); b=bins(paired['post_'+FEATURES[j]],j)
    n=weighted(a*k+b,tensor(paired.fit_mass),k*k).reshape(k,k)
    contents=sorted(gp.content_id.unique()); code=dict(zip(contents,range(len(contents)))); margins=[]
    for side,d in [('pre',gp),('post',gb)]:
        u=tensor(d.content_id.map(code),torch.long); z=bins(d[side+'_'+FEATURES[j]],j)
        margins.append(weighted(u*k+z,tensor(d.fit_mass),len(contents)*k).reshape(-1,k))
    ca,cb=margins; g=ca.T@(cb/ca.sum(1)[:,None])
    require(max(float((n.sum(0)-g.sum(0)).abs().max()),float((n.sum(1)-g.sum(1)).abs().max()))<1e-10,'Marginal mismatch')
    q=(n.sum(0)+1/k)/(n.sum()+1)
    return {'true_counts':n,'group_counts':g,'M1':(n+q)/(n.sum(1)[:,None]+1),
      'M2':(g+q)/(g.sum(1)[:,None]+1)}
def partition(score,y):
    gamma=torch.zeros((len(score),2),device=device(),dtype=torch.float64); boundaries=[]
    for label in range(6):
        ix=torch.where(y==label)[0]; s=score[ix]; n=len(ix); require(n>0 and n%2==0,'Balanced even class support')
        t=s.sort().values[n//2-1]; below=s<t; tied=s==t
        fraction=(n/2-int(below.sum()))/int(tied.sum())
        gamma[ix,0]=torch.where(below,torch.ones_like(s),torch.where(tied,torch.full_like(s,fraction),torch.zeros_like(s)))
        boundaries.append({'y':label,'threshold':float(t),'boundary_low_fraction':fraction,
                           'tied_visits':int(tied.sum()),'class_visits':n})
    gamma[:,1]=1-gamma[:,0]
    for label in range(6): require(float((gamma[y==label].sum(0)-int((y==label).sum())/2).abs().max())<1e-12,'State balance')
    return gamma,boundaries
def risks(logits,y,gamma):
    ce=F.cross_entropy(logits,y,reduction='none'); result=[]
    for state in range(2):
        result.append(torch.stack([(gamma[y==label,state]*ce[y==label]).sum()/gamma[y==label,state].sum() for label in range(6)]).mean())
    r=torch.stack(result); require(abs(float((r.mean()-ce.mean()).detach()))<1e-12,'Mean state risk differs from CE')
    return r,ce
def objective(w,b,x,y,gamma,w0,b0,alpha):
    z=x@w.T+b; r,ce=risks(z,y,gamma); robust=TAU*(torch.logsumexp(r/TAU,0)-np.log(2))
    dz=z-(x@w0.T+b0); dz=dz-dz.mean(1,keepdim=True); stay=dz.square().sum()/(5*len(x))
    l2=.0005*w.square().sum(); loss=(1-alpha)*ce.mean()+alpha*robust+l2+ETA*stay
    return loss,{'R0':r[0],'R1':r[1],'CE':ce.mean(),'robust':robust,
                 'drift_gap':robust-ce.mean(),'stay':stay,'L2':l2,'logit_rms':torch.sqrt(dz.square().mean())}
def optimize(x,y,base=None,gamma=None,alpha=0.):
    if base is None:
        w0=torch.zeros((6,96),device=device(),dtype=torch.float64); b0=torch.zeros(6,device=device(),dtype=torch.float64)
        w=torch.nn.Parameter(w0.clone()); b=torch.nn.Parameter(b0.clone())
        def value(): return F.cross_entropy(x@w.T+b,y)+.0005*w.square().sum()
    else:
        w0=base['weight']; b0=base['bias']
        dw=torch.nn.Parameter(torch.zeros_like(w0)); db=torch.nn.Parameter(torch.zeros_like(b0)); w=dw; b=db
        def value(): return objective(w0+dw,b0+db,x,y,gamma,w0,b0,alpha)[0]
    opt=torch.optim.LBFGS([w,b],max_iter=500,tolerance_grad=1e-9,tolerance_change=1e-12,line_search_fn='strong_wolfe')
    evaluations=0; started=time.perf_counter(); initial=float(value().detach())
    def closure():
        nonlocal evaluations
        evaluations+=1; opt.zero_grad(); loss=value(); require(torch.isfinite(loss),'Nonfinite loss'); loss.backward(); return loss
    opt.step(closure); final=float(closure().detach()); torch.cuda.synchronize()
    gradient=max(float(w.grad.abs().max()),float(b.grad.abs().max())); iterations=int(opt.state[w].get('n_iter',0))
    require(final<=initial+1e-10 and gradient<=1e-5 and iterations<500,'Optimization quality gate; no silent extension')
    state={'weight':w.detach() if base is None else (w0+w).detach(),
           'bias':b.detach() if base is None else (b0+b).detach()}
    return state,{'initial_objective':initial,'objective':final,'max_gradient':gradient,'iterations':iterations,
      'closure_evaluations':evaluations,'seconds':time.perf_counter()-started,'device':'cuda:0','dtype':'float64',
      'alpha':alpha,'budget_hit':iterations>=500}
