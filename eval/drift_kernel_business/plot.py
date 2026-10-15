"""Fixed scientific figures; all values are read from completed, frozen results."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from common import *

SHORT=['Bing search','MDN docs','GitHub repo','Wikipedia','YouTube search','YouTube play']
COLORS=['#617580','#3887be','#ba748f','#c7a45e','#2b9e79','#8266a8']

def save(fig,name):
    folder=OUT/'figures'
    folder.mkdir(exist_ok=True)
    fig.savefig(folder/(name+'.png'),dpi=180,bbox_inches='tight')
    fig.savefig(folder/(name+'.pdf'),bbox_inches='tight')
    plt.close(fig)

def run():
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10})
    scores=pd.read_parquet(OUT/'scores/protocol-summary.parquet')
    fig,axes=plt.subplots(2,2,figsize=(12,7),sharey=True)
    for ax,p in zip(axes.flat,PROTOCOLS):
        g=scores[scores.protocol.eq(p)].set_index('arm').loc[ARMS]
        ax.bar(ARMS,g.F1,color=COLORS)
        for i,value in enumerate(g.F1):
            ax.text(i,value+.012,f'{value:.3f}',ha='center',fontsize=9)
        ax.set(title=p,ylim=(0,1.06),ylabel='Six-class macro F1')
    fig.suptitle('Same post histograms, known deployment, content-held-out visits')
    fig.tight_layout()
    save(fig,'protocol-F1')
    fig,axes=plt.subplots(1,2,figsize=(12,4))
    for ax,metric in zip(axes,['CE','Brier']):
        for i,p in enumerate(PROTOCOLS):
            g=scores[scores.protocol.eq(p)].set_index('arm').loc[ARMS]
            ax.plot(ARMS,g[metric],marker='o',label=p)
        ax.set(ylabel=metric+' (nats)' if metric=='CE' else 'Brier (sum of 6 class errors)')
        ax.legend(fontsize=8)
    fig.tight_layout()
    save(fig,'probability-quality')
    contrast=pd.read_parquet(OUT/'comparisons/F1-contrasts.parquet')
    fig,axes=plt.subplots(1,2,figsize=(12,6),sharex=True)
    for ax,family in zip(axes,['primary','baseline']):
        g=contrast[contrast.family.eq(family)].reset_index(drop=True)
        for i,r in g.iterrows():
            ax.plot([r.family_lo,r.family_hi],[i,i],color='#3887be')
            ax.scatter([r.point],[i],color='#2b9e79')
        ax.axvline(0,color='gray',linestyle='--')
        ax.set_yticks(np.arange(len(g)),g.protocol+' '+g.comparison)
        ax.set(xlabel='Macro F1 difference',title=family+' (8-comparison family intervals)')
    fig.tight_layout()
    save(fig,'F1-contrasts')
    cm=pd.read_parquet(OUT/'scores/confusion.parquet')
    fig,axes=plt.subplots(2,2,figsize=(12,9))
    for ax,p in zip(axes.flat,PROTOCOLS):
        m=cm[cm.protocol.eq(p)&cm.arm.eq('G4')].pivot(index='truth',columns='prediction',values='count').to_numpy()
        ax.imshow(m,cmap='Blues',vmin=0,vmax=20)
        for i in range(6):
            for j in range(6):
                ax.text(j,i,str(m[i,j]),ha='center',va='center',color='white' if m[i,j]>10 else 'black')
        ax.set_xticks(range(6),SHORT,rotation=45,ha='right',fontsize=8)
        ax.set_yticks(range(6),SHORT,fontsize=8)
        ax.set(title=p+' G4',xlabel='Predicted',ylabel='True')
    fig.tight_layout()
    save(fig,'true-kernel-confusions')
    data=pd.read_parquet(OUT/'scores/scored-visits.parquet')
    reliability=[]
    fig,axes=plt.subplots(2,2,figsize=(10,8))
    for ax,p in zip(axes.flat,PROTOCOLS):
        ax.plot([0,1],[0,1],linestyle='--',color='gray')
        for arm in ARMS:
            g=data[data.protocol.eq(p)&data.arm.eq(arm)].copy()
            g['confidence']=g[[f'p{i}' for i in range(6)]].max(axis=1)
            g['correct']=g.prediction.eq(g.truth)
            g['bin']=np.minimum((g.confidence*10).astype(int),9)
            rows=[]
            for b,group in g.groupby('bin'):
                # Each seed has the same visit support. Pooled calibration points are descriptive only.
                row={'protocol':p,'arm':arm,'bin':int(b),'count':len(group),
                     'confidence':float(group.confidence.mean()),'accuracy':float(group.correct.mean())}
                rows.append(row)
                reliability.append(row)
            points=pd.DataFrame(rows)
            ax.plot(points.confidence,points.accuracy,marker='o',label=arm)
        ax.set(title=p,xlim=(0,1),ylim=(0,1),xlabel='Mean confidence',ylabel='Observed accuracy')
        ax.legend(fontsize=8,ncol=2)
    fig.tight_layout()
    save(fig,'reliability')
    saveparquet(pd.DataFrame(reliability),OUT/'scores/reliability-bins.parquet')
    dist=pd.read_parquet(OUT/'explanations/training-class-distances.parquet')
    fig,axes=plt.subplots(2,2,figsize=(12,7),sharey=True)
    for ax,p in zip(axes.flat,PROTOCOLS):
        for arm in ['G3','G4','G5','G0']:
            g=dist[dist.protocol.eq(p)&dist.arm.eq(arm)].groupby('feature').JS_nats.mean().reindex(FEATURES)
            ax.plot(range(10),g,marker='o',label=arm)
        ax.set_xticks(range(10),FEATURES,rotation=55,ha='right',fontsize=8)
        ax.set(title=p,ylabel='Mean pairwise class JS (nats, training only)')
        ax.legend(fontsize=8)
    fig.tight_layout()
    save(fig,'source-to-output-class-distances')
    flips=pd.read_parquet(OUT/'explanations/error-flips.parquet')
    fig,axes=plt.subplots(2,2,figsize=(12,7),sharey=True)
    comps=['G3','G5','G0','G1','G2']
    for ax,p in zip(axes.flat,PROTOCOLS):
        g=flips[flips.protocol.eq(p)].groupby(['comparator','seed'])[['repaired','new_error']].sum().groupby('comparator').mean().reindex(comps)
        at=np.arange(5)
        ax.bar(at-.18,g.repaired,width=.36,label='Repaired',color='#2b9e79')
        ax.bar(at+.18,g.new_error,width=.36,label='New error',color='#ba748f')
        ax.set_xticks(at,comps)
        ax.set(title=p,ylabel='Visits (G2: seed mean)')
        ax.legend(fontsize=8)
    fig.tight_layout()
    save(fig,'error-flips')
    contribution=pd.read_parquet(OUT/'explanations/visit-bin-contributions.parquet')
    examples=pd.read_parquet(OUT/'explanations/fixed-example-visits.parquet')
    fig,axes=plt.subplots(4,1,figsize=(11,12))
    for ax,p in zip(axes,PROTOCOLS):
        ids=examples[examples.protocol.eq(p)].sort_values('label_id').visit_id
        m=contribution[contribution.visit_id.isin(ids)].groupby(['visit_id','feature']).value.sum().unstack().reindex(index=ids,columns=FEATURES)
        im=ax.imshow(m,cmap='RdBu_r',vmin=-.05,vmax=.05,aspect='auto')
        ax.set_xticks(range(10),FEATURES,rotation=45,ha='right',fontsize=8)
        ax.set_yticks(range(6),SHORT,fontsize=8)
        ax.set_title(p+' fixed-ID example margin contributions (not causal effects)')
    fig.tight_layout()
    save(fig,'fixed-example-contributions')
    write(OUT/'figures/manifest.json',{'pngs':[rel(p) for p in sorted((OUT/'figures').glob('*.png'))],
           'english_labels':True,'fixed_plots':True,'raw_plot_sources':'scores and explanations parquet tables'})

if __name__=='__main__':
    run()
