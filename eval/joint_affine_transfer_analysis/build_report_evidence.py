"""Report-only replay of immutable JA outputs; never resume the failed runner."""
from pathlib import Path
import sys
import time
import json
import hashlib
import collections
import os

ROOT = Path(__file__).resolve().parents[2]
RUN = ROOT / 'outputs/joint-affine-transfer-20261007/run-01'
DEST = RUN / 'report-analysis-20261009'
sys.path.insert(0, str(ROOT / 'eval/joint_affine_transfer'))
os.environ['JA_RUN_PATH'] = str(RUN)
import common as C
import affine
import numpy as np
import pandas as pd
import torch


def write(name, value):
    path = DEST / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, default=C.base.json_scalar,
                               allow_nan=False) + '\n', encoding='utf-8')


def save(name, frame):
    path = DEST / name; path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_parquet(path, index=False)


def progress(stage, **values):
    write('progress.json', {'stage': stage, 'time_unix': time.time(), **values})
    print(stage, values, flush=True)


def integrity(c):
    C.start('report-only-integrity'); C.sealed_predictions()
    errors = []
    for p, h in c['baseline_sha256'].items():
        if C.sha(ROOT/p) != h: errors.append(p)
    for p, info in c['packages'].items():
        if C.sha(ROOT/p) != info['sha256']: errors.append(p)
    C.require(not errors, 'Frozen input/hash changed')
    for name, count in [('models',34740),('maps',8820),('slots',8820)]:
        fs=list((RUN/name).rglob('*.json'))
        C.require(len(fs)==count and len(list((RUN/name).rglob('*.pt')))==count, 'Artifact count')
        for f in fs:
            C.require(C.sha(f.with_suffix('.pt'))==C.read(f)['sha256'], 'Artifact hash')
        progress('report_hashes', artifact=name, count=count)
    write('integrity.json', {'passed': True, 'baseline_files': len(c['baseline_sha256']),
         'package_files': len(c['packages']), 'models':34740, 'maps':8820, 'slots':8820,
         'contract_sha256':C.sha(RUN/'manifests/experiment-contract.json'),
         'prediction_sha256':C.sha(RUN/'predictions/visits.parquet'),
         'original_failure_sha256':C.sha(RUN/'failure.json')})


def references(c):
    # This historical IO contract itself is directly frozen by the JA contract.
    old_contract_path=C.PREP/'manifests/experiment-contract-amended-io-v1.json'
    C.require(C.sha(old_contract_path)==c['baseline_sha256'][C.rel(old_contract_path)], 'CT5 provenance contract')
    old=C.read(old_contract_path)
    extras={(v['outer'],v['protocol']):v for v in C.read(C.V4/'manifests/reused-post-models.json')}
    choices={(v['outer'],v['target'],v['group'],v['arm']):v for v in C.read(C.V4/'selection/choices.json')}
    expected=pd.read_parquet(C.V4/'predictions/visits.parquet')
    pc=[f'p{i}' for i in range(6)]; maxerr=0.; records=[]
    for r in c['roles']:
        if r['inner'] is not None: continue
        q=C.package(C.rolepath(r)/'query.parquet','query')
        for arm in ['CT0','CT1','CT2','CT3','CT4','StrongPost','CT5']:
            if arm=='CT5':
                v=extras[(r['outer'],r['target'])]; path=ROOT/v['path']; metadata=path.parent/'complete.json'
                C.require(C.sha(path)==old['baseline_sha256'][C.rel(path)],'CT5 original weight seal')
                C.require(C.sha(metadata)==old['baseline_sha256'][C.rel(metadata)],'CT5 directory seal')
                C.require(C.read(metadata)['sha256'][path.name]==C.sha(path),'CT5 directory/weight mismatch')
                origin='historical_directory_complete_json'
            else:
                v=choices[(r['outer'],r['target'],r['group'],arm)]
                actual=v['selected_arm'] if arm=='StrongPost' else arm
                path=C.V4/'models'/r['id']/f'{actual}-t{v["t"]:g}.pt'
                C.require(C.sha(path)==C.read(path.with_suffix('.json'))['sha256'],'CT reference seal')
                origin='individual_model_json'
            model=torch.load(path,map_location=C.device(),weights_only=True)
            z=C.predict(model,q).set_index('visit_id')
            target=expected[expected.outer.eq(r['outer'])&expected.target.eq(r['target'])&expected.group.eq(r['group'])&expected.arm.eq(arm)].set_index('visit_id')
            C.require(set(z.index)==set(target.index),'Reference visit identity')
            err=float(np.max(np.abs(z.loc[target.index,pc].to_numpy()-target[pc].to_numpy())))
            C.require(err<1e-12,'Reference prediction differs from frozen version')
            maxerr=max(maxerr,err)
            records.append({'role_id':r['id'],'arm':arm,'path':C.rel(path),'sha256':C.sha(path),
                            'metadata_origin':origin,'max_probability_error':err})
    C.require(len(records)==420,'Reference replay count')
    write('reference-replay.json',{'passed':True,'models_replayed':420,'probability_max_error':maxerr,
          'CT5_metadata_format_difference_only':True,'new_fits':0,'rows':records})
    progress('report_reference_replay', logical_replays=420,max_error=maxerr)
    return expected


