"""VICReg on natural paired summaries; independently runnable, post-only heads."""
import argparse
import copy
from pathlib import Path
import platform
import time

import numpy as np
import pyarrow  # Load Arrow before Torch on Windows.
import sklearn
import torch
import yaml
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

from .mechanism_contract import cohort, read, verify as verify_legacy
from .business_representations import matrix, dictionary
from .paired_structure_contract import seal, validate_complete
from .natural_pair_ssl_data import prepare_train, apply_preprocessing, audit_partition, fingerprint
from ..paired_information.prepare import digest, table
from ..reproducibility.preflight import write_json, write_table

CONFIG = Path('configs/content-generalization-20260916-natural-pair-ssl.yaml')


def settings(config=CONFIG):
    cfg = yaml.safe_load(Path(config).read_text(encoding='utf-8'))
    return cfg, Path(cfg['business_root']), Path(cfg['output_root'])


def freeze(config=CONFIG):
    verify_legacy()
    cfg, source, root = settings(config)
    if root.exists():
        raise FileExistsError(root)
    rows = cohort(source)
    if len(rows) != 240 or len({r['session_id'] for r in rows}) != 240:
        raise ValueError('Changed cohort')
    if {r['session_id'] for r in rows} != {r['session_id'] for r in table(source/'primary-cohort.parquet')}:
        raise ValueError('Primary membership differs')
    assignment = read(source/'learning/outer-splits.json')
    captures = {}
    for r in table(source/'capture-audit.parquet'):
        captures.setdefault(r['session_id'], []).append(r)
    contexts = {}
    for task in cfg['tasks']:
        selected = [r for r in rows if task == 'six_business' or r['label_id'].startswith('youtube.com::')]
        for fold in range(5):
            train = sorted([r for r in selected if assignment[r['content_id']] != fold], key=lambda r: r['session_id'])
            test = sorted([r for r in selected if assignment[r['content_id']] == fold], key=lambda r: r['session_id'])
            audit = audit_partition(train, test, captures)
            ssl, state, diag = prepare_train(train)
            changed = [{**r, 'label_id': 'deliberately_changed'} for r in train]
            if fingerprint(prepare_train(changed)[0]) != fingerprint(ssl):
                raise ValueError('SSL depends on business labels')
            labels = sorted({r['label_id'] for r in train})
            meta = lambda rr: [{k: r[k] for k in ['session_id','content_id','label_id','protocol','repetition']} for r in rr]
            contexts[f'{task}-{fold}'] = {'task': task, 'fold': fold, 'labels': labels,
                'train': meta(train), 'test': meta(test), 'audit': audit,
                'preprocessing': state, 'scale_diagnostics': diag, 'ssl': ssl,
                'test_post': apply_preprocessing(matrix(test,'post','distribution157'), state).tolist()}
    root.mkdir(parents=True)
    for name, data in contexts.items():
        # Keep labels and evaluation matrices outside the SSL loader's file.
        ssl = data.pop('ssl')
        write_json(root/'prepared'/f'{name}.ssl.json', ssl)
        write_json(root/'prepared'/f'{name}.json', data)
    seal(root/'prepared', passed=True, contexts=10)
    sources = [Path(config), source/'side-summaries.parquet', source/'capture-audit.parquet',
               source/'primary-cohort.parquet', source/'learning/outer-splits.json']
    sources += list(Path('src/proxy_analysis').rglob('*.py'))
    write_json(root/'contract/manifest.json', {'config': cfg, 'sources': {str(p): digest(p) for p in sorted(sources)},
        'prepared_sha256': digest(root/'prepared/complete.json'), 'features': dictionary(),
        'scope': 'offline_index_assisted_post', 'labels_used_by_ssl': False,
        'source_preprocessing': 'allowed_training_post_only', 'test_pre_used': False})
    write_json(root/'contract/environment.json', {'python': platform.python_version(), 'numpy': np.__version__,
        'torch': torch.__version__, 'sklearn': sklearn.__version__, 'device': 'cpu', 'dtype': 'float64'})
    write_json(root/'contract/observation-audit.json', {
        'model_features': dictionary()['distribution157'], 'identifiers_in_X': False,
        'selection': 'observed exclusive TCP pairs from existing TrafficTracer business pipeline',
        'test_candidate_connections_depend_on_offline_index': True,
        'victim_internal_metadata_free_segmentation_verified': False,
        'interpretation': 'post-only predictor conditional on an index-assisted candidate connection set',
        'provenance_code': ['business_features.py','business_identity.py','business_representations.py'],
        'capture_audit': 'path-identity disjointness, not a fresh raw-byte duplicate audit'})
    seal(root/'contract', passed=True)
    print('Frozen 10 multi-seen contexts, label-free SSL files, train-only scaling', flush=True)


