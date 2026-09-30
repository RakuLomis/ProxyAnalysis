"""Complete P7 plots and source-only matrix concentration diagnostics."""
import argparse
from pathlib import Path
import numpy as np
from .paired_structure_contract import CONFIG,verify,read,validate_complete,seal
from ..paired_information.reference_retrain import SCALAR_NAMES
from ..paired_information.prepare import digest,table
from ..reproducibility.preflight import write_json


def run(config=CONFIG):
    cfg,source,_,root=verify(config);base=root/'p7-models';report=base/'report';out=base/'delivery'
    validate_complete(report)
    if out.exists():validate_complete(out);return
    rows={r['session_id']:r for r in table(source/'side-summaries.parquet') if r['selection']=='observed'}
    diagnostics=[]
    for job in sorted((base/'formal-jobs').iterdir()):
        fits=read(job/'fit-ledger.json');basefit=next(f for f in fits if f['arm']=='R0')
        true=next(f for f in fits if f['arm']=='R-True' and f['lambda']==cfg['primary_lambda'])
        for arm,m in read(job/'matrices.json').items():
            if arm=='R-Iso':continue
            diag=np.diag(m['raw']);j=int(diag.argmax());feature=SCALAR_NAMES[j]
            source_values=[rows[s]['post'][feature] for s in basefit['train_ids']]
            diagnostics.append({k:basefit[k] for k in ['task','protocol','outer_fold']}|{
                'arm':arm,'dominant_feature':feature,'diagonal_trace_share':float(diag[j]/sum(diag)),
                'source_feature_variance':float(np.var(source_values)),
                'source_feature_scale':basefit['preprocessing']['scaler_scale'][j],
                'raw_trace':m['trace'],'participation_rank':m['participation_rank'],
                'R0_dominant_feature_coef':np.array(basefit['state']['coef'])[:,j].tolist(),
                'RTrue_primary_dominant_feature_coef':np.array(true['state']['coef'])[:,j].tolist()})
    out.mkdir();write_json(out/'matrix-concentration.json',diagnostics)
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    metrics=read(report/'metrics.json');gains=read(report/'gains.json')
    for task in cfg['tasks']:
        fig,axes=plt.subplots(2,2,figsize=(12,8))
        for i,protocol in enumerate(cfg['protocols']):
            for j,stage in enumerate(['student','cross']):
                ax=axes[i,j];rs=[r for r in metrics if (r['task'],r['protocol'],r['stage'])==(task,protocol,stage)]
                basece=next(r['log_loss_bits'] for r in rs if r['arm']=='R0');ax.axhline(basece,label='R0',color='black',linestyle='--')
                for arm in ['R-True','R-Wrong-1','R-Wrong-2','R-Wrong-3','R-Iso']:
                    vals=sorted([r for r in rs if r['arm']==arm],key=lambda r:r['lambda'])
                    ax.plot([r['lambda'] for r in vals],[r['log_loss_bits'] for r in vals],marker='o',label=arm)
                ax.set_xscale('log');ax.set_title(f'{protocol} / {stage}');ax.set_xlabel('Frozen lambda');ax.set_ylabel('CE bits');ax.legend(fontsize=7)
        fig.suptitle(task);fig.tight_layout();fig.savefig(out/f'{task}-lambda-curves.png',dpi=160);plt.close(fig)
    write_json(out/'manifest.json',{'report_sha256':digest(report/'complete.json'),'code_sha256':digest(Path(__file__))})
    seal(out,passed=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--config',default=str(CONFIG));run(p.parse_args().config)
