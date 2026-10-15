from core import *

def projection(x,m1,m2,model,mass):
    require(torch.equal(model['mu'],m1['mu']) and torch.equal(model['scale'],m1['scale']),'Projection coordinate mismatch')
    delta=m1['matrix']-m2['matrix'];effect=(x-m1['pre_mean'])@delta.T
    ww=model['weight']-model['weight'].mean(0,keepdim=True)
    ds=effect@ww.T
    a=affine.apply(m1,x);b=affine.apply(m2,x)
    pa=torch.softmax(a@model['weight'].T+model['bias'],1);pb=torch.softmax(b@model['weight'].T+model['bias'],1)
    mapped_centered=(a@ww.T);baseline=mapped_centered-(mapped_centered*mass[:,None]).sum(0)
    return {'mapping_effect_MSE':float((mass[:,None]*effect.square()).sum()/96),
            'relative_logit_effect_MSE':float((mass[:,None]*ds.square()).sum()/6),
            'mapped_logit_variance':float((mass[:,None]*baseline.square()).sum()/6),
            'probability_L1_mean':float((mass*(pa-pb).abs().sum(1)).sum()),
            'mapped_view_class_change_mass':float((mass*(pa.argmax(1)!=pb.argmax(1))).sum()),
            'max_relative_logit_effect':float(ds.abs().max())}

