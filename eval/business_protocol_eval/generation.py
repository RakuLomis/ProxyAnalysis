"""Content-cross-fitted forward W augmentation using unchanged CUDA algebra."""
import importlib
import pandas as pd
from common import *
from packages import Bundle

sys.path.insert(0,str(ROOT/'eval/hy2_carrier_calibration'))
wm=importlib.import_module('window_model')
torch=wm.torch


def fit(pre,post,kind):
    if kind not in {'paired','cyclic','group'}:raise ValueError(kind)
    if kind=='group':
        assert set(pre)==set(post)=={'content_id',*FEATURES}
        pre=pre.sort_values(['content_id',*FEATURES]).reset_index(drop=True)
        post=post.sort_values(['content_id',*FEATURES]).reset_index(drop=True)
    else:
        assert set(pre)==set(post)=={'session_id','content_id','repetition',*FEATURES}
        pre=pre.sort_values(['content_id','repetition']).reset_index(drop=True)
        post=post.set_index('session_id').loc[pre.session_id].reset_index()
        assert pre.groupby('content_id').repetition.agg(set).map(lambda x:x=={1,2,3,4}).all()
    assert len(pre)==len(post)==72 and pre.content_id.nunique()==18
    assert pre.groupby('content_id').size().eq(4).all() and post.groupby('content_id').size().eq(4).all()
    a=pre[FEATURES].to_numpy(float);b=wm.encode(post[FEATURES].to_numpy(float))
    donor=np.arange(len(pre))
    if kind=='cyclic':
        for _,g in pre.groupby('content_id'):
            ix=g.index.to_numpy();donor[ix]=np.roll(ix,-1)
        assert (donor!=np.arange(len(pre))).all()
    if kind=='group':
        centers={c:b[np.flatnonzero(post.content_id.eq(c))].mean(0) for c in post.content_id.unique()}
        target=torch.stack([centers[c] for c in pre.content_id])
    else:target=b[donor]
    model=wm.Ridge(a,target);errors=[];logs=[]
    for c in sorted(pre.content_id.unique()):
        held=pre.content_id.eq(c).to_numpy();inner=wm.Ridge(a[~held],target[~held]);pred=inner.predict(a[held])
        if kind=='group':
            z=b[np.flatnonzero(post.content_id.eq(c))]
            residual=(z[None,:,:]-pred[:,None,:]).reshape(-1,6)
        else:residual=target[held]-pred
        errors.append(residual)
        logs.append({'held_content':c,'fit_contents':sorted(pre.loc[~held,'content_id'].unique()),
                     'fit_rows':int((~held).sum()),'residual_rows':len(residual),'normal_residual':inner.normal_residual})
    pool=torch.cat(errors)
    assert len(pool)==(288 if kind=='group' else 72) and pool.is_cuda
    return model,pool,logs,pre


def sample_query(model,pool,query,name,seed):
    a=query[FEATURES].to_numpy(float);pred=model.predict(a)
    rng=np.random.default_rng(int(digest(['business-protocol-draw-v1',name,seed])[:16],16))
    draw=rng.integers(0,len(pool),(len(query),8))
    z=pred[:,None,:]+pool[torch.as_tensor(draw,device=device())]
    decoded,audit=wm.decode(z);values=decoded.cpu().numpy();valid_w(values.reshape(-1,6))
    return values,{k:int(v.sum()) for k,v in audit.items()},draw


def generate_query(job,kind,seed):
    name=job['job'];folder=OUT/'packages'/('generator-group' if kind=='group' else 'generator-paired')/name
    bundle=Bundle(folder,kind)
    pre=bundle.get('group_pre' if kind=='group' else 'fit_pre')
    post=bundle.get('group_post' if kind=='group' else 'fit_post')
    query=bundle.get('query_pre').sort_values('session_id').reset_index(drop=True)
    assert set(query.session_id)==set(job['query_sessions'])
    assert set(pre.content_id).isdisjoint(query.content_id)
    if kind!='group':assert set(pre.session_id)==set(post.session_id)==set(job['fit_sessions'])
    model,pool,logs,canon=fit(pre,post,kind)
    values,audit,draw=sample_query(model,pool,query,name,seed)
    return {'values':values,'query':query,'model':model,'pool':pool,'loco':logs,'canonical_pre':canon,
            'access':bundle.access,'decoder_counts':audit,'draw':draw}


def allowed_generator_jobs(role):
    train=set(role['train']);result=[]
    for protocol in role['source_protocols']:
        for q in range(4):
            job=read(OUT/'generator-roles'/f'{protocol}-f{role["fold"]}-q{q}.json')
            assert set(job['fit_sessions'])|set(job['query_sessions']) <= train
            for inner in job['loco']:
                assert set(inner['fit_sessions'])|set(inner['held_sessions']) <= set(job['fit_sessions'])
            assert job['protocol']!=role.get('target') or role['experiment']!='E2'
            result.append(job['job'])
    return result
