"""Training-only CUDA smoke tests; no formal classifier and no test scoring."""
import time
from unittest.mock import patch
import pandas as pd
from common import *
from packages import Bundle
from generation import generate_query,fit,allowed_generator_jobs,wm,torch
from learning import Heads,network,scaler,schedule,independent_pre_schedule


def smoke(output_name='engineering.json'):
    assert read(OUT/'gate-packages.json')['passed']
    assert output_name in {'engineering.json','engineering-replay.json'}
    assert not (OUT/output_name).exists()
    device();torch.backends.cuda.matmul.allow_tf32=False
    torch.backends.cudnn.allow_tf32=False
    started=time.perf_counter();generation=[];classification=[];reads=[]
    original=pd.read_parquet
    def guarded(path,*args,**kwargs):
        text=str(path).replace('\\','/')
        if '/packages/inference/' in text or '/packages/scoring/' in text:
            raise AssertionError('Engineering attempted to read held-out data')
        reads.append(text)
        return original(path,*args,**kwargs)
    with patch.object(pd,'read_parquet',guarded):
        for protocol in PROTOCOLS:
            job=read(OUT/'generator-roles'/f'{protocol}-f0-q0.json')
            records={}
            for kind in ['paired','group','cyclic']:
                r=generate_query(job,kind,SEEDS[0]);records[kind]=r
                assert len(r['query'])==24 and r['values'].shape==(24,8,6)
                assert all(v['fit_rows']==68 for v in r['loco'])
                for a in [r['canonical_pre'][FEATURES].to_numpy(float),r['query'][FEATURES].to_numpy(float)]:
                    back,_=wm.decode(wm.encode(a));np.testing.assert_array_equal(back.cpu().numpy(),a)
                generation.append({'protocol':protocol,'kind':kind,'fit_rows':72,'query_rows':24,
                    'LOCO_models':18,'pool_rows':len(r['pool']),'views':192,'read_roles':r['access'],
                    'normal_residual':r['model'].normal_residual,'decoder_counts':r['decoder_counts']})
            g=Bundle(OUT/'packages/generator-group'/job['job'],'group')
            pre,post=g.get('group_pre'),g.get('group_post')
            model,pool,*_=fit(pre.sample(frac=1,random_state=41),post.sample(frac=1,random_state=42),'group')
            torch.testing.assert_close(model.weight,records['group']['model'].weight,atol=0,rtol=0)
            torch.testing.assert_close(pool,records['group']['pool'],atol=0,rtol=0)
            # Weighted mean-target and full Cartesian squared objectives agree.
            aa=[];zz=[]
            for c,rows in records['group']['canonical_pre'].groupby('content_id'):
                z=wm.encode(post[post.content_id.eq(c)][FEATURES].to_numpy(float))
                for a in rows[FEATURES].to_numpy(float):
                    for target in z:aa.append(a);zz.append(target)
            expanded=wm.Ridge(np.asarray(aa),torch.stack(zz))
            torch.testing.assert_close(expanded.weight,model.weight,atol=1e-9,rtol=1e-9)

        schedules=0;cache_checks=0
        for path in sorted((OUT/'roles').glob('*.json')):
            role=read(path);b=Bundle(OUT/'packages/training'/role['scenario'],'M1')
            post,pre=b.get('post'),b.get('pre_unpaired')
            for seed in SEEDS:
                ix=schedule(post,seed);px=independent_pre_schedule(post,pre,ix)
                assert post.iloc[ix[0]].label_id.tolist()==pre.iloc[px[0]].label_id.tolist()
                schedules+=1
            cache_checks+=len(allowed_generator_jobs(role))

        # Representative sizes, with 15 independent heads except I0's 3 seeds.
        for name,nhead in [('E1-all-f0',15),('E2-anytls-f0',15),('I0-anytls-f0',3)]:
            post=Bundle(OUT/'packages/training'/name,'M0').get('post')
            mean,scale=scaler(post);x=(np.log1p(post[FEATURES].to_numpy(float))-mean)/scale
            classes=sorted(post.label_id.unique());yy=np.array([classes.index(v) for v in post.label_id])
            ix=schedule(post,SEEDS[0])[0]
            x=torch.tensor(x[ix],device=device(),dtype=torch.float32);y=torch.tensor(yy[ix],device=device())
            torch.manual_seed(SEEDS[0]);init=network();assert sum(p.numel() for p in init.parameters())==422
            states=[{k:v.clone() for k,v in init.state_dict().items()} for _ in range(nhead)]
            heads=Heads(states).to(device());refs=[network() for _ in states]
            for h,s in zip(refs,states):h.load_state_dict(s)
            batch=torch.cat([x,x],0)[None].expand(nhead,-1,-1).clone()
            targets=torch.cat([y,y],0)[None].expand(nhead,-1).clone()
            # M0 repeated-slot objective equals conventional post-only CE+L2.
            for h in [refs[0]]:
                plain=torch.nn.functional.cross_entropy(h(x),y)+.5e-4*sum(v.square().sum() for k,v in h.named_parameters() if k.endswith('weight'))
                torch.testing.assert_close(heads.loss(batch,targets)[0],plain,atol=2e-6,rtol=2e-5)
            opt=torch.optim.Adam(heads.parameters(),lr=.001,foreach=False)
            opts=[torch.optim.Adam(h.parameters(),lr=.001,foreach=False) for h in refs]
            delta=0.
            for _ in range(5):
                opt.zero_grad(set_to_none=True);heads.loss(batch,targets).sum().backward();opt.step()
                for h,o in zip(refs,opts):
                    o.zero_grad(set_to_none=True)
                    loss=torch.nn.functional.cross_entropy(h(batch[0]),targets[0])+.5e-4*sum(v.square().sum() for k,v in h.named_parameters() if k.endswith('weight'))
                    loss.backward();o.step()
                with torch.no_grad():
                    expected=torch.stack([h(batch[0]) for h in refs]);actual=heads(batch)
                    torch.testing.assert_close(actual,expected,atol=2e-5,rtol=2e-4)
                    delta=max(delta,float((actual-expected).abs().max()))
            with torch.no_grad():
                altered=batch.clone();altered[1:]+=100
                assert torch.equal(heads(altered)[0],heads(batch)[0])
                chunk=torch.cat([heads(z) for z in batch.split(17,dim=1)],1)
                torch.testing.assert_close(chunk,heads(batch),atol=2e-6,rtol=2e-5)
                assert torch.equal(chunk.argmax(-1),heads(batch).argmax(-1))
            torch.cuda.synchronize();t=time.perf_counter()
            for _ in range(40):
                opt.zero_grad(set_to_none=True);heads.loss(batch,targets).sum().backward();opt.step()
            torch.cuda.synchronize();seconds=(time.perf_counter()-t)/40
            classification.append({'scenario':name,'heads':nhead,'combined_batch':batch.shape[1],
                'comparison_steps':5,'benchmark_steps':40,'max_logit_difference':delta,'seconds_per_step':seconds})
    write(OUT/output_name,{'passed':True,'cuda':True,'gpu':torch.cuda.get_device_name(),
        'generation':generation,'group_permutation_and_cartesian_equivalence':True,
        'generation_smoke_Ridge_fits':385,'classification':classification,'tested_seed_schedules':schedules,
        'cache_source_checks':cache_checks,'M0_double_slot_equals_post_CE':True,
        'test_feature_or_label_reads':0,'production_classifiers_trained':0,'read_files':sorted(set(reads)),
        'seconds':time.perf_counter()-started,'training_allowed':False,'script_sha256':file_hash(Path(__file__))})
    print({k:v for k,v in read(OUT/output_name).items() if k not in ['generation','read_files']})


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('--replay',action='store_true')
    smoke('engineering-replay.json' if parser.parse_args().replay else 'engineering.json')
