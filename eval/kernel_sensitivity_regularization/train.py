"""Distinct CUDA fitting, post-only prediction and label-only selection stages."""
import sys
from common import *
from matrices import build_kernel,regularizers

def roles(c,inner): return [r for r in c['roles'] if (r['inner'] is not None)==inner]

def paths(kind,r): return folder(kind,r['outer'],r['protocol'],r['inner'])

def matrix_run(inner):
    c=start('inner_matrix' if inner else 'outer_matrix')
    if not inner: require((OUT/'selection/complete.json').exists(),'Selection must be frozen first')
    summaries=[]
    for r in roles(c,inner):
        out=paths('regularizers',r); out.mkdir(parents=True,exist_ok=True)
        if resume(out): summaries.append(read(out/'summary.json')); continue
        pf=paths('packages',r)
        pre=package(pf/'fit-pre.parquet','matrix'); post=package(pf/'fit-post.parquet','matrix')
        gp=package(pf/'group-pre.parquet','matrix'); gb=package(pf/'group-post.parquet','matrix')
        hist=package(pf/'fit-post-hist.parquet','matrix'); x,mu,scale=standardize(hist)
        n=18 if inner else 24
        require(set(pre.content_id)==set(r['train_contents']) and abs(pre.fit_mass.sum()-n)<1e-10,'Wrong matrix training range/mass')
        bundles={}; kfolder=paths('kernels',r); kfolder.mkdir(parents=True,exist_ok=True)
        for feature in FEATURES:
            fresh=build_kernel(pre,post,gp,gb,feature)
            if not inner:
                old=outer_kernel(r,feature,c)
                for key in ['M1','M2','true_counts','group_counts']:
                    require(float((fresh[key]-old[key]).abs().max())<1e-10,'Outer kernel replay mismatch')
                    fresh[key]=old[key]
            bundles[feature]=fresh
            torch.save(fresh,kfolder/(feature+'.pt'))
        complete(kfolder,train_contents=r['train_contents'],inner_uses_old_outer_kernel=False,fit_mass=n)
        artifacts,summary=regularizers(bundles,hist[['content_id',*HIST]],scale)
        for arm,a in artifacts.items(): torch.save({'mu':mu,'scale':scale,**a},out/(arm+'.pt'))
        summary.update({'outer':r['outer'],'protocol':r['protocol'],'inner':r['inner'],
                        'train_contents':r['train_contents'],'fit_mass':n,'kernel_manifest_sha256':sha(kfolder/'complete.json')})
        write(out/'summary.json',summary); complete(out,train_contents=r['train_contents'],summary_sha256=sha(out/'summary.json'))
        summaries.append(summary)
        print('CUDA matrices',r['outer'],r['protocol'],r['inner'],flush=True)
    write(OUT/'manifests'/('inner-matrices.json' if inner else 'outer-matrices.json'),summaries)
    finish('inner_matrix' if inner else 'outer_matrix',roles=len(summaries),kernels=10*len(summaries),labels_used_for_matrices=False)

def fit_run(inner):
    c=start('inner_fit' if inner else 'outer_fit'); allfits=[]
    if not inner:
        select=read(OUT/'selection/choices.json')
        require(sha(OUT/'selection/choices.json')==read(OUT/'selection/complete.json')['choices_sha256'],'Selection changed')
        choices={(x['outer'],x['protocol'],x['arm']):x['t'] for x in select}
    for r in roles(c,inner):
        mf=paths('models',r); mf.mkdir(parents=True,exist_ok=True)
        if resume(mf) and (inner or read(mf/'complete.json').get('selected_final',False)):
            allfits.extend(read(mf/'complete.json')['fits']); continue
        hist=package(paths('packages',r)/'fit-post-hist.parquet','fit')
        require(set(hist.content_id)==set(r['train_contents']),'Wrong classifier fit contents')
        x,mu,scale=standardize(hist); y=tensor(truths(hist),torch.int64); logs=[]
        if inner:
            state,log=lr_fit(x,y); torch.save({'mu':mu,'scale':scale,**state},mf/'zero.pt'); logs.append(log)
        else:
            log=read(mf/'complete.json')['fits'][0]; logs.append(log)
        for arm in ARMS[1:]:
            candidates=TS if inner else [choices[(r['outer'],r['protocol'],arm)]]
            for t in candidates:
                if t==0: continue
                factor=None
                if arm!='KSR1':
                    a=artifact(paths('regularizers',r)/(arm+'.pt'),'fit')
                    require(torch.equal(a['mu'],mu) and torch.equal(a['scale'],scale),'Matrix/classifier coordinates differ')
                    factor=a['factor']
                state,log=lr_fit(x,y,arm,t,factor)
                torch.save({'mu':mu,'scale':scale,**state},mf/f'{arm}-t{t:g}.pt'); logs.append(log)
        for log in logs: log.update({'outer':r['outer'],'protocol':r['protocol'],'inner':r['inner']})
        complete(mf,fits=logs,selected_final=not inner,
                 train_contents=r['train_contents'],zero_shared=True,
                 input_sha256=sha(paths('packages',r)/'fit-post-hist.parquet'))
        allfits.extend(logs)
        print('CUDA fitted',r['outer'],r['protocol'],r['inner'],'models',len(logs),flush=True)
    saveparquet(pd.DataFrame(allfits),OUT/'manifests'/('inner-optimizer.parquet' if inner else 'outer-optimizer.parquet'))
    finish('inner_fit' if inner else 'outer_fit',independent_fits=len(allfits),all_cuda_float64=True,
           max_gradient=max(x['max_gradient'] for x in allfits),budget_hits=sum(x['hit_iteration_budget'] for x in allfits))

