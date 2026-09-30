import time
from .common import *
from .model import Ridge,fit_pool,decode,device,torch

def rows_for_task(task,paired):
    by=paired.set_index('session_id');train=by.loc[task['fit_sessions']].reset_index();query=by.loc[task['query_sessions']].reset_index()
    assert set(train.content_id)==set(task['fit_contents']) and set(query.content_id)==set(task['query_contents'])
    assert not set(train.content_id)&set(query.content_id)
    assert len(train)==72 and len(query)==24
    assert set(train.protocol)==set(query.protocol)=={task['protocol']}
    return train,query

def generate_task(task,paired):
    cfg=config();name=f"{task['protocol']}-f{task['fold']}-i{task['inner_fold']}"
    folder=OUT/'generation'/name;folder.mkdir(parents=True,exist_ok=True)
    if (folder/'complete.json').exists():
        old=read(folder/'complete.json');assert old['contract']==digest(OUT/'contract.json')
        for path,h in old['files'].items():assert digest(path)==h
        return
    started=time.perf_counter();train,query=rows_for_task(task,paired)
    true,pool,ta=fit_pool(train,False);wrong,wrong_pool,wa=fit_pool(train,True)
    torch.save({'true':true.state(),'wrong':wrong.state(),'fit_content_hash':task['fit_content_hash'],'contract':digest(OUT/'contract.json')},folder/'centers.pt')
    pool.to_parquet(folder/'true-pool.parquet',index=False);wrong_pool.to_parquet(folder/'wrong-pool.parquet',index=False)
    (folder/'residual-folds.json').write_text(json.dumps({'true':ta,'wrong':wa},indent=2),encoding='utf-8')
    a=query[[k+'_pre' for k in FEATURES]].to_numpy(float);F=query.F.to_numpy(float)
    centers=true.predict(a,F);wrong_centers=wrong.predict(a,F)
    coordinates=np.log1p(train[[k+'_pre' for k in FEATURES]+['F']].to_numpy(float))
    mean=true.mean.cpu().numpy();scale=true.scale.cpu().numpy()
    coordinates=(coordinates-mean)/scale;qc=(np.log1p(np.column_stack([a,F]))-mean)/scale
    contents=sorted(train.content_id.unique());indices={c:np.flatnonzero(train.content_id.to_numpy()==c) for c in contents}
    centroids=np.stack([coordinates[indices[c]].mean(0) for c in contents]);assert len(contents)==18
    pools={'T2':pool[[f'drift_{k}' for k in FEATURES]].to_numpy(),'T4':pool[[f'residual_{k}' for k in FEATURES]].to_numpy(),'T5':wrong_pool[[f'residual_{k}' for k in FEATURES]].to_numpy()}
    diagnostics=[]
    for seed in cfg['seeds']:
        records=[]
        for qi,source in enumerate(query.to_dict('records')):
            distances=np.linalg.norm(centroids-qc[qi],axis=1);near=np.argsort(distances,kind='stable')[:cfg['neighbor_contents']]
            for view in range(cfg['views']):
                rng_seed=int(object_hash([seed,name,source['session_id'],view])[:16],16)
                for arm in ['T1','T2','T3','T4','T5']:
                    rng=np.random.default_rng(rng_seed);attempts=[];first_raw=None;first_reason='';donor_index=None;last_donor=None
                    allowed=1 if arm in ['T1','T3'] else 1+cfg['max_redraws']
                    for attempt in range(allowed):
                        if arm=='T1':z=np.log1p(a[qi])+true.center
                        elif arm=='T3':z=centers[qi]
                        else:
                            choices=np.arange(len(contents)) if arm=='T2' else near
                            chosen=int(rng.choice(choices));c=contents[chosen];donor_index=int(rng.choice(indices[c]));last_donor=donor_index
                            assert train.iloc[donor_index].content_id not in task['query_contents']
                            base=np.log1p(a[qi]) if arm=='T2' else centers[qi] if arm=='T4' else wrong_centers[qi]
                            z=base+pools[arm][donor_index]
                        raw,rounded,reason=decode(z,F[qi]);attempts.append(reason or 'valid')
                        if attempt==0:first_raw=raw.copy();first_reason=reason
                        if not reason:break
                    fallback=bool(reason);output=a[qi] if fallback else rounded
                    assert not illegal(output,F[qi])
                    donor=pool.iloc[last_donor] if last_donor is not None else None
                    target_donor=(wrong_pool if arm=='T5' else pool).iloc[last_donor] if last_donor is not None else None
                    row={**{k:source[k] for k in ['session_id','content_id','label_id','protocol','repetition']},
                      'outer_fold':task['fold'],'inner_fold':task['inner_fold'],'seed':seed,'view':view,'arm':arm,
                      'fit_content_hash':task['fit_content_hash'],'first_invalid':bool(first_reason),'first_reason':first_reason,
                      'attempt_count':len(attempts),'fallback':fallback,'last_reason':reason,'attempt_reasons_json':json.dumps(attempts),
                      'donor_session_id':None if donor is None else donor.session_id,'donor_content_id':None if donor is None else donor.content_id,
                      'target_donor_session_id':None if target_donor is None else target_donor.target_session_id,
                      'nearest_content_distance':float(distances[near[0]]),'F':int(F[qi])}
                    for j,k in enumerate(FEATURES):row['first_raw_'+k]=float(first_raw[j]);row['last_raw_'+k]=float(raw[j]);row[k]=int(output[j])
                    records.append(row)
        pd.DataFrame(records).to_parquet(folder/f'generated-{seed}.parquet',index=False,compression='zstd')
        diagnostics.append({'seed':seed,'views':len(records),'first_invalid':sum(r['first_invalid'] for r in records),'fallback':sum(r['fallback'] for r in records)})
    result={'contract':digest(OUT/'contract.json'),'fit_contents':task['fit_contents'],'query_contents':task['query_contents'],
      'cuda':True,'dtype':'float64','ridge_fits':38,'seconds':time.perf_counter()-started,'diagnostics':diagnostics,
      'files':{str(p):digest(p) for p in folder.iterdir() if p.is_file()}}
    (folder/'complete.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(name,'done',round(result['seconds'],2),'seconds',flush=True)

def report_gate():
    paths=sorted((OUT/'generation').glob('*/generated-*.parquet'));assert len(paths)==120
    samples=save('training-oof-synthetic',pd.concat([pd.read_parquet(p) for p in paths],ignore_index=True))
    assert len(samples)==115200 and not samples.duplicated(['protocol','outer_fold','seed','arm','session_id','view']).any()
    assert samples.groupby(['protocol','outer_fold','seed','arm']).size().eq(96*8).all()
    rows=[]
    for (dep,arm),g in samples.groupby(['protocol','arm']):
        rows.append({'protocol':dep,'arm':arm,'source_views':len(g),'first_invalid_rate':float(g.first_invalid.mean()),
            'fallback_rate':float(g.fallback.mean()),'mean_attempts':float(g.attempt_count.mean()),
            'gate_passed':bool(g.first_invalid.mean()<=config()['first_invalid_gate'] and g.fallback.mean()<=config()['fallback_gate'])})
    summary=save('legality-summary',rows)
    save('legality-by-fold-seed',samples.groupby(['protocol','outer_fold','seed','arm']).agg(first_invalid_rate=('first_invalid','mean'),fallback_rate=('fallback','mean')).reset_index())
    save('legality-by-business',samples.groupby(['protocol','arm','label_id']).agg(first_invalid_rate=('first_invalid','mean'),fallback_rate=('fallback','mean')).reset_index())
    reasons=save('first-invalid-reasons',samples[samples.first_invalid].groupby(['protocol','arm','first_reason']).size().rename('source_views').reset_index())
    passed=bool(summary.gate_passed.all())
    gate={'stage':'F5','passed':passed,'thresholds':{'first_invalid_rate':.1,'fallback_rate':.01},
      'scope':'deployment_arm_pooled_outer_train_oof','classification_started':False,'outer_test_pre_used':False,
      'generated_source_views':len(samples),'independent_visits':240,'independent_contents':30,
      'cuda':True,'failed_arms':summary[~summary.gate_passed][['protocol','arm']].to_dict('records')}
    js('stage-gate.json',gate)
    txt='# F4–F5 前向漂移：训练OOF生成与合法性门\n\n40个训练内生成任务全部完成；仅使用各外层训练内容。每任务72访问拟合，24访问生成，LOCO残差不见对应内容；未读取外层测试pre进行生成，未训练业务分类器。\n\n所有Ridge拟合、条件中心预测均CUDA float64；中心中位数在CUDA计算。采样、整数解码及审计在CPU。\n\n## 冻结门限\n\n按每部署×臂汇总全部训练OOF视图：首次非法率不得超过10%，最终fallback率不得超过1%。门限和汇总口径先于结果冻结。\n\n'+table(summary)
    txt+='\n\nT1固定中心；T2无条件联合漂移；T3条件中心；T4真配条件联合残差；T5错配同机制。确定性臂复制8视图仅保持预算，不增加独立样本量；全部115200行重复使用相同240访问/30内容。\n\n## 首次失败原因\n\n'+table(reasons)
    txt+='\n\n输出保存first_raw、last_raw、整数结果及每次尝试的原因；最多32次重抽，仍失败显式回退原pre，不逐维裁剪。未将fallback标志作为分类特征。中间重抽的原始六维向量未全部持久化，可由固定输入、seed与代码重放。\n\n## 阶段结论\n\n'+('通过，可继续F6–F10。' if passed else '**未通过：按预声明停止，不启动F6测试侧生成和F7分类，不修改阈值、不删失败臂。需要用户确认是否改用支持合法联合约束的参数化。**')
    txt+='\n\n失败说明当前坐标加法采样不保证必要摘要约束，不证明代理变换不可学习，也没有产生新的分类收益数字。\n'
    (DOC/'generation-legality-report.md').write_text(txt,encoding='utf-8')
    drift=load('observed-drifts');summary_drift=drift.groupby(['protocol','feature']).agg(visits=('session_id','size'),median_difference=('difference','median'),median_log1p_difference=('log1p_difference','median'),q10_difference=('difference',lambda x:x.quantile(.1)),q90_difference=('difference',lambda x:x.quantile(.9))).reset_index()
    save('observed-drift-summary',summary_drift)
    (DOC/'drift-description.md').write_text('# 访问级有向漂移描述\n\n以下为240访问的描述性测量，不作为训练参数或模型选择；R为连接内方向段之和，不是旧FR。\n\n'+table(summary_drift)+'\n\n原始单位差、严格正值log-ratio及log1p差分别保存在observed-drifts.parquet。本轮尚未获得外层测试生成质量或分类结论。\n',encoding='utf-8')
    print(summary.to_string(index=False),flush=True)
    if not passed:raise StageGate('F5 legality failed. Preserve all arms and ask user before changing parameterization.')

def run():
    assert read(OUT/'stage-gate.json')['stage'] in ['F3','F5']
    device();primitive=load('paired-primitives');keys=['session_id','content_id','protocol','label_id','repetition','F']
    paired=primitive[primitive.side=='pre'][keys+FEATURES].merge(primitive[primitive.side=='post'][keys+FEATURES],on=keys,suffixes=('_pre','_post'),validate='one_to_one')
    tasks=read(OUT/'generation-tasks.json');assert len(tasks)==40
    js('runtime.json',{'device':torch.cuda.get_device_name(),'torch':torch.__version__,'cuda':torch.version.cuda,'ridge_dtype':'float64','ridge_fits_planned':1520,'classification_fits':0})
    for i,task in enumerate(tasks):
        generate_task(task,paired)
        js('progress.json',{'stage':'F5','completed':i+1,'total':40,'classification_started':False})
    report_gate()
