"""Editorial and layout review only; no scientific or statistical revision."""
from core import *
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def run():
    with stage('review'):
        require(C.read(OUT/'stages/synthesize.json')['passed'],'Synthesis prerequisite')
        p=pd.read_parquet(OUT/'decision-projections.parquet');p=p[p.inner.notna()]
        s=p.groupby(['classifier_arm','scope','eta'])[['relative_logit_effect_MSE','probability_L1_mean','mapped_view_class_change_mass']].median()
        a=s.loc[('JA1','heldout-pre-offline',.1)];b=s.loc[('JA1','heldout-pre-offline',1.)]
        d=s.loc[('JA2','heldout-pre-offline',.1)]
        interpretation='## 冻结读出的具体解释\n\n'
        interpretation+=f'弱正则eta=0.1下，JA1冻结分类器对两种映射留出pre视图的类别翻转比例中位数为{a.mapped_view_class_change_mass*100:.2f}%，相对logit变化MSE中位数为{a.relative_logit_effect_MSE:.6f}，概率L1变化均值的角色中位数为{a.probability_L1_mean:.6f}。JA2冻结分类器的类别翻转比例中位数同为{d.mapped_view_class_change_mass*100:.2f}%。eta=1下，JA1冻结分类器相应翻转比例为{b.mapped_view_class_change_mass*100:.2f}%，相对logit变化MSE为{b.relative_logit_effect_MSE:.6f}。\n\n'
        interpretation+='这些角色内值说明精确身份增量不仅改变恢复坐标，也可以作用到当前冻结模型的相对决策分数。因此，不能把本轮负结果一概归为“没有使用对应”或“差全部位于分类器看不见的方向”。但翻转可以修正或引入错误，而且这里输入的是离线映射pre视图；实际攻击输入为真实post。两者不能混用。\n\n'
        interpretation+='在同eta、t=0的已有内层真实post预测中，eta=0.1时JA1减JA2的角色平均未覆盖F1差，在SS、VLESS、VMess为负，在Trojan为正；其他eta也有方向不同。这些仅是固定候选描述，不是新外层主检验，也不据此选择eta。最终JA1与JA2的原家族区间跨零，不能宣布等效或认为“只需放松正则就能赢”。\n\n'
        doc=DOC/'detailed-report.md';body=doc.read_text(encoding='utf-8')
        marker='## 同候选与最终选择的区别';require(body.count(marker)==1,'Review insertion guard')
        textfile(doc,body.replace(marker,interpretation+marker))
        # Dedicated colorbar axis fixes the overlap found during actual PNG inspection.
        bb=pd.read_parquet(OUT/'block-effects.parquet');bb=bb[bb.inner.notna()]
        mm=pd.read_parquet(OUT/'moment-decomposition.parquet');mm=mm[mm.inner.notna()]
        bb=bb.merge(mm[['role_id','eta','delta_matrix_norm']],on=['role_id','eta'],validate='many_to_one')
        bb['normalized_block_norm']=bb.delta_coefficient_norm/bb.delta_matrix_norm.replace(0,np.nan)
        plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9})
        fig=plt.figure(figsize=(15,5));grid=fig.add_gridspec(1,5,width_ratios=[1,1,1,1,.045],left=.12,right=.93,bottom=.36,top=.89,wspace=.16)
        axes=[]
        for i,proto in enumerate(C.PROTOCOLS):
            ax=fig.add_subplot(grid[0,i]);axes.append(ax)
            z=bb[bb.calibration.eq(proto)&bb.eta.eq(1)].groupby(['output_block','input_block']).normalized_block_norm.mean().unstack().loc[C.FEATURES,C.FEATURES]
            im=ax.imshow(z,vmin=0,vmax=.5,cmap='viridis');ax.set_title(proto+' eta=1')
            ax.set_xticks(range(10),C.FEATURES,rotation=90,fontsize=7)
            ax.set_yticks(range(10),C.FEATURES if i==0 else ['']*10,fontsize=7)
        cax=fig.add_subplot(grid[0,4]);fig.colorbar(im,cax=cax,label='Role-normalized block norm (not information fraction)')
        for ext in ['png','pdf']:fig.savefig(DOC/'figures'/('cross-block-effects.'+ext),dpi=180,bbox_inches='tight')
        plt.close(fig)
        manifest=C.read(OUT/'figure-manifest.json');manifest['files']={C.rel(v):C.sha(v) for v in (DOC/'figures').iterdir()}
        manifest['layout_revision']='dedicated colorbar axis after PNG review; source data and scales unchanged'
        write(OUT/'figure-manifest.json',manifest)
        write(OUT/'editorial-review.json',{'passed':True,'scientific_models_changed':False,'new_statistics':False,
            'concrete_frozen_readout_interpretation_added':True,'heatmap_overlap_fixed':True,
            'new_primary_tests':0,'relative_plot_scales_unchanged':True})
if __name__=='__main__':run()