def verify(config=CONFIG):
    cfg, source, root = settings(config)
    validate_complete(root/'contract')
    manifest = read(root/'contract/manifest.json')
    if manifest['config'] != cfg:
        raise ValueError('Configuration changed')
    for p, h in manifest['sources'].items():
        if digest(Path(p)) != h:
            raise ValueError(f'Frozen input changed: {p}')
    if digest(root/'prepared/complete.json') != manifest['prepared_sha256']:
        raise ValueError('Prepared manifest changed')
    validate_complete(root/'prepared')
    torch.set_num_threads(1)
    torch.use_deterministic_algorithms(True)
    return cfg, source, root


def networks(seed):
    torch.manual_seed(seed)
    def linear(a,b):
        return torch.nn.Linear(a,b,dtype=torch.float64)
    encoder = torch.nn.Sequential(linear(157,64),torch.nn.ReLU(),linear(64,32))
    projector = torch.nn.Sequential(linear(32,32),torch.nn.ReLU(),linear(32,32))
    return encoder, projector


def state(model):
    return {k: v.detach().numpy().tolist() for k,v in model.state_dict().items()}


def restore(model, value):
    model.load_state_dict({k: torch.tensor(v,dtype=torch.float64) for k,v in value.items()})


def vicreg(a,b,cfg):
    if a.shape != b.shape or a.ndim != 2 or len(a) < 2:
        raise ValueError('VICReg requires matching batches with n >= 2')
    invariance = (a-b).square().mean()
    variance = sum(torch.relu(1-torch.sqrt(z.var(0,unbiased=True)+cfg['variance_eps'])).mean() for z in [a,b])/2
    covariance = a.new_tensor(0.)
    for z in [a,b]:
        centered = z-z.mean(0)
        cov = centered.T@centered/(len(z)-1)
        covariance = covariance+(cov-torch.diag(torch.diagonal(cov))).square().sum()/z.shape[1]
    w = cfg['vicreg_weights']
    return w[0]*invariance+w[1]*variance+w[2]*covariance, (invariance,variance,covariance)


def views(pre,post,donors,arm,step,cfg,generator):
    # Two N-row passes per update in every arm. B2 alternates full-side batches;
    # over an even step budget each side gets exactly half the updates.
    if arm == 'B1': a,b = post,post
    elif arm == 'B2': a=b=pre if step%2 == 0 else post
    elif arm == 'B3': a,b = pre,post
    elif arm == 'B4': a,b = pre[donors],post
    else: raise ValueError('Unknown SSL arm')
    def mask(x):
        return x*(torch.rand(x.shape,generator=generator,dtype=x.dtype)>=cfg['mask_rate'])
    return mask(a),mask(b)


def diagnostics(x):
    x = np.asarray(x)
    s = np.linalg.svd(x-x.mean(0),compute_uv=False)
    p = s/s.sum() if s.sum() else np.zeros_like(s)
    return {'mean_std': float(x.std(0,ddof=1).mean()), 'min_std': float(x.std(0,ddof=1).min()),
            'effective_rank': float(np.exp(-(p[p>0]*np.log(p[p>0])).sum())) if s.sum() else 0.}


