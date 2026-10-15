"""K07-K08: fit business marginals and compose frozen training-fold kernels."""
from common import *

def distribution(frame,side):
    labels=tensor(frame.label_id.map({v:i for i,v in enumerate(LABELS)}),torch.int64)
    w=tensor(frame.fit_mass)
    cm=torch.bincount(labels,weights=w,minlength=6)
    require(torch.allclose(cm,torch.full_like(cm,4),atol=1e-11),'Each business must have four training content units')
    result,counts={},{}
    for f in FEATURES:
        k=size(f)
        states=tensor(encode(frame[side+'_'+f],f),torch.int64)
        ct=torch.bincount(labels*k+states,weights=w,minlength=6*k).reshape(6,k)
        q=(ct.sum(0)+1/k)/(w.sum()+1)
        result[f]=(ct+q)/(cm[:,None]+1)
        counts[f]=ct
    return result,counts

def run():
    c=start('distribution_fit')
    times=[]
    for role in c['roles']:
        fold,p=role['fold'],role['protocol']
        folder=modelfolder(fold,p)
        folder.mkdir(parents=True,exist_ok=True)
        path=folder/'distributions.pt'
        if path.exists():
            require(sha(path)==read(folder/'distribution-complete.json')['sha256'],'Incomplete or changed distribution model')
            continue
        started=time.perf_counter()
        pre=load_package(rolefolder(fold,p)/'fit-pre.parquet','distribution_fit')
        post=load_package(rolefolder(fold,p)/'fit-post.parquet','distribution_fit')
        source,source_counts=distribution(pre,'pre')
        direct,post_counts=distribution(post,'post')
        true,group={},{}
        for f in FEATURES:
            b=kernel_load(fold,p,f,'distribution_fit')
            true[f]=source[f]@b['M1']
            group[f]=source[f]@b['M2']
        bundle={'G0':direct,'G3':source,'G4':true,'G5':group,
                'source_counts':source_counts,'post_counts':post_counts}
        for arm in ['G0','G3','G4','G5']:
            for f,q in bundle[arm].items():
                require(bool((q>0).all()) and torch.allclose(q.sum(1),torch.ones(6,device=cuda(),dtype=q.dtype),atol=1e-12), 'Invalid distribution')
        torch.save(bundle,path)
        torch.cuda.synchronize()
        elapsed=time.perf_counter()-started
        write(folder/'distribution-complete.json',{'sha256':sha(path),'seconds':elapsed,'device':'cuda:0'})
        times.append({'fold':fold,'protocol':p,'seconds':elapsed})
        print('business distributions and frozen kernels',p,fold,flush=True)
    finish('distribution_fit',models=20,kernel_files_reused=200,timing=times,test_files_opened=0)

if __name__=='__main__':
    run()
