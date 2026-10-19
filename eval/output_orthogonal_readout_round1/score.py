from common import *

def metrics(y,p,lp,missing):
    pred=p.argmax(1);cm=np.bincount(y*6+pred,minlength=36).reshape(6,6);den=cm.sum(0)+cm.sum(1)
    f1=np.divide(2*np.diag(cm),den,out=np.zeros(6),where=den>0);u=np.isin(y,missing)
    ce=-lp[np.arange(len(y)),y];br=((p-np.eye(6)[y])**2).sum(1)
    return dict(F1_all=float(f1.mean()),F1_U=float(f1[missing].mean()),F1_C=float(np.delete(f1,missing).mean()),
                CE_all=float(ce.mean()),CE_U=float(ce[u].mean()),CE_C=float(ce[~u].mean()),
                Brier=float(br.mean()),Brier_U=float(br[u].mean()),Brier_C=float(br[~u].mean()),
                accuracy=float((pred==y).mean()),confusion_matrix=cm.tolist(),class_F1=f1.tolist())

def run():
    with stage('score'):
        verify(OUT/'predictions/calibrated-complete.json');verify(OUT/'calibration/temperatures-complete.json')
        c=contract();d=pd.read_parquet(OUT/'predictions/calibrated.parquet');endpoints=[];rows=[];repair=[]
        for ri,r in enumerate(c['roles']):
            labels=pd.read_parquet(OUT/f'calibration/packages/r{ri:02d}/scoring-labels.parquet')
            z=d[d.role_id.eq(r['id'])].merge(labels[['visit_id','y']],on='visit_id',validate='many_to_one')
            base=z[z.pipeline.eq('base')].set_index('visit_id')
            paired=z[z.pipeline.eq('P_eta0p01')].set_index(['seed','visit_id'])
            for (pipe,seed),sub in z.groupby(['pipeline','seed']):
                y=sub.y.to_numpy(dtype=int);p=sub[PC].to_numpy();lp=sub[LC].to_numpy()
                rawp=sub[['raw_'+v for v in PC]].to_numpy();rawlp=sub[['raw_'+v for v in LC]].to_numpy()
                now,old=metrics(y,p,lp,r['missing']),metrics(y,rawp,rawlp,r['missing'])
                for k in ['F1_all','F1_U','F1_C','accuracy','confusion_matrix']:require(now[k]==old[k],'Calibrated classification changed')
                endpoints.append(dict(role_id=r['id'],role_target=r['target'],query_deployment=r['calibration'],pipeline=pipe,seed=int(seed),raw=old,calibrated=now))
                for i,(_,v) in enumerate(sub.iterrows()):
                    bp=base.loc[v.visit_id,['raw_'+k for k in PC]].to_numpy(dtype=float).argmax()
                    pred=int(p[i].argmax());state=('correct' if bp==y[i] else 'wrong')+'->'+('correct' if pred==y[i] else 'wrong')
                    rows.append(dict(role_id=r['id'],role_target=r['target'],query_deployment=r['calibration'],pipeline=pipe,seed=int(seed),
                        visit_id=v.visit_id,content_id=v.content_id,y=int(y[i]),split='U' if y[i] in r['missing'] else 'C',
                        state=state,prediction=pred,base_prediction=int(bp),temperature=float(v.temperature),
                        raw_CE=float(-rawlp[i,y[i]]),CE=float(-lp[i,y[i]]),
                        raw_Brier=float(((rawp[i]-np.eye(6)[y[i]])**2).sum()),Brier=float(((p[i]-np.eye(6)[y[i]])**2).sum()),
                        raw_confidence=float(rawp[i].max()),confidence=float(p[i].max())))
                    if pipe=='OR-P':
                        oldp=paired.loc[(seed,v.visit_id),PC].to_numpy(dtype=float).argmax()
                        repair.append(dict(role_id=r['id'],seed=int(seed),visit_id=v.visit_id,content_id=v.content_id,
                            query_deployment=r['calibration'],split='U' if y[i] in r['missing'] else 'C',truth=int(y[i]),
                            base_prediction=int(bp),old_P_prediction=int(oldp),OR_P_prediction=pred,
                            old_repaired=bool(bp!=y[i] and oldp==y[i]),old_added_error=bool(bp==y[i] and oldp!=y[i]),
                            old_repair_retained=bool(bp!=y[i] and oldp==y[i] and pred==y[i]),
                            OR_repaired=bool(bp!=y[i] and pred==y[i]),OR_added_error=bool(bp==y[i] and pred!=y[i])))
        require(len(endpoints)==336 and len(rows)==8064 and len(repair)==864,'Evaluation counts')
        metricnames=['F1_all','F1_U','F1_C','CE_all','CE_U','CE_C','Brier','Brier_U','Brier_C','accuracy']
        summary=[]
        for pipe in ['base','X_eta0p01','R_eta0p01','G_eta0p01','P_eta0p01',*ARMS]:
            eps=[e for e in endpoints if e['pipeline']==pipe]
            agg={phase:{k:float(np.mean([e[phase][k] for e in eps])) for k in metricnames} for phase in ['raw','calibrated']}
            by=[]
            for pr in sorted(set(e['query_deployment'] for e in eps)):
                local=[e for e in eps if e['query_deployment']==pr]
                by.append(dict(query_deployment=pr,**{phase:{k:float(np.mean([e[phase][k] for e in local])) for k in metricnames} for phase in ['raw','calibrated']}))
            summary.append(dict(pipeline=pipe,**agg,by_deployment=by))
        idx={v['pipeline']:v for v in summary};p=idx['OR-P']['calibrated'];old=idx['P_eta0p01']['calibrated'];base=idx['base']['calibrated']
        Cgates=dict(overall=p['F1_C']-base['F1_C']>=-.01-1e-12,
            by_deployment=all(v['calibrated']['F1_C']-next(b for b in idx['base']['by_deployment'] if b['query_deployment']==v['query_deployment'])['calibrated']['F1_C']>=-.02-1e-12 for v in idx['OR-P']['by_deployment']))
        utility=dict(F1_U_not_lower=p['F1_U']>=old['F1_U']-1e-12,CE_U_margin=p['CE_U']-old['CE_U']<=-.002+1e-12,
                     Brier_U_better=p['Brier_U']<old['Brier_U'],CE_all_not_worse=p['CE_all']<=old['CE_all']+1e-12,
                     Brier_all_not_worse=p['Brier']<=old['Brier']+1e-12,**Cgates)
        controls=['base','OR-X','OR-R','OR-G','OR-BIAS']
        increment={name:dict(CE_U_margin=p['CE_U']-idx[name]['calibrated']['CE_U']<=-.002+1e-12,
                        F1_U_not_worse=p['F1_U']>=idx[name]['calibrated']['F1_U']-1e-12,
                        Brier_U_not_worse=p['Brier_U']<=idx[name]['calibrated']['Brier_U']+1e-12) for name in controls}
        fullbase=dict(CE_all_not_worse=p['CE_all']<=base['CE_all']+1e-12,Brier_all_not_worse=p['Brier']<=base['Brier']+1e-12,**Cgates)
        scored=pd.DataFrame(rows);rep=pd.DataFrame(repair);transitions=[];breakdown=[]
        for (pipe,split,state),part in scored.groupby(['pipeline','split','state']):
            n=len(scored[scored.pipeline.eq(pipe)&scored.split.eq(split)])
            transitions.append(dict(pipeline=pipe,split=split,state=state,n=len(part),
                unique_visits=part.visit_id.nunique(),unique_contents=part.content_id.nunique(),
                **{k:float(part[k].mean()) for k in ['raw_CE','CE','raw_Brier','Brier','raw_confidence','confidence']},
                CE_contribution=float((part.CE-part.raw_CE).sum()/n),Brier_contribution=float((part.Brier-part.raw_Brier).sum()/n),
                wrong_conf90=int(((part.prediction!=part.y)&part.confidence.ge(.9)).sum())))
        for field in ['content_id','query_deployment','seed']:
            for (pipe,split,value),part in scored.groupby(['pipeline','split',field]):
                breakdown.append(dict(pipeline=pipe,split=split,field=field,value=str(value),n=len(part),
                    **{k:float(part[k].mean()) for k in ['raw_CE','CE','raw_Brier','Brier']},
                    repairs=int(part.state.eq('wrong->correct').sum()),added_errors=int(part.state.eq('correct->wrong').sum())))
        rsummary=[]
        for split,part in rep.groupby('split'):
            rsummary.append(dict(split=split,old_repairs=int(part.old_repaired.sum()),retained=int(part.old_repair_retained.sum()),
                OR_repairs=int(part.OR_repaired.sum()),OR_added_errors=int(part.OR_added_error.sum()),
                old_repair_unique_visits=part[part.old_repaired].visit_id.nunique(),
                retained_unique_visits=part[part.old_repair_retained].visit_id.nunique()))
        write(OUT/'scores/endpoints.json',endpoints);save(OUT/'scores/rows.parquet',scored);save(OUT/'scores/old-P-repair-retention.parquet',rep)
        write(OUT/'scores/summary.json',dict(passed=True,pipelines=summary,utility_gates=utility,utility_pass=all(utility.values()),
            increment_gates=increment,increment_full_baseline_gates=fullbase,
            increment_pass=all(all(v.values()) for v in increment.values()) and all(fullbase.values()),
            repair_retention=rsummary,transitions=transitions,breakdowns=breakdown,
            source_only=True,H_scored=False,advance_full_roles=False))
        seal(OUT/'scores/complete.json',[OUT/'scores/endpoints.json',OUT/'scores/rows.parquet',OUT/'scores/old-P-repair-retention.parquet',OUT/'scores/summary.json'])
        print(json.dumps(dict(OR_P=idx['OR-P'],utility_gates=utility,increment=increment,repair_retention=rsummary),indent=2),flush=True)
