"""F6-F10: independent additive contract, held-out generation and CUDA classifiers."""
import sys,os,time,argparse
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'src'))
from proxy_analysis.conditional_drift.common import *
from proxy_analysis.conditional_drift.model import Ridge,fit_pool,decode,device,torch
from proxy_analysis.crosscontent.record_time_business.formal_report import scores

NAMES=['macro_f1','balanced_accuracy','ce_bits','brier']
PRED=[f'p{i}' for i in range(6)]
PHASE=OUT/'phase2'

def freeze_phase2():
    assert read(OUT/'stage-gate.json')['passed'] and read(OUT/'stage-gate.json')['stage']=='F5'
    old=read(OUT/'contract.json')
    for path,h in old['inputs'].items():assert digest(path)==h,'Old frozen input changed'
    PHASE.mkdir(exist_ok=True)
    files=[Path(__file__),OUT/'contract.json',OUT/'stage-gate.json',OUT/'training-oof-synthetic.parquet',OUT/'paired-primitives.parquet',OUT/'outer-folds.parquet',CONFIG]
    obj={'inputs':{str(p):digest(p) for p in files},'device':'cuda','classification_tasks':210,'steps':1000,'inference_side':'post_only','tuning':False}
    if (PHASE/'contract.json').exists():assert read(PHASE/'contract.json')==obj,'Phase2 contract changed'
    else:(PHASE/'contract.json').write_text(json.dumps(obj,indent=2),encoding='utf-8')

def record(path,obj):
    path=Path(path);tmp=path.with_suffix('.tmp');tmp.write_text(json.dumps(obj,indent=2,ensure_ascii=False,allow_nan=False),encoding='utf-8');tmp.replace(path)

def paired_table():
    primitive=load('paired-primitives');keys=['session_id','content_id','protocol','label_id','repetition','F']
    return primitive[primitive.side=='pre'][keys+FEATURES].merge(primitive[primitive.side=='post'][keys+FEATURES],on=keys,suffixes=('_pre','_post'),validate='one_to_one')

def synthesize(train,query,models,pools,name):
    cfg=config();a=query[[k+'_pre' for k in FEATURES]].to_numpy(float);F=query.F.to_numpy(float)
    centers={key:model.predict(a,F) for key,model in models.items()}
    true=models['true'];mean=true.mean.cpu().numpy();scale=true.scale.cpu().numpy()
    coordinates=(np.log1p(train[[k+'_pre' for k in FEATURES]+['F']].to_numpy(float))-mean)/scale
    qc=(np.log1p(np.column_stack([a,F]))-mean)/scale
    contents=sorted(train.content_id.unique());indices={c:np.flatnonzero(train.content_id.to_numpy()==c) for c in contents}
    centroids=np.stack([coordinates[indices[c]].mean(0) for c in contents]);assert len(contents)==24
    values={'T2':pools['true'][[f'drift_{k}' for k in FEATURES]].to_numpy(),
            'T4':pools['true'][[f'residual_{k}' for k in FEATURES]].to_numpy(),
            'T5':pools['wrong'][[f'residual_{k}' for k in FEATURES]].to_numpy()}
    records=[];fit_hash=object_hash(contents)
    for seed in cfg['seeds']:
      for qi,source in enumerate(query.to_dict('records')):
        distances=np.linalg.norm(centroids-qc[qi],axis=1);near=np.argsort(distances,kind='stable')[:cfg['neighbor_contents']]
        for view in range(cfg['views']):
          rng_seed=int(object_hash([seed,name,source['session_id'],view])[:16],16)
          for arm in ['T1','T2','T3','T4','T5']:
            rng=np.random.default_rng(rng_seed);donor_index=None;attempts=[]
            for attempt in range(1 if arm in ['T1','T3'] else 1+cfg['max_redraws']):
                if arm=='T1':z=np.log1p(a[qi])+true.center
                elif arm=='T3':z=centers['true'][qi]
                else:
                    selected=int(rng.choice(np.arange(len(contents)) if arm=='T2' else near))
                    donor_index=int(rng.choice(indices[contents[selected]]))
                    base=np.log1p(a[qi]) if arm=='T2' else centers['true' if arm=='T4' else 'wrong'][qi]
                    z=base+values[arm][donor_index]
                raw,rounded,reason=decode(z,F[qi]);attempts.append(reason or 'valid')
                if attempt==0:first_raw=raw.copy();first_reason=reason
                if not reason:break
            output=a[qi] if reason else rounded;assert not illegal(output,F[qi])
            pool=pools['wrong' if arm=='T5' else 'true'];donor=None if donor_index is None else pool.iloc[donor_index]
            row={**{k:source[k] for k in ['session_id','content_id','label_id','protocol','repetition']},'seed':seed,'view':view,'arm':arm,'F':int(F[qi]),
                 'fit_content_hash':fit_hash,'first_invalid':bool(first_reason),'first_reason':first_reason,'fallback':bool(reason),
                 'attempt_count':len(attempts),'attempt_reasons_json':json.dumps(attempts),'nearest_content_distance':float(distances[near[0]]),
                 'donor_session_id':None if donor is None else donor.session_id,'donor_content_id':None if donor is None else donor.content_id,
                 'target_donor_session_id':None if donor is None else donor.target_session_id}
            for j,k in enumerate(FEATURES):row['first_raw_'+k]=float(first_raw[j]);row['last_raw_'+k]=float(raw[j]);row[k]=int(output[j])
            records.append(row)
    return pd.DataFrame(records)