def predict_run(inner):
    c=start('inner_predict' if inner else 'outer_predict'); rows=[]
    if not inner:
        selections=read(OUT/'selection/choices.json')
        sealed=read(OUT/'selection/complete.json')
        require(sha(OUT/'selection/choices.json')==sealed['choices_sha256'],'Selection changed')
        choices={(x['outer'],x['protocol'],x['arm']):x['t'] for x in selections}
    for r in roles(c,inner):
        q=package(paths('packages',r)/'query-post-hist.parquet','predict')
        require(len(q)==24,'Query visit coverage changed')
        for arm in (ARMS[1:] if inner else ARMS):
            ts=TS if inner else [0 if arm=='KSR0' else choices[(r['outer'],r['protocol'],arm)]]
            for t in ts:
                name='zero.pt' if t==0 else f'{arm}-t{t:g}.pt'
                model=artifact(paths('models',r)/name,'predict'); prediction=probabilities(model,q)
                prediction['outer']=r['outer']; prediction['protocol']=r['protocol']; prediction['inner']=r['inner']
                prediction['arm']=arm; prediction['t']=t; rows.append(prediction)
        print('post-only predictions',r['outer'],r['protocol'],r['inner'],flush=True)
    target=OUT/('selection' if inner else 'predictions'); target.mkdir(exist_ok=True)
    path=target/('inner-predictions.parquet' if inner else 'visits.parquet')
    saveparquet(pd.concat(rows,ignore_index=True),path)
    write(target/('predictions-complete.json' if inner else 'complete.json'),{'sha256':sha(path),
          'rows':sum(len(x) for x in rows),'labels_opened':False,'pre_kernel_Gamma_opened':False,
          'selected_before_outer_inference':not inner})
    finish('inner_predict' if inner else 'outer_predict',rows=sum(len(x) for x in rows),post_only=True)

def select():
    c=start('select')
    path=OUT/'selection/inner-predictions.parquet'
    require(sha(path)==read(OUT/'selection/predictions-complete.json')['sha256'],'Inner predictions not frozen')
    pred=pd.read_parquet(path); score=[]
    for r in roles(c,True):
        s=package(paths('packages',r)/'score-labels.parquet','select')
        s['outer']=r['outer']; s['inner']=r['inner']; score.append(s)
    labels=pd.concat(score,ignore_index=True)
    scored=pred.merge(labels,on=['outer','inner','protocol','visit_id'],validate='many_to_one')
    require(len(scored)==30720,'Inner prediction support changed')
    rows=[]; foldrows=[]; choices=[]
    for (outer,p,arm,t),df in scored.groupby(['outer','protocol','arm','t']):
        require(len(df)==96 and df.content_id.nunique()==24 and df.visit_id.nunique()==96,'Inner OOF duplicated/missing')
        m,_=metrics(truths(df),df[[f'p{i}' for i in range(6)]].to_numpy())
        rows.append({'outer':outer,'protocol':p,'arm':arm,'t':t,**m})
        for inner,f in df.groupby('inner'):
            m,_=metrics(truths(f),f[[f'p{i}' for i in range(6)]].to_numpy())
            foldrows.append({'outer':outer,'protocol':p,'arm':arm,'t':t,'inner':int(inner),**m})
    table=pd.DataFrame(rows)
    for (outer,p,arm),df in table.groupby(['outer','protocol','arm']):
        top=df.F1.max(); winner=df[df.F1>=top-1e-12].sort_values('t').iloc[0]
        choices.append({'outer':int(outer),'protocol':p,'arm':arm,'t':float(winner.t),'inner_F1':float(winner.F1)})
    require(len(choices)==80,'Selection role count wrong')
    saveparquet(table,OUT/'selection/candidate-summary.parquet')
    saveparquet(pd.DataFrame(foldrows),OUT/'selection/candidate-fold-summary.parquet')
    write(OUT/'selection/choices.json',choices)
    write(OUT/'selection/complete.json',{'choices_sha256':sha(OUT/'selection/choices.json'),
         'candidates_sha256':sha(OUT/'selection/candidate-summary.parquet'),
         'inner_predictions_sha256':sha(path),'sealed_unix':time.time(),'outer_labels_opened':False,
         'criterion':'pooled six-class macro F1; tie <=1e-12 smallest t'})
    finish('select',choices=choices,outer_data_reads=0)
    print('S11 80 choices sealed; no outer labels opened',flush=True)

if __name__=='__main__':
    {'inner-matrix':lambda:matrix_run(True),'outer-matrix':lambda:matrix_run(False),
     'inner-fit':lambda:fit_run(True),'outer-fit':lambda:fit_run(False),
     'inner-predict':lambda:predict_run(True),'predict':lambda:predict_run(False),'select':select}[sys.argv[1]]()
