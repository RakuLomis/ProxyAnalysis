"""Read-only source audits and additional tables/figures; no model selection."""
from run import *

def audit_and_describe():
    p=pd.read_parquet(FORMAL/'oof-predictions.parquet');cohort=load('cohort').sort_values('session_id')
    old_draws=pd.read_parquet(FORMAL/'content-bootstrap-draws.parquet')
    labels=sorted(cohort.label_id.unique());groups=[cohort[cohort.label_id==l].content_id.unique().tolist() for l in labels]
    rng=np.random.default_rng(20260926);ids=cohort.session_id.tolist();maxdiff=0.;draw_members=[]
    arrays={}
    for (a,s),g in p[p.arm.isin(['S1','S2'])].groupby(['arm','seed']):
        g=g.set_index('session_id').loc[ids];arrays[a,s]=g[PROBS].to_numpy();target=g.target.to_numpy()
    for draw in range(2000):
        selected=[c for group in groups for c in rng.choice(group,len(group),replace=True)]
        weights=np.array([selected.count(c) for c in cohort.content_id])
        for c in set(selected):draw_members.append({'draw':draw,'content_id':c,'multiplicity':selected.count(c)})
        result={a:np.mean([scores(target,arrays[a,s],weights) for s in cfg()['seeds']],axis=0) for a in ['S1','S2']}
        delta=(result['S2']-result['S1'])*[1,1,-1,-1]
        expected=old_draws[(old_draws.draw==draw)&(old_draws.arm=='S2')&(old_draws.reference=='S1')][NAMES].iloc[0].to_numpy()
        maxdiff=max(maxdiff,float(np.abs(delta-expected).max()))
    assert maxdiff<1e-12
    save('bootstrap-content-members',pd.DataFrame(draw_members))
    write_json(OUT/'bootstrap-reconstruction-audit.json',{'draws':2000,'verified_contrast':'S2-S1','max_difference':maxdiff})
    ledger=pd.read_parquet(OUT/'error-ledger.parquet');counts=[]
    for (comparison,state),g in ledger.groupby(['comparison','state']):
        counts.append({'comparison':comparison,'state':state,'seed_visits':len(g),'distinct_visits':g.session_id.nunique(),'distinct_contents':g.content_id.nunique()})
    counts=save('error-count-units',pd.DataFrame(counts))
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    figures=DOC/'figures';figures.mkdir(exist_ok=True)
    m=pd.read_parquet(OUT/'metrics-by-seed.parquet')
    fig,axes=plt.subplots(1,2,figsize=(10,4),layout='constrained')
    arms=['S1','S2','S4','L3']
    for ax,metric in zip(axes,['macro_f1','ce_bits']):
        for seed,g in m[m.arm.isin(arms)].groupby('seed'):
            ax.plot(arms,g.set_index('arm').loc[arms,metric],marker='o',label=str(seed))
        ax.set_ylabel(metric);ax.legend();ax.grid(alpha=.2)
    fig.savefig(figures/'seed-metrics.png',dpi=160);plt.close(fig)
    yt=pd.read_parquet(OUT/'youtube-details.parquet')
    vids=yt[yt.label_id=='youtube.com::video_playback'].content_id.unique()
    fig,ax=plt.subplots(figsize=(10,5),layout='constrained')
    x=np.arange(len(vids))
    for i,arm in enumerate(arms):
        g=yt[(yt.arm==arm)&yt.content_id.isin(vids)].groupby('content_id').correct.apply(lambda x:int((~x).sum())).reindex(vids)
        ax.bar(x+(i-1.5)*.2,g,width=.2,label=arm)
    ax.set_xticks(x,[v.replace('youtube_video:','') for v in vids]);ax.set_ylabel('Errors / 12 seed-visit predictions');ax.legend()
    fig.savefig(figures/'youtube-video-errors.png',dpi=160);plt.close(fig)
    path=DOC/'error-localization.md'
    with path.open('a',encoding='utf-8') as f:
        f.write('\n\n## 计数单位核对\n\n'+table(counts)+'\n\n![三seed指标](figures/seed-metrics.png)\n\n![视频错误](figures/youtube-video-errors.png)\n\n旧bootstrap抽样已按同一RNG重建，并逐次核对S2−S1四指标全部2000次抽样，一致性误差为'+str(maxdiff)+'。\n')
    print('Supplement audits complete',flush=True)

if __name__=='__main__':audit_and_describe()
