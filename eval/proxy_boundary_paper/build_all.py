"""Read frozen results, validate comparisons, generate manuscript figures/tables."""
from pathlib import Path
import hashlib
import json
import platform
import sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[2]
PAPER = ROOT / 'docs/paper/proxy-boundary-correspondence'
FIG = PAPER / 'figures/generated'
PREVIEW = PAPER / 'figures/preview'
TABLE = PAPER / 'tables'
EVIDENCE = PAPER / 'evidence'
SOURCES = {
    'ah': 'outputs/source-center-control-0916/run-01/report/metrics.json',
    'fidelity': 'outputs/source-center-control-0916/run-01/report/fidelity-summary.json',
    'decision_fidelity': 'outputs/source-decision-calibration-0916/run-01/report/fidelity-summary.json',
    'contrasts': 'outputs/mechanism-evidence-0916/claim-ledger.json',
    'joint': 'outputs/group-anchor-diagnostics-0916/run-01/report/joint-diagnostics.json',
    'utility': 'outputs/group-anchor-diagnostics-0916/run-01/report/utility-metrics.json',
    'transform': 'outputs/content-generalization-20260916/mechanism-01/p4-transformation/group-summary.json',
    'cross': 'outputs/source-calibration-cross-deployment-0916/run-01/report/metrics.json',
    'cross_contrasts': 'outputs/source-calibration-cross-deployment-0916/run-01/report/contrasts.json',
    'cross_flips': 'outputs/source-calibration-cross-deployment-0916/run-01/report/decision-flips.json',
    'cross_fidelity': 'outputs/source-calibration-cross-deployment-0916/run-01/report/fidelity-summary.json',
    'cross_classes': 'outputs/source-calibration-cross-deployment-0916/run-01/report/per-class.json',
    'source_flips': 'outputs/source-transfer-0916/run-01/report/decision-flips.json',
    'decision_flips': 'outputs/source-decision-calibration-0916/run-01/report/decision-flips.json',
    'center_flips': 'outputs/source-center-control-0916/run-01/report/decision-flips.json',
}
COLORS = ['#32688E', '#B45C36', '#39836B', '#8064A2', '#8C7838']

def select(rows, **conditions):
    matches = [r for r in rows if all(r.get(k) == v for k, v in conditions.items())]
    if len(matches) != 1:
        raise ValueError(f'Expected exactly one row: {conditions}; got {len(matches)}')
    return matches[0]

def load():
    return {k: json.loads((ROOT / p).read_text(encoding='utf-8')) for k, p in SOURCES.items()}

def validate(data):
    assert len(data['ah']) == 24
    for arm in 'ABCDEFGH':
        row = select(data['ah'], arm=arm, protocol='pooled')
        assert row['visits'] == 240 and 0 <= row['macro_f1'] <= 1
    assert len(data['cross']) == 20
    assert all(r['visits'] == 120 for r in data['cross'])
    assert len(data['contrasts']) == 7
    assert len(data['cross_contrasts']) == 30
    assert select(data['ah'], arm='F', protocol='pooled')['macro_f1'] > select(data['ah'], arm='C', protocol='pooled')['macro_f1']
    for r in data['contrasts']:
        assert r['macro_f1_ci'][0] <= r['macro_f1_ci'][1]
    for r in data['cross_flips']:
        assert sum(r[k] for k in ['correct_correct','correct_wrong','wrong_correct','wrong_wrong']) == 120

def save(fig, name):
    fig.savefig(FIG / (name + '.pdf'), bbox_inches='tight', metadata={'CreationDate': None})
    fig.savefig(PREVIEW / (name + '.png'), dpi=180, bbox_inches='tight')
    plt.close(fig)

def table(name, header, rows, columns):
    text = '\\begin{tabular}{' + columns + '}\n\\toprule\n'
    text += ' & '.join(header) + r' \\' + '\n\\midrule\n'
    text += '\n'.join(' & '.join(map(str, row)) + r' \\' for row in rows)
    text += '\n\\bottomrule\n\\end{tabular}\n'
    (TABLE / (name + '.tex')).write_text(text, encoding='utf-8')

