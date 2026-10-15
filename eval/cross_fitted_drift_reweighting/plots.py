"""Complete outcome and intervention figures; CPU rendering of frozen artifacts."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from common import *
def main():
    start('plots'); dst=OUT/'figures'; dst.mkdir(parents=True,exist_ok=True)
    plt.rcParams.update({'font.size':10,'savefig.dpi':180})
    summary=pd.read_parquet(OUT/'scores/protocol-summary.parquet'); mainc=pd.read_parquet(OUT/'comparisons/main-contrasts.parquet')
    fig,axs=plt.subplots(1,2,figsize=(13,4.5),layout='constrained')
    mat=summary.pivot(index='protocol',columns='arm',values='F1').loc[PROTOCOLS,ARMS]
    for k,a in enumerate(ARMS): axs[0].bar(np.arange(4)+(k-2)*.15,mat[a],width=.145,label=a)
    axs[0].set(xticks=np.arange(4),xticklabels=PROTOCOLS,ylabel='Six-class macro-F1',ylim=(0,1)); axs[0].legend(ncol=3)
    for k,row in enumerate(mainc.itertuples()):
        axs[1].hlines(k,row.family_lower,row.family_upper,color='tab:blue',lw=3)
        axs[1].plot(row.point,k,'o',color='black'); axs[1].text(row.family_upper+.002,k,f'{row.point:+.4f}',va='center')
    axs[1].axvline(0,color='grey',ls='--'); axs[1].set(yticks=range(3),yticklabels=mainc.comparison,xlabel='Equal-deployment F1 difference (98.333% CI)')
    fig.savefig(dst/'outcomes.png'); fig.savefig(dst/'outcomes.pdf'); plt.close(fig)
    dirs=pd.concat([pd.read_parquet(OUT/f'weights/{p}-directions.parquet').assign(phase=p) for p in ['inner','outer']])
    weights_table=pd.read_parquet(OUT/'weights/inner-summary.parquet'); activity=pd.read_parquet(OUT/'diagnostics/inner-base-activity.parquet')
    fig,axs=plt.subplots(2,2,figsize=(12,8),layout='constrained')
    for a in ARMS[2:]:
        d=dirs[(dirs.arm==a)&(dirs.phase=='inner')]; axs[0,0].plot(np.arange(len(d)),d.difference,'o',ms=3,label=a)
    axs[0,0].axhline(0,color='grey',ls='--'); axs[0,0].set(xlabel='Inner role index',ylabel='OOF CE high minus low'); axs[0,0].legend()
    for a in ARMS[2:]:
        d=weights_table[(weights_table.arm==a)&(weights_table.setting==4)]; axs[0,1].plot(np.arange(len(d)),d.ESS/72,'o',ms=3,label=a)
    axs[0,1].axhline(25/34,color='grey',ls='--'); axs[0,1].set(xlabel='Inner role index (r=4)',ylabel='Visit effective sample size / 72',ylim=(.7,1.02))
    for a in ARMS[2:]:
        d=activity[(activity.arm==a)&(activity.setting==4)]; axs[1,0].plot(np.arange(len(d)),d.change_gradient_norm,'o',ms=3,label=a)
    axs[1,0].set(xlabel='Inner role index (r=4)',ylabel='Fixed intervention gradient norm',yscale='log')
    choices=pd.DataFrame(read(OUT/'selection/choices.json')); counts=choices[choices.arm.isin(ARMS[2:])].groupby(['arm','setting']).size().unstack(fill_value=0).reindex(columns=RATIOS,fill_value=0)
    counts.plot.bar(ax=axs[1,1],rot=0); axs[1,1].set(ylabel='Selected outer roles (20 / arm)',xlabel=''); axs[1,1].legend(title='r')
    fig.savefig(dst/'interventions.png'); fig.savefig(dst/'interventions.pdf'); plt.close(fig)
    classes=pd.read_parquet(OUT/'scores/class-summary.parquet'); flips=pd.read_parquet(OUT/'scores/error-flip-summary.parquet')
    fig,axs=plt.subplots(1,2,figsize=(13,6),layout='constrained')
    mat=classes[classes.arm=='RW4'].pivot(index='business',columns='protocol',values='F1').loc[LABELS,PROTOCOLS]
    image=axs[0].imshow(mat,vmin=0,vmax=1,cmap='viridis'); axs[0].set(xticks=range(4),xticklabels=PROTOCOLS,yticks=range(6),yticklabels=[s.replace('::',' / ') for s in LABELS])
    for j in range(6):
        for k in range(4): axs[0].text(k,j,f'{mat.iloc[j,k]:.3f}',ha='center',va='center',color='white' if mat.iloc[j,k]<.6 else 'black')
    fig.colorbar(image,ax=axs[0],label='RW4 class F1')
    f=flips.groupby('reference')[['repaired','added']].sum().reindex(ARMS[:-1]); f.plot.bar(ax=axs[1],rot=0,color=['tab:green','tab:red'])
    axs[1].set(ylabel='Visits (480 total)',xlabel='RW4 compared with'); fig.savefig(dst/'classes-and-flips.png'); fig.savefig(dst/'classes-and-flips.pdf'); plt.close(fig)
    complete(dst,plots_complete=True); finish('RW26',figures=3)
if __name__=='__main__': main()
