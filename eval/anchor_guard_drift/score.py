"""C-only selection-conditional qualification. No downstream classifier selection."""
from common import *
from anchors import arrays,rules,distance,qtile

def pairs(pred,score,arm):
    if arm=='P':
        ordered=score.set_index('query_key').loc[pred['query_keys']]
        require(ordered.content_token.tolist()==pred['content_tokens'],'Paired scoring alignment')
        return pred['a'],tensor(ordered[HIST]),pred['b0'],pred['candidate_guard'],np.asarray(pred['content_tokens'])
    ta=np.asarray(pred['content_tokens']);tb=score.content_token.to_numpy();ix=[];iy=[];uu=[]
    require(set(ta)==set(tb),'Anonymous score contents')
    for u in sorted(set(ta)):
        aa=np.flatnonzero(ta==u);bb=np.flatnonzero(tb==u);require(len(aa)==len(bb)==4,'Validation repetitions')
        for k in aa:
            for j in bb:ix.append(k);iy.append(j);uu.append(u)
    return pred['a'][ix],tensor(score[HIST])[iy],pred['b0'][ix],pred['candidate_guard'][ix],np.asarray(uu)

def run():
    with stage('score'):
        seal=read(OUT/'diagnostics/predictions-complete.json')
        for p,h in seal['files'].items():checked(ROOT/p,h,'sealed-C-forecast')
        foldrows=[];contentrows=[]
        for ri,r in enumerate(contract()['roles']):
            for i in range(4):
                root=rolepath(r)/f'i{i}';dest=OUT/'diagnostics'/r['id']/f'i{i}'
                for arm in ['P','G']:
                    rr=read(dest/f'{arm}-rules.json');pred=artifact(dest/f'{arm}-predictions.pt')
                    ds=package(root/('P-score.parquet' if arm=='P' else 'G-post-validation.parquet'),arm+'-score')
                    a,b,b0,z,tokens=pairs(pred,ds,arm)
                    for rule in rr:
                        j=rule['block'];sl=block(j);eps=rule['epsilon'];dr=distance(a[:,sl],b[:,sl]);dm=distance(a[:,sl],b0[:,sl]);dz=distance(a[:,sl],z[:,sl])
                        hit=dr<=eps+RULE['floating_comparison_tolerance'];mv=dm>eps+RULE['floating_comparison_tolerance']
                        raw0=(b0[:,sl]-b[:,sl]).square().mean(1);raw1=(z[:,sl]-b[:,sl]).square().mean(1)
                        sc0=((b0[:,sl]-b[:,sl])/pred['scale'][sl]).square().mean(1)
                        sc1=((z[:,sl]-b[:,sl])/pred['scale'][sl]).square().mean(1)
                        base={'role_id':r['id'],'target':r['target'],'group':r['group'],'outer':r['outer'],'inner':i,'arm':arm,**rule}
                        base['reasons']=';'.join(rule['reasons'])
                        foldrows.append({**base,'coverage':float(hit.double().mean()),'v_real':float((~hit).double().mean()),
                             'v_map':float(mv.double().mean()),'excess':float(mv.double().mean()-(~hit).double().mean()),
                             'real_median':qtile(dr,.5),'real_Q90':qtile(dr,.9),'real_Q95':qtile(dr,.95),'real_max':float(dr.max()),
                             'map_median':qtile(dm,.5),'map_Q90':qtile(dm,.9),'map_Q95':qtile(dm,.95),'map_max':float(dm.max()),
                             'mean_overrun':float(torch.clamp(dm-eps,min=0).mean()),'guard_max_distance':float(dz.max()),
                             'raw_MSE_before':float(raw0.mean()),'raw_MSE_after':float(raw1.mean()),
                             'standardized_MSE_before':float(sc0.mean()),'standardized_MSE_after':float(sc1.mean()),
                             'true_inside_MSE_change':float((raw1-raw0)[hit].mean()) if bool(hit.any()) else None,
                             'true_outside_MSE_change':float((raw1-raw0)[~hit].mean()) if bool((~hit).any()) else None})
                        for u in sorted(set(tokens)):
                            ix=np.flatnonzero(tokens==u);contentrows.append({'role_id':r['id'],'arm':arm,'inner':i,'block':j,'feature':FEATURES[j],
                                 'content_token':u,'coverage':float(hit[ix].double().mean()),'v_map':float(mv[ix].double().mean()),
                                 'real_Q95':qtile(dr[ix],.95),'raw_MSE_change':float((raw1-raw0)[ix].mean())})
            if (ri+1)%12==0:progress('C_qualification_score',roles=ri+1,total=60)
        folds=pd.DataFrame(foldrows);save(folds,OUT/'scores/fold-scores.parquet');save(pd.DataFrame(contentrows),OUT/'scores/content-scores.parquet')
        final=[];registries={'P':{},'G':{}}
        for r in contract()['roles']:
            for arm in ['P','G']:
                root=rolepath(r)/'full'
                if arm=='P':
                    d=package(root/'P.parquet','P-fit');a,b=arrays(d,True);rr=rules(a,b,d.content_token.to_numpy())
                else:
                    dp=package(root/'G-pre.parquet','G-fit');db=package(root/'G-post.parquet','G-fit')
                    rr=rules(arrays(dp),arrays(db),dp.content_token.to_numpy(),db.content_token.to_numpy())
                chosen=[]
                for v in rr:
                    d=folds[folds.role_id.eq(r['id'])&folds.arm.eq(arm)&folds.block.eq(v['block'])];require(len(d)==4,'Four OOF folds')
                    trainpass=bool(d.train_eligible.all());covpass=float(d.coverage.min())>=RULE['fold_coverage_min'] and float(d.coverage.mean())>=RULE['OOF_coverage_min']
                    qual=trainpass and covpass
                    broken=float(d.excess.mean())>=RULE['excess_min'] and int((d.excess>=RULE['excess_min']).sum())>=RULE['excess_folds_min']
                    accepted=qual and broken and v['train_eligible'];why=[]
                    if not trainpass:why.append('fold_training_qualification')
                    if not covpass:why.append('heldout_coverage')
                    if not broken:why.append('map_excess')
                    if not v['train_eligible']:why.append('full_C_qualification')
                    row={'role_id':r['id'],'target':r['target'],'group':r['group'],'outer':r['outer'],'arm':arm,**v,
                         'train_eligible_folds':int(d.train_eligible.sum()),'OOF_min_coverage':float(d.coverage.min()),
                         'OOF_coverage':float(d.coverage.mean()),'OOF_v_real':float(d.v_real.mean()),'OOF_v_map':float(d.v_map.mean()),
                         'OOF_excess':float(d.excess.mean()),'excess_folds':int((d.excess>=RULE['excess_min']).sum()),
                         'relation_qualified':qual,'map_violation_gate':broken,'accepted_anchor':accepted,
                         'rejection_reasons':';'.join(why),'OOF_raw_MSE_before':float(d.raw_MSE_before.mean()),'OOF_raw_MSE_after':float(d.raw_MSE_after.mean()),
                         'OOF_standardized_MSE_before':float(d.standardized_MSE_before.mean()),'OOF_standardized_MSE_after':float(d.standardized_MSE_after.mean())}
                    row['reasons']=';'.join(v['reasons']);final.append(row)
                    if accepted:chosen.append({**v,'reasons':[]})
                registries[arm][r['id']]={'blocks':[v['block'] for v in chosen],'rules':chosen,'role_id':r['id'],
                                         'fit_scope':'all 16 allowed C contents','selection_conditional_OOF':True,
                                         'precise_identity_used':arm=='P','H_or_U_values_used':False}
        result=pd.DataFrame(final);save(result,OUT/'scores/anchor-qualification.parquet')
        for arm,d in registries.items():write(OUT/'rules'/f'{arm}-rules.json',d)
        ps=result[result.arm.eq('P')];n=int(ps.accepted_anchor.sum());nroles=int(ps[ps.accepted_anchor].role_id.nunique())
        status='awaiting_classification_confirmation' if n else ('stop_no_qualified_P_anchors' if not ps.relation_qualified.any() else 'stop_no_supported_protection_target')
        write(OUT/'rules/anchor-gate.json',{'status':status,'P_anchor_role_blocks':n,'P_roles_with_anchors':nroles,
              'P_deployments_with_anchors':sorted(ps[ps.accepted_anchor].target.unique()),'P_relation_qualified':int(ps.relation_qualified.sum()),
              'G_anchor_role_blocks':int(result[result.arm.eq('G')].accepted_anchor.sum()),'classifier_fits':0,'thresholds_changed':False,
              'stage_two_authorized':False,'not_independent_role_replicates':True})

if __name__=='__main__':run()