def quality():
    paired=paired_table().set_index('session_id');folds=load('outer-folds');frames=[];quality_rows=[];joint=[];all_truth=[]
    for dep in config()['deployments']:
      for fold in range(5):
        f=folds[(folds.protocol==dep)&(folds.fold==fold)]
        train=paired.loc[f[f.split=='train'].session_id].reset_index();query=paired.loc[f[f.split=='test'].session_id].reset_index()
        assert len(train)==96 and len(query)==24 and not set(train.content_id)&set(query.content_id)
        folder=PHASE/f'quality-{dep}-f{fold}';folder.mkdir(exist_ok=True)
        if (folder/'complete.json').exists():
            done=read(folder/'complete.json');assert done['contract']==digest(PHASE/'contract.json')
            assert digest(folder/'samples.parquet')==done['samples_sha256']
            samples=pd.read_parquet(folder/'samples.parquet')
            scaler=read(folder/'scaler.json')
        else:
            models={};pools={};audits={}
            for kind,wrong in [('true',False),('wrong',True)]:models[kind],pools[kind],audits[kind]=fit_pool(train,wrong)
            torch.save({k:m.state() for k,m in models.items()},folder/'centers.pt')
            for k,p in pools.items():p.to_parquet(folder/(k+'-pool.parquet'),index=False)
            record(folder/'residual-folds.json',audits)
            scaler={'mean':models['true'].mean.cpu().tolist(),'scale':models['true'].scale.cpu().tolist(),'fit_sessions':train.session_id.tolist()}
            record(folder/'scaler.json',scaler)
            samples=synthesize(train,query,models,pools,f'quality-{dep}-f{fold}');samples['outer_fold']=fold
            samples.to_parquet(folder/'samples.parquet',index=False)
            record(folder/'complete.json',{'contract':digest(PHASE/'contract.json'),'samples_sha256':digest(folder/'samples.parquet'),'cuda':True,'ridge_fits':50,'classifier_input':False})
        frames.append(samples)
        scale=np.array(scaler['scale'])[:6];cuts=np.quantile(np.log1p(train.U_up_pre+train.U_down_pre),[.25,.5,.75])
        for source in query.to_dict('records'):
            sid=source['session_id'];truth=np.array([source[k+'_post'] for k in FEATURES]);original=np.array([source[k+'_pre'] for k in FEATURES])
            all_truth.append({**source,'outer_fold':fold})
            for seed in config()['seeds']:
              for arm in ['T0','T1','T2','T3','T4','T5']:
                g=samples[(samples.session_id==sid)&(samples.seed==seed)&(samples.arm==arm)]
                s=np.repeat(original[None,:],8,axis=0) if arm=='T0' else g[FEATURES].to_numpy(float)
                assert s.shape==(8,6)
                normalized=np.log1p(s)/scale;t=np.log1p(truth)/scale
                energy=np.linalg.norm(normalized-t,axis=1).mean()-.5*np.linalg.norm(normalized[:,None,:]-normalized[None,:,:],axis=2).mean()
                base={'protocol':dep,'outer_fold':fold,'seed':seed,'arm':arm,'session_id':sid,'content_id':source['content_id'],'label_id':source['label_id'],
                    'load_bin':int(np.searchsorted(cuts,np.log1p(original[:2].sum()),side='right'))}
                joint.append({**base,'energy_score':float(energy)})
                for j,k in enumerate(FEATURES):
                    raw=s[:,j];v=normalized[:,j];y=t[j];lo,hi=np.quantile(raw,[.1,.9])
                    crps=np.abs(v-y).mean()-.5*np.abs(v[:,None]-v[None,:]).mean()
                    raw_crps=np.abs(raw-truth[j]).mean()-.5*np.abs(raw[:,None]-raw[None,:]).mean()
                    quality_rows.append({**base,'feature':k,'true_post':float(truth[j]),'synthetic_mean':float(raw.mean()),'synthetic_median':float(np.median(raw)),
                      'raw_mae_of_median':float(abs(np.median(raw)-truth[j])),'log_mae_of_median':float(abs(np.log1p(np.median(raw))-np.log1p(truth[j]))),
                      'scaled_log_crps':float(crps),'raw_crps':float(raw_crps),'q10':float(lo),'q90':float(hi),'covered80':bool(lo<=truth[j]<=hi),
                      'interval_width80':float(hi-lo),'sample_iqr':float(np.quantile(raw,.75)-np.quantile(raw,.25))})
        print('F6',dep,fold,flush=True)
    save('test-synthetic-offline',pd.concat(frames,ignore_index=True));save('test-truth-offline',pd.DataFrame(all_truth))
    q=save('quality-per-visit-feature',pd.DataFrame(quality_rows));j=save('quality-energy-per-visit',pd.DataFrame(joint))
    save('quality-summary',q.groupby(['protocol','arm'])[['scaled_log_crps','covered80','log_mae_of_median']].mean().reset_index().merge(j.groupby(['protocol','arm']).energy_score.mean().reset_index(),on=['protocol','arm']))
    save('quality-by-business',q.groupby(['protocol','arm','label_id','feature'])[['scaled_log_crps','covered80','raw_mae_of_median']].mean().reset_index())
    save('quality-by-load',q.groupby(['protocol','arm','load_bin','feature'])[['scaled_log_crps','covered80','raw_mae_of_median']].mean().reset_index())

