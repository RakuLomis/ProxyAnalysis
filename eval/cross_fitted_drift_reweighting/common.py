"""RW fixed OOF reweighting: independent IO, deterministic CUDA and convex loss."""
from pathlib import Path
import hashlib
import json
import os
import time
os.environ.setdefault('CUBLAS_WORKSPACE_CONFIG', ':4096:8')
import numpy as np
import pandas as pd
import pyarrow.parquet  # MUST precede torch on this Windows environment.
import torch
import torch.nn.functional as F

ROOT=Path(__file__).resolve().parents[2]
DSR=ROOT/'outputs/drift-state-group-risk-20261005/run-01'
OLD=ROOT/'outputs/kernel-sensitivity-regularization-20261005/run-01'
Q=ROOT/'outputs/protocol-probability-drift-20261004/run-01'
OUT=ROOT/'outputs/cross-fitted-drift-reweighting-20261006/run-01'
DOC=ROOT/'docs/cross-fitted-drift-reweighting'
PLAN=ROOT/'plan/cross-fitted-drift-state-reweighting-plan-20261006.md'
PROTOCOLS=['shadowsocks','vless','trojan','vmess']
LABELS=['bing.com::search_results_view','developer.mozilla.org::document_view',
 'github.com::repository_view','wikipedia.org::article_view',
 'youtube.com::search_results_view','youtube.com::video_playback']
HIST=[f'h{j:02d}_{b:02d}' for j in range(10) for b in range(9 if j<4 else 10)]
ARMS=['RW0','RW1','RW2','RW3','RW4']; RATIOS=[1.,1.5,2.,4.]; L2_SETTINGS=[0.,.25,1.,4.]
ETA=.1; EPS=1e-12; ACCESS=[]
OPT_COLUMNS=['outer','inner','protocol','arm','setting','alias','iterations','closures',
 'seconds','max_gradient','initial_objective','final_objective','device','dtype',
 'initial_weighted_CE','final_weighted_CE','initial_CE','final_CE','initial_R0',
 'final_R0','initial_R1','final_R1','initial_L2','final_L2','initial_stay','final_stay',
 'weight_delta_norm','bias_delta_norm','centered_logit_RMS','centered_logit_max',
 'probability_max_change','training_class_changes','weighted_CE_gradient_norm',
 'CE_gradient_norm','L2_gradient_norm','protection_gradient_norm','change_gradient_norm',
 'base_residual_gradient_norm','change_CE_cosine','change_L2_cosine',
 'change_CE_norm_ratio','change_L2_norm_ratio','L2_bias_gradient_norm']

def require(ok,msg):
    if not ok: raise RuntimeError(msg)
