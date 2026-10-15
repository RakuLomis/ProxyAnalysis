"""Post-only model calls; validation labels opened only by separate selector."""
import sys
from common import *
def main(inner):
    c=start('class-predict'); rows=[]
    for r in c['roles']:
        if (r['inner'] is not None)!=inner: continue
        query=package(r,'query-post','class-predict'); require(len(query)==24,'Query count')
        for arm in ARMS:
            settings=([0.] if arm=='RW0' else L2_SETTINGS if arm=='RW1' else RATIOS) if inner else [None]
            for setting in settings:
                if not inner: m=artifact(folder('models',r)/(arm+'.pt'),'frozen-classifier')
                elif arm in ['RW0','RW1']: m=baseline(r,setting)
                else: m=artifact(folder('models',r)/f'{arm}-r{setting:g}.pt','frozen-classifier')
                d=probabilities(m,query); d['outer']=r['outer']; d['inner']=r['inner']; d['protocol']=r['protocol']; d['arm']=arm
                if inner: d['setting']=setting
                rows.append(d)
    dst=OUT/('selection' if inner else 'predictions'); dst.mkdir(parents=True,exist_ok=True)
    result=pd.concat(rows,ignore_index=True); require(len(result)==(32640 if inner else 2400),'Prediction matrix complete')
    save(result,dst/('inner-predictions.parquet' if inner else 'visits.parquet'))
    complete(dst,prediction_post_only=True,query_labels_pre_states_weights_selection_not_read=True)
    finish('RW14' if inner else 'RW20',rows=len(result),CUDA_inference=True)
def select():
    c=start('inner-select'); dst=OUT/'selection'; p=dst/'inner-predictions.parquet'
    require(read(dst/'complete.json')['sha256'][p.name]==sha(p),'Inner predictions sealed'); labels=[]
    for r in c['roles']:
        if r['inner'] is None: continue
        d=package(r,'score-labels','inner-select'); d['outer']=r['outer']; d['inner']=r['inner']; labels.append(d)
    pred=pd.read_parquet(p).merge(pd.concat(labels,ignore_index=True),on=['outer','inner','protocol','visit_id'],validate='many_to_one')
    rows=[]
    for (o,proto,arm,setting),d in pred.groupby(['outer','protocol','arm','setting']):
        require(len(d)==96 and d.visit_id.is_unique and d.content_id.nunique()==24,'Validation OOF membership')
        m,_=metrics(truths(d),d[[f'p{i}' for i in range(6)]].to_numpy()); rows.append({'outer':int(o),'protocol':proto,'arm':arm,'setting':float(setting),**m})
    summary=pd.DataFrame(rows); choices=[]
    original={(v['outer'],v['protocol']):v['t'] for v in read(OLD/'selection/choices.json') if v['arm']=='KSR1'}
    for (o,proto,arm),d in summary.groupby(['outer','protocol','arm']):
        if arm=='RW0': continue
        win=d[d.F1>=d.F1.max()-1e-12].sort_values('setting').iloc[0]
        if arm=='RW1': require(win.setting==original[(o,proto)],'RW1 fair L2 exact selection replay')
        choices.append({'outer':int(o),'protocol':proto,'arm':arm,'setting':float(win.setting),'inner_F1':float(win.F1)})
    require(len(choices)==80,'Choice matrix'); save(summary,dst/'candidate-summary.parquet'); write(dst/'choices.json',choices)
    write(dst/'complete.json',{'time_unix':time.time(),'choices_sha256':sha(dst/'choices.json'),
      'predictions_sha256':sha(p),'candidates_sha256':sha(dst/'candidate-summary.parquet'),
      'criterion':'pooled full-six-class macro-F1; tie 1e-12 smallest setting','outer_outcomes_opened':False})
    finish('RW15-RW16',choices=80,RW1_exact_replay=True)
if __name__=='__main__': {'inner':lambda:main(True),'outer':lambda:main(False),'select':select}[sys.argv[1]]()
