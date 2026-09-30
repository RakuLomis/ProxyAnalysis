"""Frozen A-H evidence figures and traceable claim ledger; no fitting."""
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from .source_hierarchy_contract import verify
from .mechanism_contract import read
from .paired_structure_contract import seal,validate_complete
from ..paired_information.prepare import digest
from ..reproducibility.preflight import write_json


def run():
    _,center,decision,source=verify();out=Path('outputs/mechanism-evidence-0916')
    if out.exists():validate_complete(out)
    for base in (center,decision,source):
        validate_complete(base/'report');validate_complete(base/'audit')
    out.mkdir(parents=True,exist_ok=True)
    m=read(center/'report/metrics.json');fig,ax=plt.subplots(2,3,figsize=(13,7),layout='constrained')
    for k,pr in enumerate(('pooled','SHADOWSOCKS','VLESS')):
        rr=sorted([r for r in m if r['protocol']==pr],key=lambda r:r['arm'])
        for row,metric in enumerate(('macro_f1','ce_bits')):
            ax[row,k].bar([r['arm'] for r in rr],[r[metric] for r in rr],color='#3a769b')
            ax[row,k].set_title(pr);ax[row,k].set_ylabel(metric);ax[row,k].grid(axis='y',alpha=.2)
            if row==0:ax[row,k].set_ylim(0,1)
    fig.savefig(out/'AH-metrics.png',dpi=170);plt.close(fig)
    evidence=[]
    for base,choices in [(source,['B-A','C-B','C-D']),
        (decision,['decision_true_lambda_1 - C','decision_true_lambda_1 - decision_wrong_lambda_1']),
        (center,['H-F','H-G'])]:
        for r in read(base/'report/paired-contrasts.json'):
            if r['protocol']=='pooled' and r.get('subset','Full')=='Full' and r['contrast'] in choices:
                evidence.append({**r,'path':str(base/'report/paired-contrasts.json'),
                    'scope':'conditional fitted-model, unadjusted content bootstrap; no equivalence claim'})
    if len(evidence)!=7:raise ValueError('Expected seven fixed Full contrasts')
    fig,axes=plt.subplots(1,2,figsize=(13,6),layout='constrained')
    labels=[r['contrast'].replace('decision_true_lambda_1','F').replace('decision_wrong_lambda_1','G') for r in evidence]
    for ax,metric in zip(axes,('macro_f1','ce_bits')):
        for i,r in enumerate(evidence):
            point=r[metric+'_gain'];lo,hi=r[metric+'_ci'];ax.plot([lo,hi],[i,i],color='#3a769b');ax.plot(point,i,'o',color='#bd5637')
        ax.axvline(0,color='grey',ls='--');ax.set_yticks(range(len(labels)),labels);ax.set_xlabel(metric+' gain (positive better)')
    fig.savefig(out/'paired-gains.png',dpi=170);plt.close(fig)
    fid=[r for r in read(center/'report/fidelity-summary.json') if r['split']=='test']
    fig,axes=plt.subplots(1,2,figsize=(10,4),layout='constrained')
    for r in fid:
        y=next(x['macro_f1'] for x in m if x['arm']==r['arm'] and x['protocol']=='pooled')
        for ax,key in zip(axes,('target_mse','centered_logit_mse')):
            ax.scatter(r[key],y,s=45);ax.annotate(r['arm'],(r[key],y),xytext=(5,5),textcoords='offset points');ax.set_xlabel(key);ax.set_ylabel('macro-F1');ax.grid(alpha=.2)
    fig.savefig(out/'FGH-recovery-task.png',dpi=170);plt.close(fig)
    write_json(out/'claim-ledger.json',evidence)
    write_json(out/'provenance.json',{'new_fits':0,'sources':{str(p):digest(p) for base in (center,decision,source) for p in [base/'contract/manifest.json',base/'report/complete.json',base/'audit/validation.json']},
        'not_verified':['true direct-to-proxy','single flow classification','index-free online segmentation','external VPS/network generalization'],
        'cross_deployment_calibration':'Separate X experiment, not evidence in this A-H chain'})
    seal(out,passed=True);print('A-H evidence figures and ledger complete',flush=True)


if __name__=='__main__':run()
