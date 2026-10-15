"""Independent closeout; writes are restricted to new roots, no training API."""
from pathlib import Path
import ast
import hashlib
import json
import os
import sys
import time
import traceback
os.environ.setdefault('CUBLAS_WORKSPACE_CONFIG',':4096:8')
import numpy as np
import pandas as pd
import torch

ROOT=Path(__file__).resolve().parents[2]
PARENT=ROOT/'outputs/invariant-anchor-guarded-drift-20261012/run-01'
OUT=ROOT/'outputs/invariant-anchor-diagnostic-closeout-20261012/run-01'
DOC=ROOT/'docs/invariant-anchor-guarded-drift/closeout-20261012'
PLAN=ROOT/'plan/anchor-qualification-projection-closeout-plan-20261012.md'
FEATURES=['W_up','W_down','U_up','U_down','P_up','P_down','E_up','E_down','FR_packet_runs','R_unique_zero_runs']
SIZES=[9]*4+[10]*6
HIST=[f'h{j:02d}_{k:02d}' for j,n in enumerate(SIZES) for k in range(n)]
PROTOCOLS=['shadowsocks','vless','trojan','vmess']
QUADS=['II','IO','OI','OO']
READS=[]
_C=None
_CACHE={}

def need(x,msg):
    if not bool(x):raise RuntimeError(msg)
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def rel(p):return Path(p).resolve().relative_to(ROOT).as_posix()
def sha(p):
    p=Path(p);need(p.suffix.lower() not in {'.pcap','.pcapng','.cap'},'Capture IO forbidden')
    h=hashlib.sha256()
    with p.open('rb') as f:
        for s in iter(lambda:f.read(1024*1024),b''):h.update(s)
    return h.hexdigest()
def scalar(v):
    if isinstance(v,np.generic):return v.item()
    raise TypeError(type(v).__name__)
def target(p):
    p=Path(p).resolve();need(p.is_relative_to(OUT) or p.is_relative_to(DOC),'Write outside new roots')
    p.parent.mkdir(parents=True,exist_ok=True);return p
def write(p,v):
    p=target(p);q=p.with_name(p.name+'.tmp');q.write_text(json.dumps(v,ensure_ascii=False,indent=2,sort_keys=True,allow_nan=False,default=scalar)+'\n',encoding='utf-8');os.replace(q,p)
def textfile(p,s):target(p).write_text(s,encoding='utf-8')
def save(d,name):
    p=target(OUT/'tables'/f'{name}.parquet');d.to_parquet(p,index=False)
    # Numerical intermediates for artifact-tool-authored static CSV, not a spreadsheet model.
    p=target(OUT/'csv-intermediates'/f'{name}.json');p.write_text(d.to_json(orient='split',index=False,double_precision=15,force_ascii=False),encoding='utf-8')
def configure():
    need(torch.cuda.is_available(),'CUDA required; CPU fallback forbidden');torch.set_num_threads(1)
    torch.use_deterministic_algorithms(True);torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False
def t(x):return torch.as_tensor(np.asarray(x),device='cuda:0',dtype=torch.float64)
def sl(j):return slice(sum(SIZES[:j]),sum(SIZES[:j+1]))
def contract():
    global _C
    if _C is None:
        p=OUT/'closeout-contract.json';need(sha(p)==read(OUT/'seal.json')['sha256'],'Closeout contract changed');_C=read(p)
    return _C
def checked(p,purpose):
    p=Path(p);c=contract();h=c['files'].get(rel(p));need(h is not None,'Unregistered input: '+rel(p))
    sig=(p.stat().st_size,p.stat().st_mtime_ns)
    if _CACHE.get(str(p))!=(sig,h):need(sha(p)==h,'Input hash mismatch: '+rel(p));_CACHE[str(p)]=(sig,h)
    READS.append({'path':rel(p),'purpose':purpose,'sha256':h});return p
def table(p,purpose='diagnostic-table',columns=None):
    checked(p,purpose);return pd.read_parquet(p,columns=columns)
def obj(p):
    checked(p,'frozen-C-tensor');return torch.load(p,map_location='cuda:0',weights_only=True)
def package(p,arm,role):
    c=contract();p=Path(p);info=c['packages'].get(rel(p));need(info is not None,'Package not whitelisted')
    allowed={'P':{'P-train','P-full','P-score'},'G':{'G-pre-train','G-post-train','G-pre-full','G-post-full','G-score'}}
    need(info['kind'] in allowed[arm],'P/G permission violation')
    d=table(p,'C-'+arm+'-'+info['kind']);need(list(d)==info['columns'] and len(d)==info['rows'],'C package schema/count')
    allowed_tokens={hashlib.sha256(('ja-content:'+str(u)).encode()).hexdigest() for u in role['C_contents']}
    need(set(d.content_token)<=allowed_tokens,'Outside C contents');need(d.groupby('content_token').size().eq(4).all(),'Four repetitions')
    need(not set(d)&{'label_id','content_id','visit_id','repetition','pair_id','protocol'},'Unsafe identity/labels')
    if arm=='G':need(set(d)<=set(['content_token','query_key','fit_mass',*HIST]),'Group paired identity leak')
    return d
