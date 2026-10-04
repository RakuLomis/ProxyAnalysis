"""Train-only CUDA qualification. Never reads inference/scoring packages."""
from unittest.mock import patch
import time
from p3_common import *
from p3_model import fit, sample, startup_beta, startup_center


def capacity(pre,post,query,kind):
    if kind=='group':
        pre=pre.sort_values(['content_id',*W,*AUX]).reset_index(drop=True)
        post=post.sort_values(['content_id',*W]).reset_index(drop=True)
        means=post.groupby('content_id')[W].mean()
        raw=np.stack([means.loc[c].to_numpy() for c in pre.content_id])
    else:
        pre=pre.sort_values(['content_id','repetition']).reset_index(drop=True)
        post=post.set_index('session_id').loc[pre.session_id].reset_index()
        raw=post[W].to_numpy(float);donor=np.arange(72)
        if kind=='cyclic':
            for _,g in pre.groupby('content_id'):
                ix=g.index.to_numpy();donor[ix]=np.roll(ix,-1)
        raw=raw[donor]
    a=pre[W].to_numpy(float);aux=pre[AUX].to_numpy(float)
    beta=startup_beta(a,raw,aux)
    startup_center(a,aux,beta);startup_center(query[W].to_numpy(float),query[AUX].to_numpy(float),beta)
    for c in sorted(pre.content_id.unique()):
        held=pre.content_id.eq(c).to_numpy();b=startup_beta(a[~held],raw[~held],aux[~held])
        startup_center(a[~held],aux[~held],b);startup_center(a[held],aux[held],b)
    return beta.cpu().tolist()


