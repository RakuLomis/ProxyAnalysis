"""Allowlisted experimental role packages; not an operating-system sandbox."""
from pathlib import Path
import pandas as pd
from .audit import read,file_hash


class Bundle:
    ALLOWED={'paired':{'C_pre','C_post','U_pre','labels'},'group':{'G_pre','G_post','U_pre'}}
    def __init__(self,path,kind):
        if kind not in self.ALLOWED:raise PermissionError('Reference/scoring access requires a later sealed stage')
        self.path=Path(path);self.kind=kind;self.meta=read(self.path/'manifest.json');self.access=[]
        assert self.meta['kind']==kind

    def get(self,name):
        if name not in self.ALLOWED[self.kind]:raise PermissionError('Forbidden role: '+name)
        item=self.meta['files'][name];path=self.path/item['filename']
        assert path.resolve().parent==self.path.resolve()
        assert file_hash(path)==item['sha256']
        frame=pd.read_parquet(path)
        assert list(frame.columns)==item['columns']
        self.access.append(name)
        return frame