def schedule(train,seed):
    rng=np.random.default_rng(seed);contents=sorted(train.content_id.unique());rng.shuffle(contents)
    indices={c:np.flatnonzero(train.content_id.to_numpy()==c) for c in contents};result=[]
    for step in range(1000):
        block=contents[(step%4)*6:(step%4+1)*6]
        result.append(np.concatenate([indices[c] for c in block]))
    a=np.stack(result);assert a.shape==(1000,24) and np.bincount(a.ravel(),minlength=96).tolist()==[250]*96
    return a,rng.integers(0,8,(1000,24))

def predict_post(head,post_array,mean,scale,dev):
    """Only a numeric post matrix enters this prediction interface."""
    assert post_array.ndim==2 and post_array.shape[1]==7
    head.eval()
    with torch.no_grad():
        x=torch.tensor((np.log1p(post_array)-mean)/scale,device=dev,dtype=torch.float32)
        prob=head(x).softmax(1);assert prob.is_cuda and torch.isfinite(prob).all()
        return prob.cpu().numpy()

def classify():
    assert read(OUT/'stage-gate.json')['passed']
    primitive=load('paired-primitives');folds=load('outer-folds');synthetic=load('training-oof-synthetic');labels=sorted(primitive.label_id.unique())
    numeric=FEATURES+['F'];completed=0
    for dep in config()['deployments']:
      for fold in range(5):
        f=folds[(folds.protocol==dep)&(folds.fold==fold)]
        tr=f[f.split=='train'].sort_values(['content_id','repetition']).reset_index(drop=True)
        te=f[f.split=='test'].sort_values(['content_id','repetition']).reset_index(drop=True)
        assert len(tr)==96 and len(te)==24 and not set(tr.content_id)&set(te.content_id)
        pre=primitive[primitive.side=='pre'].set_index('session_id').loc[tr.session_id,numeric].to_numpy(float)
        post=primitive[primitive.side=='post'].set_index('session_id').loc[tr.session_id,numeric].to_numpy(float)
        test_post=primitive[primitive.side=='post'].set_index('session_id').loc[te.session_id,numeric].to_numpy(float)
        mean=np.log1p(pre).mean(0);scale=np.log1p(pre).std(0);scale[scale<1e-10]=1
        for seed in config()['seeds']:
          batches,views=schedule(tr,seed)
          for arm in [f'T{i}' for i in range(7)]:
            name=f'{dep}-f{fold}-s{seed}-{arm}';folder=PHASE/name;folder.mkdir(exist_ok=True)
            if (folder/'complete.json').exists():
                old=read(folder/'complete.json');assert old['contract']==digest(PHASE/'contract.json')
                assert digest(folder/'head.pt')==old['checkpoint_sha256'] and digest(folder/'predictions.parquet')==old['predictions_sha256']
                completed+=1;continue
            dev=device();torch.manual_seed(seed);head=torch.nn.Sequential(torch.nn.Linear(7,32),torch.nn.ReLU(),torch.nn.Linear(32,6)).to(dev)
            initial=object_hash({n:p.detach().cpu().tolist() for n,p in head.named_parameters()})
            if arm in ['T0','T6']:arr=np.repeat((pre if arm=='T0' else post)[:,None,:],8,axis=1)
            else:
                g=synthetic[(synthetic.protocol==dep)&(synthetic.outer_fold==fold)&(synthetic.seed==seed)&(synthetic.arm==arm)].set_index(['session_id','view'])
                assert len(g)==768 and set(g.index.get_level_values(0))==set(tr.session_id)
                arr=np.stack([g.loc[sid].sort_index()[numeric].to_numpy(float) for sid in tr.session_id])
            assert arr.shape==(96,8,7)
            x=torch.tensor((np.log1p(arr)-mean)/scale,device=dev,dtype=torch.float32)
            y=torch.tensor([labels.index(v) for v in tr.label_id],device=dev)
            ix=torch.tensor(batches,device=dev);vi=torch.tensor(views,device=dev)
            opt=torch.optim.Adam(head.parameters(),lr=.001);head.train();history=[];started=time.perf_counter()
            for step in range(1000):
                opt.zero_grad(set_to_none=True);ce=torch.nn.functional.cross_entropy(head(x[ix[step],vi[step]]),y[ix[step]])
                loss=ce+.5*1e-4*sum(p.square().sum() for n,p in head.named_parameters() if n.endswith('weight'))
                assert torch.isfinite(loss);loss.backward();opt.step()
                history.append({'step':step+1,'loss':float(loss.detach()),'ce_nats':float(ce.detach())})
            prob=predict_post(head,test_post,mean,scale,dev)
            rows=[]
            for r,v in zip(te.to_dict('records'),prob):rows.append({**r,'arm':arm,'seed':seed,'target':labels.index(r['label_id']),'prediction':int(v.argmax()),**dict(zip(PRED,v.tolist()))})
            pd.DataFrame(rows).to_parquet(folder/'predictions.parquet',index=False)
            pd.DataFrame(history).to_parquet(folder/'training-log.parquet',index=False)
            torch.save({'head':head.state_dict(),'mean':mean,'scale':scale,'labels':labels,'train_sessions':tr.session_id.tolist(),'test_sessions':te.session_id.tolist(),
                        'contract':digest(PHASE/'contract.json'),'initial_head_hash':initial,'schedule_hash':object_hash([batches.tolist(),views.tolist()])},folder/'head.pt')
            torch.cuda.synchronize();record(folder/'complete.json',{'contract':digest(PHASE/'contract.json'),'steps':1000,'cuda':True,'test_pre':False,
                'seconds':time.perf_counter()-started,'checkpoint_sha256':digest(folder/'head.pt'),'predictions_sha256':digest(folder/'predictions.parquet')})
            completed+=1;record(PHASE/'progress.json',{'completed':completed,'total':210,'status':'running'})
            print('F7',name,completed,'/210',flush=True)
    record(PHASE/'progress.json',{'completed':210,'total':210,'status':'complete'})

