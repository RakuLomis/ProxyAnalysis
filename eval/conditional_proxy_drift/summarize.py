"""F10 read-only lineage/distribution audits and scientific figures."""
from phase2 import *
from scipy.stats import wasserstein_distance

def audit_lineage():
    tasks=read(OUT/'generation-tasks.json');samples=load('training-oof-synthetic');checks=[]
    for task in tasks:
        name=f"{task['protocol']}-f{task['fold']}-i{task['inner_fold']}";folder=OUT/'generation'/name
        done=read(folder/'complete.json');assert done['contract']==digest(OUT/'contract.json')
        for path,h in done['files'].items():assert digest(path)==h
        g=samples[(samples.protocol==task['protocol'])&(samples.outer_fold==task['fold'])&(samples.inner_fold==task['inner_fold'])]
        assert len(g)==2880 and set(g.session_id)==set(task['query_sessions'])
        assert set(g.fit_content_hash)=={task['fit_content_hash']}
        assert not set(task['fit_contents'])&set(g.content_id)
        selected=g[g.donor_session_id.notna()]
        assert set(selected.donor_session_id).issubset(set(task['fit_sessions']))
        assert set(selected.target_donor_session_id).issubset(set(task['fit_sessions']))
        assert not (selected.content_id==selected.donor_content_id).any()
        aud=read(folder/'residual-folds.json')
        for kind,rows in aud.items():
            assert len(rows)==18
            for row in rows:assert row['held_content'] not in row['fit_contents'] and row['cuda']
        for kind in ['true','wrong']:
            pool=pd.read_parquet(folder/(kind+'-pool.parquet'));assert set(pool.session_id)==set(task['fit_sessions'])
            lookup=pool.set_index('session_id').content_id
            assert (pool.target_session_id.map(lookup)==pool.content_id).all()
            assert (pool.target_session_id==pool.session_id).all() if kind=='true' else (pool.target_session_id!=pool.session_id).all()
        checks.append({'task':name,'source_unseen_to_generator':True,'residual_content_oof':True,'same_deployment':True,'cuda':True})
    assert len(checks)==40;save('lineage-audit',pd.DataFrame(checks))
    js('lineage-audit.json',{'tasks':40,'all_passed':True,'model_dtype':'float64','classification_test_pre':False})

def distributions():
    samples=load('test-synthetic-offline');truth=load('test-truth-offline');rows=[];corr=[]
    for (dep,arm,seed),g in samples.groupby(['protocol','arm','seed']):
        actual=truth[truth.protocol==dep].set_index('session_id').loc[sorted(g.session_id.unique())]
        x=g[FEATURES].to_numpy(float);y=actual[[k+'_post' for k in FEATURES]].to_numpy(float)
        cx=np.corrcoef(np.log1p(x),rowvar=False);cy=np.corrcoef(np.log1p(y),rowvar=False)
        corr.append({'protocol':dep,'arm':arm,'seed':seed,'log_correlation_frobenius':float(np.linalg.norm(cx-cy))})
        for j,k in enumerate(FEATURES):
            for label in ['ALL',*sorted(actual.label_id.unique())]:
                xx=x[:,j] if label=='ALL' else g[g.label_id==label][k].to_numpy(float)
                yy=y[:,j] if label=='ALL' else actual[actual.label_id==label][k+'_post'].to_numpy(float)
                rows.append({'protocol':dep,'arm':arm,'seed':seed,'label_id':label,'feature':k,
                   'log_wasserstein':float(wasserstein_distance(np.log1p(xx),np.log1p(yy))),
                   'synthetic_mean':float(xx.mean()),'real_mean':float(yy.mean()),'synthetic_std':float(xx.std()),'real_std':float(yy.std()),
                   'synthetic_q10':float(np.quantile(xx,.1)),'real_q10':float(np.quantile(yy,.1)),
                   'synthetic_q90':float(np.quantile(xx,.9)),'real_q90':float(np.quantile(yy,.9))})
    save('distribution-by-business',pd.DataFrame(rows));save('joint-correlation-difference',pd.DataFrame(corr))
    legality=samples.groupby(['protocol','arm']).agg(first_invalid_rate=('first_invalid','mean'),fallback_rate=('fallback','mean'),nearest_content_distance=('nearest_content_distance','mean')).reset_index()
    save('test-legality-diagnostic',legality)
    q=load('quality-summary')
    (DOC/'generation-quality-report.md').write_text('# F6 外层留出内容：生成质量\n\n仅在外层训练24内容拟合；测试pre只用于本离线生成诊断，不进入分类器训练或推理。两部署各120访问，每个随机模型每源访问8视图、三个seed；不增加独立内容。\n\n'+table(q)+'\n\nscaled_log_crps及energy_score越低越好，采用外层训练pre标准差缩放。covered80是8样本10/90分位区间的经验覆盖率；确定性模型区间退化，不能将此指标误解为其未训练的概率校准目标。\n\n## 测试合法性（不回流选模型）\n\n'+table(legality)+'\n\n## 联合结构\n\n'+table(pd.DataFrame(corr).groupby(['protocol','arm']).log_correlation_frobenius.mean().reset_index())+'\n\n相关结构只比较所选六维log摘要，不是序列或协议合法性。业务/负载分层CRPS与原始单位MAE已保存；全部业务分层均值、方差、尾分位与边缘Wasserstein见distribution-by-business.parquet。边缘距离不是实际对应误差。\n',encoding='utf-8')