def score(c, ref):
    labels=[]
    for r in c['roles']:
        if r['inner'] is not None: continue
        d=C.package(C.rolepath(r)/'labels.parquet','score').drop(columns='protocol')
        for k in ['outer','target','group']:d[k]=r[k]
        labels.append(d)
    pred=pd.concat([pd.read_parquet(RUN/'predictions/visits.parquet'),ref],ignore_index=True)
    d=pred.merge(pd.concat(labels),on=['outer','target','group','visit_id'],validate='many_to_one')
    C.require(len(d)==14400,'Labeled budget')
    pc=[f'p{i}' for i in range(6)]; scenes=[]; classes=[]; matrices=[]; folds=[]
    for (a,p,g),part in d.groupby(['arm','target','group']):
        C.require(len(part)==120 and part.visit_id.is_unique and part.content_id.nunique()==30,'OOF coverage')
        m,cm,f=C.metrics(C.truths(part),part[pc].to_numpy(),C.MASKS[g]); scenes.append({'arm':a,'target':p,'group':g,**m})
        matrices.append({'arm':a,'target':p,'group':g,'matrix':cm.tolist()})
        for y in range(6):
            tp=int(cm[y,y]); fp=int(cm[:,y].sum()-tp); fn=int(cm[y].sum()-tp)
            classes.append({'arm':a,'target':p,'group':g,'label':C.LABELS[y],'label_index':y,
                'F1':float(f[y]),'precision':tp/(tp+fp) if tp+fp else 0.,
                'recall':tp/(tp+fn) if tp+fn else 0.,'uncovered':y in C.MASKS[g],
                'support':int(cm[y].sum()),'TP':tp,'FP':fp,'FN':fn})
    for (a,p,g,f),part in d.groupby(['arm','target','group','outer']):
        m,_,_=C.metrics(C.truths(part),part[pc].to_numpy(),C.MASKS[g])
        folds.append({'arm':a,'target':p,'group':g,'outer':int(f),**m})
    scenes=pd.DataFrame(scenes); values=['F1_all','F1_uncovered','F1_aux','accuracy','CE_nats','CE_bits','Brier']
    targets=scenes.groupby(['arm','target'])[values].mean().reset_index()
    pooled=scenes.groupby('arm')[values].mean().reset_index().merge(
        targets.groupby('arm').F1_uncovered.min().rename('worst_target_uncovered'),on='arm')
    for name,frame in [('scenarios',scenes),('targets',targets),('pooled',pooled),('classes',pd.DataFrame(classes)),('outer-folds',pd.DataFrame(folds)),('labeled-predictions',d)]:
        save('scores/'+name+'.parquet',frame)
    write('scores/confusion-matrices.json',matrices)
    oldscore=pd.read_parquet(C.V4/'scores/equal-weight-summary.parquet').set_index('arm')
    olderr=max(abs(float(pooled.set_index('arm').loc[a,col])-float(oldscore.loc[a,col]))
               for a in oldscore.index for col in values)
    C.require(olderr<1e-12,'Historical metric replay mismatch')
    write('scores/historical-reproduction.json',{'passed':True,'max_metric_error':olderr})
    arms=sorted(d.arm.unique()); contents=sorted(d.content_id.unique()); groups=list(C.MASKS)
    ai={a:i for i,a in enumerate(arms)}; ui={u:i for i,u in enumerate(contents)}
    cm=np.zeros((len(arms),4,3,30,6,6),dtype=np.int32)
    for (a,p,g,u),part in d.groupby(['arm','target','group','content_id']):
        y=C.truths(part);z=part[pc].to_numpy().argmax(1)
        cm[ai[a],C.PROTOCOLS.index(p),groups.index(g),ui[u]]=np.bincount(y*6+z,minlength=36).reshape(6,6)
    cl=d[['content_id','label_id']].drop_duplicates().set_index('content_id').loc[contents].label_id
    rng=np.random.default_rng(20261007); weights=np.zeros((10000,30),dtype=np.int32)
    for label in C.LABELS:
        ids=np.where(cl.to_numpy()==label)[0];C.require(len(ids)==5,'Content stratum')
        picks=rng.choice(ids,size=(10000,5),replace=True)
        for b in range(10000):weights[b]+=np.bincount(picks[b],minlength=30)
    uu=np.empty((10000,len(arms)));aa=np.empty_like(uu)
    for left in range(0,10000,250):
        cc=np.einsum('bc,apgcyz->bapgyz',weights[left:left+250],cm,optimize=True)
        den=cc.sum(-1)+cc.sum(-2)
        f=np.divide(2*np.diagonal(cc,axis1=-2,axis2=-1),den,out=np.zeros_like(den,dtype=float),where=den>0)
        us=[];aux=[]
        for gi,g in enumerate(groups):
            us.append(np.take(f[:,:,:,gi,:],C.MASKS[g],axis=-1).mean(-1))
            aux.append(np.delete(f[:,:,:,gi,:],C.MASKS[g],axis=-1).mean(-1))
        uu[left:left+250]=np.stack(us,-1).mean((2,3));aa[left:left+250]=np.stack(aux,-1).mean((2,3))
    point=pooled.set_index('arm'); comparisons=[]
    for arm in c['primary_comparators']:
        delta=uu[:,ai['JA1']]-uu[:,ai[arm]]
        comparisons.append({'reference':arm,'delta':float(point.loc['JA1','F1_uncovered']-point.loc[arm,'F1_uncovered']),
            'CI_98_75':np.quantile(delta,[.00625,.99375]).tolist(),
            'CI_95':np.quantile(delta,[.025,.975]).tolist(),'positive_increment':bool(np.quantile(delta,.00625)>0)})
    margins={a:float(point.loc['JA1','F1_aux']-point.loc[a,'F1_aux']) for a in ['StrongPost','CT1','JA2']}
    tt=targets.set_index(['arm','target'])
    worst=min(float(tt.loc[('JA1',p),'F1_aux']-tt.loc[('StrongPost',p),'F1_aux']) for p in C.PROTOCOLS)
    safety=all(v>=-.02 for v in margins.values()) and worst>=-.05
    write('comparisons/primary.json',{'comparisons':comparisons,'family':4,'bootstrap_samples':10000,
          'seed':20261007,'aux_margins':margins,'worst_target_aux_gap':worst,'safety_screen_passed':safety,
          'full_business_claim_passed':all(v['positive_increment'] for v in comparisons[:3]) and safety,
          'structure_claim_passed':comparisons[3]['positive_increment'],
          'model_conditional_not_external_validation':True,'original_pipeline_complete':False})
    np.savez_compressed(DEST/'comparisons/bootstrap.npz',arms=np.asarray(arms),content_ids=np.asarray(contents),weights=weights,uncovered=uu,auxiliary=aa)
    flips=[]
    for (outer,p,g),part in d.groupby(['outer','target','group']):
        a=part[part.arm.eq('JA1')].set_index('visit_id');y=C.truths(a);good=a.prediction.to_numpy()==y
        for reference in ['JA0','JA2','StrongPost','CT1','CT3','CT4','CT5']:
            b=part[part.arm.eq(reference)].set_index('visit_id').loc[a.index]; before=b.prediction.to_numpy()==y
            for j,visit in enumerate(a.index):
                flips.append({'outer':int(outer),'target':p,'group':g,'visit_id':visit,'content_id':a.iloc[j].content_id,
                    'label_id':a.iloc[j].label_id,'uncovered':int(y[j]) in C.MASKS[g],'reference':reference,
                    'reference_correct':bool(before[j]),'JA1_correct':bool(good[j]),
                    'fixed_error':bool(good[j] and not before[j]),'new_error':bool(before[j] and not good[j]),
                    'prediction_changed':bool(a.iloc[j].prediction!=b.iloc[j].prediction)})
    save('scores/error-flips.parquet',pd.DataFrame(flips))
    progress('report_scored',rows=len(d),full_business_claim_passed=all(v['positive_increment'] for v in comparisons[:3]) and safety)


