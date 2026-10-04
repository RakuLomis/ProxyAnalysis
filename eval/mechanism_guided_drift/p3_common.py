"""Independent P3 paths, immutable arm budget and file capabilities."""
from pathlib import Path
import numpy as np
import pandas as pd
from common import ROOT, LATEST, DOC, read_json as read, write_json as write, file_hash, digest
from diagnostics import W, AUX
from p3_legacy import LC, LP, LG, LE
from p3_model import wm, torch

OUT=ROOT/'outputs/mechanism-guided-drift-20261003/experiment/run-01'
P2=OUT.parents[1]/'diagnostics'
SEEDS=[20260918,20260919,20260920]
ARMS=['M0','D0_pair','D1_pair','D2_pair','D2_group','D2_cyclic']
GENERATORS={'D0_pair':('D0','paired'),'D1_pair':('D1','paired'),
            'D2_pair':('D2','paired'),'D2_group':('D2','group'),'D2_cyclic':('D2','cyclic')}


class Bundle:
    ALLOWED={'classifier':{'post'},'inference':{'test_post'},'scoring':{'test_labels'},
             'paired':{'fit_pre','fit_post','query_pre'},'cyclic':{'fit_pre','fit_post','query_pre'},
             'group':{'group_pre','group_post','query_pre'}}
    def __init__(self,folder,capability):
        self.folder=folder;self.capability=capability;self.meta=read(folder/'manifest.json');self.access=[]
    def get(self,name):
        if name not in self.ALLOWED[self.capability] or name not in self.meta['files']:raise PermissionError(name)
        item=self.meta['files'][name];path=self.folder/item['filename']
        assert path.resolve().parent==self.folder.resolve() and file_hash(path)==item['sha256']
        f=pd.read_parquet(path);assert len(f)==item['rows'] and list(f)==item['columns']
        self.access.append(name);return f


def export(folder,frames,meta):
    folder.mkdir(parents=True,exist_ok=True);assert not (folder/'manifest.json').exists()
    files={}
    for name,f in frames.items():
        path=folder/(name+'.parquet');f.to_parquet(path,index=False)
        files[name]={'filename':path.name,'rows':len(f),'columns':list(f),'sha256':file_hash(path)}
    write(folder/'manifest.json',{**meta,'files':files})


def enable_cuda():
    LC.device();torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False


def authorize():
    record=read(OUT/'authorization.json');assert record['G2_accepted']
    seal=read(OUT/'seal.json');assert seal['contract_sha256']==file_hash(OUT/'model-contract.json')
    for path,h in seal['hashes'].items():assert file_hash(ROOT/path)==h,'sealed file changed: '+path
    assert read(OUT/'qualification.json')['passed'];enable_cuda();return read(OUT/'model-contract.json')


def completed(folder):
    path=folder/'complete.json'
    if not path.exists():return False
    done=read(path);assert done['seal_sha256']==file_hash(OUT/'seal.json')
    for name,h in done['files'].items():assert file_hash(folder/name)==h
    return True


def complete(folder,metadata):
    write(folder/'complete.json',{**metadata,'seal_sha256':file_hash(OUT/'seal.json'),
          'files':{p.name:file_hash(p) for p in folder.iterdir() if p.is_file() and p.name!='complete.json'}})


def generator_bundle(job,kind):
    return Bundle(OUT/'packages'/('generator-group' if kind=='group' else 'generator-paired')/job['job'],kind)


def generator_frames(job,method,kind):
    bundle=generator_bundle(job,kind)
    pre=bundle.get('group_pre' if kind=='group' else 'fit_pre')
    post=bundle.get('group_post' if kind=='group' else 'fit_post')
    query=bundle.get('query_pre').sort_values('session_id').reset_index(drop=True)
    if method=='D0':pre=pre.drop(columns=AUX);query=query.drop(columns=AUX)
    assert set(query.session_id)==set(job['query_sessions']) and set(pre.content_id).isdisjoint(query.content_id)
    if kind!='group':assert set(pre.session_id)==set(post.session_id)==set(job['fit_sessions'])
    else:assert set(pre)=={'content_id',*W,*AUX} and set(post)=={'content_id',*W}
    return pre,post,query,bundle.access
