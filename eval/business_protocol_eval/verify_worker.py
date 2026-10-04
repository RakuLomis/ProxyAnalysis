"""Production array assembly with synthetic generation stubs, never fit/scored."""
from unittest.mock import patch
import pandas as pd
from common import *
import run


def main():
    assert not (OUT/'worker-assembly.json').exists()
    original=pd.read_parquet;reads=[]
    def guarded(path,*a,**kw):
        text=str(path).replace('\\','/')
        assert '/packages/inference/' not in text and '/packages/scoring/' not in text
        reads.append(text);return original(path,*a,**kw)
    checks=[]
    with patch.object(pd,'read_parquet',guarded):
        for name in ['E1-all-f0','E2-anytls-f0','I0-anytls-f0']:
            role=read(OUT/'roles'/f'{name}.json')
            def generated(r,arm,seed,ids):
                assert r==role and set(ids)==set(role['train'])
                # Explicit synthetic legal W values, not cached predictions.
                return np.tile([20,30,4,5,2,2],(len(ids),8,1))
            with patch.object(run,'generated_for',generated):
                h,x,ix,v,y,jobs,mu,sd,classes=run.prepare_classifiers(role)
            assert len(jobs)==(3 if role['experiment']=='I0' else 15)
            assert x.is_cuda and ix.is_cuda and v.is_cuda and y.is_cuda
            assert h.w1.shape[-1]==6 and h.w2.shape[1]==6
            for job in jobs:
                assert job['main_schedule_hash']==next(j['main_schedule_hash'] for j in jobs if j['seed']==job['seed'])
            import torch
            heads=torch.arange(len(jobs),device=device())
            batch=x[heads[:,None],ix[:,0],v[:,0]];target=y[heads[:,None],ix[:,0]]
            with torch.no_grad():assert torch.isfinite(h.loss(batch,target)).all()
            checks.append({'scenario':name,'heads':len(jobs),'full_schedule_shape':list(ix.shape),
                           'test_reads':0,'optimizer_updates':0,'synthetic_generation_stub':True})
    write(OUT/'worker-assembly.json',{'passed':True,'checks':checks,'test_reads':0,
         'actual_generation_files_tested':False,'production_models_trained':0,'read_files':sorted(set(reads)),
         'script_sha256':file_hash(Path(__file__))})
    print(checks)


if __name__=='__main__':main()