def figures():
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    dest=DOC/'figures';dest.mkdir(exist_ok=True)
    m=load('classification-metrics-by-seed');q=load('quality-summary')
    fig,axes=plt.subplots(2,2,figsize=(12,8),layout='constrained')
    for i,dep in enumerate(config()['deployments']):
        for j,metric in enumerate(['macro_f1','ce_bits']):
            for seed,g in m[m.protocol==dep].groupby('seed'):
                g=g.sort_values('arm');axes[i,j].plot(g.arm,g[metric],marker='o',label=str(seed))
            axes[i,j].set_title(dep);axes[i,j].set_ylabel(metric);axes[i,j].grid(alpha=.2);axes[i,j].legend()
    fig.savefig(dest/'business-by-seed.png',dpi=160);plt.close(fig)
    fig,axes=plt.subplots(1,2,figsize=(11,4),layout='constrained')
    for ax,metric in zip(axes,['scaled_log_crps','energy_score']):
        for dep,g in q.groupby('protocol'):ax.plot(g.arm,g[metric],marker='o',label=dep)
        ax.set_ylabel(metric+' (lower is better)');ax.legend();ax.grid(alpha=.2)
    fig.savefig(dest/'generation-quality.png',dpi=160);plt.close(fig)
    gains=load('classification-gains');fig,axes=plt.subplots(1,2,figsize=(12,4),layout='constrained')
    for ax,dep in zip(axes,config()['deployments']):
        g=gains[gains.protocol==dep];y=np.arange(len(g));ax.hlines(y,g.macro_f1_low,g.macro_f1_high);ax.scatter(g.macro_f1_gain,y);ax.axvline(0,color='gray')
        ax.set_yticks(y,[f'{a}-{b}' for a,b in zip(g.arm,g.reference)]);ax.set_title(dep);ax.set_xlabel('F1 gain; content-bootstrap 95% interval')
    fig.savefig(dest/'paired-gains.png',dpi=160);plt.close(fig)

if __name__=='__main__':
    freeze_phase2();audit_lineage();distributions();figures()
    files=[*Path(__file__).parent.glob('*.py'),*Path(ROOT/'src/proxy_analysis/conditional_drift').glob('*.py'),CONFIG]
    js('implementation-manifest.json',{'files':{str(p):digest(p) for p in files},'old_contract_intact':True})
    print('F10 lineage, distribution tables and figures complete',flush=True)
