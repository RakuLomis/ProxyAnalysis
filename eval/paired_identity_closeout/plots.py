from core import *
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def run():
    with stage('plots'):
        require(C.read(OUT/'projection-verification.json')['passed'],'Projection prerequisite')
        figdir=DOC/'figures';figdir.mkdir(parents=True,exist_ok=True)
        a=pd.read_parquet(OUT/'moment-decomposition.parquet');a=a[a.inner.notna()]
        p=pd.read_parquet(OUT/'decision-projections.parquet');p=p[p.inner.notna()]
        b=pd.read_parquet(OUT/'block-effects.parquet');b=b[b.inner.notna()]
        plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'axes.spines.top':False,'axes.spines.right':False})
        def finish(fig,name):
            fig.tight_layout();fig.savefig(figdir/(name+'.png'),dpi=180);fig.savefig(figdir/(name+'.pdf'));plt.close(fig)
        fig,ax=plt.subplots(figsize=(8,3.8))
        rr=pd.read_parquet(OUT/'identity-residuals.parquet').groupby('check').normalized.max().sort_values()
        ax.barh(rr.index,rr.values);ax.axvline(1e-10,color='red',ls='--',label='fixed gate 1e-10');ax.set_xscale('log')
        ax.set_xlabel('Maximum normalized residual (zero omitted on log axis)');ax.legend();finish(fig,'identity-verification')
        fig,axes=plt.subplots(1,4,figsize=(12.4,3.6),sharey=True)
        for ax,proto in zip(axes,C.PROTOCOLS):
            z=a[a.calibration.eq(proto)]
            for g,d in z.groupby('group'):
                q=d.groupby('eta').C_effect_MSE.median();ax.plot(q.index,q.values,marker='o',label=g)
            ax.set_xscale('log');ax.set_yscale('log');ax.set_title(proto);ax.set_xlabel('eta');ax.legend(fontsize=8)
        axes[0].set_ylabel('C mapped-view change MSE, median per role');finish(fig,'within-effect-by-eta')
        norms=a[['role_id','eta','delta_matrix_norm']]
        b=b.merge(norms,on=['role_id','eta'],validate='many_to_one')
        b['normalized_block_norm']=b.delta_coefficient_norm/b.delta_matrix_norm.replace(0,np.nan)
        fig,axes=plt.subplots(1,4,figsize=(14,4.2),sharey=True)
        # eta=1 is one registered panel, not selected from outcomes; all eta remain in tables.
        for ax,proto in zip(axes,C.PROTOCOLS):
            z=b[b.calibration.eq(proto)&b.eta.eq(1)].groupby(['output_block','input_block']).normalized_block_norm.mean().unstack().loc[C.FEATURES,C.FEATURES]
            im=ax.imshow(z,vmin=0,vmax=.5,cmap='viridis');ax.set_title(proto+' eta=1')
            ax.set_xticks(range(10),C.FEATURES,rotation=90,fontsize=7);ax.set_yticks(range(10),C.FEATURES,fontsize=7)
        fig.colorbar(im,ax=axes.ravel().tolist(),fraction=.025,pad=.02,label='Role-normalized block norm (not information fraction)')
        fig.subplots_adjust(bottom=.30,right=.91,wspace=.12)
        for ext in ['png','pdf']:fig.savefig(figdir/('cross-block-effects.'+ext),dpi=180,bbox_inches='tight')
        plt.close(fig)
        fig,axes=plt.subplots(1,2,figsize=(10,4))
        for ax,arm in zip(axes,['JA1','JA2']):
            z=p[p.scope.eq('heldout-pre-offline')&p.classifier_arm.eq(arm)]
            for proto,d in z.groupby('calibration'):
                d=d[(d.mapping_effect_MSE>0)&(d.relative_logit_effect_MSE>0)]
                ax.scatter(d.mapping_effect_MSE,d.relative_logit_effect_MSE,s=8,alpha=.28,label=proto)
            ax.set_xscale('log');ax.set_yscale('log');ax.set_xlabel('Offline mapped-pre change MSE');ax.set_title('Frozen '+arm+' classifier');ax.legend(fontsize=7)
        axes[0].set_ylabel('Centered-logit change MSE');finish(fig,'mapped-view-and-decision')
        rec=pd.read_parquet(REPORT/'diagnostics/recovery.parquet');rec=rec[rec.inner.isna()].groupby(['arm','calibration']).MSE.mean().unstack(0)
        actual=pd.read_parquet(CLOSE/'scores/targets.parquet').pivot(index='target',columns='arm',values='F1_uncovered')
        fig,axes=plt.subplots(1,2,figsize=(9,3.8))
        idx=np.arange(4);protos=C.PROTOCOLS
        axes[0].bar(idx,(rec.JA2-rec.JA1).loc[protos]);axes[0].set_title('Recovery MSE: JA2 minus JA1')
        axes[1].bar(idx,(actual.JA1-actual.JA2).loc[protos]*100);axes[1].set_title('Actual post F1: JA1 minus JA2 (pp)')
        for ax in axes:ax.set_xticks(idx,['SS','VLESS','Trojan','VMess']);ax.axhline(0,color='gray',ls='--')
        fig.suptitle('Selected methods; different eta/t possible; descriptive only');finish(fig,'recovery-and-actual-classification')
        write(OUT/'figure-manifest.json',{'files':{C.rel(v):C.sha(v) for v in figdir.iterdir()},
            'sources':{C.rel(v):C.sha(v) for v in [OUT/'moment-decomposition.parquet',OUT/'block-effects.parquet',OUT/'decision-projections.parquet',REPORT/'diagnostics/recovery.parquet',CLOSE/'scores/targets.parquet']},
            'eta_panel_not_selection':1.,'all_eta_in_numeric_tables':True})
if __name__=='__main__':run()
