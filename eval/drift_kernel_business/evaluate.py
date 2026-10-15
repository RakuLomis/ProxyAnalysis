"""Independent offline scoring, after all predictions have been frozen."""
from common import *

def metrics(y,pred,prob,weights=None):
    w=np.ones(len(y)) if weights is None else np.asarray(weights,dtype=float)
    cm=np.bincount(np.asarray(y)*6+np.asarray(pred),weights=w,minlength=36).reshape(6,6)
    tp=np.diag(cm)
    den=cm.sum(0)+cm.sum(1)
    f1=np.divide(2*tp,den,out=np.zeros(6),where=den>0)
    ce=-np.average(np.log(prob[np.arange(len(y)),np.asarray(y)]),weights=w)
    br=np.average(np.square(prob-np.eye(6)[y]).sum(1),weights=w)
    return {'F1':float(f1.mean()),'accuracy':float(tp.sum()/cm.sum()),'CE':float(ce),'Brier':float(br)},cm,f1

def joined(role='score'):
    contract=read(OUT/'manifests/experiment-contract.json')
    done=read(OUT/'predictions/complete.json')
    for p,h in done['sha256'].items():
        require(sha(ROOT/p)==h,'Predictions altered before scoring')
    pred=pd.read_parquet(OUT/'predictions/visits.parquet')
    labels=pd.concat([load_package(rolefolder(r['fold'],r['protocol'])/'score-labels.parquet',role) for r in contract['roles']],ignore_index=True)
    require(labels.visit_id.is_unique and len(labels)==480,'Score label identity changed')
    data=pred.merge(labels.drop(columns=['fold','protocol']),on='visit_id',validate='many_to_one')
    data['truth']=data.label_id.map({v:i for i,v in enumerate(LABELS)})
    return data

def run():
    start('score')
    data=joined()
    rows,classes,confusion=[],[],[]
    for (p,arm,seed),g in data.groupby(['protocol','arm','seed']):
        result,cm,f1=metrics(g.truth.to_numpy(),g.prediction.to_numpy(),g[[f'p{i}' for i in range(6)]].to_numpy())
        rows.append({'protocol':p,'arm':arm,'seed':int(seed),'visits':len(g),**result})
        for i,label in enumerate(LABELS):
            classes.append({'protocol':p,'arm':arm,'seed':int(seed),'label':label,'F1':float(f1[i]),
              'precision':float(cm[i,i]/cm[:,i].sum()) if cm[:,i].sum()>0 else 0.,
              'recall':float(cm[i,i]/cm[i].sum()),'support':int(cm[i].sum())})
            for j in range(6):
                confusion.append({'protocol':p,'arm':arm,'seed':int(seed),'truth':i,'prediction':j,'count':int(cm[i,j])})
    scores=pd.DataFrame(rows)
    saveparquet(scores,OUT/'scores/protocol-seed.parquet')
    summary=scores.groupby(['protocol','arm'])[['F1','accuracy','CE','Brier']].mean().reset_index()
    for metric in ['F1','accuracy','CE','Brier']:
        ranges=scores.groupby(['protocol','arm'])[metric].agg(['min','max']).reset_index()
        summary=summary.merge(ranges.rename(columns={'min':metric+'_min','max':metric+'_max'}),on=['protocol','arm'])
    saveparquet(summary,OUT/'scores/protocol-summary.parquet')
    saveparquet(pd.DataFrame(classes),OUT/'scores/class-seed.parquet')
    saveparquet(pd.DataFrame(confusion),OUT/'scores/confusion.parquet')
    content=data.assign(correct=data.prediction.eq(data.truth)).groupby(['protocol','arm','seed','content_id','label_id']).agg(visits=('visit_id','size'),correct=('correct','sum')).reset_index()
    saveparquet(content,OUT/'scores/content-errors.parquet')
    global_rows=[]
    for arm,g in summary.groupby('arm'):
        global_rows.append({'arm':arm,'protocol_equal_F1':float(g.F1.mean()),'worst_protocol_F1':float(g.F1.min()),
                            'protocol_equal_CE':float(g.CE.mean()),'protocol_equal_Brier':float(g.Brier.mean())})
    saveparquet(pd.DataFrame(global_rows),OUT/'scores/global-summary.parquet')
    saveparquet(data,OUT/'scores/scored-visits.parquet')
    finish('score',visits=480,rows=len(data),no_model_refit=True)
    print(summary[['protocol','arm','F1','CE','Brier']].to_string(index=False),flush=True)

if __name__=='__main__':
    run()
