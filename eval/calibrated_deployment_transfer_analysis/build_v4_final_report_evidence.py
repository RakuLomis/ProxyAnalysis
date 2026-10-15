"""Read-only aggregation of sealed v4 predictions and fit logs; no model inference."""
from pathlib import Path
import hashlib
import json
from datetime import datetime
from zoneinfo import ZoneInfo
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
RUN = ROOT/'outputs/calibrated-deployment-business-transfer-20261006/run-04'
DEST = ROOT/'outputs/calibrated-deployment-business-transfer-analysis-20261007/run-04'
LABELS = ['bing.com::search_results_view', 'developer.mozilla.org::document_view',
          'github.com::repository_view', 'wikipedia.org::article_view',
          'youtube.com::search_results_view', 'youtube.com::video_playback']
MASKS = {'G0': [2,4], 'G1': [0,3], 'G2': [1,5]}
FEATURES = ['W_up','W_down','U_up','U_down','P_up','P_down','E_up','E_down',
            'FR_packet_runs','R_unique_zero_runs']
FW = np.array([1/12]*8+[1/6]*2)
INPUTS = {}

def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as src:
        for chunk in iter(lambda: src.read(1024*1024), b''): h.update(chunk)
    return h.hexdigest()

def read(path):
    INPUTS[path.relative_to(ROOT).as_posix()] = sha(path)
    return json.loads(path.read_text(encoding='utf-8-sig'))

def table(rel):
    path = RUN/rel
    INPUTS[path.relative_to(ROOT).as_posix()] = sha(path)
    return pd.read_parquet(path)

def write(name, value):
    path = DEST/name
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False,
                    default=lambda x: x.item() if isinstance(x,np.generic) else str(x))+'\n', encoding='utf8')

def save(name, df): df.to_parquet(DEST/(name+'.parquet'), index=False)

def markdown(df):
    def cell(v):
        if isinstance(v,(float,np.floating)): return f'{v:.6f}'
        return str(v).replace('|','\\|').replace('\n',' ')
    return '\n'.join(['| '+' | '.join(map(str,df.columns))+' |',
         '| '+' | '.join(['---']*len(df.columns))+' |']+
         ['| '+' | '.join(cell(v) for v in row)+' |' for row in df.itertuples(index=False,name=None)])