def pretrain(ssl,arm,seed,cfg):
    if set(ssl) != {'session_ids','pre','post','donor_indices'}:
        raise ValueError('Unexpected SSL fields: labels/evaluation metadata prohibited')
    encoder,projector=networks(seed)
    initial={'encoder':state(encoder),'projector':state(projector)}
    opt=torch.optim.Adam(list(encoder.parameters())+list(projector.parameters()),lr=cfg['learning_rate'],foreach=False)
    pre,post=[torch.tensor(ssl[k],dtype=torch.float64) for k in ['pre','post']]
    gen=torch.Generator().manual_seed(seed+100000)
    trace=[]
    for step in range(cfg['steps']):
        a,b=views(pre,post,ssl['donor_indices'],arm,step,cfg,gen)
        opt.zero_grad()
        loss,parts=vicreg(projector(encoder(a)),projector(encoder(b)),cfg)
        loss.backward()
        grad=max(float(p.grad.abs().max()) for p in list(encoder.parameters())+list(projector.parameters()))
        if not np.isfinite(float(loss.detach())) or not np.isfinite(grad):
            raise ValueError('Nonfinite SSL optimization')
        opt.step()
        trace.append({'step':step,'objective':float(loss.detach()),'invariance':float(parts[0].detach()),
            'variance':float(parts[1].detach()),'covariance':float(parts[2].detach()),'gradient_inf':grad})
    with torch.no_grad():
        h=encoder(post).numpy();z=projector(encoder(post)).numpy()
    info={'initial':initial,'encoder':state(encoder),'projector':state(projector),
          'input_sha256':fingerprint(ssl),'train_ids':ssl['session_ids'],
          'encoder_diagnostics':diagnostics(h),'projection_diagnostics':diagnostics(z),
          'steps':cfg['steps'],'row_view_exposures':2*len(pre)*cfg['steps'],
          'arm':arm,'seed':seed,'labels_used':False}
    return encoder,info,trace


def engineering(config=CONFIG):
    cfg,_,root=verify(config)
    out=root/'engineering'
    if (out/'complete.json').exists():
        validate_complete(out);return
    records=[]
    smoke={**cfg,'steps':cfg['engineering_steps']}
    # Four arms each replayed: eight fits, no test arrays loaded.
    ssl=read(root/'prepared/six_business-0.ssl.json')
    for arm in cfg['ssl_arms']:
        _,a,trace=pretrain(ssl,arm,cfg['seeds'][0],smoke)
        _,b,_=pretrain(ssl,arm,cfg['seeds'][0],smoke)
        if fingerprint(a)!=fingerprint(b):
            raise ValueError('Engineering determinism failed')
        # Constant solutions must fail; this is not a task-performance gate.
        if a['encoder_diagnostics']['effective_rank']<1.1 or a['encoder_diagnostics']['mean_std']<1e-6:
            raise ValueError('Collapsed engineering representation')
        records.append({'arm':arm,'repeat_identical':True,**a})
        write_table(out/f'{arm}-trajectory.parquet',trace)
        print(f'engineering {arm}: {a["encoder_diagnostics"]}',flush=True)
    write_json(out/'fits.json',records)
    write_json(out/'validation.json',{'passed':True,'fits':8,'steps_per_fit':smoke['steps'],
        'test_predictions_used':False,'scope':'six_business fold0 all four arms; other contexts formally audited later'})
    seal(out,passed=True)


def encoded(encoder,x):
    with torch.no_grad():
        return encoder(torch.tensor(x,dtype=torch.float64)).numpy()


def supervised(encoder,x,y,k,seed,cfg):
    torch.manual_seed(seed+200000)
    head=torch.nn.Linear(32,k,dtype=torch.float64)
    model=torch.nn.Sequential(encoder,head)
    initial=state(model)
    opt=torch.optim.Adam(model.parameters(),lr=cfg['learning_rate'],foreach=False)
    x=torch.tensor(x,dtype=torch.float64);y=torch.tensor(y,dtype=torch.long)
    trace=[]
    for step in range(cfg['steps']):
        opt.zero_grad()
        ce=torch.nn.functional.cross_entropy(model(x),y)
        penalty=cfg['weight_l2']/2*sum(p.square().sum() for n,p in model.named_parameters() if n.endswith('weight'))
        loss=ce+penalty;loss.backward()
        grad=max(float(p.grad.abs().max()) for p in model.parameters())
        if not np.isfinite(float(loss.detach())) or not np.isfinite(grad):
            raise ValueError('Nonfinite supervised optimization')
        opt.step()
        trace.append({'step':step,'objective':float(loss.detach()),'ce_nats':float(ce.detach()),'gradient_inf':grad})
    return model,{'initial':initial,'final':state(model)},trace


