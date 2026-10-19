"""After all H probabilities and labels, complete comparisons and diagnostics."""
from common import *

def run():
    barrier('P6-complete.json');d=pd.read_parquet(OUT/'scores/labeled-predictions.parquet')
    from formal import truth,metrics
    predcols=[f'l{k}' for k in range(6)];y=truth(d);lp=d[predcols].to_numpy();p=np.exp(lp)
    d['CE_i']=-lp[np.arange(len(d)),y];d['Brier_i']=((p-np.eye(6)[y])**2).sum(1)
    d['scope']=['U' if k in MASKS[g] else 'C' for k,g in zip(y,d.group)]
    d['correct']=d.prediction.to_numpy()==y;d['confidence']=p.max(1)
    save(OUT/'scores/row-costs.parquet',d)
    bycontent=d.groupby(['pipeline','target','group','seed','content_id','scope']).agg(accuracy=('correct','mean'),CE=('CE_i','mean'),Brier=('Brier_i','mean')).reset_index()
    save(OUT/'scores/content-costs.parquet',bycontent)
    ranges=pd.read_parquet(OUT/'scores/scenarios.parquet').groupby(['pipeline','seed']).mean(numeric_only=True).reset_index()
    save(OUT/'scores/seed-summary.parquet',ranges)
    # Error-flip costs use both methods' probabilities, not merely prediction IDs.
    main=d[d.pipeline=='F-P-FUSE'];rows=[]
    for ref in ['B0','E-post-FUSE','N-P-FUSE','F-G-FUSE','R-P-FUSE']:
        other=d[d.pipeline==ref][['role_id','visit_id','seed','CE_i','Brier_i','correct','confidence']]
        z=main.merge(other,on=['role_id','visit_id','seed'],suffixes=('','_reference'),validate='one_to_one')
        z['flip']=np.select([z.correct&~z.correct_reference,~z.correct&z.correct_reference,z.correct&z.correct_reference],['repaired','introduced','both_correct'],default='both_wrong')
        z['delta_CE']=z.CE_i-z.CE_i_reference;z['delta_Brier']=z.Brier_i-z.Brier_i_reference;z['reference']=ref
        rows.append(z)
    save(OUT/'scores/error-flip-costs.parquet',pd.concat(rows,ignore_index=True))
    freq=read(OUT/'selections/decisions.json');save(OUT/'scores/selection-frequency.parquet',pd.DataFrame(freq).groupby(['arm','policy','candidate','beta']).size().reset_index(name='roles'))
    labels=d[['role_id','visit_id','content_id','label_id','target','group','outer']].drop_duplicates()
    desc=pd.read_parquet(OUT/'predictions/selected-PURE-head-stages.parquet').merge(labels,on=['role_id','visit_id'],validate='many_to_one')
    stages=[]
    for key,part in desc.groupby(['pipeline','classifier_stage','target','group','seed']):
        m,_,_=metrics(truth(part),part[predcols].to_numpy(),MASKS[key[3]])
        stages.append(dict(zip(['pipeline','classifier_stage','target','group','seed'],key),**m))
    save(OUT/'scores/selected-PURE-stage-summary.parquet',stages)
    primary=read(OUT/'comparisons/primary.json');screen=read(OUT/'comparisons/practical-screen.json');pooled=pd.read_parquet(OUT/'scores/pooled.parquet')
    lines=['# DP-GAN1-M v1 NER1 完整实验报告','','原科学合同不变；累计40小时活动、32小时保守预计门。','',
        '720源内任务与60外层角色；13条逻辑管线，完整H预测56160行。以下为同批历史数据的完整内部评价，不是外部盲测。','',
        '## 完整H结果','','| 管线 | F1 U | F1 C | F1 全六类 | CE U | Brier U | 最差部署F1 U |','| --- | ---: | ---: | ---: | ---: | ---: | ---: |']
    for r in pooled.to_dict('records'):lines.append('| '+r['pipeline']+' | '+' | '.join(f'{r[k]:.6f}' for k in ['F1_U','F1_C','F1_all','CE_U','Brier_U','worst_deployment_F1_U'])+' |')
    lines+=['','## 五项主比较','','| F P FUSE 相对 | Δ F1 U | 95%区间 | 家族99%区间 | 家族正增量 |','| --- | ---: | --- | --- | --- |']
    for r in primary['comparisons']:lines.append(f"| {r['reference']} | {r['delta_F1_U']:.6f} | {r['CI95']} | {r['CI99']} | {r['positive_family_increment']} |")
    lines+=['','## 实践代价与边界','',f"C总体筛查：{screen['overall_passed']}；逐部署合并筛查：{screen['passed']}。",'',
        '五比较使用共享全局内容簇bootstrap，重复访问、角色和seed不作为独立内容。区间条件于固定已拟合模型，不能消除反复开发与模型选择的历史影响。',
        '源内选择与H评价分别保存；未据H改变参数、选择β或回退。PURE阶段分解是描述性分析，不替代主FUSE比较。',
        '整体效力、矩组合、精确对应和概率代价必须分别依照相应对照解释。训练raw/std误差、矩分项和梯度轨迹保存在每条trace.json；H-pre未读取，不能报告H上的真实pre恢复误差。','',
        '## 追溯文件','','详见scores中的部署、类别、内容、seed、逐行CE/Brier和错误翻转表，comparisons中的区间与实践筛查，以及budget.json。']
    path=writable(OUT/'reports/complete-report.md');require(not path.exists(),'Immutable final report');path.write_text('\n'.join(lines)+'\n',encoding='utf-8')
    v=read(OUT/'comparisons/primary.json');effects={r['reference']:r['positive_family_increment'] for r in v['comparisons']}
    immutable(OUT/'reports/effects.json',dict(fused_effect_vs_B0=effects['B0'],fused_effect_vs_Epost=effects['E-post-FUSE'],
        moment_increment=effects['N-P-FUSE'],exact_pair_increment=effects['F-G-FUSE'],dynamic_vs_static=effects['R-P-FUSE'],C_cost_screen=screen['passed']))
    seal(OUT/'manifests/report-complete.json',[path,OUT/'reports/effects.json']+list((OUT/'scores').glob('*.parquet')))
