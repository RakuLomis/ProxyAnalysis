"""Sealed post-only predictions; only afterwards source-query-pre diagnostics."""
from common import *
from model import residual
import pyarrow.dataset as ds

def seal_models():
    configure('fit');files=[]
    for r in roles():
        for arm in ARMS:verifyseal(modelroot(r,arm)/'complete.json');files.append(modelroot(r,arm)/'complete.json')
        for arm in ['B0-R']+ARMS:
            p=OUT/'classifiers'/r['id']/(arm+'.pt');quality=read(p.with_suffix('.quality.json'))
            require(quality['accepted'] and quality['iterations']<2000 and quality['evaluations']<10000,'Complete accepted heads')
            files.extend([p,p.with_suffix('.quality.json')])
        files.append(OUT/'packages'/r['id']/'base.pt')
    immutable(OUT/'manifests/zero-aliases.json',dict(roles=[r['id'] for r in roles()],ZERO='direct frozen B0 reference',exact=True,new_fits=0))
    files.append(OUT/'manifests/zero-aliases.json');seal(OUT/'manifests/models-complete.json',files,heads=192,paths=144,actual_H_U_read=False)

def predict():
    configure('inference');barrier('models-complete.json');rows=[];qfiles=[]
    for i,r in enumerate(roles()):
        q=external(PREP/'packages'/r['id']/'query.parquet',r['id'],'query')
        require(set(q)=={'visit_id',*HIST} and len(q)==24 and q.visit_id.is_unique,'Closed query schema')
        raw=tensor(q[HIST]);base=own(OUT/'packages'/r['id']/'base.pt',r['id']);x=(raw-base['mu'])/base['scale']
        for arm in PIPES:
            if arm=='B0':w,b=base['weight'],base['bias']
            else:
                h=own(OUT/'classifiers'/r['id']/(arm+'.pt'),r['id']);w,b=h['W'],h['c']
            with torch.no_grad():lp=F.log_softmax(F.linear(x,w,b),1)
            require(bool(torch.isfinite(lp).all()),'Finite log probabilities')
            d=pd.DataFrame(cpu(lp),columns=[f'l{k}' for k in range(6)]);d['prediction']=cpu(lp.argmax(1));d['visit_id']=q.visit_id.tolist()
            d['role_id']=r['id'];d['pipeline']=arm;d['role_target']=r['target'];d['query_deployment']=r['calibration'];d['group']=r['group'];d['inner']=r['inner'];rows.append(d)
        p=OUT/'diagnostic-query'/r['id']/'post.pt';put(p,dict(raw=raw,visit_ids=q.visit_id.tolist()),role_id=r['id'],capability='diag');qfiles.append(p)
        flush('predict');progress('post_only_inference',completed=i+1,total=48)
    p=OUT/'predictions/post-only.parquet';save(p,pd.concat(rows,ignore_index=True))
    seal(OUT/'manifests/predictions-complete.json',[p]+qfiles,rows=5760,query_pre_reads=0,label_reads=0,models_sealed_first=True)

