"""Fixed scientific summaries; no selection or fitting."""
from common import *
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

NAMES={'shadowsocks':'SS','vless':'VLESS','trojan':'Trojan','vmess':'VMess'}
def figsave(fig,name):
    dst=DOC/'figures'; dst.mkdir(parents=True,exist_ok=True); fig.tight_layout()
    fig.savefig(dst/(name+'.png'),dpi=180); fig.savefig(dst/(name+'.pdf')); plt.close(fig)
def main():
    start('plots'); plt.rcParams.update({'font.size':9,'axes.spines.top':False,'axes.spines.right':False})
    d=pd.read_parquet(OUT/'scores/protocol-summary.parquet'); fig,ax=plt.subplots(figsize=(10,4)); ix=np.arange(4)
    for k,a in enumerate(ARMS): ax.bar(ix+(k-2)*.15,d[d.arm==a].set_index('protocol').loc[PROTOCOLS].F1,.15,label=a)
    ax.set_xticks(ix,[NAMES[p] for p in PROTOCOLS]); ax.set_ylim(0,1); ax.set_ylabel('Six-class macro F1'); ax.legend(ncol=5); figsave(fig,'protocol-performance')
    c=pd.read_parquet(OUT/'comparisons/main-contrasts.parquet'); fig,ax=plt.subplots(figsize=(8,3))
    ax.hlines(np.arange(3),c.family_lower,c.family_upper,color='tab:blue'); ax.scatter(c.point,np.arange(3),s=30); ax.axvline(0,color='gray'); ax.axvline(.01,color='gray',ls='--')
    ax.set_yticks(np.arange(3),c.comparison); ax.set_xlabel('Deployment-equal F1 gain; three-family adjusted interval'); figsave(fig,'main-contrasts')
    choices=pd.DataFrame(read(OUT/'selection/choices.json')); choices=choices[choices.arm!='DSR1']
    fig,ax=plt.subplots(figsize=(8,4)); x=np.arange(3)
    for i,a in enumerate(ALPHAS): ax.bar(x+(i-1.5)*.18,[int(((choices.arm==arm)&(choices.alpha==a)).sum()) for arm in ARMS[2:]],.18,label=str(a))
    ax.set_xticks(x,ARMS[2:]); ax.set_ylabel('Selected outer roles / 20'); ax.legend(title='alpha',ncol=4); figsave(fig,'alpha-selection')
    comp=pd.read_parquet(OUT/'states/outer-composition.parquet'); fig,axes=plt.subplots(1,4,figsize=(12,3.5),sharey=True)
    for ax,p in zip(axes,PROTOCOLS):
        sub=comp[comp.protocol==p].groupby(['arm','state']).OOF_CE.mean().unstack()
        sub.loc[ARMS[2:]].plot.bar(ax=ax); ax.set_title(NAMES[p]); ax.set_xlabel(''); ax.tick_params(axis='x',rotation=0); ax.legend(title='state',fontsize=7)
    axes[0].set_ylabel('Cross-fitted baseline CE (nat; descriptive)'); figsave(fig,'state-OOF-difficulty')
    act=pd.read_parquet(OUT/'diagnostics/outer-base-activity.parquet'); fig,ax=plt.subplots(figsize=(9,4))
    for i,a in enumerate(ARMS[2:]):
        vals=act[act.arm==a].groupby('protocol').drift_gap.mean().loc[PROTOCOLS]; ax.bar(ix+(i-1)*.23,vals,.23,label=a)
    ax.set_xticks(ix,[NAMES[p] for p in PROTOCOLS]); ax.set_ylabel('Baseline smooth risk minus mean CE (nat)'); ax.legend(); figsave(fig,'baseline-risk-pressure')
    flips=pd.read_parquet(OUT/'scores/error-flip-summary.parquet'); fig,axes=plt.subplots(1,4,figsize=(12,3.5),sharey=True)
    for ax,p in zip(axes,PROTOCOLS):
        sub=flips[flips.protocol==p].set_index('reference').loc[ARMS[:-1]]
        sub[['repaired','added']].plot.bar(ax=ax); ax.set_title(NAMES[p]); ax.set_xlabel(''); ax.tick_params(axis='x',rotation=30); ax.legend(fontsize=7)
    axes[0].set_ylabel('DSR4 repaired / newly wrong visits'); figsave(fig,'error-flips')
    classes=pd.read_parquet(OUT/'scores/class-summary.parquet'); fig,axes=plt.subplots(1,4,figsize=(14,5),sharey=True)
    short=['Bing search','MDN document','GitHub repo','Wikipedia article','YouTube search','YouTube video']
    for ax,p in zip(axes,PROTOCOLS):
        matrix=classes[classes.protocol==p].pivot(index='business',columns='arm',values='F1').loc[LABELS,ARMS].to_numpy()
        im=ax.imshow(matrix,vmin=0,vmax=1,cmap='Blues',aspect='auto'); ax.set_title(NAMES[p]); ax.set_xticks(range(5),ARMS,rotation=45); ax.set_yticks(range(6),short)
        for j in range(6):
            for k in range(5): ax.text(k,j,f'{matrix[j,k]:.2f}',ha='center',va='center',fontsize=7,color='white' if matrix[j,k]>.7 else 'black')
    figsave(fig,'business-F1'); finish('D24',figures=7)

if __name__=='__main__': main()
