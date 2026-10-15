"""Post-result visual QA companion: expose the small margins with an explicit scale.

No change to the sealed analysis, fixed example membership, predictions or original figures.
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from common import *

def run():
    values=pd.read_parquet(OUT/'explanations/visit-bin-contributions.parquet')
    examples=pd.read_parquet(OUT/'explanations/fixed-example-visits.parquet')
    short=['Bing search','MDN docs','GitHub repo','Wikipedia','YouTube search','YouTube play']
    fig,axes=plt.subplots(4,1,figsize=(14,13))
    for ax,p in zip(axes,PROTOCOLS):
        names=examples[examples.protocol.eq(p)].sort_values('label_id').visit_id
        matrix=values[values.visit_id.isin(names)].groupby(['visit_id','feature']).value.sum().unstack().reindex(index=names,columns=FEATURES)
        extent=max(float(np.abs(matrix.to_numpy()).max()),1e-12)
        im=ax.imshow(matrix,cmap='RdBu_r',vmin=-extent,vmax=extent,aspect='auto')
        for i in range(6):
            for j in range(10):
                ax.text(j,i,f'{matrix.iloc[i,j]:.4f}',ha='center',va='center',fontsize=8,
                        color='white' if abs(matrix.iloc[i,j])>.65*extent else 'black')
        ax.set_xticks(range(10),FEATURES,rotation=30,ha='right',fontsize=9)
        ax.set_yticks(range(6),short,fontsize=9)
        ax.set_title(p+' fixed-ID examples; individual panel scales; log-score contribution, not causal effect')
        fig.colorbar(im,ax=ax,fraction=.025,pad=.02,label='Margin contribution (natural log score)')
    fig.tight_layout()
    for suffix in ['png','pdf']:
        fig.savefig(OUT/'figures'/('fixed-example-contributions-scaled.'+suffix),dpi=180,bbox_inches='tight')
    plt.close(fig)
    write(OUT/'manifests/postprocessing-source-manifest.json',{'stage':'visual QA after frozen results',
          'source_sha256':{rel(Path(__file__)):sha(Path(__file__))},
          'purpose':'Companion contribution plot with numeric values and colorbars; original fixed examples unchanged',
          'sealed_scientific_sources_modified':False,'models_or_predictions_modified':False})

if __name__=='__main__':
    run()
