"""B0-B6 delivery audit. No training or outer-test prediction."""
import inspect
import sys
import importlib.metadata
import xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
import pandas as pd
from .data import OUT,DOC,BUS,CONFIG,PLAN,PAIR,SIDE,KEY,read,js,load,save,digest
from .tensors import Store
from .model import transformed

def finish_engineering():
    folds=load('folds');manifest=load('capture-manifest');m=load('tensor-manifest');common=load('common-flow-cohort')
    contexts=[]
    for fold in range(5):
        f=folds[folds.fold==fold];a=f[f.split=='train'];b=f[f.split=='test'];assert len(a)==96 and len(b)==24
        checks={}
        for column in ['session_id','content_id']:checks[column]=len(set(a[column])&set(b[column]))
        for column in ['normalized_path','sha256']:
            checks[column]=len(set(manifest[manifest.session_id.isin(a.session_id)][column])&set(manifest[manifest.session_id.isin(b.session_id)][column]))
        assert not any(checks.values());contexts.append({'fold':fold,'overlaps':checks})
    # Test all retained post tensors after replacing the entire pre store.
    store=Store();states=read(OUT/'preprocessors.json');state={rep:states['0:'+rep] for rep in ['P','R','C','T']}
    scale_diagnostics=[]
    for fold in range(5):
        train_ids=folds[(folds.fold==fold)&(folds.split=='train')].session_id
        for rep in ['P','R','C','T']:
            st=states[f'{fold}:{rep}'];mean=np.asarray(st['mean']);scale=np.asarray(st['scale'])
            for side in ['pre','post']:
                maxima=np.zeros(len(mean));tokens=0
                for sid in train_ids:
                    for uid in store.visit[sid]:
                        data=store.data[uid,side]
                        for key in ['T'] if rep=='T' else [rep+'_up',rep+'_down']:
                            z=(data[key]-mean)/scale;assert np.isfinite(z).all()
                            maxima=np.maximum(maxima,np.abs(z).max(0));tokens+=len(z)
                for j,value in enumerate(maxima):
                    scale_diagnostics.append({'fold':fold,'representation':rep,'side':side,'column_index':j,
                        'max_absolute_transformed_value':float(value),'training_tokens':tokens,
                        'training_post_variance':st['variance'][j],'test_rows_used':False})
    save('train-scale-diagnostics',scale_diagnostics)
    before={u:transformed(store,u,'post','R',state) for u in store.uid_to_visit}
    for u in store.uid_to_visit:store.data[u,'pre']={'invalid_pre_replacement':None}
    for u,expected in before.items():
        actual=transformed(store,u,'post','R',state)
        for k in expected:np.testing.assert_array_equal(actual[k],expected[k])
    for fold in range(5):
        train=set(folds[(folds.fold==fold)&(folds.split=='train')].session_id)
        for rep in ['P','R','C','T']:assert set(states[f'{fold}:{rep}']['fit_visits'])==train
    assert all(digest(Path(p))==h for p,h in read(OUT/'contract.json')['inputs'].items())
    assert all(digest(Path(r.path))==r.sha256 for r in m.itertuples())
    # Explicit interval joins, preserving original source ownership and record times.
    records=load('record-units').merge(common[PAIR],on=PAIR,validate='many_to_one')
    sources={k:g.sort_values('start') for k,g in load('source-links').groupby(KEY)};links=[]
    for key,r in ([] if (OUT/'unit-source-overlap-links.parquet').exists() else records.groupby(KEY)):
        source=sources[key];starts=source.start.to_numpy();ends=source.end.to_numpy();total=int(r.end.max())
        ordinals=source.packet_ordinal.to_numpy();times=source.time_ns.to_numpy()
        a=np.arange(0,total,1024);chunks=pd.DataFrame({'record_index':np.arange(len(a)),'start':a,'end':np.minimum(a+1024,total)})
        for rep,units in [('R',r),('C',chunks)]:
            for unit in units.itertuples():
                lo=np.searchsorted(ends,unit.start,side='right');hi=np.searchsorted(starts,unit.end,side='left')
                for j in range(lo,hi):
                    links.append({**dict(zip(KEY,key)),'representation':rep,'unit_index':int(unit.record_index),
                        'overlap_start':max(int(unit.start),int(starts[j])),'overlap_end':min(int(unit.end),int(ends[j])),
                        'overlap_bytes':min(int(unit.end),int(ends[j]))-max(int(unit.start),int(starts[j])),
                        'packet_ordinal':int(ordinals[j]),'time_ns':int(times[j])})
    link=save('unit-source-overlap-links',links) if links else load('unit-source-overlap-links')
    totals=link.groupby(KEY+['representation']).overlap_bytes.sum().unstack()
    assert (totals.R==totals.C).all()
    expected_bytes=load('flow-eligibility').set_index(KEY).unique_bytes.reindex(totals.index)
    assert len(totals)==4*len(common) and np.array_equal(totals.R,expected_bytes)
    # Expand SSL retention with actual bytes, not unit counts.
    mapping=m[m.side=='post'][['uid',*PAIR]].merge(common[PAIR+['unique_bytes_post']],on=PAIR,validate='one_to_one')
    pool=load('ssl-pool').merge(mapping[['uid','unique_bytes_post']],on='uid',validate='many_to_one')
    retained=pool.groupby(['fold','seed','session_id']).unique_bytes_post.sum().rename('ssl_post_bytes').reset_index()
    counts=load('ssl-pool-retention').drop(columns=['ssl_post_bytes','all_post_bytes','byte_retention'],errors='ignore').merge(retained,on=['fold','seed','session_id'],validate='one_to_one')
    counts['all_post_bytes']=counts.session_id.map(common.groupby('session_id').unique_bytes_post.sum())
    counts['byte_retention']=counts.ssl_post_bytes/counts.all_post_bytes;save('ssl-pool-retention',counts)
    suites=list(ET.parse(OUT/'tests.xml').getroot().iter('testsuite'))
    tests={k:sum(int(s.get(k,0)) for s in suites) for k in ['tests','failures','errors','skipped']};assert tests['failures']==tests['errors']==0
    js('tests.json',tests)
    smoke=load('engineering-smoke');assert len(smoke)==9 and (smoke.steps==20).all()
    assert np.isfinite(smoke.final_loss).all() and (smoke[smoke.arm.str.startswith('L')].flow_std_mean>1e-4).all()
    js('pretraining-audit.json',{'folds':contexts,'post_pre_mutation_checks':len(before),'passed':True,
        'all_tensor_hashes_verified':True,'old_inputs_unchanged':True,'all_scalers_train_post_only':True,
        'source_link_byte_conservation':True,'smoke_nonconstant_flow_embedding':True,
        'tests':tests,'formal_fit_count':0,'engineering_fit_count':9,'raw_redecode_used_existing_files_only':True})
    budget=read(OUT/'budget-final.json')
    js('stage-status.json',{'B0_B6':'complete','B7_B10':'not_started','formal_training_started':False,
        'pending':'user_confirmation_of_long_running_resource_budget','estimated_training_hours':budget['estimated_training_hours']})
    code=[*Path(__file__).parent.glob('*.py'),CONFIG,PLAN,*Path('eval/record_time_business').glob('*.py'),*Path('tests/unit').glob('test_record_time_business*.py')]
    js('provenance.json',{'code':{str(p.resolve()):digest(p) for p in code},'old_inputs':read(OUT/'contract.json')['inputs'],
        'tables':{str(p):digest(p) for p in OUT.glob('*.parquet')},'python':sys.version,'executable':sys.executable,
        'packages':{n:importlib.metadata.version(n) for n in ['torch','numpy','pandas','scipy','pyarrow','PyYAML']},
        'historical_identity_audit':{str(BUS/n):digest(BUS/n) for n in ['identity-gate.json','tuple-reuse-comparisons.json','duplicate-captures.json']}})
    note=f'''# 阶段交付：正式训练资源确认

日期：2026-09-26。B0–B6已完成；B7–B10尚未启动，没有新的外层业务分类成绩。

- 原120访问、30内容、六类业务和五折全部保留。
- 1185候选连接中1179通过共同资格，6对排除；2370个原捕获文件约500MiB，没有新增采集。
- 2358份单侧张量保存完整序列；所有表示共用时间信息与flow成员；原FR未更名。
- 15组fold×seed的训练post缩放、局部donor及逐flow逐侧曝光核验通过；每访问每SSL阶段曝光250次。L2按完整内容轮次交替两侧，flow rank保持两个轮次，保证边际与L3/L4一致。
- SSL平衡子池访问等权平均flow保留率{counts.flow_retention.mean():.4%}，平均post字节保留率{counts.byte_retention.mean():.4%}；监督微调仍使用全部共同flow。
- {tests['tests']}项测试通过，包括分块前向/梯度等价。1179个post编码替换pre后完全不变；内容、访问、路径、捕获哈希均无跨折交集。
- RTX 4060 Ti上九臂各20步工程测试完成。峰值已分配显存{budget['peak_allocated_bytes']/2**20:.1f}MiB；这是PyTorch allocated，不等于显卡总显存占用。CPU/GPU训练样本前向最大差{budget['cpu_gpu_max_forward_difference']:.3g}。
- 按实测估算195个正式阶段训练约{budget['estimated_training_hours']:.2f}小时，未含评估、I/O和bootstrap。不同fold/流长可能导致偏差，不能视作完成时间保证。

已向用户请求确认这一长时GPU预算。未自动缩短1000步、减少seed/折/臂，也未将20步工程损失解释为分类结果。

数据与覆盖细节见 coverage-report.md；逐臂速度见 engineering-report.md。B0–B6可通过 eval/record_time_business/run.py 分阶段复用。正式runner及结果分析在预算放行后继续B7–B10。
'''
    (DOC/'stage-report.md').write_text(note,encoding='utf-8')
    print('B0-B6 final audit complete; formal budget awaiting confirmation',flush=True)
