"""K00-K02: cache-only source hashes, entity isolation and frozen-kernel replay."""
import platform
import time
import pandas as pd
import torch
from common import *

def run():
    require(not (OUT/'manifests/experiment-contract.json').exists(), 'Already sealed; use verify')
    OUT.mkdir(parents=True,exist_ok=True)
    device=cuda()
    t=torch.arange(4,device=device,dtype=torch.float64)
    require(float((t*t).sum())==14,'CUDA float64 failed')
    write(OUT/'manifests/environment.json',{'python':platform.python_version(),'torch':torch.__version__,
         'gpu':torch.cuda.get_device_name(0),'cuda':torch.version.cuda,'device':str(device),
         'probability_dtype':'float64','MLP_dtype':'float32','CPU_fallback':False})
    original=read(OLD/'manifests/baseline-manifest.json')
    for p,h in original['sha256'].items():
        require(sha(ROOT/p)==h,'Original baseline modified: '+p)
    require(read(OLD/'verification.json')['passed'],'Old probability verification absent')
    files={rel(p):sha(p) for p in OLD.rglob('*') if p.is_file() and '__pycache__' not in str(p)}
    files[rel(PLAN)]=sha(PLAN)
    for p in (ROOT/'eval/protocol_probability_drift').rglob('*.py'):
        files[rel(p)]=sha(p)
    parents=pd.read_parquet(OLD/'cohorts/parents.parquet')
    pairs=pd.read_parquet(OLD/'cohorts/pairs.parquet')
    frame=pd.read_parquet(OLD/'features/paired-flow-features.parquet')
    require(len(parents)==600 and len(pairs)==23566 and len(frame)==23566,'Fixed cohort changed')
    require(frame.groupby('protocol').size().to_dict()==EXPECTED,'Protocol counts changed')
    require(set(frame.pair_id)==set(pairs.pair_id) and frame.pair_id.is_unique,'Pair identity mismatch')
    require(frame.groupby('content_id').fold.nunique().max()==1,'Content crosses folds')
    for c in ['session_id','logical_id','carrier_id','pair_id']:
        require(pairs.groupby(c).fold.nunique().max()==1,'Entity crosses folds: '+c)
        require(pairs.groupby(c).content_id.nunique().max()==1,'Entity crosses contents: '+c)
    require(set(frame.label_id)==set(LABELS),'Labels changed')
    require(frame.session_id.nunique()==480 and frame.content_id.nunique()==30,'Parent coverage changed')
    require(parents.groupby('protocol').config_profile_hash.nunique().eq(1).all(),'Multiple configuration identities')
    roles=[r for r in read(OLD/'manifests/experiment-contract.json')['roles'] if r['variant']=='primary']
    require(len(roles)==20,'Expected twenty primary roles')
    kernel_hashes={}
    errors=[]
    for role in roles:
        fold,p=role['fold'],role['protocol']
        tr=frame[frame.protocol.eq(p)&frame.fold.ne(fold)]
        te=frame[frame.protocol.eq(p)&frame.fold.eq(fold)]
        require(set(tr.content_id)==set(role['train_contents']) and set(te.content_id)==set(role['test_contents']), 'Kernel role membership mismatch')
        oldfolder=OLD/'packages/primary'/f'f{fold}'/p
        trainpath=oldfolder/'train.parquet'
        oc=read(OLD/'manifests/experiment-contract.json')
        for name in ['train','group-pre','group-post']:
            path=oldfolder/(name+'.parquet')
            require(sha(path)==oc['packages_sha256'][rel(path)],'Original training package modified')
        train=pd.read_parquet(trainpath)
        require(set(train.pair_id)==set(tr.pair_id),'Saved training package members differ')
        ix=train.set_index('pair_id').loc[tr.pair_id]
        cols=[s+'_'+f for s in ['pre','post'] for f in FEATURES]
        require(np.array_equal(ix[cols].to_numpy(),tr[cols].to_numpy()),'Frozen features differ from kernel training')
        require(np.allclose(train.fit_mass,mass(train),atol=1e-15),'Old fitting mass changed')
        w=tensor(train.fit_mass)
        gi={c:i for i,c in enumerate(sorted(train.content_id.unique()))}
        g=tensor(train.content_id.map(gi),torch.int64)
        for f in FEATURES:
            path=OLD/'kernels/primary'/f'f{fold}'/p/(f+'.pt')
            h=sha(path)
            require(h==read(path.parent/'complete.json')['sha256'][path.name],'Kernel SHA mismatch')
            kernel_hashes[rel(path)]=h
            b=torch.load(path,map_location=device,weights_only=True)
            require(not b['merged'] and not b['conditioned'] and b['feature']==f,'Wrong kernel coordinates')
            k=size(f)
            a=tensor(encode(train['pre_'+f],f),torch.int64)
            z=tensor(encode(train['post_'+f],f),torch.int64)
            true=torch.bincount(a*k+z,weights=w,minlength=k*k).reshape(k,k)
            ga=torch.bincount(g*k+a,weights=w,minlength=24*k).reshape(24,k)
            gb=torch.bincount(g*k+z,weights=w,minlength=24*k).reshape(24,k)
            group=ga.T@(gb/ga.sum(1)[:,None])
            err=max(float((true-b['true_counts']).abs().max()),float((group-b['group_counts']).abs().max()))
            require(err<1e-10,'Kernel count replay failed')
            for arm,counts in [('M1',true),('M2',group)]:
                qb=(counts.sum(0)+1/k)/(counts.sum()+1)
                kernel=(counts+qb)/(counts.sum(1)[:,None]+1)
                require(torch.allclose(kernel,b[arm],atol=1e-12,rtol=1e-12),'Kernel smoothing replay failed')
            errors.append(err)
        print('inventory kernel replay',p,fold,flush=True)
    write(OUT/'manifests/baseline-manifest.json',{'sha256':files,'kernel_sha256':kernel_hashes,
          'frozen_files':len(files),'raw_PCAP_reads':0,'old_sources_unchanged':True})
    write(OUT/'manifests/cohort-audit.json',{'passed':True,'pairs':23566,'parents':480,'contents':30,
          'protocol_pairs':EXPECTED,'kernel_files_replayed':len(kernel_hashes),'max_kernel_count_error':max(errors),
          'registered_entity_cross_fold':0,'test_train_content_overlap':0,
          'deployment_profiles':parents[parents.protocol.isin(PROTOCOLS)][['protocol','config_profile_hash','implementation_sha']].drop_duplicates().to_dict('records'),
          'boundary':'Registered logical/carrier audit; historical incomplete TCP epochs not universally reconstructed'})

if __name__=='__main__':
    run()