def numerical_and_recovery(c):
    selected=C.choices(); models=0; maps=0; maxg=0.; maxe=0.; maxmap=0.; maxmape=0.
    recovered=[]; coefficients=[]; shapes=[]
    for index,r in enumerate(c['roles']):
        h=C.package(ROOT/r['heldout_visits'],'explain-visits')
        for arm in C.ARMS:
            grid=C.ETAS if r['inner'] is not None else [C.chosen(r,arm,selected)['eta']]
            selected_eta=C.chosen(r,arm,selected)['eta']
            for eta in grid:
                mapper=C.get(C.mappath(r,arm,eta));info=C.read(C.mappath(r,arm,eta).with_suffix('.json'))
                mu,scale=mapper['mu'],mapper['scale']
                if arm=='JA2':
                    pre=C.package(ROOT/r['C_group_pre'],'group-map').copy();post=C.package(ROOT/r['C_group_post'],'group-map').copy()
                    pre[C.HIST]=((C.tensor(pre[C.HIST])-mu)/scale).cpu().numpy()
                    post[C.HIST]=((C.tensor(post[C.HIST])-mu)/scale).cpu().numpy()
                    x=C.tensor(pre[C.HIST]);y,constant=affine.group_targets(pre,post);mass=C.tensor(pre.fit_mass)
                    C.require(not info['exact_visit_identity_used'],'Group identity')
                else:
                    paired=C.package(ROOT/r['C_paired'],'paired-map')
                    x=(C.tensor(paired[['pre_'+v for v in C.HIST]])-mu)/scale
                    y=(C.tensor(paired[['post_'+v for v in C.HIST]])-mu)/scale
                    mass=C.tensor(paired.fit_mass);constant=0.
                mm=mapper['matrix'].clone().requires_grad_();bb=mapper['bias'].clone().requires_grad_()
                objective=((x@mm.T+bb-y).square()*mass[:,None]).sum()/96+constant/96
                objective+=float(mapper['alpha'])*(mm-torch.eye(96,device=C.device(),dtype=torch.float64)).square().sum()/96
                gm,gb=torch.autograd.grad(objective,(mm,bb));mask=torch.ones_like(mm,dtype=torch.bool)
                if arm=='JA0':
                    mask.zero_()
                    for j in range(10):mask[C.block(j),C.block(j)]=True
                    C.require((mm.detach()[~mask]==0).all(),'Block sparsity')
                g=max(float(gm[mask].abs().max()),float(gb.abs().max()))
                error=abs(float(objective.detach())-info['mapping']['objective'])
                C.require(g<=1e-8 and error<1e-10,'Independent map replay')
                maps+=1;maxmap=max(maxmap,g);maxmape=max(maxmape,error)
                slot=C.get(C.slotpath(r,arm,eta))
                ts=C.TS if r['inner'] is not None else [C.chosen(r,arm,selected)['t']]
                for t in ts:
                    path=C.modelpath(r,arm,eta,t);model=C.get(path);log=C.read(path.with_suffix('.json'))['optimizer']
                    C.require(torch.equal(model['mu'],slot['mu']) and torch.equal(model['scale'],slot['scale']),'Classifier coordinate')
                    w=model['weight'].clone().requires_grad_();b=model['bias'].clone().requires_grad_()
                    logits=slot['x']@w.T+b
                    loss=(slot['mass']*(torch.logsumexp(logits,1)-logits.gather(1,slot['y'][:,None]).squeeze(1))).sum()+.0005*(1+t)*w.square().sum()
                    gw,gb=torch.autograd.grad(loss,(w,b));g=max(float(gw.abs().max()),float(gb.abs().max()))
                    error=abs(float(loss.detach())-log['objective'])
                    C.require(g<=1e-5 and error<1e-10 and log['iterations']<2000,'Independent classifier replay')
                    C.require(log['settings']['max_iter']==2000 and log['settings']['max_eval']==10000,'Budget changed')
                    models+=1;maxg=max(maxg,g);maxe=max(maxe,error)
                if eta==selected_eta:
                    xx=(C.tensor(h[['pre_'+v for v in C.HIST]])-mu)/scale
                    yy=(C.tensor(h[['post_'+v for v in C.HIST]])-mu)/scale
                    err=affine.apply(mapper,xx)-yy
                    for j,a in enumerate(h.to_dict('records')):
                        row={k:a[k] for k in ['visit_id','content_id','label_id']}
                        row.update(role_id=r['id'],target=r['target'],calibration=r['calibration'],outer=r['outer'],
                                   inner=r['inner'],group=r['group'],arm=arm,eta=eta,MSE=float(err[j].square().mean()),
                                   coordinate_bias=float(err[j].mean()),test_pre_used_for_classification=False)
                        for k in range(10):row['MSE_'+C.FEATURES[k]]=float(err[j,C.block(k)].square().mean())
                        recovered.append(row)
                    if r['inner'] is None:
                        for j in range(10):
                            for k in range(10):
                                coefficients.append({'role_id':r['id'],'target':r['target'],'group':r['group'],'arm':arm,
                                    'output_block':C.FEATURES[j],'input_block':C.FEATURES[k],
                                    'Frobenius_norm':float(mapper['matrix'][C.block(j),C.block(k)].norm()),'causal_attribution':False})
                        shapes.append({'role_id':r['id'],'target':r['target'],'group':r['group'],'arm':arm,
                                       **C.read(C.slotpath(r,arm,eta).with_suffix('.json'))['shape']})
        if index%20==0:progress('report_numeric_replay',roles=index,models=models,maps=maps)
    C.require(models==34740 and maps==8820,'Independent count')
    write('independent-numeric-audit.json',{'passed':True,'models':models,'maps':maps,
        'classifier_gradient_max':maxg,'classifier_objective_error_max':maxe,
        'mapping_gradient_max':maxmap,'mapping_objective_error_max':maxmape,
        'all_fit_and_inference_CUDA_float64':True,'original_pipeline_verification_created':False})
    save('diagnostics/recovery.parquet',pd.DataFrame(recovered))
    save('diagnostics/cross-block-coefficients.parquet',pd.DataFrame(coefficients))
    save('diagnostics/source-view-shape.parquet',pd.DataFrame(shapes))
    progress('report_numeric_replay_complete',models=models,maps=maps,recovery_rows=len(recovered))