def run(config=CONFIG):
    cfg,_,root=verify(config)
    validate_complete(root/'engineering')
    if not read(root/'engineering/validation.json')['passed']:
        raise ValueError('Engineering gate failed')
    for task in cfg['tasks']:
        for fold in range(5):
            name=f'{task}-{fold}';data=read(root/'prepared'/f'{name}.json');ssl=read(root/'prepared'/f'{name}.ssl.json')
            y=[data['labels'].index(r['label_id']) for r in data['train']]
            for seed in cfg['seeds']:
                for arm in ['B0']+cfg['ssl_arms']:
                    job=root/'jobs'/f'{name}-{seed}-{arm}'
                    if (job/'complete.json').exists():
                        validate_complete(job);continue
                    start=time.time();encoder,_=networks(seed)
                    if arm!='B0':
                        encoder,info,trace=pretrain(ssl,arm,seed,cfg)
                        write_json(job/'ssl-fit.json',info);write_table(job/'ssl-trajectory.parquet',trace)
                    predictions=[]
                    if arm!='B0':
                        h=encoded(encoder,ssl['post']);sc=StandardScaler().fit(h)
                        lr=LogisticRegression(C=cfg['probe_C'],max_iter=10000,tol=1e-8).fit(sc.transform(h),y)
                        if int(lr.n_iter_.max())>=10000:
                            raise ValueError('Probe did not converge')
                        p=lr.predict_proba(sc.transform(encoded(encoder,data['test_post'])))
                        write_json(job/'probe-fit.json',{'encoder':state(encoder),'mean':sc.mean_.tolist(),
                            'scale':sc.scale_.tolist(),'coef':lr.coef_.tolist(),'intercept':lr.intercept_.tolist(),
                            'classes':lr.classes_.tolist(),'n_iter':lr.n_iter_.tolist()})
                        predictions.extend(prediction_rows(data,p,'probe',seed,arm))
                    model,info,trace=supervised(copy.deepcopy(encoder),ssl['post'],y,len(data['labels']),seed,cfg)
                    write_json(job/'finetune-fit.json',info);write_table(job/'finetune-trajectory.parquet',trace)
                    with torch.no_grad():
                        p=torch.softmax(model(torch.tensor(data['test_post'],dtype=torch.float64)),1).numpy()
                    predictions.extend(prediction_rows(data,p,'finetune',seed,arm))
                    write_table(job/'predictions.parquet',predictions)
                    write_json(job/'membership.json',{'train_ids':ssl['session_ids'],'test_ids':[r['session_id'] for r in data['test']],
                        'context':name,'seed':seed,'arm':arm,'stages':1 if arm=='B0' else 3,
                        'prepared_sha256':digest(root/'prepared'/f'{name}.json'),'ssl_input_sha256':fingerprint(ssl),
                        'wall_seconds':time.time()-start})
                    seal(job,passed=True)
                    print(f'completed {job.name} {time.time()-start:.1f}s',flush=True)


def prediction_rows(data,p,stage,seed,arm):
    if not np.isfinite(p).all() or not np.allclose(p.sum(1),1):
        raise ValueError('Invalid probabilities')
    return [{**row,'probabilities':prob.tolist(),'labels':data['labels'],'task':data['task'],'fold':data['fold'],
             'stage':stage,'seed':seed,'arm':arm} for row,prob in zip(data['test'],p)]


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--config',default=str(CONFIG))
    parser.add_argument('--mode',choices=['freeze','verify','engineering','run'],required=True)
    args=parser.parse_args();globals()[args.mode](args.config)
