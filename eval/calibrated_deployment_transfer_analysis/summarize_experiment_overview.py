"""Export frozen diagnostic tables and run counts; no fitting or prediction."""
from pathlib import Path
import json
import hashlib
from datetime import datetime, timezone, timedelta
import pandas as pd

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'outputs/calibrated-deployment-business-transfer-20261006'
OLD_ANALYSIS=ROOT/'outputs/calibrated-deployment-business-transfer-analysis-20261006/run-01'
OUT=ROOT/'outputs/calibrated-deployment-business-transfer-analysis-20261006/overview'
PROTOCOLS=['shadowsocks','vless','trojan','vmess']
DISPLAY={'shadowsocks':'SS','vless':'VLESS','trojan':'Trojan','vmess':'VMess'}

def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()
def table(df):
    lines=['| '+' | '.join(str(c) for c in df.columns)+' |',
           '| '+' | '.join('---' for _ in df.columns)+' |']
    for row in df.itertuples(index=False,name=None):
        cells=[f'{v:.6f}' if isinstance(v,float) else str(v) for v in row]
        lines.append('| '+' | '.join(cells)+' |')
    return '\n'.join(lines)
def matrix(df,value):
    m=df.pivot(index='source',columns='target',values=value).loc[PROTOCOLS,PROTOCOLS]
    return m.rename(index=DISPLAY,columns=DISPLAY).rename_axis('源部署').reset_index()

def run():
    inputs=[BASE/'run-01/diagnostics/classification-summary.parquet',
            OLD_ANALYSIS/'diagnostic-equal-cell-summary.parquet',
            OLD_ANALYSIS/'diagnostic-kernel-composites.parquet',
            OLD_ANALYSIS/'cross-deployment-feature-losses.parquet',
            OLD_ANALYSIS/'diagnostic-class-results.parquet']
    cls=pd.read_parquet(inputs[0]);equal=pd.read_parquet(inputs[1])
    kernels=pd.read_parquet(inputs[2]);features=pd.read_parquet(inputs[3])
    classes=pd.read_parquet(inputs[4])
    assert len(cls)==36 and len(kernels)==16 and len(classes)==216
    matrices={kind:matrix(cls[cls.kind.eq(kind)],'F1_all') for kind in ['pre','post']}
    matrices['kernel_loss_bits']=matrix(kernels,'conditional_loss_bits')
    matrices['kernel_gain_bits']=matrix(kernels,'gain_bits')
    # Sanity-check saved equal-cell results without reading any new test package.
    for row in equal.itertuples(index=False):
        part=cls[cls.kind.eq(row.kind)]
        if row.kind!='postmix':
            same=part.source.eq(part.target)
            part=part[same if row.scope=='same_deployment' else ~same]
        assert len(part)==row.cells and abs(part.F1_all.mean()-row.F1_all)<1e-12
    summaries=[]
    for number in [1,2,3]:
        root=BASE/f'run-{number:02d}'
        progress=read(root/'progress.json')
        assert progress['stage']=='engineering_stop'
        main=list((root/'models/main').rglob('*.pt'))
        diagnostics=list((root/'models/diagnostics').rglob('*.pt'))
        pilot=list((root/'pilot/models').rglob('*.pt'))
        accepted=len(diagnostics)+len(main)+(len(pilot) if number==3 else 0)
        assert [len(diagnostics),len(main),len(pilot)]=={1:[680,4,0],2:[0,104,60],3:[0,0,24]}[number]
        absent={str(p):not (root/p).exists() for p in [Path('completion.json'),
            Path('verification.json'),Path('selection/choices.json'),Path('predictions/visits.parquet')]}
        assert all(absent.values())
        summaries.append({'run':number,'diagnostic_models':len(diagnostics),'main_candidates':len(main),
            'pilot_copies':len(pilot),'accepted_unique_artifacts_without_v2_duplicates':accepted,
            'status':progress['stage'],'stop_time_Asia_Shanghai':datetime.fromtimestamp(
                progress['time_unix'],timezone(timedelta(hours=8))).isoformat(),'main_result_absent':absent})
    sources={}
    for p in [BASE/'run-01/manifests/experiment-contract-amended-io-v1.json',
        BASE/'run-02/manifests/experiment-contract-v2.json',BASE/'run-03/manifests/experiment-contract-v3.json']:
        c=read(p);sources.update(c['source_sha256']);inputs.append(p)
    assert all(sha(ROOT/p)==h for p,h in sources.items())
    feature_rows=[{'feature':str(index),**row.to_dict()} for index,row in features.iterrows()]
    OUT.mkdir(parents=True,exist_ok=True)
    result={'source_hashes_checked':len(sources),'input_sha256':{p.relative_to(ROOT).as_posix():sha(p) for p in inputs},
        'classification_cells':36,'class_rows':216,'kernel_cells':16,'run_counts':summaries,
        'equal_cell_summary':equal.to_dict(orient='records'),
        'matrices':{k:v.to_dict(orient='records') for k,v in matrices.items()},
        'cross_feature_scores':feature_rows,'kernel_scores':kernels.to_dict(orient='records'),
        'new_fits':0,'new_inference':0,'new_raw_capture_reads':0,'new_test_package_reads':0}
    (OUT/'overview-audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    appendix=['# 辅助业务校准迁移实验已完成诊断的完整数值表',
        '这些表来自第一版已封存预测和评分，不是三版修复后的主实验结果。所有值保留六位小数；核分数以原Parquet未舍入数值为准。']
    for name,df in matrices.items():appendix += ['## '+name,table(df)]
    appendix += ['## 等权诊断汇总',table(equal),
        '## 全部三十六个分类单元',table(cls),
        '## 全部十六个源核评分单元',table(kernels),
        '## 跨部署逐特征分数',table(pd.DataFrame(feature_rows))]
    (OUT/'diagnostic-tables.md').write_text('\n\n'.join(appendix)+'\n',encoding='utf-8')
    print(json.dumps({'run_counts':summaries,'source_files':len(sources),
        'features':feature_rows,'kernel_VM_to_Trojan':kernels[kernels.source.eq('vmess')&kernels.target.eq('trojan')].to_dict(orient='records')},
        ensure_ascii=False,indent=2))

if __name__=='__main__':run()
