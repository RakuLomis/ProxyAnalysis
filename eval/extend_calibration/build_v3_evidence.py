"""Read-only experiment audit; writes only new documentation and evidence-review outputs.

No training imports, PCAP reads, new bootstrap draws, checkpoint changes or selection.
"""
from pathlib import Path
import hashlib,json
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'outputs/extend-calibration-20260930/run-01/extraction-03'
FORMAL=BASE/'formal-01';PREP=BASE/'training-preparation-01'
DEST=BASE/'evidence-review-01';DOC=ROOT/'docs/extend-calibration-20260930'
INPUTS={}
LABELS={'github.com::repository_view':'GitHub 仓库浏览','youtube.com::search_results_view':'YouTube 搜索',
        'bing.com::search_results_view':'Bing 搜索','wikipedia.org::article_view':'Wikipedia 文章',
        'developer.mozilla.org::document_view':'MDN 文档','youtube.com::video_playback':'YouTube 视频播放'}

def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
    return h.hexdigest()

def register(p):
    p=Path(p);INPUTS[str(p.relative_to(ROOT))]=sha(p);return p

def read(p):return json.loads(register(p).read_text(encoding='utf-8'))
def frame(p):return pd.read_parquet(register(p))
def table(f):return f.to_markdown(index=False,floatfmt='.6f')

