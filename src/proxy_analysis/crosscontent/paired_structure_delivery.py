"""Content-equal summaries and figures for the completed P5/P6 partial delivery."""
import argparse
import numpy as np
from .paired_structure_contract import CONFIG, verify,validate_complete,seal
from .count_decomposition import grouped
from ..paired_information.prepare import table
from ..reproducibility.preflight import write_json,write_table


def run(config=CONFIG):
    cfg,source,legacy,root=verify(config);out=root/'report'/'p5-p6'
    if out.exists():validate_complete(out);return
    validate_complete(root/'audit/p5-p6')
    margins=table(root/'p6-diagnostics/margin-contributions.parquet')
    matching=table(root/'p6-diagnostics/matched-margin-shifts.parquet')
    transitions=table(root/'p6-diagnostics/confidence-transitions.parquet')
    shifts=table(root/'p6-diagnostics/standardized-shifts.parquet')
    content=[];summary=[];confidence=[]
    keys=['task','protocol','representation','stage']
    for key,rs in grouped(margins,keys+['content_id']):
        family=['scalar'] if key[2]=='scalar14' else ['scalar','length','IAT','curve']
        means={f:float(np.mean([r[f] for r in rs])) for f in family}
        content.append({**dict(zip(keys+['content_id'],key)),
            'mean_loss_bits':float(np.mean([r['loss_bits'] for r in rs])),
            'error_fraction':float(np.mean([not r['correct'] for r in rs])),
            'worst_mean_family':min(means,key=means.get),
            **{f'mean_margin_{f}':v for f,v in means.items()}})
    for key,rs in grouped(content,keys):
        family=['scalar'] if key[2]=='scalar14' else ['scalar','length','IAT','curve']
        summary.append({**dict(zip(keys,key)),'contents':len(rs),
            'CE_bits':float(np.mean([r['mean_loss_bits'] for r in rs])),
            'error_fraction':float(np.mean([r['error_fraction'] for r in rs])),
            'worst_mean_family_counts':{f:sum(r['worst_mean_family']==f for r in rs) for f in family},
            **{f'mean_margin_{f}':float(np.mean([r[f'mean_margin_{f}'] for r in rs])) for f in family}})
    for key,rs in grouped(transitions,keys):
        confidence.append({**dict(zip(keys,key)),
            'wrong_to_correct':sum(not r['M0_correct'] and r['M2_correct'] for r in rs),
            'correct_to_wrong':sum(r['M0_correct'] and not r['M2_correct'] for r in rs),
            'same_label':sum(r['same_label'] for r in rs),
            'mean_CE_advantage':float(np.mean([r['CE_advantage'] for r in rs]))})
    out.mkdir(parents=True);write_table(out/'content-margins.parquet',content)
    write_json(out/'content-equal-summary.json',summary);write_json(out/'confidence-summary.json',confidence)
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,axes=plt.subplots(1,2,figsize=(12,5))
    for ax,task in zip(axes,['six_business','youtube_activity']):
        for idx,protocol in enumerate(cfg['protocols']):
            rs=[r for r in matching if r['task']==task and r['protocol']==protocol and r['representation']=='distribution157']
            fam=['scalar','length','IAT','curve'];values=[np.mean([r[f+'_shift'] for r in rs]) for f in fam]
            ax.bar(np.arange(4)+(idx-.5)*.35,values,.35,label=protocol)
        ax.set_xticks(range(4),fam);ax.set_title(task);ax.axhline(0,color='black',linewidth=.5)
        ax.set_ylabel('Mean target - source margin (fixed target competitor)');ax.legend()
    fig.tight_layout();fig.savefig(out/'matched-margin-shift.png',dpi=160);plt.close(fig)
    fig,ax=plt.subplots(figsize=(11,5))
    selected=[r for r in shifts if r['task']=='six_business' and r['representation']=='distribution157' and r['stage']=='cross']
    for protocol in cfg['protocols']:
        rs=[r for r in selected if r['protocol']==protocol];features=sorted({r['feature'] for r in rs})
        values=[np.mean([r['fraction_gt_5'] for r in rs if r['feature']==f]) for f in features]
        ax.plot(range(len(features)),values,label=protocol)
    ax.set_xlabel('Feature index (lexicographic name order; exact values in standardized-shifts.parquet)')
    ax.set_ylabel('Target fraction |z| > 5, mean over source folds');ax.legend();fig.tight_layout()
    fig.savefig(out/'target-standardized-shift.png',dpi=160);plt.close(fig)
    seal(out,passed=True,P7_formal_complete=False)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--config',default=str(CONFIG));run(p.parse_args().config)