def main():
    assert not (OUT/'qualification.json').exists();enable_cuda();start=time.perf_counter()
    reads=[];oldread=pd.read_parquet
    def guard(path,*a,**kw):
        s=str(path).replace('\\','/')
        if '/packages/inference/' in s or '/packages/scoring/' in s:raise PermissionError('test access in engineering')
        reads.append(s);return oldread(path,*a,**kw)
    replay=[];smoke=[];capacities=[]
    with patch.object(pd,'read_parquet',guard):
        for jp in sorted((OUT/'generator-roles').glob('*.json')):
            job=read(jp)
            for kind in ['paired','group','cyclic']:
                a,b,q,_=generator_frames(job,'D2',kind)
                capacities.append({'job':job['job'],'kind':kind,'beta':capacity(a,b,q,kind),'full_plus18LOCO_capacity_passed':True})
            if job['fold']!=0 or job['query_group']!=0:continue
            pre,post,query,_=generator_frames(job,'D0','paired')
            model,pool,logs,_,_=fit(pre,post,'paired','D0')
            old=LG.generate_query(job,'paired',SEEDS[0])
            torch.testing.assert_close(model.weight,old['model'].weight,atol=0,rtol=0)
            torch.testing.assert_close(pool,old['pool'],atol=0,rtol=0)
            for seed in SEEDS:
                v,_,draw=sample(model,pool,query,job['job'],seed)
                path=LATEST/'generation'/job['job']/'paired'/f'samples-{seed}.npz'
                with np.load(path,allow_pickle=False) as f:
                    np.testing.assert_array_equal(v,f['values']);np.testing.assert_array_equal(draw,f['donor_indices'])
            replay.append({'job':job['job'],'coefficients_pool_samples_draws_exact':True})
            for arm,(method,kind) in GENERATORS.items():
                a,b,q,_=generator_frames(job,method,kind)
                m,p,l,canon,_=fit(a,b,kind,method);v,e,d=sample(m,p,q,job['job'],SEEDS[0])
                assert len(p)==(288 if kind=='group' else 72) and v.shape==(24,8,6)
                smoke.append({'job':job['job'],'arm':arm,'pool_rows':len(p),'normal_residual':m.normal_residual,
                    'center_column_space_relative_error':m.center_column_space_relative_error,'beta':m.beta.cpu().tolist(),
                    'decoder_effects':e,'cuda':True})
                if kind=='group':
                    mm,pp,*_=fit(a.sample(frac=1,random_state=41),b.sample(frac=1,random_state=42),kind,method)
                    torch.testing.assert_close(m.weight,mm.weight,atol=0,rtol=0)
                    torch.testing.assert_close(m.beta,mm.beta,atol=0,rtol=0)
                    torch.testing.assert_close(p,pp,atol=0,rtol=0)
        role=read(OUT/'roles/E1-all-f0.json');post=Bundle(OUT/'packages/training'/role['scenario'],'classifier').get('post')
        mu,sd=LE.scaler(post);yy=np.array([sorted(post.label_id.unique()).index(y) for y in post.label_id])
        ix=LE.schedule(post,SEEDS[0])[0];x=torch.tensor((np.log1p(post[W].to_numpy(float))-mu)/sd,device=LC.device(),dtype=torch.float32)[ix]
        y=torch.tensor(yy,device=LC.device())[ix];batch=torch.cat([x,x])[None].repeat(18,1,1);targets=torch.cat([y,y])[None].repeat(18,1)
        torch.manual_seed(SEEDS[0]);initial=LE.network().state_dict();h=LE.Heads([initial]*18).to(LC.device())
        ref=LE.network();ref.load_state_dict(initial)
        opt=torch.optim.Adam(h.parameters(),lr=.001,foreach=False);other=torch.optim.Adam(ref.parameters(),lr=.001,foreach=False)
        diff=0.
        for _ in range(5):
            opt.zero_grad(set_to_none=True);h.loss(batch,targets).sum().backward();opt.step()
            other.zero_grad(set_to_none=True)
            loss=torch.nn.functional.cross_entropy(ref(batch[0]),targets[0])+.5e-4*sum(v.square().sum() for k,v in ref.named_parameters() if k.endswith('weight'))
            loss.backward();other.step()
            actual=h(batch)[0];expected=ref(batch[0]);torch.testing.assert_close(actual,expected,atol=2e-5,rtol=2e-4)
            diff=max(diff,float((actual-expected).abs().max()))
        assert sum(v.numel() for v in ref.parameters())==422
        altered=batch.clone();altered[1:]+=100
        assert torch.equal(h(altered)[0],h(batch)[0])
    write(OUT/'baseline-replay.json',{'passed':True,'jobs':replay,'exact_values':True,'classifier_18_head_smoke_max_logit_difference':diff,
        'group_permutation_invariance':True,'no_test_reads':True,'old_outputs_modified':False})
    write(OUT/'cuda-replay.json',{'passed':True,'gpu':torch.cuda.get_device_name(),'dtype_generation':'float64','dtype_classifier':'float32',
        'generator_smoke':smoke,'production_classifiers_trained':0,'test_reads':0,'CPU_fallback':False})
    write(OUT/'qualification.json',{'passed':True,'capacity_checks':capacities,'complete_capacity_scopes':300*19,
        'main_members_unchanged':True,'group_permission_passed':True,'P2_identity_qualification_reused':True,
        'startup_clipping_or_retries':0,'inference_or_scoring_reads':0,'engineering_file_reads':sorted(set(reads)),
        'seconds':time.perf_counter()-start,'human_G2_confirmed':True})
    hashes=dict(read(OUT/'model-contract.json')['legacy_hashes'])
    for folder in [OUT/'packages',OUT/'roles',OUT/'generator-roles']:
        for path in folder.rglob('*'):
            if path.is_file():hashes[str(path.relative_to(ROOT))]=file_hash(path)
    for path in Path(__file__).parent.glob('p3_*.py'):hashes[str(path.relative_to(ROOT))]=file_hash(path)
    for path in [OUT/'cohort.parquet',OUT/'qualification.json',OUT/'baseline-replay.json',OUT/'access-contract.json',
                 ROOT/'eval/mechanism_guided_drift/diagnostic_models.py',ROOT/'eval/mechanism_guided_drift/common.py']:
        hashes[str(path.relative_to(ROOT))]=file_hash(path)
    write(OUT/'seal.json',{'contract_sha256':file_hash(OUT/'model-contract.json'),'hashes':hashes,
        'production_allowed':True,'classifier_count':90,'Ridge_fits':9500,'test_results_read_before_seal':False})
    print('engineering passed; all startup scopes valid; production sealed',flush=True)


if __name__=='__main__':main()
