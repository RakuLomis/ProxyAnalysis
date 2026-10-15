"""Post-result artifact QA only; does not change estimators or selection rules.

Added after Q21 to strengthen stored-matrix/qualification replay and expose
already saved Brier/tail calibration scores. No new fitting or model selection.
"""
from common import *

def main():
    c=start('supplementary_QA'); q=pd.read_parquet(OUT/'qualification/all-relations.parquet')
    oof=pd.read_parquet(OUT/'moments/inner-oof.parquet'); cov_error=0.; matrix_count=0
    for r in c['roles']:
        if r['inner'] is not None: continue
        p=folder('decomposition',r); manifest=read(p/'complete.json')
        for j,f in enumerate(FEATURES):
            require(manifest['sha256'][f+'.pt']==sha(p/(f+'.pt')),'Stored decomposition SHA')
            saved=torch.load(p/(f+'.pt'),map_location=device(),weights_only=True)
            b=load_bundle(r,j); n=b['true_by_y']
            frozen=load_old('models',r,'zero'); offset=sum(size(v) for v in range(j)); ss=frozen['scale'][offset:offset+size(j)]
            for tag,rows in [('empirical',empirical_rows(n)),('smoothed',b['true_1'])]:
                wi,be,total,mean,nu=covariance(n,rows)
                expected={'within':wi,'between':be,'total':total,'mixture':mean,'nu':nu,
                          'within_scaled':wi/ss[:,None]/ss[None,:]*WEIGHTS[j],
                          'between_scaled':be/ss[:,None]/ss[None,:]*WEIGHTS[j]}
                for name,value in expected.items():
                    err=float((value-saved[tag][name]).abs().max()); cov_error=max(cov_error,err)
                    require(err<1e-12,'Stored matrix replay')
                require(min(float(torch.linalg.eigvalsh(saved[tag][name]).min()) for name in ['within','between','total'])>-1e-10,'Stored matrix PSD')
                matrix_count+=1
    for row in q.itertuples():
        role=oof[(oof.outer==row.outer)&(oof.protocol==row.protocol)]
        sub=role[(role.y==row.y)&(role.j==row.j)]
        e=sub.error_T1.to_numpy(); _,_,lo,hi,nonempty=interval(row.target,e)
        relevance=abs(sub.actual.mean()/PI-role[(role.y!=row.y)&(role.j==row.j)].actual.mean()/PI)
        basic=bool(len(sub)==4 and np.isfinite(e).all() and max(abs(e))<=.1*PI and nonempty and hi-lo<=.5*PI and relevance>=.05)
        gains={t:float((abs(sub['error_'+t])-abs(sub.error_T1)).mean()) for t in ['G1','P0','P1']}
        positive={t:int((abs(sub['error_'+t])>abs(sub.error_T1)).sum()) for t in gains}
        inc=all(gains[t]>=.01*PI and positive[t]>=3 for t in gains)
        require(basic==row.reliable and inc==row.incremental,'Qualification flags replay')
        require(abs(relevance-row.relevance)<1e-12,'Relevance replay')
    require(int((q.reliable&q.incremental).sum())==0 and not q.selected.any(),'Empty selected set replay')
    d=pd.read_parquet(OUT/'scores/content-feature-probabilities.parquet')
    arms=['D0','DG','DB','D1-1','D2-1','D3-1']; rows=[]
    for p in PROTOCOLS:
        for a in arms:
            sub=d[(d.protocol==p)&(d.arm==a)].copy(); weight=sub.j.map(dict(enumerate(WEIGHTS)))
            rows.append({'protocol':p,'arm':a,'categorical_Brier':float((sub.brier*weight).sum()/30),
                'tail_Brier':float((sub.tail_brier*weight).sum()/30),
                'tail_forecast':float((sub.tail_forecast*weight).sum()/30),
                'tail_actual':float((sub.tail_actual*weight).sum()/30),
                'mean_tail_error':float(((sub.tail_forecast-sub.tail_actual)*weight).sum()/30)})
    scored=pd.DataFrame(rows); save(scored,OUT/'scores/brier-tail-summary.parquet')
    code=Path(__file__); figures={rel(p):sha(p) for p in (DOC/'figures').glob('*.png')}
    write(OUT/'verification-supplementary.json',{'pass':True,'source_sha256':{rel(code):sha(code)},
        'purpose':'Post-result verification/reporting only, no estimator/rule changes or new fits',
        'coherent_covariance_sets_reloaded':matrix_count,'stored_matrix_replay_max':cov_error,
        'qualification_flags_replayed':len(q),'empty_selection_replayed':True,
        'seven_PNGs_visually_inspected':len(figures)==7,'PNG_sha256':figures,
        'zero_classifier_fits':True})
    from report import table
    lines=['# 补充产物复核与既有概率校准分项','',
           'Q21后进行的交付QA，不改变封存估计器、门限、候选或十二项主家族，不拟合新模型。','',
           f'重载{matrix_count}组经验/一致平滑协方差，矩阵最大重放差{cov_error:g}；1200个基本可靠与真配增量标志均从原四内容残差重算一致，可靠与增量交集确认为空。七张PNG已逐张视觉检查。','',
           '## 已保存预测的Brier与尾概率校准','',
           '这些数值是出口箱状态预测，不是业务类别Brier。每变量先内容等权，再用原族权重合成；上尾为箱>=4，预测与观测的均值差只表示总体校准偏差，不能代替可靠性曲线或完整校准证明。D1/D2/D3使用oracle Y。无额外主显著性检验。','',table(scored),'',
           '补充实现qa.py的SHA单独记录于verification-supplementary.json，因为它在结果后增加，只进行已冻结产物复核及分项展示，不属于拟合前的估计器源码清单。']
    (DOC/'supplementary-diagnostics.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    finish('supplementary-QA',stored_matrix_replay_max=cov_error,qualification_flags=len(q),new_fits=0)

if __name__=='__main__': main()