def make_tables(d):
    rows = [select(d['ah'], arm=a, protocol='pooled') for a in 'ABCDEFGH']
    table('ah', ['Arm','F1','CE (bits)','Brier','BA'],
          [[r['arm']] + [f'{r[k]:.4f}' for k in ['macro_f1','ce_bits','brier','balanced_accuracy']] for r in rows], 'lrrrr')
    table('cross', ['Source','Test','Arm','F1','CE','Brier'],
          [[{'SHADOWSOCKS':'SS','VLESS':'VL'}[r['source_protocol']],r['domain'],r['arm'] if r['arm']!='E' else r'$E_s$'] + [f'{r[k]:.4f}' for k in ['macro_f1','ce_bits','brier']] for r in d['cross']], 'lllrrr')
    table('fidelity', ['Arm',r'Stat. MSE',r'Logit MSE',r'Agreement'],
          [[r['arm']] + [f'{r[k]:.4f}' for k in ['target_mse','centered_logit_mse','source_class_agreement']] for r in [select(d['decision_fidelity'],arm='C',split='test',target_relation='true')] + [r for r in d['fidelity'] if r['split']=='test']], 'lrrr')
    macros = '\n'.join(r'\newcommand{\FOne' + r['arm'] + '}{' + f"{r['macro_f1']:.4f}" + '}' for r in rows)
    (TABLE / 'numbers.tex').write_text(macros + '\n', encoding='utf-8')
    utility = [r for r in d['utility'] if r['protocol']=='pooled']
    table('utility', ['Input','F1','CE','Brier'], [[r['subset']] + [f'{r[k]:.4f}' for k in ['macro_f1','ce_bits','brier']] for r in utility], 'lrrr')
    table('cross_contrasts', ['Source','Contrast',r'$\Delta$F1 [95\% CI]',r'CE gain [95\% CI]'],
          [[{'SHADOWSOCKS':'SS','VLESS':'VL'}[r['source_protocol']],r['contrast'].replace('E','E$_s$'),
            f"{r['macro_f1_gain']:+.3f} [{r['macro_f1_ci'][0]:+.3f}, {r['macro_f1_ci'][1]:+.3f}]",
            f"{r['ce_bits_gain']:+.3f} [{r['ce_bits_ci'][0]:+.3f}, {r['ce_bits_ci'][1]:+.3f}]"] for r in d['cross_contrasts'] if r.get('domain')=='target'], 'llll')

