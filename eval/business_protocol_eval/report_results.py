"""Read sealed results only; no fitting, selection, or changes to frozen code."""
import json
from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from common import OUT, ROOT, PROTOCOLS, read, write, file_hash, check_files

DOC = ROOT / 'docs/business-protocol-eval-extend'


def table(df):
    def fmt(x):
        if isinstance(x, float):
            return '—' if pd.isna(x) else f'{x:.4f}'
        return str(x).replace('|', '/')
    return '| ' + ' | '.join(map(str, df.columns)) + ' |\n|' + '|'.join(['---']*len(df.columns)) + '|\n' + '\n'.join('| ' + ' | '.join(fmt(x) for x in row) + ' |' for row in df.itertuples(index=False, name=None))


def main():
    assert (OUT/'score-complete.json').exists()
    contract=read(OUT/'contract.json');check_files(contract['code_hashes'])
    seal=read(OUT/'prediction-seal.json')
    assert file_hash(OUT/'predictions.parquet')==seal['sha256']
    detail=pd.read_parquet(OUT/'per-protocol-seed-metrics.parquet')
    agg=pd.read_parquet(OUT/'aggregate-seed-metrics.parquet')
    contrast=pd.read_parquet(OUT/'primary-contrasts.parquet')
    decisions=pd.read_parquet(OUT/'visit-decisions.parquet')
    conf=read(OUT/'confusion-matrices.json')
    classes=conf[0]['classes']
    cr=[]
    for item in conf:
        import numpy as np
        cm=np.asarray(item['matrix']);tp=np.diag(cm)
        for k,name in enumerate(classes):
            denom=cm[k].sum()+cm[:,k].sum()
            cr.append({**{c:item[c] for c in ['experiment','arm','seed','protocol']},'business':name,
                       'F1':2*tp[k]/denom if denom else 0,'recall':tp[k]/cm[k].sum()})
    perclass=pd.DataFrame(cr)
    perclass.to_parquet(OUT/'report-per-class.parquet',index=False)
    errors=[]
    for e in ['E1','E2']:
        a=decisions[decisions.experiment.eq(e)&decisions.arm.eq('M2')]
        for ref in ['M0','M1','M3','M4']:
            b=decisions[decisions.experiment.eq(e)&decisions.arm.eq(ref)]
            pairs=a.merge(b,on=['seed','session_id','protocol','content_id','y'],suffixes=('_m2','_ref'),validate='one_to_one')
            pairs['repaired']=(pairs.prediction_m2==pairs.y)&(pairs.prediction_ref!=pairs.y)
            pairs['new_error']=(pairs.prediction_m2!=pairs.y)&(pairs.prediction_ref==pairs.y)
            g=pairs.groupby(['seed','protocol','content_id','y'])[['repaired','new_error']].sum().reset_index()
            g['experiment']=e;g['comparison']='M2-'+ref;g['business']=g.y.map(dict(enumerate(classes)))
            errors.append(g)
    errors=pd.concat(errors,ignore_index=True)
    errors.to_parquet(OUT/'report-content-errors.parquet',index=False)
    DOC.mkdir(parents=True,exist_ok=True)
    parts=['# 多部署统一业务模型与留一部署实验：详细结果表',
           '本文件由 `eval/business_protocol_eval/report_results.py` 从封存预测生成，无模型拟合或选择。所有F1为0–1；先逐seed合并五折OOF，再对seed取均值。主报告见 [formal-results.md](formal-results.md)。']
    fig,axes=plt.subplots(1,2,figsize=(12,4),sharey=True)
    for e,ax in zip(['E1','E2'],axes):
        parts += [f'## {e} 汇总',table(agg[agg.experiment.eq(e)].groupby('arm')[['protocol_equal_F1','worst_protocol_F1','pooled_F1']].mean().reset_index()),
                  '最差F1为每seed先取五部署最小值，再平均，不等于先平均seed再取最小值。',
                  '### 逐部署三seed均值',table(detail[detail.experiment.eq(e)].groupby(['arm','protocol'])[['F1','CE_bits','Brier','accuracy','BA']].mean().reset_index()),
                  '### 主对照与次要错配对照',table(contrast[contrast.experiment.eq(e)]),
                  'adjusted为本实验三项主比较的Bonferroni分位区间；M2−M4仅提供未校正描述区间。',
                  '### 每个seed的完整OOF成绩',table(agg[agg.experiment.eq(e)]),
                  '### 六业务逐类F1（部署等权、seed平均）',table(perclass[perclass.experiment.eq(e)].groupby(['arm','business'])[['F1','recall']].mean().reset_index()),
                  '### 修复／新增错误（全部seed判断次数之和，不是独立样本数）',table(errors[errors.experiment.eq(e)].groupby(['comparison','protocol'])[['repaired','new_error']].sum().reset_index())]
        pivot=detail[detail.experiment.eq(e)].groupby(['protocol','arm']).F1.mean().unstack().reindex(PROTOCOLS)
        pivot.plot.bar(ax=ax,rot=25);ax.set_title(e);ax.set_ylim(0,1);ax.set_ylabel('Six-class macro-F1');ax.set_xlabel('Deployment');ax.grid(axis='y',alpha=.2)
        ax.get_legend().remove()
    handles,labels=axes[0].get_legend_handles_labels()
    fig.legend(handles,labels,ncol=5,loc='lower center',frameon=False)
    fig.tight_layout(rect=(0,.08,1,1));fig.savefig(DOC/'protocol-results.png',dpi=180);plt.close(fig)
    parts += ['## I0 独立部署参照',table(detail[detail.experiment.eq('I0')].groupby('protocol')[['F1','CE_bits','Brier','accuracy']].mean().reset_index()),table(agg[agg.experiment.eq('I0')]),
              'I0需部署身份路由且合计五个模型，不能把其与M0的差直接归因为参数共享。',
              '## 完整逐部署逐业务表',table(perclass.groupby(['experiment','arm','protocol','business'])[['F1','recall']].mean().reset_index()),
              '## 每内容每seed的错误转移',table(errors),
              '这部分列出所有比较，不筛选有利内容。四重复×三seed的判断不能视为十二个独立内容。']
    (DOC/'detailed-results.md').write_text('\n\n'.join(parts)+'\n',encoding='utf-8')
    generation=[read(p) for p in (OUT/'generation').glob('*/*/complete.json')]
    models=[read(p) for p in (OUT/'models').glob('*/complete.json')]
    assert len(generation)==300 and sum(x['ridge_fits'] for x in generation)==5700
    assert len(models)==55 and sum(x['classifiers'] for x in models)==525
    assert all(x['cuda'] and x['test_reads']==0 for x in generation+models)
    assert len(decisions)==19800
    for folder in [OUT/'generation',OUT/'models']:
        for path in folder.rglob('complete.json'):
            obj=read(path)
            assert obj['contract_sha256']==file_hash(OUT/'contract.json')
            for name,sha in obj['files'].items():assert file_hash(path.parent/name)==sha
    check_files(contract['artifact_hashes'])
    write(OUT/'report-audit.json',{'generation_jobs':len(generation),'Ridge_fits':5700,'classifiers':525,
          'prediction_rows':len(decisions),'training_loop_seconds_sum':sum(x['seconds'] for x in models),
          'all_cuda':True,'all_registered_hashes_valid':True,'test_reads_during_fitting':0,
          'report_script_sha256':file_hash(Path(__file__))})
    print(agg.groupby(['experiment','arm'])[['protocol_equal_F1','worst_protocol_F1','pooled_F1']].mean().to_string())
    print(contrast.to_string(index=False));print(json.dumps(read(OUT/'report-audit.json'),indent=2))


if __name__=='__main__':main()