def run():
    DEST.mkdir(parents=True, exist_ok=True)
    complete = read(RUN/'completion.json'); verification = read(RUN/'verification.json')
    assert complete['verification_passed'] and verification['passed']
    assert not (RUN/'failure.json').exists() and not (RUN/'runner.lock').exists()
    v4 = read(RUN/'manifests/experiment-contract-v4.json')
    c = read(ROOT/'outputs/calibrated-deployment-business-transfer-20261006/run-01/manifests/experiment-contract-amended-io-v1.json')
    sources = {**c['source_sha256'], **v4['previous_source_sha256'], **v4['source_sha256']}
    for path, expected in sources.items(): assert sha(ROOT/path) == expected, path
    assert sha(RUN/'manifests/experiment-contract-v4.json') == read(RUN/'manifests/contract-seal.json')['sha256']
    d = table('scores/scored-visits.parquet'); summary = table('scores/target-group-summary.parquet')
    classes = table('scores/class-results.parquet'); equal = table('scores/equal-weight-summary.parquet')
    targets = table('scores/target-summary.parquet'); contrasts = table('comparisons/primary-contrasts.parquet')
    assert len(d)==10080 and d.visit_id.nunique()==480 and d.content_id.nunique()==30
    y = d.label_id.map(dict(zip(LABELS,range(6)))).to_numpy(int)
    p = d[[f'p{i}' for i in range(6)]].to_numpy()
    assert np.all(p>0) and np.isfinite(p).all() and np.max(np.abs(p.sum(1)-1))<1e-12
    assert np.array_equal(p.argmax(1), d.prediction.to_numpy())
    assert not d.duplicated(['target','group','arm','visit_id']).any()
    assert sha(RUN/'predictions/visits.parquet') == read(RUN/'predictions/complete.json')['sha256']
    cmfile = RUN/'scores/confusion-matrices.npz'; INPUTS[cmfile.relative_to(ROOT).as_posix()] = sha(cmfile)
    savedcm = np.load(cmfile)
    maxerr = 0.; classerr = 0.
    classidx = classes.set_index(['target','group','arm','label_id'])
    for key, part in d.groupby(['target','group','arm']):
        yy = part.label_id.map(dict(zip(LABELS,range(6)))).to_numpy(int)
        pp = part[[f'p{i}' for i in range(6)]].to_numpy(); zz = pp.argmax(1)
        assert len(part)==120 and part.visit_id.is_unique
        cm = np.bincount(yy*6+zz,minlength=36).reshape(6,6)
        assert np.array_equal(cm,savedcm['_'.join(key)])
        den = cm.sum(0)+cm.sum(1); f1 = np.divide(2*np.diag(cm),den,out=np.zeros(6),where=den>0)
        metrics = {'F1_all':f1.mean(),'accuracy':(yy==zz).mean(),
                   'CE_nats':-np.log(pp[np.arange(len(yy)),yy]).mean(),
                   'Brier':((pp-np.eye(6)[yy])**2).sum(1).mean(),
                   'F1_uncovered':f1[MASKS[key[1]]].mean(),
                   'F1_aux':np.delete(f1,MASKS[key[1]]).mean()}
        metrics['CE_bits']=metrics['CE_nats']/np.log(2)
        saved = summary.set_index(['target','group','arm']).loc[key]
        maxerr = max(maxerr, *(abs(float(saved[k])-float(v)) for k,v in metrics.items()))
        for j,label in enumerate(LABELS):
            ref = classidx.loc[(*key,label)]
            assert int(ref.support)==int(cm[j].sum())==20
            classerr=max(classerr,abs(float(ref.F1)-f1[j]))
    assert maxerr<1e-12 and classerr<1e-12
    pool = summary.groupby('arm').mean(numeric_only=True)
    for arm,row in equal.set_index('arm').iterrows():
        for field in ['F1_uncovered','F1_all','F1_aux','CE_nats','Brier','accuracy']:
            assert abs(row[field]-pool.loc[arm,field])<1e-12
    bp=RUN/'comparisons/bootstrap-metrics.npz'; INPUTS[bp.relative_to(ROOT).as_posix()]=sha(bp)
    boots=np.load(bp); cierr=0.
    for row in contrasts.itertuples():
        comparator=row.comparison.removeprefix('CT4-')
        delta=boots['CT4_F1_uncovered']-boots[comparator+'_F1_uncovered']
        assert len(delta)==10000
        ci95=np.quantile(delta,[.025,.975]); ci98=np.quantile(delta,[.05/6,1-.05/6])
        cierr=max(cierr,abs(ci95[0]-row.CI95_low),abs(ci95[1]-row.CI95_high),
                  abs(ci98[0]-row.CI98_333_low),abs(ci98[1]-row.CI98_333_high))
    assert cierr<1e-12
    choices=read(RUN/'selection/choices.json')
    choice_df=pd.DataFrame([x for x in choices if x['arm']!='StrongPost'])
    selection=choice_df.groupby(['arm','t']).size().rename('outer_scenarios').reset_index()
    strong = pd.Series([x['selected_arm'] for x in choices if x['arm']=='StrongPost']).value_counts().to_dict()
    assert strong=={'CT2':60}
    for outer_role in [x for x in c['main'] if x['inner'] is None]:
        for arm in ['CT0','CT1','CT2','CT3','CT4']:
            row=choice_df[(choice_df.outer==outer_role['outer'])&(choice_df.target==outer_role['target'])&
                          (choice_df.group==outer_role['group'])&(choice_df.arm==arm)]
            assert len(row)==1
    assert (d[d.arm.eq('StrongPost')][['target','group','visit_id','p0','p1','p2','p3','p4','p5']].sort_values(['target','group','visit_id']).reset_index(drop=True)
            .equals(d[d.arm.eq('CT2')][['target','group','visit_id','p0','p1','p2','p3','p4','p5']].sort_values(['target','group','visit_id']).reset_index(drop=True)))
    numeric_rows=[]
    for i,path in enumerate(sorted((RUN/'models/main').rglob('CT*.json'))):
        info=json.loads(path.read_text(encoding='utf8')); log=info['optimizer']
        assert log['accepted'] and all(log['gates'].values())
        assert log['settings']['max_iter']==2000 and log['settings']['max_eval']==10000
        assert log['numeric_policy_sha256']==v4['numeric_policy_sha256']
        numeric_rows.append({'role_id':info['role_id'],'arm':info['arm'],'t':info['t'],
             'scope':'outer' if path.parent.name=='outer' else 'inner',
             **{k:log[k] for k in ['iterations','function_evaluations','seconds','max_gradient',
                 'objective_replay_error','gradient_replay_error','original_audit_evaluations',
                 'evaluation_budget_overshoot','optimizer_exit_reason']}})
        if (i+1)%3000==0: print('fit logs audited',i+1,flush=True)
    nr=pd.DataFrame(numeric_rows)
    assert len(nr)==14700 and nr.scope.eq('inner').sum()==14400 and nr.scope.eq('outer').sum()==300
    numeric=[]
    for arm,part in nr.groupby('arm'):
        numeric.append({'arm':arm,'models':len(part),'iterations_median':part.iterations.median(),
             'iterations_p95':part.iterations.quantile(.95),'iterations_max':part.iterations.max(),
             'evaluations_p95':part.function_evaluations.quantile(.95),
             'evaluations_max':part.function_evaluations.max(),'iterations_ge_500':part.iterations.ge(500).sum(),
             'evaluations_ge_625':part.function_evaluations.ge(625).sum(),
             'fit_seconds_sum':part.seconds.sum(),'fit_seconds_mean':part.seconds.mean(),
             'max_original_gradient':part.max_gradient.max()})
    numeric=pd.DataFrame(numeric)
    d['uncovered']=np.array([j in MASKS[g] for j,g in zip(y,d.group)])
    flips=[]
    base=d[d.arm.eq('CT4')]
    for comparator in ['StrongPost','CT0','CT1','CT2','CT3','CT5']:
        merged=base.merge(d[d.arm.eq(comparator)][['target','group','visit_id','prediction']],
             on=['target','group','visit_id'],suffixes=('','_reference'),validate='one_to_one')
        yy=merged.label_id.map(dict(zip(LABELS,range(6)))).to_numpy(int)
        merged['repair']=(merged.prediction_reference!=yy)&(merged.prediction==yy)
        merged['added_error']=(merged.prediction_reference==yy)&(merged.prediction!=yy)
        merged['wrong_to_wrong']=(merged.prediction_reference!=yy)&(merged.prediction!=yy)&(merged.prediction_reference!=merged.prediction)
        for scope,part in [('all_masks',merged),('uncovered',merged[merged.uncovered])]:
            for target, subset in [('all',part)]+list(part.groupby('target')):
                flips.append({'comparator':comparator,'scope':scope,'target':target,'prediction_rows':len(subset),
                    **{k:int(subset[k].sum()) for k in ['repair','added_error','wrong_to_wrong']},
                    'net_correct':int(subset.repair.sum()-subset.added_error.sum())})
    flips=pd.DataFrame(flips)
    original_flips=table('scores/error-flips.parquet').groupby('comparator')[['repair','added_error','wrong_to_wrong']].sum()
    for row in flips[(flips.scope=='all_masks')&(flips.target=='all')].itertuples():
        for field in ['repair','added_error','wrong_to_wrong']:assert getattr(row,field)==original_flips.loc[row.comparator,field]
    uc=classes[np.array([LABELS.index(label) in MASKS[group] for label,group in zip(classes.label_id,classes.group)])]
    ucmean=uc.groupby(['label_id','arm'],as_index=False)[['F1','precision','recall']].mean()
    pair=summary.pivot(index=['target','group'],columns='arm',values='F1_uncovered').reset_index()
    for comparator in ['StrongPost','CT0','CT1','CT3']:
        pair['CT4_minus_'+comparator]=pair.CT4-pair[comparator]
    kernel=table('scores/uncovered-kernel-visit-scores.parquet')
    ks=kernel[kernel.uncovered].groupby(['target','group','arm','feature'],as_index=False)[['loss_bits','marginal_bits']].mean()
    ks['feature_weight']=ks.feature.map(dict(zip(FEATURES,FW)))
    ks['weighted_loss']=ks.loss_bits*ks.feature_weight;ks['weighted_marginal']=ks.marginal_bits*ks.feature_weight
    kcomp=ks.groupby(['target','group','arm'],as_index=False)[['weighted_loss','weighted_marginal']].sum()
    kcomp['gain_bits']=kcomp.weighted_marginal-kcomp.weighted_loss
    kfeat=ks.groupby(['feature','arm'],as_index=False)[['loss_bits','marginal_bits']].mean()
    kfeat['gain_bits']=kfeat.marginal_bits-kfeat.loss_bits
    support=table('scores/source-pre-support.parquet')
    sup=support.groupby(['target','arm'],as_index=False).agg(
        mean_feature_zero_support=('mean_zero_support_mass','mean'),
        largest_visit_feature_zero_support=('max_zero_support_mass','max'))
    timeline=[]
    markers=sorted((RUN/'manifests/stages').glob('*.json'))
    start=(read(RUN/'manifests/contract-seal.json'))['time_unix']
    previous=start
    for marker in markers:
        state=read(marker); ts=state['time_unix']
        timeline.append({'stage':marker.stem,'completed_Asia_Shanghai':datetime.fromtimestamp(ts,ZoneInfo('Asia/Shanghai')).isoformat(),
                         'elapsed_seconds_since_previous_marker':ts-previous})
        previous=ts
    for name,frame in [('numeric-model-log-summary',nr),('numeric-arm-summary',numeric),
         ('selection-counts',selection),('error-flip-summary',flips),('uncovered-class-summary',ucmean),
         ('target-group-comparison',pair),('kernel-uncovered-composites',kcomp),
         ('kernel-uncovered-feature-summary',kfeat),('source-support-summary',sup),('stage-timeline',pd.DataFrame(timeline))]:save(name,frame)
    evidence={'completed_at_Asia_Shanghai':datetime.fromtimestamp(complete['time_unix'],ZoneInfo('Asia/Shanghai')).isoformat(),
         'contract_sealed_at_Asia_Shanghai':datetime.fromtimestamp(start,ZoneInfo('Asia/Shanghai')).isoformat(),
         'seconds_from_seal_to_completion':complete['time_unix']-start,
         'classification_replay_max_error':maxerr,'class_F1_replay_max_error':classerr,'bootstrap_quantile_replay_max_error':cierr,
         'classification_cells':len(summary),'class_rows':len(classes),'prediction_rows':len(d),'unique_visits':480,'contents':30,
         'source_hashes_checked':len(sources),'strongpost_selection':strong,
         'numeric_models':len(nr),'numeric_exit_reasons':nr.optimizer_exit_reason.value_counts().to_dict(),
         'iterations_ge_500':int(nr.iterations.ge(500).sum()),'evaluations_ge_625':int(nr.function_evaluations.ge(625).sum()),
         'max_iterations':int(nr.iterations.max()),'max_evaluations':int(nr.function_evaluations.max()),
         'max_gradient_replay_error':float(nr.gradient_replay_error.max()),
         'view_group_wins':{x:int((pair['CT4_minus_'+x]>0).sum()) for x in ['StrongPost','CT0','CT1','CT3']},
         'input_sha256':INPUTS,'new_fits':0,'new_inference':0,'raw_capture_reads':0,
         'frozen_training_sources_or_outputs_modified':False}
    write('report-evidence.json',evidence)
    sections=['# 第四版完整结果数值附录','所有表来自封存预测、评分和模型日志。未重新训练或推理。']
    for title,frame in [('部署和业务组等权成绩',equal),('三项预登记比较',contrasts),('各目标部署',targets),
           ('十二场景未覆盖业务对照',pair),('未覆盖条件下逐业务均值',ucmean),
           ('修复与新增错误',flips),('源内选择次数',selection),('逐臂数值成本',numeric),
           ('未覆盖业务核评分',kcomp),('核特征评分',kfeat),('源pre未见入口箱质量',sup),
           ('阶段时间',pd.DataFrame(timeline)),('全部84个六类评分单元',summary),('全部504条逐类结果',classes)]:
        sections.extend(['## '+title,markdown(frame)])
    (DEST/'complete-numeric-appendix.md').write_text('\n\n'.join(sections)+'\n',encoding='utf8')
    print(json.dumps({k:v for k,v in evidence.items() if k!='input_sha256'},ensure_ascii=False,indent=2))

if __name__=='__main__':run()