def figures(d):
    fig, axes = plt.subplots(2,3, figsize=(7.1,3.8),layout='constrained')
    for j, (protocol, label) in enumerate([('pooled','Pooled'),('SHADOWSOCKS','SS'),('VLESS','VLESS')]):
        rows = [select(d['ah'],arm=a,protocol=protocol) for a in 'ABCDEFGH']
        for ax, metric, ylabel in zip(axes[:,j], ['macro_f1','ce_bits'], ['Macro-F1','CE (bits)']):
            ax.bar(list('ABCDEFGH'),[r[metric] for r in rows],color=COLORS[0],width=.65)
            ax.set_ylabel(ylabel); ax.grid(axis='y', alpha=.18); ax.set_axisbelow(True)
            if metric=='macro_f1': ax.set_ylim(0,1); ax.set_title(label)
    save(fig,'ah-performance')
    fig,axes=plt.subplots(1,2,figsize=(7.1,2.7),layout='constrained')
    for ax,metric,title in zip(axes,['macro_f1','ce_bits'],['Macro-F1 gain','CE reduction (bits)']):
        for i,r in enumerate(d['contrasts']):
            ax.plot(r[metric+'_ci'],[i,i],color=COLORS[0]);ax.scatter(r[metric+'_gain'],i,color=COLORS[1],s=18)
        labels=[r['contrast'].replace('decision_true_lambda_1','F').replace('decision_wrong_lambda_1','G').replace(' ','') for r in d['contrasts']]
        ax.set_yticks(range(7),labels);ax.axvline(0,color='.5',ls='--',lw=.7);ax.set_xlabel(title);ax.invert_yaxis()
    save(fig,'paired-contrasts')
    fig,axes=plt.subplots(1,3,figsize=(7.1,2.2),layout='constrained')
    groups=[select(d['joint'],group=f'G{i}',protocol='pooled') for i in range(1,7)]
    skills=[select(r['heldout_recovery'],model='Ridge-true',split='test',relation='true')['skill_mse'] for r in groups]
    axes[0].bar(range(6),skills,color=COLORS[0]);axes[0].set_ylabel('Held-out recovery skill')
    axes[1].bar(range(6),[r['only_group']['macro_f1'] for r in groups],color=COLORS[2]);axes[1].set_ylabel('Only-group macro-F1')
    for i,r in enumerate(groups):
        v=r['deletion_increment'];axes[2].plot([i,i],v['f1_ci'],color=COLORS[0]);axes[2].scatter(i,v['f1_gain'],color=COLORS[1],s=18)
    axes[2].set_ylabel('Full minus deleted-group F1');axes[2].axhline(0,color='.5',ls='--',lw=.7)
    for ax in axes: ax.set_xticks(range(6),[f'G{i}' for i in range(1,7)]);ax.grid(axis='y',alpha=.15)
    axes[0].set_ylim(0,1.05);axes[1].set_ylim(0,1.05)
    save(fig,'group-utility')
    fids=[select(d['decision_fidelity'],arm='C',split='test',target_relation='true')]+[r for r in d['fidelity'] if r['split']=='test']
    fig,axes=plt.subplots(1,2,figsize=(7.1,2.5),layout='constrained')
    for r in fids:
        for ax,key in zip(axes,['target_mse','centered_logit_mse']):
            y=select(d['ah'],arm=r['arm'],protocol='pooled')['macro_f1']
            ax.scatter(r[key],y,s=26);ax.annotate(r['arm'],(r[key],y),xytext=(5,5),textcoords='offset points')
            ax.set_ylabel('Macro-F1');ax.grid(alpha=.15);ax.margins(.2)
    axes[0].set_xlabel('Statistical recovery MSE');axes[1].set_xlabel('Centered-logit MSE')
    save(fig,'recovery-task')
    fig,axes=plt.subplots(2,2,figsize=(7.1,3.8),layout='constrained')
    for j,p in enumerate(['SHADOWSOCKS','VLESS']):
        arms=['A','B','F','H','E'];x=np.arange(5)
        for ax,key,ylabel in zip(axes[:,j],['macro_f1','ce_bits'],['Macro-F1','CE (bits)']):
            for i,domain in enumerate(['source','target']):
                vals=[select(d['cross'],source_protocol=p,domain=domain,arm=a)[key] for a in arms]
                ax.bar(x+(i-.5)*.35,vals,.35,label=domain+' holdout',color=COLORS[i],hatch='///' if i else None,edgecolor='white',linewidth=.3)
            ax.set_xticks(x,['A','B','F','H','$E_s$']);ax.set_ylabel(ylabel);ax.grid(axis='y',alpha=.15);ax.set_axisbelow(True)
            if key=='macro_f1':ax.set_ylim(0,1.05);ax.set_title('SS → VLESS' if j==0 else 'VLESS → SS')
    handles,labels=axes[0,0].get_legend_handles_labels()
    fig.legend(handles,labels,loc='upper center',bbox_to_anchor=(.5,1.09),ncol=2,frameon=False,fontsize=8)
    save(fig,'cross-deployment')
    fig,axes=plt.subplots(1,2,figsize=(7.1,2.3),layout='constrained')
    for ax,p in zip(axes,['SHADOWSOCKS','VLESS']):
        rows=[select(d['cross_flips'],source_protocol=p,domain='target',transition=t) for t in ['B->F','B->H','F->H']]
        x=np.arange(3)
        ax.bar(x-.17,[r['wrong_correct'] for r in rows],.34,color=COLORS[2],label='Wrong → correct')
        ax.bar(x+.17,[r['correct_wrong'] for r in rows],.34,color=COLORS[1],label='Correct → wrong')
        ax.set_xticks(x,['B → F','B → H','F → H']);ax.set_ylabel('Visits (out of 120)');ax.set_ylim(0,40)
        ax.set_title('SS → VLESS' if p=='SHADOWSOCKS' else 'VLESS → SS');ax.grid(axis='y',alpha=.15)
    axes[0].legend(fontsize=7)
    save(fig,'decision-changes')

def main():
    for p in [FIG,PREVIEW,TABLE,EVIDENCE/'figure_data']:p.mkdir(parents=True,exist_ok=True)
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':8,'axes.titlesize':9,'axes.labelsize':8,'xtick.labelsize':7,'ytick.labelsize':7,'pdf.fonttype':42,'ps.fonttype':42,'axes.spines.top':False,'axes.spines.right':False})
    d=load();validate(d)
    manifest={'new_model_fits':0,'python':platform.python_version(),'matplotlib':matplotlib.__version__,'sources':{}}
    for k,p in SOURCES.items():
        manifest['sources'][k]={'path':p,'sha256':hashlib.sha256((ROOT/p).read_bytes()).hexdigest()}
        (EVIDENCE/'figure_data'/f'{k}.json').write_text(json.dumps(d[k],indent=2,ensure_ascii=False),encoding='utf-8')
    (EVIDENCE/'artifact_manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    make_tables(d);figures(d)
    print('Validated frozen results; tables and six figure panels generated; no fits.')

if __name__=='__main__':main()
