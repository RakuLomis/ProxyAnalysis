"""Additional frozen measurement panel; no raw traffic processing."""
import build_all as b
import numpy as np
import matplotlib.pyplot as plt

def main():
    d=b.load();metrics=['packet_count','transport_bytes','burst_count','fr_runs']
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':8,'pdf.fonttype':42})
    fig,axes=plt.subplots(1,2,figsize=(7.1,2.4),layout='constrained')
    for i,p in enumerate(['SHADOWSOCKS','VLESS']):
        rows=[b.select(d['transform'],cohort='0916_240',protocol=p,metric=m,level='all',group='all') for m in metrics]
        x=np.arange(4)+(i-.5)*.34
        axes[0].bar(x,[r['exp_median_content_delta'] for r in rows],.34,color=b.COLORS[i],label='SS' if i==0 else 'VLESS')
        axes[1].bar(x,[r['median_within_content_MAD'] for r in rows],.34,color=b.COLORS[i])
    for ax in axes:
        ax.set_xticks(range(4),['Packets','Payload','Bursts','FR runs']);ax.grid(axis='y',alpha=.15);ax.set_axisbelow(True)
    axes[0].axhline(1,color='.5',ls='--',lw=.7);axes[0].set_ylabel('Typical post/pre ratio');axes[0].legend(fontsize=7)
    axes[1].set_ylabel('Within-content MAD (log ratio)')
    b.save(fig,'transformations')
    rows=[r for r in d['transform'] if r['cohort']=='0916_240' and r['level']=='all']
    b.table('transform',['Deploy.','Metric','Ratio / JS','MAD','IQR'],
       [[{'SHADOWSOCKS':'SS','VLESS':'VL'}[r['protocol']],r['metric'].replace('_',r'\_'),f"{(r['exp_median_content_delta'] if r['exp_median_content_delta'] is not None else r['median_content_delta']):.4f}",f"{r['median_within_content_MAD']:.4f}",f"{r['median_within_content_IQR']:.4f}"] for r in rows],'llrrr')

if __name__=='__main__':main()
