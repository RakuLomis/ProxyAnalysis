"""Read-only scientific inputs; bounded CUDA diagnostics and additive closeout."""
from pathlib import Path
import sys, os, time, json, hashlib, contextlib
ROOT = Path(__file__).resolve().parents[2]
RUN = ROOT/'outputs/joint-affine-transfer-20261007/run-01'
REPORT = RUN/'report-analysis-20261009'
CLOSE = RUN/'closeout-20261009'
OUT = ROOT/'outputs/paired-identity-decomposition-20261009/run-01'
DOC = ROOT/'docs/paired-identity-decomposition'
PLAN = ROOT/'plan/paired-identity-decomposition-and-evidence-closeout-plan-20261009.md'
sys.path.insert(0,str(ROOT/'eval/joint_affine_transfer'))
os.environ['JA_RUN_PATH']=str(RUN)
import common as C
import affine
import numpy as np
import pandas as pd
import torch
E=C.module('ja_report_evidence',ROOT/'eval/joint_affine_transfer_analysis/build_report_evidence.py')
require=C.require

def write(path,obj):
    p=Path(path).resolve();require(any(p.is_relative_to(v) for v in [OUT,CLOSE,DOC]),'Unsafe output')
    p.parent.mkdir(parents=True,exist_ok=True)
    tmp=p.with_name(p.name+'.tmp')
    tmp.write_text(json.dumps(obj,ensure_ascii=False,indent=2,allow_nan=False,default=C.base.json_scalar)+'\n',encoding='utf-8')
    os.replace(tmp,p)
def save(path,df):
    p=Path(path).resolve();require(p.is_relative_to(OUT) or p.is_relative_to(CLOSE),'Unsafe table output')
    p.parent.mkdir(parents=True,exist_ok=True);df.to_parquet(p,index=False)
def textfile(path,text):
    p=Path(path).resolve();require(p.is_relative_to(DOC) or p.is_relative_to(CLOSE),'Unsafe document output')
    p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text,encoding='utf-8')
def progress(stage,**kw):
    write(OUT/'progress.json',{'stage':stage,'time_unix':time.time(),**kw});print(stage,kw,flush=True)
def start(stage):
    c=C.start('paired-identity-'+stage);C.sealed_predictions()
    inv=C.read(OUT/'input-manifest.json')
    for p,h in inv['fixed_files'].items():require(C.sha(ROOT/p)==h,'Input changed: '+p)
    require(C.sha(PLAN)==inv['plan_sha256'],'Plan changed')
    require(C.sha(Path(__file__))==inv['core_sha256'],'Core changed')
    require(not (OUT/'completion.json').exists(),'Analysis already complete')
    return c
@contextlib.contextmanager
def stage(name):
    start(name);path=OUT/'stages'/f'{name}.json'
    require(not path.exists(),'Completed stage cannot be rerun: '+name)
    script=Path(sys.argv[0]).resolve();started=time.time()
    lock=OUT/'stage.lock';lock.parent.mkdir(parents=True,exist_ok=True)
    fd=os.open(lock,os.O_CREAT|os.O_EXCL|os.O_WRONLY);os.write(fd,str(os.getpid()).encode());os.close(fd)
    try:
        progress(name+'_running',pid=os.getpid())
        yield
        require(time.time()-started<=1800,'30 minute stage budget exceeded')
        write(path,{'passed':True,'seconds':time.time()-started,'script':C.rel(script),'script_sha256':C.sha(script),'time_unix':time.time()})
        progress(name+'_complete',seconds=time.time()-started)
    except BaseException as exc:
        write(OUT/'failure.json',{'stage':name,'exception':str(exc),'time_unix':time.time(),'automatic_retry':False})
        raise
    finally:
        if lock.exists() and lock.read_text()==str(os.getpid()):lock.unlink()

def residual(a,b):
    absolute=float((a-b).abs().max());den=max(1.,float(a.abs().max()),float(b.abs().max()))
    return absolute,absolute/den
def check_equal(a,b,message):
    absolute,relative=residual(a,b);require(relative<=1e-10,message)
    return {'absolute':absolute,'normalized':relative}
def selected():return C.choices()
def pairs(c):
    s=selected()
    for r in c['roles']:
        if r['inner'] is not None:
            for eta in C.ETAS:yield r,eta
        elif C.chosen(r,'JA1',s)['eta']==C.chosen(r,'JA2',s)['eta']:
            yield r,C.chosen(r,'JA1',s)['eta']

def tensors(r,mu,scale):
    d=C.package(ROOT/r['C_paired'],'paired-map')
    gp=C.package(ROOT/r['C_group_pre'],'group-map')
    gb=C.package(ROOT/r['C_group_post'],'group-map')
    # Compare independent anonymous marginals, never join using visit identity.
    for side,g in [('pre',gp),('post',gb)]:
        cols=['content_token','fit_mass',*C.HIST]
        p=d[['content_token','fit_mass',*[side+'_'+h for h in C.HIST]]].rename(columns={side+'_'+h:h for h in C.HIST})
        a=p[cols].sort_values(cols).reset_index(drop=True);b=g[cols].sort_values(cols).reset_index(drop=True)
        require(a.equals(b),'Anonymous marginal differs from paired input')
    x=(C.tensor(d[['pre_'+h for h in C.HIST]])-mu)/scale
    y=(C.tensor(d[['post_'+h for h in C.HIST]])-mu)/scale
    w=C.tensor(d.fit_mass)
    for g in [gp,gb]:g[C.HIST]=((C.tensor(g[C.HIST])-mu)/scale).cpu().numpy()
    gx=C.tensor(gp[C.HIST]);gy,constant=affine.group_targets(gp,gb)
    mx,my,sxx,cba=affine.data_moments(x,y,w)
    gmx,gmy,gsxx,gsyx=affine.data_moments(gx,gy,C.tensor(gp.fit_mass))
    xc=x.clone();yc=y.clone();cb=torch.zeros_like(cba)
    for token,indices in d.groupby('content_token',sort=True).indices.items():
        ix=torch.as_tensor(indices,device=C.device(),dtype=torch.long);mass=w[ix].sum();local=w[ix]/mass
        ax=(local[:,None]*x[ix]).sum(0);by=(local[:,None]*y[ix]).sum(0)
        xc[ix]=x[ix]-ax;yc[ix]=y[ix]-by
        cb+=mass*(by-my)[:,None]*(ax-mx)[None,:]
    cw=yc.T@(xc*w[:,None])
    for a,b,name in [(mx,gmx,'pre means'),(my,gmy,'post means'),(sxx,gsxx,'ALL input covariance'),(cb,gsyx,'anonymous group covariance')]:check_equal(a,b,name)
    return x,y,w,mx,my,sxx,cba,cb,cw,constant

def algebra(x,y,w,tokens):
    mx,my,sxx,cba=affine.data_moments(x,y,w);cb=torch.zeros_like(cba);xc=x.clone();yc=y.clone()
    for token in sorted(set(tokens)):
        ix=torch.tensor([i for i,t in enumerate(tokens) if t==token],device=x.device);mass=w[ix].sum();local=w[ix]/mass
        ax=(x[ix]*local[:,None]).sum(0);by=(y[ix]*local[:,None]).sum(0)
        cb+=mass*(by-my)[:,None]*(ax-mx)[None,:];xc[ix]-=ax;yc[ix]-=by
    return sxx,cba,cb,yc.T@(xc*w[:,None])