def run():
    with stage('project'):
        require(C.read(OUT/'algebra-verification.json')['passed'],'Algebra prerequisite')
        c=C.contract();s=selected();rows=[];recovery=[];actual=[];byclass=[]
        inn=pd.read_parquet(RUN/'selection/inner-predictions.parquet');innerseal=C.read(RUN/'selection/predictions-complete.json')
        require(C.sha(RUN/'selection/inner-predictions.parquet')==innerseal['sha256'],'Inner prediction seal')
        require(len(inn)==829440,'Inner row budget')
        outerpred=pd.read_parquet(RUN/'predictions/visits.parquet');pc=[f'p{i}' for i in range(6)]
        for ix,(r,e) in enumerate(pairs(c)):
            m1=C.get(C.mappath(r,'JA1',e));m2=C.get(C.mappath(r,'JA2',e))
            cp=C.package(ROOT/r['C_paired'],'paired-map');sp=C.package(C.rolepath(r)/'source-pre.parquet','source-fit')
            post=C.package(C.rolepath(r)/'source-post.parquet','source-fit')
            h=C.package(ROOT/r['heldout_visits'],'explain-visits')
            hx=(C.tensor(h[['pre_'+a for a in C.HIST]])-m1['mu'])/m1['scale']
            hy=(C.tensor(h[['post_'+a for a in C.HIST]])-m1['mu'])/m1['scale']
            metadata={'role_id':r['id'],'inner':r['inner'],'outer':r['outer'],'target':r['target'],'calibration':r['calibration'],'group':r['group'],'eta':e}
            for arm,m in [('JA1',m1),('JA2',m2)]:
                errors=(affine.apply(m,hx)-hy).square()
                for j,entry in enumerate(h.to_dict('records')):
                    recovery.append({**metadata,'arm':arm,'visit_id':entry['visit_id'],'content_id':entry['content_id'],
                        'label_id':entry['label_id'],'uncovered':C.LABELS.index(entry['label_id']) in C.MASKS[r['group']],
                        'MSE':float(errors[j].mean()),'offline_pre_only_diagnostic':True,'classification_input_pre':False})
            for classifier_arm in ['JA1','JA2']:
                t=0. if r['inner'] is not None else C.chosen(r,classifier_arm,s)['t']
                model=C.get(C.modelpath(r,classifier_arm,e,t));ww=model['weight']-model['weight'].mean(0,keepdim=True)
                zz=(C.tensor(post[C.HIST])-m1['mu'])/m1['scale'];scores=zz@ww.T
                realvar=float((scores-scores.mean(0)).square().mean())
                inputs=[('C',(C.tensor(cp[['pre_'+a for a in C.HIST]])-m1['mu'])/m1['scale'],C.tensor(cp.fit_mass)),
                        ('source-pre',(C.tensor(sp[C.HIST])-m1['mu'])/m1['scale'],C.tensor(np.full(len(sp),1/len(sp)))),
                        ('heldout-pre-offline',hx,C.tensor(np.full(len(h),1/len(h))))]
                for scope,x,mass in inputs:
                    v=projection(x,m1,m2,model,mass)
                    rows.append({**metadata,'classifier_arm':classifier_arm,'t':t,'scope':scope,'rows':len(x),
                        'source_post_relative_logit_variance':realvar,'is_attack_score':False,**v})
                # Per-class signed effects, reported in the same role coordinate.
                ds=((hx-m1['pre_mean'])@(m1['matrix']-m2['matrix']).T)@ww.T
                for label in C.LABELS:
                    mask=C.tensor(h.label_id.eq(label).to_numpy(),torch.bool)
                    for k in range(6):byclass.append({**metadata,'classifier_arm':classifier_arm,'scope':'heldout-pre-offline',
                        'true_label':label,'score_label':C.LABELS[k],'mean_relative_logit_effect':float(ds[mask,k].mean()),
                        'mean_squared_effect':float(ds[mask,k].square().mean()),'is_attack_score':False})
            if r['inner'] is not None:
                parts=inn[inn.outer.eq(r['outer'])&inn.target.eq(r['target'])&inn.group.eq(r['group'])&inn.inner.eq(r['inner'])&inn.calibration.eq(r['calibration'])&inn.eta.eq(e)&inn.t.eq(0)]
            else:
                parts=outerpred[outerpred.outer.eq(r['outer'])&outerpred.target.eq(r['target'])&outerpred.group.eq(r['group'])]
            labels=C.package(C.rolepath(r)/'labels.parquet','select' if r['inner'] is not None else 'score').set_index('visit_id')
            a=parts[parts.arm.eq('JA1')].set_index('visit_id');b=parts[parts.arm.eq('JA2')].set_index('visit_id').loc[a.index]
            require(len(a)==24 and a.index.is_unique,'Actual frozen prediction coverage')
            truth=C.truths(labels.loc[a.index]);good=a.prediction.to_numpy()==truth;before=b.prediction.to_numpy()==truth
            metrics1=C.metrics(truth,a[pc].to_numpy(),C.MASKS[r['group']])[0];metrics2=C.metrics(truth,b[pc].to_numpy(),C.MASKS[r['group']])[0]
            actual.append({**metadata,'F1_U_JA1':metrics1['F1_uncovered'],'F1_U_JA2':metrics2['F1_uncovered'],
                'F1_U_delta':metrics1['F1_uncovered']-metrics2['F1_uncovered'],'repair':int((good&~before).sum()),
                'added_error':int((~good&before).sum()),'prediction_changed':int((a.prediction!=b.prediction).sum()),
                'uses_real_post_predictions':True,'same_t':True if r['inner'] is not None else C.chosen(r,'JA1',s)['t']==C.chosen(r,'JA2',s)['t'],
                'descriptive_not_new_success_test':True})
            if (ix+1)%100==0:progress('projection',completed=ix+1,total=2929)
        save(OUT/'decision-projections.parquet',pd.DataFrame(rows));save(OUT/'relative-class-score-effects.parquet',pd.DataFrame(byclass))
        save(OUT/'matched-candidate-recovery.parquet',pd.DataFrame(recovery));save(OUT/'actual-post-candidate-comparisons.parquet',pd.DataFrame(actual))
        write(OUT/'projection-verification.json',{'passed':True,'pairs':2929,'projection_rows':len(rows),'recovery_rows':len(recovery),
            'classifier_updates':0,'new_fits':0,'all_tensor_arithmetic_CUDA_float64':True,'inner_fixed_t':0,
            'test_pre_only_after_original_prediction_seal':True,'offline_mapped_views_are_not_post_attack_results':True})
if __name__=='__main__':run()
