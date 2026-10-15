"""Gate traces and C-only independent numerical replay; zero parameter fitting."""
from common import *
from arithmetic import *

KEY=['role_id','arm','inner','block']
NUM=['epsilon','pre_variation','post_variation','variation','epsilon_variation_ratio',
     'train_median','train_Q95','train_max']

class Audit:
    def __init__(self):self.maxima={};self.checks=0
    def close(self,name,a,b,tol=1e-12):
        if a is None or (np.isscalar(a) and bool(pd.isna(a))):need(b is None or pd.isna(b),name+' missing-value mismatch');err=0.
        else:
            aa=np.asarray(a);bb=np.asarray(b);err=float(np.max(np.abs(aa-bb)))
        self.maxima[name]=max(self.maxima.get(name,0.),err);self.checks+=1
        need(err<=tol,name+f' mismatch {err:.4g} > {tol}')
    def flag(self,name,a,b):self.checks+=1;need(bool(a)==bool(b),name+' boolean mismatch')

def fit_data(root,arm,r,full=False):
    if arm=='P':
        d=package(root/('P.parquet' if full else 'P-fit.parquet'),arm,r)
        a,b=raw(d,'pre'),raw(d,'post');ta=d.content_token.to_numpy();tb=None;parts=[d]
    else:
        da=package(root/('G-pre.parquet' if full else 'G-pre-fit.parquet'),arm,r)
        db=package(root/('G-post.parquet' if full else 'G-post-fit.parquet'),arm,r)
        a,b=raw(da),raw(db);ta=da.content_token.to_numpy();tb=db.content_token.to_numpy();parts=[da,db]
    n=64 if full else 48;nc=16 if full else 12
    need(len(a)==len(b)==n and len(set(ta))==nc,'Fit sample size')
    for d in parts:need(np.allclose(d.fit_mass,1/n,atol=1e-15,rtol=0) and abs(d.fit_mass.sum()-1)<1e-12,'Fit mass not content/visit equal')
    return a,b,ta,tb

def gate_columns(d,prefix=''):
    out=d.copy()
    out[prefix+'variation_margin']=out.variation-.1
    out[prefix+'epsilon_margin']=.1-out.epsilon
    out[prefix+'ratio_margin']=.5-out.epsilon_variation_ratio
    out[prefix+'variation_pass']=out.variation>=.1
    out[prefix+'epsilon_pass']=out.epsilon<=.1
    out[prefix+'ratio_defined']=out.epsilon_variation_ratio.notna()
    out[prefix+'ratio_pass']=out.epsilon_variation_ratio.notna()&(out.epsilon_variation_ratio<=.5)
    out[prefix+'replayed_train_eligible']=out[[prefix+'variation_pass',prefix+'epsilon_pass',prefix+'ratio_pass']].all(axis=1)
    out[prefix+'unclipped_Q90']=out.epsilon;out[prefix+'epsilon_was_clipped']=False
    return out