def reconstruct_query_pre(r,query):
    import common
    require(common.CAP=='diagnostic','Diagnostic-only producer')
    barrier('predictions-complete.json');c=contract();require(c['query_pre_authorized_after_predictions'],'No query-pre authorization')
    require(r['calibration']!=r['target'] and r['calibration'] in r['sources']+[r['calibration']],'Pseudo only')
    outer0=set(roles()[0]['train_contents'])|set(roles()[0]['validation_contents'])
    require(set(r['validation_contents'])<=outer0,'Outer f0 H forbidden')
    require(sha(NATIVE)==c['files'][rel(NATIVE)]['sha256'],'Diagnostic native binding')
    allow=(ds.field('protocol')==r['calibration'])&ds.field('content_id').isin(r['validation_contents'])
    cols=['session_id','protocol','content_id','pair_id','repetition']+['pre_'+f for f in FEATURES]
    frame=ds.dataset(NATIVE,format='parquet').to_table(columns=cols,filter=allow).to_pandas()
    require(frame.pair_id.is_unique and not frame.protocol.eq(r['target']).any(),'Diagnostic role/pair')
    frame['visit_id']=frame.session_id.map(lambda s:hashlib.sha256(('business-query-v1:'+s).encode()).hexdigest())
    require(set(frame.visit_id)==set(query['visit_ids']),'Query-pre visit binding')
    meta=frame[['visit_id','content_id','repetition']].drop_duplicates();require(len(meta)==24 and meta.groupby('content_id').size().eq(4).all(),'Query-pre grid')
    ix=frame.visit_id.map({v:i for i,v in enumerate(query['visit_ids'])}).to_numpy(int);den=np.bincount(ix,minlength=24);counts=np.zeros((24,96),dtype=np.int64)
    for j,f in enumerate(FEATURES):
        values=frame['pre_'+f].to_numpy();require(np.isfinite(values).all() and (values>=0).all() and (values==np.floor(values)).all(),'Diagnostic integer features')
        edges=[1,256,1024,4096,16384,65536,262144,1048576] if j<4 else [1,2,3,4,8,16,32,64,128]
        bins=np.searchsorted(edges,values,side='right');counts[:,block(j)]=np.bincount(ix*SIZES[j]+bins,minlength=24*SIZES[j]).reshape(24,SIZES[j])
        require(np.all(counts[:,block(j)].sum(1)==den),'Query-pre integer denominator')
    READS.append(dict(path=rel(NATIVE),kind='source-query-pre-filtered',role_id=r['id'],capability='diagnostic',sha256=c['files'][rel(NATIVE)]['sha256'],
        rows=len(frame),protocol=r['calibration'],contents=r['validation_contents'],columns=cols,only_after_predictions_seal=True))
    return tensor(counts/den[:,None]),counts,den

def diagnose():
    import common
    configure('diagnostic');barrier('predictions-complete.json');files=[];rows=[];legality=[]
    for i,r in enumerate(roles()):
        rid=r['id'];d=own(OUT/'packages'/rid/'shared.pt',rid);query=own(OUT/'diagnostic-query'/rid/'post.pt',rid)
        # reconstruct_query_pre checks common's capability explicitly.
        a,counts,den=reconstruct_query_pre(r,query);xa=(a-d['mu'])/d['scale'];zb=(query['raw']-d['mu'])/d['scale'];z0=xa@d['M'].T+d['bias'];w=own(OUT/'packages'/rid/'base.pt',rid)['weight'];wc=w-w.mean(0)
        outputs={'B0':z0}
        for arm in ARMS:
            s=own(modelroot(r,arm)/'export.pt',rid)['parameters']
            with torch.no_grad():outputs[arm]=z0+residual(s,xa)
        for arm,z in outputs.items():
            e=z-zb;raw=d['mu']+d['scale']*z
            for j in range(24):rows.append(dict(role_id=rid,pipeline=arm,visit_id=query['visit_ids'][j],role_target=r['target'],query_deployment=r['calibration'],group=r['group'],
                Q_MSE=float((e[j]@d['Q']).square().mean()),relative_logit_MSE=float((wc@e[j]).square().mean()),std_MSE=float(e[j].square().mean()),
                raw_MSE=float((d['scale']*e[j]).square().mean())))
            for j in range(10):
                b=raw[:,block(j)];legality.append(dict(role_id=rid,pipeline=arm,block=j,negative_fraction=float((b<0).double().mean()),minimum=float(b.min()),maximum=float(b.max()),mass_error_max=float((b.sum(1)-1).abs().max())))
        p=OUT/'diagnostics'/rid/'outputs.pt';put(p,dict(outputs=outputs,true_post=zb,visit_ids=query['visit_ids'],Q=d['Q'],pre_counts=torch.from_numpy(counts),denominator=torch.from_numpy(den)),role_id=rid,capability='diag');files.append(p)
        flush('diagnostic');progress('source_query_pre_diagnostic',completed=i+1,total=48)
    for name,df in [('generation-errors',rows),('legality',legality)]:
        p=OUT/'diagnostics'/(name+'.parquet');save(p,df);files.append(p)
    seal(OUT/'manifests/diagnostics-complete.json',files,source_query_pre_read=True,actual_H_U_reads=0,query_labels_read=False,no_fit=True)

if __name__=='__main__':
    import sys
    action=sys.argv[1]
    try:{'seal':seal_models,'predict':predict,'diagnose':diagnose}[action]()
    except BaseException as e:failure('evaluation-'+action,e);raise