def main():
    DEST.mkdir(exist_ok=True);checks={}
    assert read(FORMAL/'pipeline-progress.json')['status']=='complete'
    revision=read(FORMAL/'execution-contract-revision-02.json')
    prep=read(PREP/'preregistration.json')
    for manifest,keys in [(revision,['files']),(prep,['source_hashes','package_manifest_hashes'])]:
        for key in keys:
            for p,h in manifest[key].items():
                path=Path(p);path=path if path.is_absolute() else ROOT/path
                assert sha(register(path))==h,p
    old=read(FORMAL/'execution-contract.json');compat=read(FORMAL/'repair-02/compatibility.json')
    assert sha(FORMAL/'execution-contract.json')==revision['repair']['old_contract_sha256']
    assert sha(FORMAL/'repair-02/compatibility.json')==revision['repair']['compatibility_sha256']
    read(FORMAL/'repair-02/resume-verification.json')
    for mode,total in [('restricted',19440),('reference',3240)]:
        seal=read(FORMAL/f'{mode}-prediction-seal.json')
        assert seal['passed'] and seal['cuda'] and seal['models']==total and not seal['test_pre_read'] and not seal['labels_read']
        assert sha(register(FORMAL/f'{mode}-predictions.parquet'))==seal['predictions_hash']
        count=0
        for path in (FORMAL/'classifiers'/mode).glob('*/complete.json'):
            d=read(path);assert d['cuda'] and d['steps']==1000 and not d['H_read'] and d['U_post_read']==(mode=='reference')
            assert d['contract']==sha(FORMAL/'execution-contract-revision-02.json')
            for p,h in d['files'].items():assert sha(register(p))==h
            count+=d['models']
        assert count==total
    checks['models_predictions_and_source_hashes']=True
    stat=read(FORMAL/'statistics-complete.json');p=frame(FORMAL/'scored-predictions.parquet')
    assert sha(FORMAL/'scored-predictions.parquet')==stat['scored_hash'] and len(p)==544320
    assert read(FORMAL/'generation-gate.json')['views']==9331200
    roles=frame(PREP/'roles.parquet');assert len(roles)==129600
    keys=['session_id','content_id','label_id','repetition','business_group','rotation','fold','role','business_role']
    for dep in sorted(roles[roles.track.eq('T')].protocol.unique()):
        a=roles[(roles.track=='W')&(roles.protocol==dep)][keys].sort_values(keys).reset_index(drop=True)
        b=roles[(roles.track=='T')&(roles.protocol==dep)][keys].sort_values(keys).reset_index(drop=True)
        pd.testing.assert_frame_equal(a,b)
    for _,g in roles.groupby('scenario'):
        assert len(g)==120 and g.session_id.is_unique and g.groupby('content_id').role.nunique().eq(1).all()
        assert g.groupby('role').size().to_dict()=={'C':24,'H':24,'U':72}
        assert not g[g.role.eq('C')].business_role.eq('new').any()
        assert len(g[(g.role=='U')&(g.business_role=='new')])==32
    checks['WT_shared_visits_roles_and_folds_identical']=True
    checks['scenario_roles_and_new_business_permissions']=True
    # Independent confusion reconstruction: no new fitted models or statistical tests.
    metrics=frame(FORMAL/'metrics-seed-rotation.parquet')
    groupkeys=['track','protocol','business_group','rotation','seed','arm']
    computed=[]
    for key,g in p.groupby(groupkeys,sort=True):
        cm=np.zeros((6,6));np.add.at(cm,(g.target.to_numpy(int),g.prediction.to_numpy(int)),1)
        f1=np.divide(2*np.diag(cm),cm.sum(0)+cm.sum(1),out=np.zeros(6),where=(cm.sum(0)+cm.sum(1))>0)
        new=g.loc[g.business_role.eq('new'),'target'].unique();assert len(new)==2
        computed.append(dict(zip(groupkeys,key))|{'F1_new':f1[new].mean(),'F1_all':f1.mean()})
    reconstructed=pd.DataFrame(computed).merge(metrics,on=groupkeys,validate='one_to_one',suffixes=('_check',''))
    for metric in ['F1_new','F1_all']:np.testing.assert_allclose(reconstructed[metric+'_check'],reconstructed[metric],atol=1e-12,rtol=0)
    checks['full_six_class_F1_reconstructed']=len(reconstructed)
    contrasts=frame(FORMAL/'contrasts.parquet');names=['F1_new','F1_all','BA_all','CE_all_bits','Brier_all','CE_new_bits','Brier_new']
    for (track,dep),con in contrasts.groupby(['track','protocol']):
        saved=np.load(register(FORMAL/f'bootstrap-contrasts-{track}-{dep}.npz'))
        for r in con.itertuples():
            draws=saved[f'g{r.business_group}_{r.contrast.removeprefix("paired-")}'][:,names.index(r.metric)]
            np.testing.assert_allclose(np.quantile(draws,[.025,.975]),[r.low95,r.high95],atol=1e-12,rtol=0)
            if r.primary:
                n=10 if track=='W' else 8
                np.testing.assert_allclose(np.quantile(draws,[.05/(2*n),1-.05/(2*n)]),[r.adjusted_low,r.adjusted_high],atol=1e-12,rtol=0)
    checks['saved_bootstrap_intervals_verified_without_resampling']=len(contrasts)
    # Coverage uses the SAME W byte measure in numerator and denominator, never unique U / W.
    coverage=frame(BASE/'full-coverage.parquet');retained=[]
    wfeatures=frame(BASE/'full-W-features.parquet').set_index(['session_id','side'])
    for r in coverage[coverage.protocol.ne('anytls')].itertuples():
        directory=BASE/'sessions'/r.session_id;pairs=read(directory/'T-pairs.json')
        common=[x for x in pairs if x['common_valid_nonempty']]
        assert len(pairs)==r.T_candidate_pairs and len(common)==r.T_common_pairs
        for side,key in [('pre','logical_id'),('post','carrier_id')]:
            events=frame(directory/f'{side}-W-events.parquet');ids={x[key] for x in common};candidates={x[key] for x in pairs}
            for direction in [1,-1]:
                e=events[events.direction.eq(direction)]
                assert int(e.payload_bytes.sum())==int(wfeatures.loc[(r.session_id,side),'W_up' if direction==1 else 'W_down'])
                retained.append({'protocol':r.protocol,'side':side,'direction':direction,
                    'all_selected_W_bytes':int(e.payload_bytes.sum()),
                    'candidate_T_members_W_bytes':int(e.loc[e.entity_id.isin(candidates),'payload_bytes'].sum()),
                    'common_T_members_W_bytes':int(e.loc[e.entity_id.isin(ids),'payload_bytes'].sum())})
    share=pd.DataFrame(retained).groupby(['protocol','side','direction']).sum().reset_index()
    share['retained_W_payload_fraction']=share.common_T_members_W_bytes/share.all_selected_W_bytes
    share['within_candidate_W_payload_retention']=share.common_T_members_W_bytes/share.candidate_T_members_W_bytes
    checks['coverage_denominators_equal_frozen_W_features']=True
    counts=coverage.groupby('protocol')[['T_candidate_pairs','T_common_pairs']].sum().reset_index()
    counts=counts[counts.protocol.ne('anytls')];counts['pair_retention_fraction']=counts.T_common_pairs/counts.T_candidate_pairs
    share.to_parquet(DEST/'common-pair-W-byte-coverage.parquet',index=False)
    counts.to_parquet(DEST/'pair-retention.parquet',index=False)
    business=frame(FORMAL/'business-metrics.parquet')
    bus=business.groupby(['track','protocol','label_id','is_new','arm'])[['F1','recall']].mean().reset_index();bus['业务']=bus.label_id.map(LABELS)
    seeds=frame(FORMAL/'metrics-by-seed.parquet');groups=frame(FORMAL/'metrics-by-group.parquet');summary=frame(FORMAL/'metrics-summary.parquet')
    errors=frame(FORMAL/'error-counts.parquet').groupby(['track','protocol','contrast','business_role'])[['repaired','introduced','changed']].sum().reset_index()
    groupnames={0:'GitHub 仓库浏览 + YouTube 搜索',1:'Bing 搜索 + Wikipedia 文章',2:'MDN 文档 + YouTube 视频播放'}
    groups['新增业务组']=groups.business_group.map(groupnames)
    text='# Extend v3 结果补充\n\n本附件追溯整理已完成实验，不是新预注册或新检验。不重训、不重新抽样；全部区间来自已保存的内容簇 bootstrap 数组。分数为 0–1，差值也使用该尺度，乘 100 才是百分点。\n\n'
    text+='主比较 W 十项与 T 八项分别校正，不构成合并十八项家族的统一错误率保证。其余对照仅显示普通 95% 区间，是描述性次要比较；不得根据这里的高分替换主方法。reference 不是同资源参照或理论上界。\n\n'
    sections=[('总体指标',summary),('预定主比较',contrasts[contrasts.primary]),
              ('全部次要 F1 对照区间',contrasts[(contrasts.metric=='F1_new')&(~contrasts.primary)]),
              ('概率指标对照区间',contrasts[(contrasts.business_group==-1)&contrasts.metric.isin(['CE_new_bits','Brier_new'])]),
              ('命名业务组',groups),('逐类别作为新增业务',bus[bus.is_new][['track','protocol','业务','arm','F1','recall']]),
              ('逐类别作为校准业务',bus[~bus.is_new][['track','protocol','业务','arm','F1','recall']]),('逐种子',seeds),('错误修复与新增',errors)]
    for title,f in sections:text+='## '+title+'\n\n'+table(f)+'\n\n'
    text+='## 计数与解释边界\n\n每部署每个对照，新增业务错误表包含 2880 个预测实例，即 120 个独立访问 × 8 轮换 × 3 种子；校准业务为 5760 个实例。同一内容重复、种子与轮换不是新的独立样本。逐类别作为新增业务只取该类别被留作新增业务的业务组；校准业务表平均另外两个组。逐 seed 表先平均业务组与轮换，不是 seed 级显著性检验。\n\n'
    text+='所有九个轨道与部署组合通过预定双增量，不意味着条件模型普遍最优。T 的 SS 上 paired−marginal 为负且普通区间不跨零；W 的 Trojan/VLESS 与简单漂移方法接近。Brier 的改善不能替代 CE 的独立检查。区间条件于既有模型、内容和校准集合，不是外部验证；区间跨零不等于等效。\n'
    (DOC/'v3-results-supplement.md').write_text(text,encoding='utf-8')
    covtext='# Extend v3 连接与字节保留统计\n\n此附件由已有窗口事件与 pair 台账计算，不读取 PCAP。访问集合是最终冻结队列。\n\n## 排他连接保留\n\n'+table(counts)+'\n\n'
    covtext+='分母是本轮候选排他 TCP pair，而非整个页面全部连接；分子要求双侧共同有效且非空。不能将连接保留率当作字节保留率。\n\n## 同口径观测字节保留\n\n'+table(share)+'\n\n'
    covtext+='direction=1 为客户端发出，−1 为返回。retained_W_payload_fraction 的分母为相同访问共同窗口的全部选中 W 载荷字节，分子为落在 T 共同有效 pair 成员上的 W 载荷字节；两者都包括 TCP 重传，不是 U/W 比值。within_candidate_W_payload_retention 则以候选 T 成员的同口径字节为分母，区分候选观测范围与资格筛选损失。全部 W 字节分母已逐访问对照冻结 full-W-features。它只衡量相对所选观测范围的字节保留，不保证对网页全部业务字节的覆盖。AnyTLS 没有适用的排他 T，因此不填零。\n\n'
    covtext+='共同 T 成员承载的下行载荷仅占所选 W 下行约 16%–31%。这不是丢包率，也不能仅由该比例归因为某个协议机制。W/T 使用相同父访问不代表观察相同流量范围，约 99.60% 的候选连接保留率不能替代字节覆盖说明。\n'
    (DOC/'v3-coverage-tables.md').write_text(covtext,encoding='utf-8')
    for path,h in INPUTS.items():assert sha(ROOT/path)==h,'Input changed during review: '+path
    checks['all_reviewed_inputs_unchanged']=True
    manifest={'passed':True,'checks':checks,'inputs':INPUTS,'script_sha256':sha(__file__),
              'new_training':False,'new_bootstrap_draws':False,'raw_pcap_reads':False}
    (DEST/'audit.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
    index='# Extend v3 证据索引\n\n本索引引用实际存在的冻结记录；完整输入清单在本地 `evidence-review-01/audit.json`。本轮没有修改原始实验记录。\n\n'
    keypaths=[PREP/'preregistration.json',FORMAL/'execution-contract.json',FORMAL/'execution-contract-revision-02.json',
              FORMAL/'repair-02/compatibility.json',FORMAL/'generation-gate.json',FORMAL/'restricted-prediction-seal.json',
              FORMAL/'reference-prediction-seal.json',FORMAL/'statistics-complete.json',FORMAL/'contrasts.parquet',PREP/'roles.parquet']
    index+=table(pd.DataFrame([{'文件':str(p.relative_to(ROOT)),'SHA256':sha(p)} for p in keypaths]))
    index+='\n\n## 核对结果\n\n'+table(pd.DataFrame([{'检查':k,'结果':str(v)} for k,v in checks.items()]))+'\n'
    (DOC/'v3-evidence-index.md').write_text(index,encoding='utf-8')
    print(json.dumps({'passed':True,'checks':checks,'inputs':len(INPUTS)},ensure_ascii=False),flush=True)

if __name__=='__main__':main()
