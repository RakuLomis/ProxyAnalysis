"""Readable layout of frozen error counts; changes no analysis or model."""
from run import *
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ledger=pd.read_parquet(OUT/'error-ledger.parquet')
index=pd.read_parquet(OUT/'figure-content-index.parquet')
fig,axes=plt.subplots(1,3,figsize=(12,10),layout='constrained',sharey=True)
for ax,name in zip(axes,['S2-S1','S2-S4','L3-S2']):
    g=ledger[ledger.comparison==name]
    x=g.assign(net=(g.state=='corrected').astype(int)-(g.state=='new_error').astype(int)).pivot_table(index='content_id',columns='seed',values='net',aggfunc='sum').reindex(index.content_id)
    im=ax.imshow(x,vmin=-4,vmax=4,cmap='RdBu',aspect='auto')
    ax.set_title(name+' net corrections');ax.set_xticks(range(3),['20260918','20260919','20260920'],rotation=30,ha='right');ax.set_yticks(range(30),index.row)
    ax.set_xlabel('Seed')
axes[0].set_ylabel('Content row (complete mapping in report appendix)')
fig.colorbar(im,ax=axes,label='Corrected minus new errors (4 visits/content/seed)')
fig.savefig(DOC/'figures/content-changes.png',dpi=160);plt.close(fig)
(DOC/'content-index.md').write_text('# 内容行号完整映射\n\n'+table(index)+'\n',encoding='utf-8')
write_json(OUT/'implementation-manifest.json',{'files':{str(p):digest(p) for p in Path(__file__).parent.glob('*.py')},'tests':str(ROOT/'tests/unit/test_record_time_localization.py'),'old_contract_unchanged':True})
