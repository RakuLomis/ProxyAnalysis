"""Publication-style static figures, computed from the same frozen result tables."""
from itertools import combinations
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from common import OUT, PROTOCOLS, FEATURES
from bins import labels, load
from weights import mass

NAMES={'shadowsocks':'SS','vless':'VLESS','trojan':'Trojan','vmess':'VMess','anytls':'AnyTLS'}
DEST=OUT/'figures'


def save(fig,name):
    fig.savefig(DEST/(name+'.png'),dpi=180,bbox_inches='tight')
    fig.savefig(DEST/(name+'.pdf'),bbox_inches='tight')
    plt.close(fig)


def run():
    DEST.mkdir(exist_ok=True)
    plt.rcParams.update({'font.size':9,'axes.spines.top':False,'axes.spines.right':False})
    table=pd.read_parquet(OUT/'probability-tables/joint-and-conditional.parquet')
    x=table[table.weighting.eq('hierarchical')&table.feature.eq('U_down')]
    fig,axes=plt.subplots(4,2,figsize=(11,14),layout='constrained')
    maxmass=x.weighted_mass.max()
    for i,p in enumerate(PROTOCOLS):
        t=x[x.protocol.eq(p)]
        for j,(column,title,maximum) in enumerate([('weighted_mass','Joint mass',maxmass),('conditional_empirical','Conditional probability',1)]):
            mat=t.pivot(index='A',columns='B',values=column).to_numpy()
            cmap=plt.get_cmap('viridis').copy();cmap.set_bad('#dddddd')
            im=axes[i,j].imshow(np.ma.masked_invalid(mat),origin='lower',vmin=0,vmax=maximum,cmap=cmap)
            axes[i,j].set(title=NAMES[p]+' '+title,xlabel='Post unique down bytes',ylabel='Pre unique down bytes')
            axes[i,j].set_xticks(range(9),labels('U_down'),rotation=50,ha='right',fontsize=7)
            axes[i,j].set_yticks(range(9),labels('U_down'),fontsize=7)
            fig.colorbar(im,ax=axes[i,j],shrink=.7)
    save(fig,'unique-down-joint-and-kernel')
    info=pd.read_parquet(OUT/'information/information-summary.parquet')
    info=info[info.weighting.eq('hierarchical')&info.estimator.eq('empirical_true')]
    fig,axes=plt.subplots(1,2,figsize=(13,4),layout='constrained')
    for ax,metric,title in zip(axes,['MI','H_B_given_A'],['Discrete paired MI (bits)','Conditional entropy H(B|A) (bits)']):
        mat=info.pivot(index='protocol',columns='feature',values=metric).reindex(index=PROTOCOLS,columns=FEATURES)
        im=ax.imshow(mat.to_numpy(),vmin=0,cmap='viridis',aspect='auto')
        ax.set_xticks(range(len(FEATURES)),FEATURES,rotation=60,ha='right',fontsize=8)
        ax.set_yticks(range(4),[NAMES[p] for p in PROTOCOLS]);ax.set_title(title)
        fig.colorbar(im,ax=ax,shrink=.7)
    save(fig,'information-profile')
    contrasts=pd.read_parquet(OUT/'comparisons/composite-contrasts.parquet')
    primary=contrasts[contrasts.variant.eq('primary')]
    fig,ax=plt.subplots(figsize=(8,5),layout='constrained')
    for j,name in enumerate(['M0-M1','M2-M1']):
        t=primary[primary.contrast.eq(name)].set_index('protocol').loc[PROTOCOLS]
        y=np.arange(4)+(j-.5)*.18
        ax.hlines(y,t.family_low,t.family_high,color=['#1b78a4','#d86f25'][j],linewidth=2)
        ax.scatter(t.gain_bits,y,label=name,color=['#1b78a4','#d86f25'][j])
    ax.axvline(0,color='gray',linestyle='--');ax.set_yticks(range(4),[NAMES[p] for p in PROTOCOLS])
    ax.set(xlabel='Composite held-out log-loss gain (bits)',title='True correspondence gains; family-adjusted content-cluster intervals')
    ax.legend();save(fig,'content-heldout-gains')
    distance=pd.read_parquet(OUT/'comparisons/kernel-distances.parquet')
    distance['pair']=distance.protocol_1.map(NAMES)+' / '+distance.protocol_2.map(NAMES)
    mat=distance.groupby(['pair','feature']).conditional_JS_bits.mean().unstack().reindex(columns=FEATURES)
    fig,ax=plt.subplots(figsize=(10,4),layout='constrained')
    cmap=plt.get_cmap('magma').copy();cmap.set_bad('#dddddd')
    im=ax.imshow(np.ma.masked_invalid(mat.to_numpy()),vmin=0,cmap=cmap,aspect='auto')
    ax.set_xticks(range(len(FEATURES)),FEATURES,rotation=60,ha='right',fontsize=8)
    ax.set_yticks(range(len(mat)),mat.index);ax.set_title('Training-only common-support kernel JS; mean of overlapping folds')
    fig.colorbar(im,ax=ax,label='JS bits',shrink=.7);save(fig,'common-support-kernel-JS')
    zero=pd.read_parquet(OUT/'information/zero-direction-summary.parquet')
    zero=zero[zero.weighting.eq('hierarchical')&zero.feature.eq('U_down')].set_index('protocol').reindex(PROTOCOLS)
    fig,ax=plt.subplots(figsize=(7,4),layout='constrained')
    ax.bar([NAMES[p] for p in PROTOCOLS],zero.positive_post_given_zero_pre,color='#1b78a4')
    for i,(_,r) in enumerate(zero.iterrows()):ax.text(i,min(float(r.positive_post_given_zero_pre)+.035,1.04),f'n={int(r.zero_pre_pairs)}',ha='center')
    ax.set(ylim=(0,1.1),ylabel='P(post U_down > 0 | pre U_down = 0)',title='Observed zero-input downlink; content/visit/flow weighting')
    save(fig,'zero-downlink-conversion')
    f=pd.read_parquet(OUT/'features/paired-flow-features.parquet')
    fig,axes=plt.subplots(2,4,figsize=(13,6),layout='constrained')
    for col,p in enumerate(PROTOCOLS):
        g=f[f.protocol.eq(p)].copy();w=mass(g);l=load(g.pre_U_up+g.pre_U_down)
        for row,d in enumerate(['up','down']):
            delta=(g['post_U_'+d]-g['pre_U_'+d]).to_numpy()
            for state in range(3):
                mask=l==state
                order=np.argsort(delta[mask]);v=delta[mask][order];ww=w[mask][order]
                if not len(v):continue
                quant=v[np.minimum(np.searchsorted(np.cumsum(ww)/ww.sum(),[.25,.5,.75]),len(v)-1)]
                axes[row,col].vlines(state,quant[0],quant[2],color='#1b78a4',linewidth=3)
                axes[row,col].plot(state,quant[1],'o',color='#d86f25')
            axes[row,col].set_xticks(range(3),['<4KiB','4-64KiB','>=64KiB'],rotation=25,fontsize=8)
            axes[row,col].set(title=NAMES[p]+' '+d,ylabel='Delta unique bytes')
    save(fig,'unique-delta-by-fixed-pre-load')


if __name__=='__main__':run()
