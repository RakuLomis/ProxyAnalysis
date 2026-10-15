"""Legal source-inner selection; avoids shadowing Python's select module."""
from common import *

def inner_predict():
    c=start('inner_predict');rows=[]
    for index,r in enumerate(c['roles']):
        if r['inner'] is None:continue
        q=package(rolepath(r)/'query.parquet','query')
        for arm in ARMS:
            for eta in ETAS:
                for t in TS:
                    d=predict(get(modelpath(r,arm,eta,t)),q)
                    for k in ['outer','inner','target','calibration','group']:d[k]=r[k]
                    d['arm']=arm;d['eta']=eta;d['t']=t;rows.append(d)
        if index%40==0:progress('JA_inner_predict',roles=index)
    d=pd.concat(rows,ignore_index=True);require(len(d)==829440,'Inner prediction count')
    p=OUT/'selection/inner-predictions.parquet';save(d,p)
    complete(p.with_name('predictions-complete.json'),sha256=sha(p),rows=len(d),outer_labels_read=False)
    finish('inner_predict',rows=len(d))

def select():
    c=start('select');p=OUT/'selection/inner-predictions.parquet'
    require(sha(p)==read(p.with_name('predictions-complete.json'))['sha256'],'Inner prediction seal')
    pred=pd.read_parquet(p);labels=[]
    for r in c['roles']:
        if r['inner'] is None:continue
        d=package(rolepath(r)/'labels.parquet','select').drop(columns='protocol')
        for k in ['outer','inner','target','calibration','group']:d[k]=r[k]
        labels.append(d)
    score=pred.merge(pd.concat(labels),on=['outer','inner','target','calibration','group','visit_id'],validate='many_to_one')
    rows=[]
    for key,d in score.groupby(['outer','target','group','arm','eta','t']):
        vals=[]
        for pseudo,part in d.groupby('calibration'):
            require(len(part)==96 and part.content_id.nunique()==24 and part.visit_id.is_unique,'Pseudo target coverage')
            vals.append(metrics(truths(part),part[[f'p{i}' for i in range(6)]].to_numpy(),MASKS[key[2]])[0]['F1_uncovered'])
        require(len(vals)==3,'Pseudo target count')
        rows.append(dict(zip(['outer','target','group','arm','eta','t'],key),F1=float(np.mean(vals))))
    table=pd.DataFrame(rows);selected=[]
    for key,d in table.groupby(['outer','target','group','arm']):
        v=d[d.F1>=d.F1.max()-1e-12].sort_values(['eta','t'],ascending=[False,True]).iloc[0]
        selected.append(dict(zip(['outer','target','group','arm'],key),eta=float(v.eta),t=float(v.t),source_inner_F1=float(v.F1)))
    require(len(selected)==180,'Choice count')
    save(table,OUT/'selection/candidates.parquet');write(OUT/'selection/choices.json',selected)
    complete(OUT/'selection/complete.json',sha256=sha(OUT/'selection/choices.json'),choices=180,actual_target_used=False)
    finish('select',choices=180)

def outer_predict():
    c=start('predict');selected=choices();rows=[]
    for r in c['roles']:
        if r['inner'] is not None:continue
        q=package(rolepath(r)/'query.parquet','query')
        for arm in ARMS:
            v=chosen(r,arm,selected);d=predict(get(modelpath(r,arm,v['eta'],v['t'])),q)
            for k in ['outer','target','group']:d[k]=r[k]
            d['arm']=arm;d['eta']=v['eta'];d['t']=v['t'];rows.append(d)
    d=pd.concat(rows,ignore_index=True);require(len(d)==4320,'Outer new prediction count')
    p=OUT/'predictions/visits.parquet';save(d,p)
    complete(p.with_name('complete.json'),sha256=sha(p),rows=len(d),outer_labels_read=False,test_pre_read=False)
    finish('predict',rows=len(d),post_only=True)

if __name__=='__main__':{'inner-predict':inner_predict,'select':select,'predict':outer_predict}[sys.argv[1]]()