def progress(s,**v):
    write(OUT/'progress.json',{'stage':s,'time_unix':time.time(),**v});print(s,v,flush=True)

def register():
    configure();need(not (OUT/'seal.json').exists(),'Do not overwrite an existing sealed closeout')
    completion=read(PARENT/'completion.json');need(completion['passed'] and completion['first_stage_complete'],'Parent not complete')
    need(sha(PARENT/'stage-1-verification.json')==completion['verification_sha256'],'Parent verification hash')
    pv=read(PARENT/'stage-1-verification.json');pc=read(PARENT/'manifests/experiment-contract.json')
    need(sha(PARENT/'manifests/experiment-contract.json')==read(PARENT/'manifests/seal.json')['contract_sha256'],'Parent contract seal')
    for p,h in pc['source_sha256'].items():need(sha(ROOT/p)==h,'Parent source changed')
    tree=ast.parse((ROOT/'eval/anchor_guard_drift/common.py').read_text(encoding='utf-8'))
    rule=next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(a,ast.Name) and a.id=='RULE' for a in n.targets))
    need(rule==pc['rule'],'Contract and original RULE disagree')
    gate=read(PARENT/'rules/anchor-gate.json');need(gate['status']=='stop_no_supported_protection_target' and gate['P_anchor_role_blocks']==gate['G_anchor_role_blocks']==0,'Parent stop state changed')
    idx=read(PARENT/'packages/index.json');need(sha(PARENT/'packages/index.json')==read(PARENT/'packages/complete.json')['index_sha256'],'Package index seal')
    files={};packages={}
    def add(p,h=None):
        h=h or pv['files'].get(rel(p));need(h is not None,'Missing parent provenance: '+rel(p));need(sha(p)==h,'Changed parent input');files[rel(p)]=h
    for p in [PARENT/'completion.json',PARENT/'stage-1-verification.json',PARENT/'rules/anchor-gate.json',PARENT/'manifests/experiment-contract.json',
              PARENT/'manifests/seal.json',PARENT/'packages/index.json',PARENT/'packages/complete.json',
              PARENT/'scores/fold-scores.parquet',PARENT/'scores/anchor-qualification.parquet',PARENT/'scores/content-scores.parquet',
              PARENT/'diagnostics/predictions-complete.json',PARENT/'rules/P-rules.json',PARENT/'rules/G-rules.json']:
        add(p,sha(p) if p.name in {'completion.json','stage-1-verification.json'} else None)
    for p,h in pc['source_sha256'].items():files[p]=h
    forecasts=read(PARENT/'diagnostics/predictions-complete.json')['files']
    for r in pc['roles']:
        for i in range(4):
            root=PARENT/'packages'/r['id']/f'i{i}';dest=PARENT/'diagnostics'/r['id']/f'i{i}'
            add(root/'scaler.pt');add((root/'scaler.pt').with_suffix('.json'))
            for arm in ['P','G']:
                for suffix in ['rules.json','map.pt','map.json','predictions.pt','predictions.json']:add(dest/f'{arm}-{suffix}')
                need(forecasts[rel(dest/f'{arm}-predictions.pt')]==files[rel(dest/f'{arm}-predictions.pt')],'C forecast seal')
            for fn in ['P-fit.parquet','P-score.parquet','G-pre-fit.parquet','G-post-fit.parquet','G-post-validation.parquet']:
                p=root/fn;info=idx[rel(p)];add(p,info['sha256']);packages[rel(p)]=info
        for fn in ['P.parquet','G-pre.parquet','G-post.parquet']:
            p=PARENT/'packages'/r['id']/'full'/fn;info=idx[rel(p)];add(p,info['sha256']);packages[rel(p)]=info
        p=ROOT/'outputs/calibrated-deployment-business-transfer-20261006/run-01/packages'/r['id']/'source-post.parquet'
        info=pc['parent_packages'][rel(p)];add(p,info['sha256'])
    env={'python':sys.executable,'torch':torch.__version__,'cuda':torch.version.cuda,'gpu':torch.cuda.get_device_name(0),'dtype':'float64','CPU_fallback':False}
    c={'version':'AC-closeout-v1','plan_sha256':sha(PLAN),'roles':pc['roles'],'rule':rule,'files':files,'packages':packages,
       'parent_verification_sha256':completion['verification_sha256'],'source_sha256':{rel(p):sha(p) for p in [*Path(__file__).parent.glob('*.py'),*Path(__file__).parent.glob('*.mjs')]},
       'new_mapping_fits':0,'new_classifier_fits':0,'H_allowed':False,'U_allowed':False,'PCAP_allowed':False,
       'environment':env,'candidate_blocks':1200,'fold_blocks':4800,'quad_rows':19200,'point_block_rows':192000}
    write(OUT/'closeout-contract.json',c);write(OUT/'seal.json',{'sha256':sha(OUT/'closeout-contract.json')});write(OUT/'environment.json',env)
    write(OUT/'parent-input-manifest.json',{'files':files,'parent_stop':gate,'parent_completion':completion})
    progress('registered',roles=60,new_fits=0,gpu=env['gpu'])
