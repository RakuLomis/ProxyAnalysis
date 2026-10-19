"""Visualize existing predictions only; no training or new data decoding."""
from pathlib import Path
import json,hashlib
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'outputs/recent-confusion-matrix-review-20261017'
LABELS=['bing.com::search_results_view','developer.mozilla.org::document_view','github.com::repository_view','wikipedia.org::article_view','youtube.com::search_results_view','youtube.com::video_playback']
SHORT=['Bing','MDN','GitHub','Wiki','YT-search','YT-video']
SPECS={
 'DA-pilot':('outputs/decision-aware-forward-drift-20261017/pilot-03/scores/labeled-predictions.parquet','pipeline',['B0','DA-P','DA-G','Full-P']),
 'Full-NER1':('outputs/deproxy-moment-game-v1-20261016/full-ner1-01/scores/labeled-predictions.parquet','pipeline',['B0','F-P-FUSE']),
 'JAT1':('outputs/joint-associated-post-classifier-20261016/run-01/scores/labeled-predictions.parquet','arm',['B0','JP']),
 'ST1':('outputs/shape-source-task-attribution-20261016/run-01/scored-predictions.parquet','arm',['PP','GP']),
}

def main():
    OUT.mkdir(parents=True,exist_ok=True);results={};bindings={}
    for tag,(path,key,arms) in SPECS.items():
        p=ROOT/path;d=pd.read_parquet(p);bindings[path]=hashlib.sha256(p.read_bytes()).hexdigest();results[tag]={}
        for arm in arms:
            part=d[d[key].eq(arm)];y=part.label_id.map(dict(zip(LABELS,range(6)))).to_numpy(int);z=part.prediction.to_numpy(int)
            cm=np.bincount(y*6+z,minlength=36).reshape(6,6);pct=100*cm/cm.sum(1)[:,None]
            results[tag][arm]=dict(counts=cm.tolist(),row_percent=pct.tolist(),logical_rows=len(part),unique_visits=part.visit_id.nunique(),
                unique_contents=part.content_id.nunique(),true_row_counts=cm.sum(1).tolist(),descriptive_pooled_C_and_U=True,
                official_F1_not_recomputed_from_pooled_matrix=True)
    assert results['Full-NER1']['B0']['counts']==results['JAT1']['B0']['counts']
    payload=dict(labels=LABELS,short_labels=SHORT,rows='truth',columns='prediction',
        warning='Pooled C/U, masks and seeds for visualization only. Logical counts are not independent samples. Official metrics average per-scenario F1 instead.',
        input_sha256=bindings,results=results)
    (OUT/'matrices.json').write_text(json.dumps(payload,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    def draw(ax,tag,arm):
        r=results[tag][arm];a=np.array(r['row_percent']);im=ax.imshow(a,cmap='Blues',vmin=0,vmax=100)
        ax.set_xticks(range(6),SHORT,rotation=35,ha='right');ax.set_yticks(range(6),SHORT);ax.set_ylabel('True class');ax.set_xlabel('Predicted class')
        for i in range(6):
            for j in range(6):ax.text(j,i,f'{a[i,j]:.1f}',ha='center',va='center',fontsize=9,color='white' if a[i,j]>55 else 'black')
        ax.set_title(f'{tag} / {arm}\n{r["unique_contents"]} contents, {r["unique_visits"]} distinct visits',fontsize=11)
        return im
    fig,axes=plt.subplots(2,2,figsize=(11.4,10.4),constrained_layout=True)
    for ax,arm in zip(axes.flat,['B0','DA-P','DA-G','Full-P']):im=draw(ax,'DA-pilot',arm)
    fig.colorbar(im,ax=axes.ravel().tolist(),label='Row-normalized percent',shrink=.7)
    fig.suptitle('DA-FGAN1 source-only pilot: pooled six-class confusion\n192 logical predictions per true-class row; not 192 independent samples',fontsize=13)
    fig.savefig(OUT/'DA-pilot-confusion.png',dpi=170);plt.close(fig)
    fig,axes=plt.subplots(1,3,figsize=(17.5,5.2),constrained_layout=True)
    for ax,(tag,arm) in zip(axes,[('Full-NER1','B0'),('JAT1','JP'),('Full-NER1','F-P-FUSE')]):im=draw(ax,tag,arm)
    fig.colorbar(im,ax=axes.ravel().tolist(),label='Row-normalized percent',shrink=.7)
    fig.suptitle('Completed H evaluations: same 30 contents / 480 distinct visits\nPooled C/U, masks, 3 seeds; 720 logical predictions per row',fontsize=13)
    fig.savefig(OUT/'full-H-confusion.png',dpi=170);plt.close(fig)
    print(OUT)

if __name__=='__main__':main()
