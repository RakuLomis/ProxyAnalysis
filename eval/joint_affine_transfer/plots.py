"""Scientific plots from sealed tables; no fitting or candidate selection."""
from common import *
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def run():
    start('plots');dst=writable(OUT/'figures');dst.mkdir(parents=True,exist_ok=True)
    pooled=pd.read_parquet(OUT/'scores/pooled.parquet').set_index('arm')
    arms=['CT1','CT3','CT4','StrongPost','JA0','JA1','JA2']
    fig,ax=plt.subplots(figsize=(8.2,4.5));ax.bar(arms,pooled.loc[arms,'F1_uncovered'],color=['#b7c4d4']*4+['#4b8cbd','#db7b3b','#67976a'])
    ax.set_ylabel('Uncovered-business macro F1');ax.set_ylim(0,1);ax.grid(axis='y',alpha=.25);fig.tight_layout()
    for ext in ['png','pdf']:fig.savefig(dst/f'uncovered-f1.{ext}',dpi=180)
    plt.close(fig)
    comparison=read(OUT/'comparisons/primary.json')['comparisons'];fig,ax=plt.subplots(figsize=(7.5,4.2))
    for i,r in enumerate(comparison):
        lo,hi=r['CI_98_75'];v=r['delta_F1_uncovered'];ax.plot([lo,hi],[i,i],color='#3b7598');ax.plot(v,i,'o',color='#3b7598')
    ax.set_yticks(range(4),['JA1 - '+r['reference'] for r in comparison]);ax.axvline(0,color='black',lw=.8)
    ax.set_xlabel('F1 difference (98.75% family-adjusted intervals)');fig.tight_layout()
    for ext in ['png','pdf']:fig.savefig(dst/f'primary-contrasts.{ext}',dpi=180)
    plt.close(fig)
    recovery=pd.read_parquet(OUT/'diagnostics/recovery.parquet');recovery=recovery[recovery.inner.isna()]
    vals=recovery.groupby(['arm','target']).MSE.mean().unstack().loc[ARMS,PROTOCOLS]
    fig,ax=plt.subplots(figsize=(7.2,3.8));im=ax.imshow(vals,aspect='auto',cmap='viridis')
    ax.set_xticks(range(4),PROTOCOLS);ax.set_yticks(range(3),ARMS);fig.colorbar(im,ax=ax,label='Offline standardized forward MSE')
    for i in range(3):
        for j in range(4):ax.text(j,i,f'{vals.iloc[i,j]:.3f}',ha='center',va='center',color='white')
    fig.tight_layout()
    for ext in ['png','pdf']:fig.savefig(dst/f'forward-recovery.{ext}',dpi=180)
    plt.close(fig);finish('plots',figures=3)

if __name__=='__main__':run()