def report():
    paths=sorted(PHASE.glob('*-s*-T*/predictions.parquet'));assert len(paths)==210
    p=save('classification-oof',pd.concat([pd.read_parquet(path) for path in paths],ignore_index=True));assert len(p)==5040
    assert not p.duplicated(['protocol','arm','seed','session_id']).any()
    metrics=[];arrays={};cohort=load('cohort');seeds=config()['seeds'];arms=[f'T{i}' for i in range(7)]
    for (dep,arm,seed),g in p.groupby(['protocol','arm','seed']):
        g=g.sort_values('session_id');v=g[PRED].to_numpy();arrays[dep,arm,seed]=v
        metrics.append({'protocol':dep,'arm':arm,'seed':seed,**dict(zip(NAMES,scores(g.target,v)))})
    metrics=save('classification-metrics-by-seed',pd.DataFrame(metrics));avg=metrics.groupby(['protocol','arm'])[NAMES].mean()
    summary=save('classification-summary',avg.reset_index());draws=[];contrasts=[('T4',f'T{i}') for i in range(6) if i!=4]
    label_order=sorted(cohort.label_id.unique());groups=[sorted(cohort[cohort.label_id==l].content_id.unique()) for l in label_order]
    rng=np.random.default_rng(20260926)
    # One content draw is shared across both deployments, all seeds and all arms.
    for draw in range(2000):
        selected=[c for group in groups for c in rng.choice(group,len(group),replace=True)]
        counts={c:selected.count(c) for c in set(selected)}
        for dep in config()['deployments']:
            order=cohort[cohort.protocol==dep].sort_values('session_id');w=np.array([counts.get(c,0) for c in order.content_id]);target=np.array([label_order.index(l) for l in order.label_id])
            vals={a:np.mean([scores(target,arrays[dep,a,s],w) for s in seeds],axis=0) for a in arms}
            for a,b in contrasts:draws.append({'draw':draw,'protocol':dep,'arm':a,'reference':b,**dict(zip(NAMES,(vals[a]-vals[b])*[1,1,-1,-1]))})
    draws=save('classification-bootstrap',pd.DataFrame(draws));gains=[];changes=[]
    for dep in config()['deployments']:
      for a,b in contrasts:
        d=draws[(draws.protocol==dep)&(draws.arm==a)&(draws.reference==b)];row={'protocol':dep,'arm':a,'reference':b}
        for metric,sign in zip(NAMES,[1,1,-1,-1]):row[metric+'_gain']=float(sign*(avg.loc[(dep,a),metric]-avg.loc[(dep,b),metric]));row[metric+'_low']=d[metric].quantile(.025);row[metric+'_high']=d[metric].quantile(.975)
        gains.append(row)
        for seed in seeds:
            aa=p[(p.protocol==dep)&(p.arm==a)&(p.seed==seed)].sort_values('session_id');bb=p[(p.protocol==dep)&(p.arm==b)&(p.seed==seed)].sort_values('session_id')
            ca=aa.prediction.to_numpy()==aa.target.to_numpy();cb=bb.prediction.to_numpy()==bb.target.to_numpy()
            changes.append({'protocol':dep,'arm':a,'reference':b,'seed':seed,'corrected':int((ca&~cb).sum()),'new_error':int((~ca&cb).sum())})
    gains=save('classification-gains',pd.DataFrame(gains));save('classification-decision-changes',pd.DataFrame(changes))
    recalls=save('classification-recall',p.assign(correct=p.prediction==p.target).groupby(['protocol','arm','seed','label_id']).correct.mean().rename('recall').reset_index())
    (DOC/'business-results.md').write_text('# F7–F8 真实post上的业务用途\n\n210/210个统一七维MLP完成。合成分类训练数据来自训练内容OOF生成，测试仅真实post摘要。T0原pre、T1固定中心、T2无条件联合漂移、T3条件中心、T4真配条件残差、T5错配条件残差、T6真实post监督。\n\n## 三seed均值\n\n'+table(summary)+'\n\n## 逐seed\n\n'+table(metrics)+'\n\n## 固定对照\n\n正值表示改善，CE为bits。2000次按业务分层的内容bootstrap，跨部署/臂/seed共同重采。区间条件于固定模型、未作多重比较校正；跨零不是等效。\n\n'+table(gains)+'\n\n没有新增独立内容，也没有证明节省目标post抓包或标签；生成器使用了真实配对校准数据。本轮七维摘要MLP不与旧R+T序列网络做公平方法排名。\n',encoding='utf-8')
    print(summary.to_string(index=False),flush=True)