def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,obj):
    p=Path(p); p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(obj,ensure_ascii=False,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf-8')
def sha(p):
    require(Path(p).suffix.lower() not in ['.pcap','.pcapng','.cap'],'No PCAP reads')
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
    return h.hexdigest()
def rel(p): return Path(p).resolve().relative_to(ROOT).as_posix()
def save(df,p):
    p=Path(p); p.parent.mkdir(parents=True,exist_ok=True); df.to_parquet(p,index=False)
def device():
    require(torch.cuda.is_available(),'CUDA required; no CPU fallback'); return torch.device('cuda:0')
def configure():
    device(); torch.set_num_threads(1); torch.use_deterministic_algorithms(True)
    torch.backends.cuda.matmul.allow_tf32=False; torch.backends.cudnn.allow_tf32=False
    torch.cuda.reset_peak_memory_stats()
def tensor(a,dtype=torch.float64): return torch.as_tensor(np.asarray(a),device=device(),dtype=dtype)
def truths(d):
    y=d.label_id.map(dict(zip(LABELS,range(6)))); require(y.notna().all(),'Unknown label'); return y.to_numpy(int)
def rolekey(r): return f"f{r['outer']}/{r['protocol']}/"+('outer' if r['inner'] is None else f"i{r['inner']}")
def folder(kind,r): return OUT/kind/'main'/rolekey(r)
def oldfolder(r):
    p=OLD/'models'/('outer' if r['inner'] is None else 'inner')/f"f{r['outer']}"/r['protocol']
    return p if r['inner'] is None else p/f"i{r['inner']}"
def contract(): return read(OUT/'manifests/experiment-contract.json')
def start(stage):
    configure(); ACCESS.clear(); c=contract()
    for p,h in c['source_sha256'].items(): require(sha(ROOT/p)==h,'RW source changed '+p)
    return c
def checked(p,mapping,role):
    h=sha(p); require(mapping.get(rel(p))==h,'Unsealed/changed '+rel(p))
    ACCESS.append({'role':role,'path':rel(p),'sha256':h})
def package(r,name,role):
    allowed={'weight-build':{'train-post','train-OOF'},'risk-fit':{'train-post'},
      'class-predict':{'query-post'},'inner-select':{'score-labels'},
      'outer-score':{'score-labels'},'verify':{'train-post','train-OOF','query-post','score-labels'}}
    require(name in allowed[role],'Forbidden package for '+role)
    if role=='inner-select': require(r['inner'] is not None,'No outer labels for selection')
    if role=='outer-score': require((OUT/'predictions/complete.json').exists(),'Seal predictions first')
    p=folder('packages',r)/(name+'.parquet'); checked(p,contract()['packages_sha256'],role)
    d=pd.read_parquet(p)
    if role=='class-predict': validate_query(d)
    return d
def validate_query(d): require(set(d)=={'visit_id',*HIST},'Only opaque ID and post histogram accepted')
def validate_scope(source,query,parent):
    a=set(source); b=set(query); whole=set(parent)
    require(not a&b and a|b==whole,'CF source/query must partition exactly this role training scope')
def complete(p,**extra):
    p=Path(p); write(p/'complete.json',{'time_unix':time.time(),
      'sha256':{x.name:sha(x) for x in p.iterdir() if x.suffix in ['.pt','.parquet','.npy']},**extra})
def artifact(p,role):
    p=Path(p); require(read(p.parent/'complete.json')['sha256'].get(p.name)==sha(p),'Artifact seal mismatch '+rel(p))
    ACCESS.append({'role':role,'path':rel(p),'sha256':sha(p)})
    return torch.load(p,weights_only=True,map_location=device())
def baseline(r,setting=0.):
    p=oldfolder(r)/('zero.pt' if setting==0 else f'KSR1-t{setting:g}.pt')
    checked(p,contract()['baseline_sha256'],'frozen-base'); return artifact(p,'frozen-base')
def finish(stage,**kw):
    kw['cuda_peak_allocated_MiB']=torch.cuda.max_memory_allocated()/1048576
    write(OUT/'manifests'/f'{stage}-ledger.json',{'reads':ACCESS,'completed_unix':time.time(),**kw})
    write(OUT/'progress.json',{'stage':stage,'time_unix':time.time(),**kw}); print(stage,kw,flush=True)
def probabilities(m,q):
    validate_query(q)
    with torch.no_grad():
        x=(tensor(q[HIST])-m['mu'])/m['scale']; p=torch.softmax(x@m['weight'].T+m['bias'],1)
    d=pd.DataFrame(p.cpu().numpy(),columns=[f'p{i}' for i in range(6)])
    d['visit_id']=q.visit_id.to_numpy(); d['prediction']=p.argmax(1).cpu().numpy(); return d
def metrics(y,p):
    y=np.asarray(y,int); z=p.argmax(1); cm=np.bincount(y*6+z,minlength=36).reshape(6,6)
    den=cm.sum(0)+cm.sum(1); f=np.divide(2*np.diag(cm),den,out=np.zeros(6),where=den>0)
    return {'F1':float(f.mean()),'accuracy':float((y==z).mean()),
      'CE':float(-np.log(p[np.arange(len(y)),y]).mean()),'Brier':float(((p-np.eye(6)[y])**2).sum(1).mean())},cm
def validate_gamma(g,y):
    require(g.shape==(len(y),2) and g.dtype==torch.float64 and g.is_cuda,'Gamma coordinates')
    require(bool(torch.isfinite(g).all() and (g>=0).all() and (g<=1).all()),'Gamma range')
    require(float((g.sum(1)-1).abs().max())<1e-12,'Gamma simplex')
    for j in range(6):
        ix=y==j; require(int(ix.sum())>0,'Missing business')
        require(float((g[ix].sum(0)-int(ix.sum())/2).abs().max())<1e-10,'Class state mass')
def risks(loss,y,g):
    return torch.stack([torch.stack([(loss[y==j]*g[y==j,k]).sum()/g[y==j,k].sum()
      for j in range(6)]).mean() for k in range(2)])
def direction(d,y,g):
    validate_gamma(g,y); v=risks(d,y,g); delta=float(v[1]-v[0])
    return (1 if delta>EPS else 0 if delta<-EPS else None),v
def weights(g,hard,r):
    require(r in RATIOS,'Unregistered ratio')
    return torch.ones(g.shape[0],device=device(),dtype=torch.float64) if hard is None or r==1 else 2/(1+r)*(1+(r-1)*g[:,hard])
def partition(s,y):
    g=torch.zeros((len(y),2),device=device(),dtype=torch.float64)
    for j in range(6):
        ix=torch.where(y==j)[0]; v=s[ix]; n=len(ix); require(n>0 and n%2==0,'Even business support')
        t=v.sort().values[n//2-1]; low=v<t; tie=v==t; frac=(n/2-int(low.sum()))/int(tie.sum())
        g[ix,0]=torch.where(low,torch.ones_like(v),torch.where(tie,torch.full_like(v,frac),torch.zeros_like(v)))
    g[:,1]=1-g[:,0]; return g
def objective(W,b,x,y,w,g,base):
    logits=x@W.T+b; ce=F.cross_entropy(logits,y,reduction='none')
    delta=logits-(x@base['weight'].T+base['bias']); centered=delta-delta.mean(1,keepdim=True)
    rr=risks(ce,y,g); parts={'weighted_CE':(w*ce).mean(),'CE':ce.mean(),
      'R0':rr[0],'R1':rr[1],'L2':.0005*W.square().sum(),'stay':centered.square().sum(1).mean()/5}
    total=parts['weighted_CE']+parts['L2']+ETA*parts['stay']; return total,parts
def gradients(W,b,x,y,w,g,base):
    W=W.detach().clone().requires_grad_(); b=b.detach().clone().requires_grad_()
    total,p=objective(W,b,x,y,w,g,base); out={}; vectors={}
    targets={'weighted_CE':p['weighted_CE'],'CE':p['CE'],'L2':p['L2'],
      'protection':ETA*p['stay'],'change':p['weighted_CE']-p['CE'],
      'base_residual':p['CE']+p['L2']}
    for name,target in targets.items():
        if name=='L2': gw=torch.autograd.grad(target,W,retain_graph=True)[0]; gb=torch.zeros_like(b)
        else: gw,gb=torch.autograd.grad(target,[W,b],retain_graph=True)
        v=torch.cat([gw.flatten(),gb]); vectors[name]=v; out[name+'_gradient_norm']=float(v.norm())
    out['L2_bias_gradient_norm']=0.
    for name in ['CE','L2']:
        a=vectors['change']; z=vectors[name]; den=float(a.norm()*z.norm())
        out['change_'+name+'_cosine']=float(torch.dot(a,z))/den if den>0 else None
        out['change_'+name+'_norm_ratio']=float(a.norm()/z.norm()) if float(z.norm())>0 else None
    return out
def optimize(x,y,base,w,g):
    dW=torch.zeros_like(base['weight'],requires_grad=True); db=torch.zeros_like(base['bias'],requires_grad=True)
    opt=torch.optim.LBFGS([dW,db],lr=1.,max_iter=500,tolerance_grad=1e-9,
      tolerance_change=1e-12,line_search_fn='strong_wolfe'); calls=0; started=time.time()
    initial,ip=objective(base['weight'],base['bias'],x,y,w,g,base)
    def closure():
        nonlocal calls
        opt.zero_grad(); loss,_=objective(base['weight']+dW,base['bias']+db,x,y,w,g,base)
        loss.backward(); calls+=1; return loss
    opt.step(closure)
    value=closure(); maxgrad=max(float(dW.grad.abs().max()),float(db.grad.abs().max()))
    it=opt.state[dW]['n_iter']; W=(base['weight']+dW).detach(); b=(base['bias']+db).detach()
    final,fp=objective(W,b,x,y,w,g,base)
    require(bool(torch.isfinite(final)) and float(final)<=float(initial)+1e-10 and maxgrad<=1e-5 and it<500,
      f'Engineering fit gate: objective {float(initial)} -> {float(final)}, gradient {maxgrad}, iterations {it}')
    logits=x@W.T+b; ref=x@base['weight'].T+base['bias']; delta=logits-ref; delta-=delta.mean(1,keepdim=True)
    p=torch.softmax(logits,1); p0=torch.softmax(ref,1)
    log={'alias':False,'iterations':it,'closures':calls,'seconds':time.time()-started,
      'max_gradient':maxgrad,'initial_objective':float(initial),'final_objective':float(final),
      'device':'cuda:0','dtype':'float64','weight_delta_norm':float(dW.norm()),'bias_delta_norm':float(db.norm()),
      'centered_logit_RMS':float(delta.square().mean().sqrt()),'centered_logit_max':float(delta.abs().max()),
      'probability_max_change':float((p-p0).abs().max()),'training_class_changes':int((p.argmax(1)!=p0.argmax(1)).sum())}
    for name in ip: log['initial_'+name]=float(ip[name]); log['final_'+name]=float(fp[name])
    log.update(gradients(W,b,x,y,w,g,base)); return {'mu':base['mu'],'scale':base['scale'],'weight':W,'bias':b},log
