"""Two training-only CUDA engineering runs; no H/reference reads or scoring."""
from pathlib import Path
import sys
import time
import numpy as np

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'src'))
sys.path.insert(0,str(ROOT/'eval/hy2_carrier_calibration'))
from proxy_analysis.extend_calibration.audit import read,write,file_hash
from proxy_analysis.extend_calibration.bundles import Bundle
from proxy_analysis.feasible_summary_calibration import model as tm
import window_model as wm
import torch

BASE=ROOT/'outputs/extend-calibration-20260930/run-01/extraction-03/training-preparation-01'


def main():
    assert read(BASE/'package-gate.json')['passed'] and torch.cuda.is_available()
    assert not (BASE/'cuda-smoke.json').exists()
    records=[]
    for track in ['W','T']:
        scenario=f'{track}-shadowsocks-f0-g0-r0'
        bundle=Bundle(BASE/'packages/paired'/scenario,'paired')
        c,cp,u,labels=[bundle.get(n) for n in ['C_pre','C_post','U_pre','labels']]
        features=bundle.meta['numeric_classifier_features'];target_features=features if track=='W' else features[:-1]
        cp=cp.set_index('session_id').loc[c.session_id].reset_index()
        module=wm if track=='W' else tm
        a=c[target_features].to_numpy(float);target=module.encode(cp[target_features].to_numpy(float))
        if track=='W':
            generator=module.Ridge(a,target);latent=generator.predict(u[features].to_numpy(float));decoded,_=module.decode(latent)
        else:
            generator=module.Ridge(a,c.F.to_numpy(float),target)
            latent=generator.predict(u[target_features].to_numpy(float),u.F.to_numpy(float));decoded,_=module.decode(latent,u.F.to_numpy(float))
        assert generator.weight.is_cuda and decoded.is_cuda
        import pandas as pd
        source=pd.concat([c,u],ignore_index=True).sort_values('session_id').reset_index(drop=True).merge(labels,on='session_id',validate='one_to_one')
        assert len(source)==96
        # Raw arm engineering: C supplies true post; U supplies unchanged pre.
        values=source[features].to_numpy(float)
        post_lookup=cp.set_index('session_id')
        for i,sid in enumerate(source.session_id):
            if sid in post_lookup.index:values[i]=post_lookup.loc[sid,features].to_numpy(float)
        mean=np.log1p(c[features].to_numpy(float)).mean(0);scale=np.log1p(c[features].to_numpy(float)).std(0);scale[scale<1e-10]=1
        x=torch.tensor((np.log1p(values)-mean)/scale,device='cuda',dtype=torch.float32)
        classes=sorted(source.label_id.unique());assert len(classes)==6
        y=torch.tensor([classes.index(v) for v in source.label_id],device='cuda')
        seed=20260918;torch.manual_seed(seed)
        head=torch.nn.Sequential(torch.nn.Linear(len(features),32),torch.nn.ReLU(),torch.nn.Linear(32,6)).cuda()
        rng=np.random.default_rng(seed);groups={l:sorted(g.content_id.unique()) for l,g in source.groupby('label_id')}
        for contents in groups.values():assert len(contents)==4;rng.shuffle(contents)
        positions={c:np.flatnonzero(source.content_id.eq(c).to_numpy()) for g in groups.values() for c in g}
        schedule=np.stack([np.concatenate([positions[groups[l][step%4]] for l in classes]) for step in range(1000)])
        assert np.bincount(schedule.ravel(),minlength=96).tolist()==[250]*96
        schedule=torch.tensor(schedule,device='cuda');optimizer=torch.optim.Adam(head.parameters(),lr=.001,foreach=False)
        started=time.perf_counter()
        for ix in schedule:
            optimizer.zero_grad(set_to_none=True);logits=head(x[ix]);loss=torch.nn.functional.cross_entropy(logits,y[ix])
            loss=loss+.5e-4*sum(v.square().sum() for k,v in head.named_parameters() if k.endswith('weight'))
            assert logits.is_cuda and torch.isfinite(loss)
            loss.backward();assert all(p.grad.is_cuda for p in head.parameters());optimizer.step()
        with torch.no_grad():pred=head(x);assert pred.is_cuda and pred.shape==(96,6) and torch.isfinite(pred).all()
        torch.cuda.synchronize()
        records.append({'scenario':scenario,'track':track,'seed':seed,'cuda':True,'device':torch.cuda.get_device_name(0),
            'generator_fit_C_visits':24,'generator_prediction_U_visits':72,'classifier_training_visits':96,
            'classes':6,'input_dimension':len(features),'hidden_dimension':32,'steps':1000,'batch':24,
            'seconds':time.perf_counter()-started,'read_roles':bundle.access,'test_or_reference_read':False,
            'loss_finite':True,'generation_decoding_passed':True,'formal_experiment_result':False})
    write(BASE/'cuda-smoke.json',{'passed':True,'runs':records,'formal_training_allowed':False,
        'no_heldout_metrics_computed':True,'code_sha256':file_hash(Path(__file__))})
    print({'passed':True,'CUDA_training_only_runs':len(records),'heldout_read':False},flush=True)


if __name__=='__main__':main()
