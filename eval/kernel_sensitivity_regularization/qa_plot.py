"""Post-result visual QA only: consistent arm colors, no fitting or selection."""
from pathlib import Path
import hashlib
import json
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'outputs/kernel-sensitivity-regularization-20261005/run-01'

def digest(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def run():
    source=OUT/'explanations/matrix-spectra.parquet'
    frame=pd.read_parquet(source)
    fig,axes=plt.subplots(1,2,figsize=(10,4))
    colors={'KSR2':'tab:blue','KSR3':'tab:orange','KSR4':'tab:green'}
    for j,p in enumerate(['shadowsocks','vless','trojan','vmess']):
        for ai,arm in enumerate(colors):
            df=frame[(frame.protocol==p)&(frame.arm==arm)&(frame.coordinates=='raw')]
            x=[j+(ai-1)*.15]*len(df)
            axes[0].scatter(x,df.trace,s=18,color=colors[arm],label=arm if j==0 else None)
            axes[1].scatter(x,df.effective_rank,s=18,color=colors[arm])
    axes[0].set_yscale('log'); axes[0].set_ylabel('Native standardized trace (log scale)'); axes[0].legend()
    axes[1].set_ylabel('Effective rank')
    for ax in axes: ax.set_xticks(range(4),['SS','VLESS','Trojan','VMess'])
    fig.tight_layout(); outputs=[]
    for ext in ['png','pdf']:
        path=OUT/'figures'/f'matrix-scale-spectrum-reviewed.{ext}'; fig.savefig(path,dpi=180); outputs.append(path)
    plt.close(fig)
    record={'purpose':'post-result presentation only; consistent arm colors across protocols',
         'classification_fitting_or_selection':False,'saved_numeric_results_changed':False,
         'source_sha256':digest(__file__),'data_sha256':digest(source),
         'original_scientific_plot_source_unchanged':True,
         'reviewed_figures_sha256':{p.name:digest(p) for p in outputs}}
    (OUT/'manifests/visual-qa.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')

if __name__=='__main__': run()
