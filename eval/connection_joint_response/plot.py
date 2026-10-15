"""Plots from fixed C-only diagnostic caches; no model or feature selection."""
from common import *
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def run():
    s=pd.read_parquet(OUT/'diagnostics/scores/content-scores.parquet')
    r=s.groupby(['target','role_id','block','arm']).CE_nats.mean().reset_index()
    p=r.groupby(['target','block','arm']).CE_nats.mean().reset_index()
    fig,axes=plt.subplots(2,2,figsize=(10,7),constrained_layout=True)
    for g,ax in zip(NAMES,axes.flat):
        q=p[p.block.eq(g)].pivot(index='target',columns='arm',values='CE_nats').reindex(PROTOCOLS)
        xx=np.arange(4)
        for i,a in enumerate(['M0','KP','KG']):ax.bar(xx+(i-1)*.24,q[a],width=.24,label=a)
        ax.set_xticks(xx,['SS','VLESS','Trojan','VMess']); ax.set_title(g); ax.set_ylabel('C-only heldout CE (nats)')
        ax.legend()
    dest=OUT/'figures'; dest.mkdir(parents=True,exist_ok=True)
    fig.savefig(dest/'C-conditional-predictive-risk.png',dpi=180); plt.close(fig)
    native=pd.read_parquet(OUT/'diagnostics/scores/native-C-responses.parquet')
    native['target']=native.role_id.str.split('/').str[2]
    rows=[]
    for key,d in native.groupby(['target','role_id','direction','pre_load_bin','pre_empty']):
        for content,q in d.groupby('content_id'):
            w=q.flow_mass.to_numpy(); denominator=w.sum()
            for f in ['delta_U','delta_E','pre_U_per_E','post_U_per_E']:
                valid=q[f].notna().to_numpy(); vw=w*valid
                value=float(vw@q[f].fillna(0).to_numpy()/vw.sum()) if vw.sum()>0 else np.nan
                rows.append(dict(zip(['target','role_id','direction','pre_load_bin','pre_empty'],key),
                    content_id=content,metric=f,value=value,within_content_mass=denominator))
    content=pd.DataFrame(rows); save(content,OUT/'diagnostics/scores/load-stratified-content-responses.parquet')
    fig,axes=plt.subplots(1,2,figsize=(10,4),constrained_layout=True)
    for direction,ax in zip(['up','down'],axes):
        q=content[content.direction.eq(direction)&content.metric.eq('delta_E')&~content.pre_empty]
        byrole=q.groupby(['target','role_id','pre_load_bin']).value.mean().reset_index()
        z=byrole.groupby(['target','pre_load_bin']).value.mean()
        for protocol in PROTOCOLS:
            t=z.loc[protocol]; ax.plot(t.index,t.values,marker='o',label=protocol)
        ax.set_title(direction); ax.set_xlabel('Fixed pre unique-byte load bin'); ax.set_ylabel('Mean observed event delta')
        ax.set_xticks(range(4)); ax.legend(fontsize=8)
    fig.savefig(dest/'C-load-dependent-event-response.png',dpi=180); plt.close(fig)
    write(OUT/'diagnostics/figures.json',{'figures':[rel(p) for p in dest.glob('*.png')],
         'new_classifier_fits':0,'H_reads':0,'interpretation':'descriptive C-only response; not protocol chunk counts'})

if __name__=='__main__':run()