def verify():
    primitive=load('paired-primitives');checks=[];initials={};schedules={}
    for folder in sorted(PHASE.glob('*-s*-T*')):
        done=read(folder/'complete.json');assert done['cuda'] and not done['test_pre'] and done['steps']==1000
        state=torch.load(folder/'head.pt',map_location=device(),weights_only=False)
        assert state['contract']==digest(PHASE/'contract.json')
        pred=pd.read_parquet(folder/'predictions.parquet');key=(pred.protocol.iloc[0],int(pred.fold.iloc[0]),int(pred.seed.iloc[0]))
        initials.setdefault(key,state['initial_head_hash']);schedules.setdefault(key,state['schedule_hash'])
        assert initials[key]==state['initial_head_hash'] and schedules[key]==state['schedule_hash']
        assert not set(state['train_sessions'])&set(state['test_sessions'])
        train=load('cohort').set_index('session_id').loc[state['train_sessions']];test=load('cohort').set_index('session_id').loc[state['test_sessions']]
        assert not set(train.content_id)&set(test.content_id)
        head=torch.nn.Sequential(torch.nn.Linear(7,32),torch.nn.ReLU(),torch.nn.Linear(32,6)).to(device());head.load_state_dict(state['head'])
        post=primitive[primitive.side=='post'].set_index('session_id').loc[pred.session_id,FEATURES+['F']].to_numpy(float)
        actual=np.concatenate([predict_post(head,post[i:i+6],state['mean'],state['scale'],device()) for i in range(0,24,6)])
        expected=pred[PRED].to_numpy();np.testing.assert_allclose(actual,expected,atol=2e-5,rtol=2e-4)
        assert np.array_equal(actual.argmax(1),pred.prediction)
        checks.append({'job':folder.name,'cuda':True,'same_decisions':True,'content_disjoint':True,'max_probability_delta':float(np.abs(actual-expected).max())})
    assert len(checks)==210;save('classification-replay-audit',pd.DataFrame(checks))
    record(PHASE/'completion.json',{'tasks':210,'cuda':True,'all_replays_passed':True,'max_probability_delta':max(r['max_probability_delta'] for r in checks),'contract':digest(PHASE/'contract.json')})
    print('F9 audit passed: 210 classifiers',flush=True)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--stage',choices=['quality','classify','report','verify','all'],default='all');arg=parser.parse_args()
    freeze_phase2()
    if arg.stage in ['quality','all']:quality()
    if arg.stage in ['classify','all']:classify()
    if arg.stage in ['report','all']:report()
    if arg.stage in ['verify','all']:verify()
