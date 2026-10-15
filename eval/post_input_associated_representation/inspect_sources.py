"""Read metadata and one authorized source task; never H/U numeric data."""
from pathlib import Path
import json
import pandas as pd
import pyarrow.parquet as pq
import torch

ROOT=Path(__file__).resolve().parents[2]
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
dfroot=ROOT/'outputs/dynamic-soft-drift-business-formal-20261012/run-02'
c=read(dfroot/'manifests/experiment-contract.json')
r=c['inner_roles'][0]
print('roles',len(c['roles']),len(c['inner_roles']),flush=True)
print('inner',json.dumps(r,ensure_ascii=False),flush=True)
print('outer',json.dumps(c['roles'][0],ensure_ascii=False),flush=True)
refs=[x for x in c['references'] if x['arm']=='P-small']
print('reference',refs[0],flush=True)
p=ROOT/'outputs/protocol-probability-drift-20261004/run-01/features/paired-flow-features.parquet'
print('native_schema',pq.read_schema(p).names,flush=True)
root=ROOT/'outputs/calibrated-deployment-business-transfer-20261006/run-01/packages'/r['id']
for name in ['source-pre.parquet','source-post.parquet','C-post.parquet']:
    d=pd.read_parquet(root/name)
    print(name,len(d),list(d)[:8],flush=True)
q=torch.load(dfroot/'tasks'/r['id']/'P.pt',map_location='cpu',weights_only=True)
print('task',list(q),{k:list(v.shape) for k,v in q['view'].items() if isinstance(v,torch.Tensor)},flush=True)
for base in ['outputs/dynamic-soft-drift-implicit-v2-20261012/run-01',
             'outputs/dynamic-soft-drift-business-formal-20261012/run-02']:
    b=ROOT/base
    print('candidate_dirs',base,[x.name for x in b.iterdir() if x.is_dir()],flush=True)
print('env',torch.__version__,torch.cuda.get_device_name(0),torch.version.cuda,flush=True)