def run():
    configure();c=contract();rulespec=c['rule'];need(rulespec=={'variation_min':.1,'epsilon_max':.1,'epsilon_variation_ratio_max':.5,
           'quantile':.9,'fold_coverage_min':.875,'OOF_coverage_min':.9,'excess_min':.1,'excess_folds_min':2,'floating_comparison_tolerance':1e-12},'Unrecognized parent scientific policy')
    audit=Audit();fold=table(PARENT/'scores/fold-scores.parquet');role=table(PARENT/'scores/anchor-qualification.parquet')
    need(len(fold)==4800 and len(role)==1200 and not fold.duplicated(KEY).any(),'Parent grid')
    fidx=fold.set_index(KEY);ridx=role.set_index(['role_id','arm','block']);quantrows=[];scaleraudit=[]
    ppoints=[];quadrows=[];coordrows=[];geom_rows=[]
    need(read(checked(PARENT/'rules/anchor-gate.json','parent-gate'))['P_anchor_role_blocks']==0,'Nonempty final Guard not covered by closeout')
    for ri,r in enumerate(c['roles']):
        src=ROOT/'outputs/calibrated-deployment-business-transfer-20261006/run-01/packages'/r['id']/'source-post.parquet'
        sd=table(src,'source-post-scaler-replay',columns=['content_id',*HIST])
        need(len(sd)==288 and set(sd.content_id)<=set(r['train_contents']),'Source scope')
        for i in range(4):
            root=PARENT/'packages'/r['id']/f'i{i}';dest=PARENT/'diagnostics'/r['id']/f'i{i}'
            held=set(r['C_diagnostic_contents'][i]);allowed=sd[~sd.content_id.isin(held)]
            need(len(allowed)==240,'Scaler source exclusion')
            gpost=package(root/'G-post-fit.parquet','G',r);values=torch.cat([raw(allowed),raw(gpost)])
            mu=values.sum(0)/len(values);constant=values.amax(0)==values.amin(0)
            sc=torch.sqrt(((values-mu)**2).sum(0)/len(values));sc=torch.where(constant,torch.ones_like(sc),sc)
            savedcoord=obj(root/'scaler.pt');audit.close('scaler_mu',mu.cpu().numpy(),savedcoord['mu'].cpu().numpy())
            audit.close('scaler_scale',sc.cpu().numpy(),savedcoord['scale'].cpu().numpy())
            need(bool((savedcoord['scale']>0).all()),'Nonpositive frozen scale')
            scaleraudit.append({'role_id':r['id'],'inner':i,'source_rows':240,'C_rows':48,'constant_dimensions':int(constant.sum()),
                                'heldout_source_contents_excluded':True,'scale_min':float(savedcoord['scale'].min())})
            for arm in ['P','G']:
                a,b,ta,tb=fit_data(root,arm,r);reproduced=independent_rules(a,b,ta,tb)
                archived=read(checked(dest/f'{arm}-rules.json','C-frozen-rules'))
                for v,old in zip(reproduced,archived):
                    j=v['block'];row=fidx.loc[(r['id'],arm,i,j)]
                    for k in NUM:audit.close('rule_'+k,v[k],old[k]);audit.close('fold_'+k,v[k],row[k])
                    audit.flag('train_eligible',v['train_eligible'],old['train_eligible'])
                    quantrows.append({'role_id':r['id'],'arm':arm,'inner':i,'block':j,'scope':'training_fold',
                                      'contents':12,'side_visits':48,'observations':v['observations'],'element_mass':1/v['observations'],
                                      'Q90_rank':v['Q90_rank'],'content_distance_count':v['content_distance_count'],
                                      'content_Q90_rank':v['content_Q90_rank'],'epsilon':old['epsilon'],'Q90_replay':v['epsilon'],
                                      'epsilon_cap':.1,'clipped':False,'executed_order':'Q90_then_qualification','replay_passed':True})
                pred=obj(dest/f'{arm}-predictions.pt');model=obj(dest/f'{arm}-map.pt')
                need(pred['a'].shape==(16,96) and len(set(pred['content_tokens']))==4,'C query shape')
                audit.close('prediction_scale',pred['scale'].cpu().numpy(),savedcoord['scale'].cpu().numpy())
                replay=((pred['a']-savedcoord['mu'])/savedcoord['scale'])@model['matrix'].T+model['bias']
                replay=replay*savedcoord['scale']+savedcoord['mu']
                audit.close('frozen_forward',replay.cpu().numpy(),pred['b0'].cpu().numpy(),1e-10)
                scored=package(root/('P-score.parquet' if arm=='P' else 'G-post-validation.parquet'),arm,r)
                aa,bb,mm,zz,ztrain,tokens=prepare_pairs(pred,scored,arm)
                need(len(aa)==(16 if arm=='P' else 64),'P actual pairs / G Cartesian size')
                for old in archived:
                    j=old['block'];slc=sl(j);eps=old['epsilon'];base={'role_id':r['id'],'target':r['target'],'group':r['group'],
                         'outer':r['outer'],'arm':arm,'inner':i,'block':j,'feature':FEATURES[j]}
                    dr=distance(aa[:,slc],bb[:,slc]);dm=distance(aa[:,slc],mm[:,slc])
                    inside=dr<=eps+1e-12;mapinside=dm<=eps+1e-12
                    labels=np.where(inside.cpu().numpy(),np.where(mapinside.cpu().numpy(),'II','IO'),np.where(mapinside.cpu().numpy(),'OI','OO'))
                    newz=projection(aa[:,slc],mm[:,slc],eps);nt=newz if old['train_eligible'] else mm[:,slc]
                    audit.close('candidate_projection',newz.cpu().numpy(),zz[:,slc].cpu().numpy(),1e-10)
                    audit.close('training_projection',nt.cpu().numpy(),ztrain[:,slc].cpu().numpy(),1e-10)
                    sigma=pred['scale'][slc];raw0,std0=losses(mm[:,slc],bb[:,slc],sigma)
                    raw1,std1=losses(zz[:,slc],bb[:,slc],sigma);rt,st=losses(ztrain[:,slc],bb[:,slc],sigma)
                    rd=raw1-raw0;ds=std1-std0
                    oldrow=fidx.loc[(r['id'],arm,i,j)]
                    for name,v in [('coverage',inside.double().mean()),('v_real',(~inside).double().mean()),('v_map',(~mapinside).double().mean()),
                         ('excess',(~mapinside).double().mean()-(~inside).double().mean()),('raw_MSE_before',raw0.mean()),('raw_MSE_after',raw1.mean()),
                         ('standardized_MSE_before',std0.mean()),('standardized_MSE_after',std1.mean())]:audit.close('score_'+name,float(v),oldrow[name],1e-10)
                    strict=dr<=eps;worst=float(rd[strict].max()) if bool(strict.any()) else 0.
                    need(worst<=1e-10,'Euclidean projection worsened a strictly inside true target')
                    n=len(aa);mass=1/n;correction=torch.sqrt(((zz[:,slc]-mm[:,slc])**2).sum(1))
                    boundary=(dr>eps)&(dr<=eps+1e-12);mboundary=(dm>eps)&(dm<=eps+1e-12)
                    pp=pd.DataFrame({'content_token':tokens,'observation_index':np.arange(n),'quadrant':labels,
                        'element_mass':mass,'real_distance':dr.cpu().numpy(),'map_distance':dm.cpu().numpy(),
                        'raw_before':raw0.cpu().numpy(),'raw_after':raw1.cpu().numpy(),'raw_delta':rd.cpu().numpy(),
                        'std_before':std0.cpu().numpy(),'std_after':std1.cpu().numpy(),'std_delta':ds.cpu().numpy(),
                        'train_raw_delta':(rt-raw0).cpu().numpy(),'train_std_delta':(st-std0).cpu().numpy(),
                        'correction':correction.cpu().numpy(),'real_boundary_band':boundary.cpu().numpy(),'map_boundary_band':mboundary.cpu().numpy()})
                    for k,v in base.items():pp[k]=v
                    pp['train_eligible']=old['train_eligible'];pp['accepted_anchor']=False;pp['scope']='all_candidate_blocks'
                    ppoints.append(pp)
                    for q in QUADS:
                        ix=np.flatnonzero(labels==q);m=len(ix)/n;row={**base,'quadrant':q,'observations':len(ix),'contents':len(set(tokens[ix])),
                            'mass':m,'train_eligible':old['train_eligible'],'accepted_anchor':False,'scope':'all_candidate_blocks',
                            'raw_contribution':float(rd[ix].sum())/n,'std_contribution':float(ds[ix].sum())/n,
                            'train_raw_contribution':float((rt[ix]-raw0[ix]).sum())/n,'train_std_contribution':float((st[ix]-std0[ix]).sum())/n,
                            'raw_before_contribution':float(raw0[ix].sum())/n,'raw_after_contribution':float(raw1[ix].sum())/n,
                            'std_before_contribution':float(std0[ix].sum())/n,'std_after_contribution':float(std1[ix].sum())/n}
                        for name,v in [('real_distance',dr),('map_distance',dm),('overrun',torch.clamp(dm-eps,min=0)),('correction',correction),
                             ('raw_before',raw0),('raw_after',raw1),('raw_delta',rd),('std_before',std0),('std_after',std1),('std_delta',ds),
                             ('train_raw_delta',rt-raw0),('train_std_delta',st-std0)]:row[name]=float(v[ix].mean()) if len(ix) else None
                        for name,v in [('modified',correction>1e-12),('raw_improved',rd< -1e-12),('raw_worsened',rd>1e-12),
                                       ('std_improved',ds< -1e-12),('std_worsened',ds>1e-12),('real_boundary',boundary),('map_boundary',mboundary)]:
                            row[name+'_mass']=float(v[ix].double().sum())/n
                        quadrows.append(row)
                    # Coordinate contributions retain positive and negative changes before cancellation.
                    coordinate_raw=((zz[:,slc]-bb[:,slc])**2-(mm[:,slc]-bb[:,slc])**2)/SIZES[j]
                    coordinate_std=coordinate_raw/sigma.square()
                    for k in range(SIZES[j]):
                        delta=coordinate_std[:,k];row={**base,'coordinate':HIST[slc.start+k],'scale':float(sigma[k]),
                            'constant_coordinate':bool(constant[slc.start+k]),'raw_positive':float(torch.clamp(coordinate_raw[:,k],min=0).mean()),
                            'raw_negative':float(torch.clamp(coordinate_raw[:,k],max=0).mean()),'std_positive':float(torch.clamp(delta,min=0).mean()),
                            'std_negative':float(torch.clamp(delta,max=0).mean()),'std_net':float(delta.mean())}
                        for q in QUADS:
                            ix=np.flatnonzero(labels==q);row[q+'_std_positive']=float(torch.clamp(delta[ix],min=0).sum())/n
                            row[q+'_std_negative']=float(torch.clamp(delta[ix],max=0).sum())/n
                        coordrows.append(row)
                    geom_rows.append({**base,'strict_inside_max_raw_increase':worst,'real_boundary_mass':float(boundary.double().mean()),
                                      'map_boundary_mass':float(mboundary.double().mean()),'quad_mass_total':1.,'scale_min':float(sigma.min())})
        for arm in ['P','G']:
            a,b,ta,tb=fit_data(PARENT/'packages'/r['id']/'full',arm,r,True)
            reproduced=independent_rules(a,b,ta,tb)
            for v in reproduced:
                row=ridx.loc[(r['id'],arm,v['block'])]
                for k in NUM:audit.close('full_C_'+k,v[k],row[k])
                audit.flag('full_C_eligible',v['train_eligible'],row.train_eligible)
                quantrows.append({'role_id':r['id'],'arm':arm,'inner':-1,'block':v['block'],'scope':'full_C','contents':16,'side_visits':64,
                                  'observations':v['observations'],'element_mass':1/v['observations'],'Q90_rank':v['Q90_rank'],
                                  'content_distance_count':v['content_distance_count'],'content_Q90_rank':v['content_Q90_rank'],
                                  'epsilon':float(row.epsilon),'Q90_replay':v['epsilon'],'epsilon_cap':.1,'clipped':False,
                                  'executed_order':'Q90_then_qualification','replay_passed':True})
        if (ri+1)%12==0:progress('independent_C_replay',roles=ri+1,total=60,checks=audit.checks)
    point=pd.concat(ppoints,ignore_index=True);quad=pd.DataFrame(quadrows);coordinate=pd.DataFrame(coordrows)
    need(len(point)==192000 and len(quad)==19200 and len(coordinate)==46080,'Closed diagnostic row budgets')
    save(point,'pointwise-errors');save(quad,'quadrant-errors');save(coordinate,'standardized-coordinate-contributions')
    save(pd.DataFrame(quantrows),'quantile-weight-audit');save(pd.DataFrame(scaleraudit),'scaler-replay-audit');save(pd.DataFrame(geom_rows),'geometry-audit')
    fg=gate_columns(fold);fg['coverage_margin']=fg.coverage-.875;fg['coverage_pass']=fg.coverage>=.875
    fg['excess_margin']=fg.excess-.1;fg['excess_pass']=fg.excess>=.1
    need(fg.replayed_train_eligible.equals(fg.train_eligible),'Fold gate export mismatch')
    rg=gate_columns(role,'full_C_');flags=[]
    for _,row in rg.iterrows():
        d=fg[(fg.role_id==row.role_id)&(fg.arm==row.arm)&(fg.block==row.block)].sort_values('inner')
        alltrain=bool(d.train_eligible.all());mincov=float(d.coverage.min());coverage=float(d.coverage.mean());excess=float(d.excess.mean());nf=int((d.excess>=.1).sum())
        relpass=alltrain and mincov>=.875 and coverage>=.9;mp=excess>=.1 and nf>=2;full=bool(row.full_C_replayed_train_eligible)
        for name,v in [('relation_qualified',relpass),('map_violation_gate',mp),('accepted_anchor',relpass and mp and full)]:audit.flag(name,v,row[name])
        why=[]
        if not alltrain:why.append('fold_training_qualification')
        if not (mincov>=.875 and coverage>=.9):why.append('heldout_coverage')
        if not mp:why.append('map_excess')
        if not full:why.append('full_C_qualification')
        need(';'.join(why)==row.rejection_reasons,'Failure set mismatch')
        item={'four_fold_train_pass':alltrain,'min_coverage_margin':mincov-.875,'min_coverage_pass':mincov>=.875,
              'pooled_coverage_margin':coverage-.9,'pooled_coverage_pass':coverage>=.9,'mean_excess_margin':excess-.1,
              'mean_excess_pass':excess>=.1,'excess_fold_count_margin':nf-2,'excess_fold_count_pass':nf>=2,
              'replayed_relation_qualified':relpass,'replayed_map_violation_gate':mp,'replayed_accepted_anchor':relpass and mp and full,
              'replayed_rejection_reasons':';'.join(why),'failure_set_matches':True}
        for i,dr in d.iterrows():
            k=int(dr.inner);item[f'fold{k}_train_pass']=bool(dr.train_eligible);item[f'fold{k}_coverage']=float(dr.coverage);item[f'fold{k}_excess']=float(dr.excess)
        flags.append(item)
    rg=pd.concat([rg.reset_index(drop=True),pd.DataFrame(flags)],axis=1)
    save(fg,'qualification-fold-gates');save(rg,'qualification-role-gates')
    trace=rg[rg.relation_qualified|rg.map_violation_gate][['role_id','arm','block']]
    save(fg.merge(trace,on=['role_id','arm','block'],how='inner'),'candidate-traces-folds')
    save(rg.merge(trace,on=['role_id','arm','block'],how='inner'),'candidate-traces-full-C')
    # Close four-cell losses against parent scores. Empty cells contribute zero, never a zero conditional mean.
    closure=quad.groupby(KEY)[['mass','raw_before_contribution','raw_after_contribution','std_before_contribution','std_after_contribution']].sum()
    originals=fold.set_index(KEY).loc[closure.index]
    audit.close('four_grid_mass',closure.mass.to_numpy(),np.ones(len(closure)),1e-12)
    for a,b in [('raw_before_contribution','raw_MSE_before'),('raw_after_contribution','raw_MSE_after'),
                ('std_before_contribution','standardized_MSE_before'),('std_after_contribution','standardized_MSE_after')]:audit.close('four_grid_'+a,closure[a].to_numpy(),originals[b].to_numpy(),1e-10)
    # Coordinate net closure is distinct from the sum of positive-only coordinate losses.
    co=coordinate.groupby(KEY).std_net.sum();expected=fold.set_index(KEY).loc[co.index]
    audit.close('coordinate_standardized_closure',co.to_numpy(),(expected.standardized_MSE_after-expected.standardized_MSE_before).to_numpy(),1e-10)
    write(OUT/'audits/numerical-replay-audit.json',{'passed':True,'checks':audit.checks,'max_errors':audit.maxima,'no_parent_functions_called':True,
          'saved_thresholds_only':True,'parent_gate_reproduced':True,'new_mapping_fits':0,'new_classifier_fits':0})
    progress('replay_complete',checks=audit.checks,point_rows=len(point),quad_rows=len(quad),new_fits=0)

if __name__=='__main__':run()