def final_audit(c):
    logs=[]
    for f in (RUN/'models').rglob('*.json'):
        d=C.read(f);l=d['optimizer'];logs.append({'arm':d['arm'],'eta':d['eta'],'t':d['t'],
            'inner': '/i' in d['role_id'],'seconds':l['seconds'],'iterations':l['iterations'],
            'function_evaluations':l['function_evaluations'],'max_gradient':l['max_gradient'],
            'cuda_peak_MiB':l['cuda_peak_MiB'],'accepted':l['accepted'],'device':l['device'],'dtype':l['dtype']})
    save('audit/classifier-fit-summary.parquet',pd.DataFrame(logs))
    # CUDA replay of the already selected new outer classifiers as well as their probability seal.
    expected=pd.read_parquet(RUN/'predictions/visits.parquet'); choices=C.choices();pc=[f'p{i}' for i in range(6)]; err=0.
    for r in c['roles']:
        if r['inner'] is not None:continue
        q=C.package(C.rolepath(r)/'query.parquet','query')
        for arm in C.ARMS:
            v=C.chosen(r,arm,choices);z=C.predict(C.get(C.modelpath(r,arm,v['eta'],v['t'])),q).set_index('visit_id')
            a=expected[expected.outer.eq(r['outer'])&expected.target.eq(r['target'])&expected.group.eq(r['group'])&expected.arm.eq(arm)].set_index('visit_id')
            err=max(err,float(np.max(np.abs(z.loc[a.index,pc].to_numpy()-a[pc].to_numpy()))))
    C.require(err<1e-12,'New prediction replay')
    # Selection, source and terminal-failure artifacts must remain unchanged after this analysis.
    initial=C.read(DEST/'integrity.json')
    C.require(C.sha(RUN/'failure.json')==initial['original_failure_sha256'],'Failure state changed')
    C.require(not (RUN/'completion.json').exists() and not (RUN/'verification.json').exists(),'Unexpected formal completion')
    C.start('report-only-final-source-audit')
    write('complete.json',{'report_analysis_complete':True,'original_pipeline_complete':False,
         'new_fits':0,'time_unix':time.time(),'prediction_replay_max_error':err,
         'original_failure_preserved':True,'scientific_source_changed':False,
         'evidence_builder_sha256':C.sha(Path(__file__)),
         'independent_numeric_audit_passed':C.read(DEST/'independent-numeric-audit.json')['passed']})
    progress('report_evidence_complete', new_fits=0, original_pipeline_complete=False)


if __name__=='__main__':
    C.require(not (DEST/'complete.json').exists(),'Report analysis already complete; preserve it')
    DEST.mkdir(parents=True,exist_ok=True)
    c=C.start('report-only-start');C.require((RUN/'failure.json').exists(),'Expected frozen failed run')
    if '--reuse-hash-audit' in sys.argv:
        old=C.read(DEST/'integrity.json')
        C.require(old['passed'] and old['contract_sha256']==C.sha(RUN/'manifests/experiment-contract.json')
                  and old['prediction_sha256']==C.sha(RUN/'predictions/visits.parquet')
                  and old['original_failure_sha256']==C.sha(RUN/'failure.json'), 'Prior report hash audit changed')
    else:
        integrity(c)
    ref=references(c);score(c,ref);numerical_and_recovery(c);final_audit(c)
