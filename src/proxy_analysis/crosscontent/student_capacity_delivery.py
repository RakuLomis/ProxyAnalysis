"""Plot complete fixed N1 results; no best-seed or best-arm selection."""
import argparse
from pathlib import Path
import numpy as np
from .student_capacity import CONFIG,verify
from .paired_structure_contract import read,validate_complete,seal
from ..paired_information.prepare import table,digest
from ..reproducibility.preflight import write_json


def run(config=CONFIG):
    cfg,_,_,root=verify(config);report=root/'report';validate_complete(report)
    if not read(report/'validation.json')['passed']:raise ValueError('Audit not passed')
    out=root/'delivery'
    if out.exists():validate_complete(out);return
    metrics=read(report/'metrics-summary.json');gains=read(report/'gains-seed-average.json')
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    out.mkdir()
    for task in cfg['tasks']:
        fig,axes=plt.subplots(2,4,figsize=(17,8))
        for i,rep in enumerate(cfg['representations']):
            for j,(protocol,stage) in enumerate((p,s) for p in cfg['protocols'] for s in ['student','cross']):
                ax=axes[i,j];rs=[r for r in metrics if (r['task'],r['representation'],r['protocol'],r['stage'])==(task,rep,protocol,stage)]
                values=[next(r for r in rs if r['arm']==a) for a in cfg['arms']]
                mean=np.array([r['log_loss_bits_mean'] for r in values]);low=np.array([r['log_loss_bits_min'] for r in values]);high=np.array([r['log_loss_bits_max'] for r in values])
                ax.bar(cfg['arms'],mean);ax.errorbar(range(4),mean,yerr=[mean-low,high-mean],fmt='none',color='black',capsize=3)
                ax.set_title(f'{rep}\n{protocol} / {stage}');ax.set_ylabel('CE bits: seed mean and range')
        fig.suptitle(task);fig.tight_layout();fig.savefig(out/f'{task}-all-arms.png',dpi=150);plt.close(fig)
    settings=sorted({(r['task'],r['protocol'],r['representation'],r['stage']) for r in gains})
    fig,ax=plt.subplots(figsize=(13,9))
    for j,comparison in enumerate(['G_task','G_pair','G_soft']):
        rs=[next(r for r in gains if (r['task'],r['protocol'],r['representation'],r['stage'])==s and r['comparison']==comparison) for s in settings]
        mean=np.array([r['advantage_bits'] for r in rs]);low=np.array([r['conditional_ci_low'] for r in rs]);high=np.array([r['conditional_ci_high'] for r in rs])
        ax.errorbar(mean,np.arange(len(settings))+(j-1)*.22,xerr=[mean-low,high-mean],fmt='o',capsize=2,label=comparison)
    ax.set_yticks(range(len(settings)),[' / '.join(s).replace('SHADOWSOCKS','SS') for s in settings],fontsize=8)
    ax.axvline(0,color='black',linewidth=.7);ax.set_xlabel('CE advantage in bits; conditional content bootstrap 95% interval')
    ax.legend();fig.tight_layout();fig.savefig(out/'paired-gains.png',dpi=150);plt.close(fig)
    write_json(out/'manifest.json',{'audit_sha256':digest(report/'validation.json'),
        'code_sha256':digest(Path(__file__)),'curves':'all settings, all arms, five-seed range; not confidence interval'})
    seal(out,passed=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--config',default=str(CONFIG));run(p.parse_args().config)
