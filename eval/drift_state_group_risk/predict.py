"""Frozen post-only predictions, isolated label-only inner selection."""
import sys
from common import *

def main(inner):
    c=start('class-predict'); rows=[]
    oldchoices={(x['outer'],x['protocol']):x['t'] for x in read(OLD/'selection/choices.json') if x['arm']=='KSR1'}
    selected=None
    if not inner: selected={(x['outer'],x['protocol'],x['arm']):x['alpha'] for x in read(OUT/'selection/choices.json')}
    for r in c['roles']:
        if (r['inner'] is not None)!=inner: continue
        query=package(mainfolder('packages',r)/'query-post.parquet','class-predict'); require(len(query)==24,'Query size')
        for arm in ARMS:
            values=([0,.25,1,4] if inner else [oldchoices[(r['outer'],r['protocol'])]]) if arm=='DSR1' else ([0] if arm=='DSR0' else ALPHAS if inner else [selected[(r['outer'],r['protocol'],arm)]])
            for a in values:
                if arm=='DSR1': m=oldartifact('models',r,'zero' if a==0 else f'KSR1-t{a:g}')
                else: m=artifact(mainfolder('models',r)/('zero.pt' if a==0 else f'{arm}-a{a:g}.pt'))
                pred=probabilities(m,query); pred['outer']=r['outer']; pred['inner']=r['inner']; pred['protocol']=r['protocol']; pred['arm']=arm; pred['setting']=a; rows.append(pred)
    dst=OUT/('selection' if inner else 'predictions'); dst.mkdir(parents=True,exist_ok=True)
    save(pd.concat(rows,ignore_index=True),dst/('inner-predictions.parquet' if inner else 'visits.parquet'))
    complete(dst,prediction_post_only=True,labels_pre_states_read=False)
    finish('D16' if inner else 'D20',rows=sum(len(d) for d in rows),cuda_inference=True)

def select():
    c=start('inner-select'); labels=[]; dst=OUT/'selection'; p=dst/'inner-predictions.parquet'
    require(read(dst/'complete.json')['sha256'][p.name]==sha(p),'Inner prediction seal')
    pred=pd.read_parquet(p)
    for r in c['roles']:
        if r['inner'] is None: continue
        d=package(mainfolder('packages',r)/'score-labels.parquet','inner-select'); d['outer']=r['outer']; d['inner']=r['inner']; labels.append(d)
    pred=pred.merge(pd.concat(labels,ignore_index=True),on=['outer','inner','protocol','visit_id'],validate='many_to_one')
    summaries=[]; choices=[]
    for (o,p,arm,a),sub in pred.groupby(['outer','protocol','arm','setting']):
        require(len(sub)==96 and sub.visit_id.is_unique and sub.content_id.nunique()==24,'Inner OOF coverage')
        values,_=metrics(truths(sub),sub[[f'p{i}' for i in range(6)]].to_numpy()); summaries.append({'outer':o,'protocol':p,'arm':arm,'setting':a,**values})
    summary=pd.DataFrame(summaries)
    oldchoices={(x['outer'],x['protocol']):x['t'] for x in read(OLD/'selection/choices.json') if x['arm']=='KSR1'}
    for (o,p,arm),sub in summary.groupby(['outer','protocol','arm']):
        if arm=='DSR0': continue
        maximum=sub.F1.max(); win=sub[sub.F1>=maximum-1e-12].sort_values('setting').iloc[0]
        if arm=='DSR1': require(win.setting==oldchoices[(o,p)],'Strong L2 selection replay differs')
        choices.append({'outer':int(o),'protocol':p,'arm':arm,'alpha':float(win.setting),'inner_F1':float(win.F1)})
    save(summary,dst/'candidate-summary.parquet'); write(dst/'choices.json',choices)
    write(dst/'complete.json',{'time_unix':time.time(),'choices_sha256':sha(dst/'choices.json'),
      'predictions_sha256':sha(dst/'inner-predictions.parquet'),'candidates_sha256':sha(dst/'candidate-summary.parquet'),
      'criterion':'pooled six-class OOF macro F1; tie 1e-12 smallest setting','outer_outcomes_opened':False})
    finish('D17',choices=len(choices),strong_L2_choices_exact_replay=True)

if __name__=='__main__':
    {'inner':lambda:main(True),'outer':lambda:main(False),'select':select}[sys.argv[1]]()
