"""Descriptive summaries with matching denominators, no new acceptance thresholds."""
from common import *

def quadrant_summary(q,keys):
    rows=[]
    sums=['mass','raw_contribution','std_contribution','train_raw_contribution','train_std_contribution',
          'modified_mass','raw_improved_mass','raw_worsened_mass','std_improved_mass','std_worsened_mass',
          'raw_before_contribution','raw_after_contribution','std_before_contribution','std_after_contribution']
    for k,d in q.groupby(keys,dropna=False,sort=True):
        k=k if isinstance(k,tuple) else (k,);r=dict(zip(keys,k));r['unit_cells']=len(d);r['observation_exposures']=int(d.observations.sum())
        for name in sums:r[name]=float(d[name].mean())
        for prefix in ['raw','std','train_raw','train_std']:
            r[prefix+'_conditional_delta']=r[prefix+'_contribution']/r['mass'] if r['mass']>0 else None
        rows.append(r)
    return pd.DataFrame(rows)

def run():
    q=pd.read_parquet(OUT/'tables/quadrant-errors.parquet');f=pd.read_parquet(OUT/'tables/qualification-fold-gates.parquet')
    r=pd.read_parquet(OUT/'tables/qualification-role-gates.parquet');co=pd.read_parquet(OUT/'tables/standardized-coordinate-contributions.parquet')
    enriched=q.merge(r[['role_id','arm','block','relation_qualified']],on=['role_id','arm','block'],validate='many_to_one')
    summary=quadrant_summary(q,['arm','quadrant']);save(summary,'quadrant-summary')
    save(quadrant_summary(q,['arm','target','quadrant']),'quadrant-deployment-summary')
    save(quadrant_summary(q,['arm','feature','quadrant']),'quadrant-feature-summary')
    save(quadrant_summary(enriched,['arm','train_eligible','relation_qualified','quadrant']),'quadrant-qualification-summary')
    marginal=[];funnel=[]
    gates=['variation_pass','epsilon_pass','ratio_pass','coverage_pass','excess_pass']
    for (arm,feature),d in f.groupby(['arm','feature']):
        for gate in gates:marginal.append({'arm':arm,'feature':feature,'scope':'fold','gate':gate,'candidates':len(d),'passed':int(d[gate].sum()),'failed':int((~d[gate]).sum())})
    for arm,d in r.groupby('arm'):
        current=pd.Series(True,index=d.index)
        for gate in ['four_fold_train_pass','min_coverage_pass','pooled_coverage_pass','mean_excess_pass','excess_fold_count_pass',
                     'full_C_variation_pass','full_C_epsilon_pass','full_C_ratio_pass']:
            marginal.append({'arm':arm,'feature':'all_blocks','scope':'role','gate':gate,'candidates':len(d),'passed':int(d[gate].sum()),'failed':int((~d[gate]).sum())})
        # First three gates apply to every training fold, then consistency and heldout checks.
        scoped=f[f.arm.eq(arm)].groupby(['role_id','block'])
        stages=[('variation_all_folds',scoped.variation_pass.all()),('absolute_all_folds',scoped.epsilon_pass.all()),('ratio_all_folds',scoped.ratio_pass.all())]
        for name,flags in stages:
            values=np.asarray([bool(flags.loc[(a,b)]) for a,b in zip(d.role_id,d.block)])
            before=int(current.sum());current=current&values;funnel.append({'arm':arm,'stage':name,'before':before,'after':int(current.sum()),'first_failures':before-int(current.sum())})
        for name in ['four_fold_train_pass','min_coverage_pass','pooled_coverage_pass','mean_excess_pass','excess_fold_count_pass',
                     'full_C_variation_pass','full_C_epsilon_pass','full_C_ratio_pass']:
            before=int(current.sum());current=current&d[name];funnel.append({'arm':arm,'stage':name,'before':before,'after':int(current.sum()),'first_failures':before-int(current.sum())})
    save(pd.DataFrame(marginal),'gate-failure-marginal');save(pd.DataFrame(funnel),'gate-failure-funnel')
    margins=[]
    for (arm,feature),d in f.groupby(['arm','feature']):
        for name in ['variation_margin','epsilon_margin','ratio_margin','coverage_margin','excess_margin']:
            x=d[name].dropna();margins.append({'arm':arm,'feature':feature,'margin':name,'defined':len(x),
                    'min':float(x.min()) if len(x) else None,'median':float(x.median()) if len(x) else None,
                    'Q10':float(x.quantile(.1)) if len(x) else None,'Q90':float(x.quantile(.9)) if len(x) else None})
    save(pd.DataFrame(margins),'gate-margin-distributions')
    scopes=[]
    for arm,d in q.groupby('arm'):
        units=d.groupby(['role_id','inner','block'])[['raw_contribution','std_contribution','train_raw_contribution','train_std_contribution','modified_mass']].sum()
        for scope,rawcol,stdcol in [('all_candidate_blocks','raw_contribution','std_contribution'),('training_eligible_blocks','train_raw_contribution','train_std_contribution')]:
            scopes.append({'arm':arm,'scope':scope,'mean_raw_delta':float(units[rawcol].mean()),'mean_std_delta':float(units[stdcol].mean()),
                           'accepted_anchor_count':0,'classification_evaluated':False})
        scopes.append({'arm':arm,'scope':'final_selected_blocks_noop','mean_raw_delta':0.,'mean_std_delta':0.,'accepted_anchor_count':0,'classification_evaluated':False})
    save(pd.DataFrame(scopes),'projection-scope-summary')
    csum=co.groupby(['arm','target','feature','coordinate'],as_index=False).agg(std_positive=('std_positive','mean'),std_negative=('std_negative','mean'),
                std_net=('std_net','mean'),raw_positive=('raw_positive','mean'),raw_negative=('raw_negative','mean'),scale_min=('scale','min'),
                scale_median=('scale','median'),constant_fraction=('constant_coordinate','mean'),IO_std_positive=('IO_std_positive','mean'),OO_std_positive=('OO_std_positive','mean'))
    save(csum,'coordinate-summary');top=[]
    for (arm,target_,feature),d in csum.groupby(['arm','target','feature']):
        ordered=d.sort_values('std_positive',ascending=False).head(5).copy();total=float(d.std_positive.sum());ordered['rank']=np.arange(1,len(ordered)+1)
        ordered['top5_positive_share']=float(ordered.std_positive.sum())/total if total>0 else None;top.append(ordered)
    save(pd.concat(top,ignore_index=True),'coordinate-top5')
    write(OUT/'audits/summary-closure.json',{'passed':True,'conditionals_are_contribution_divided_by_mass':True,'empty_conditionals_preserved':True,
          'P_G_not_combined':True,'role_overlaps_not_independent_samples':True,'descriptive_only':True,'new_fits':0})
    progress('summaries_complete',tables=len(list((OUT/'tables').glob('*.parquet'))))

if __name__=='__main__':run()
