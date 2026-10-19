"""AD1 four-effect family; unchanged full-six-class metrics/content resampling."""
from common import *
from weight_schedule import registry,A,B,C_NEW,D_NEW,BASELINE,EFFECTS
PC=[f'p{i}' for i in range(6)]
LPC=[f'logp{i}' for i in range(6)]
_path=PARENT_CODE/'score.py'
_tree=ast.parse(_path.read_text(encoding='utf-8'))
_tree.body=[n for n in _tree.body if isinstance(n,ast.FunctionDef) and n.name in ['per_visit','cm_f1','metrics','bootstrap']]

class _ShapeOnly(ast.NodeTransformer):
    def visit_Constant(self,node):
        return ast.copy_location(ast.Constant(5),node) if isinstance(node.value,int) and node.value==39 else node

_tree=_ShapeOnly().visit(_tree)
exec(compile(ast.fix_missing_locations(_tree),str(_path),'exec'),globals())

def run():
    with stage('P6'):
        raw=pd.read_parquet(OUT/'predictions/visits.parquet');labels=[]
        for r in contract()['roles']:
            d=package(rolepath(r)/'labels.parquet','score')[['visit_id','content_id','label_id']].copy()
            d['role_id']=r['id'];labels.append(d)
        labs=pd.concat(labels,ignore_index=True);require(not labs.duplicated(['role_id','visit_id']).any(),'Label role uniqueness')
        d=raw.merge(labs,on=['role_id','visit_id'],validate='many_to_one')
        require(len(d)==7200 and d.content_id.nunique()==30,'Full scored coverage')
        save(d,OUT/'scores/labeled-predictions.parquet')
        scenes=[];classes=[];cms=[];folds=[];contents=[]
        for (pid,p,g),part in d.groupby(['policy_id','target','group']):
            require(len(part)==120 and part.visit_id.is_unique,'Pool all five folds before F1')
            m,cm,f=metrics(part,MASKS[g]);scenes.append(dict(policy_id=pid,target=p,group=g,**m))
            cms.append(dict(policy_id=pid,target=p,group=g,matrix=cm.astype(int).tolist()))
            for y in range(6):
                tp=cm[y,y];classes.append(dict(policy_id=pid,target=p,group=g,label=LABELS[y],label_index=y,
                    scope='U' if y in MASKS[g] else 'C',F1=float(f[y]),recall=float(tp/cm[y].sum()),
                    precision=float(tp/cm[:,y].sum()) if cm[:,y].sum() else 0.,support=int(cm[y].sum()),
                    predicted_count=int(cm[:,y].sum()),TP=int(tp),FP=int(cm[:,y].sum()-tp),FN=int(cm[y].sum()-tp)))
        for (pid,p,g,o),part in d.groupby(['policy_id','target','group','outer']):
            m,_,_=metrics(part,MASKS[g]);folds.append(dict(policy_id=pid,target=p,group=g,outer=o,**m))
        for (pid,p,g,u),part in d.groupby(['policy_id','target','group','content_id']):
            y,ce,br=per_visit(part);contents.append(dict(policy_id=pid,target=p,group=g,content_id=u,label_id=part.label_id.iloc[0],
                scope='U' if y[0] in MASKS[g] else 'C',visits=len(part),accuracy=float((part.prediction.to_numpy()==y).mean()),CE=float(ce.mean()),Brier=float(br.mean())))
        scene=pd.DataFrame(scenes);cols=[k for k in scene if k not in ['policy_id','target','group']]
        pooled=scene.groupby('policy_id')[cols].mean().reset_index();targets=scene.groupby(['policy_id','target'])[cols].mean().reset_index()
        pooled=pooled.merge(targets.groupby('policy_id').F1_U.min().rename('worst_target_F1_U'),on='policy_id')
        for nm,frame in [('scenarios',scene),('targets',targets),('pooled',pooled),('classes',pd.DataFrame(classes)),
                         ('outer-folds',pd.DataFrame(folds)),('contents',pd.DataFrame(contents))]:save(frame,OUT/'scores'/(nm+'.parquet'))
        write(OUT/'scores/confusion-matrices.json',cms)
        arms,ct,w,u,aux,cm=bootstrap(d)
        np.savez_compressed(writable(OUT/'comparisons/bootstrap.npz'),arms=np.array(arms),contents=np.array(ct),weights=w,F1_U=u,F1_C=aux,content_confusions=cm)
        point=pooled.set_index('policy_id');comparisons=[]
        for a,b,name in EFFECTS:
            delta=u[:,arms.index(a)]-u[:,arms.index(b)];lo,hi=np.quantile(delta,[.00625,.99375],method='linear')
            comparisons.append(dict(name=name,candidate=a,reference=b,delta_F1_U=float(point.loc[a,'F1_U']-point.loc[b,'F1_U']),
                CI_family=[float(lo),float(hi)],CI95=np.quantile(delta,[.025,.975],method='linear').tolist(),
                positive=bool(lo>0),negative=bool(hi<0),delta_CE_U=float(point.loc[a,'CE_U']-point.loc[b,'CE_U']),
                delta_Brier_U=float(point.loc[a,'Brier_U']-point.loc[b,'Brier_U'])))
        write(OUT/'comparisons/primary.json',dict(family=4,marginal_coverage=.9875,family_nominal_coverage=.95,
            samples=10000,seed=20261017,quantile_method='linear',comparisons=comparisons,
            fixed_model_conditional=True,retrospective_internal_evaluation=True,no_H_selection=True))
        it=u[:,arms.index(D_NEW)]-u[:,arms.index(A)]-u[:,arms.index(B)]+u[:,arms.index(C_NEW)]
        write(OUT/'comparisons/interaction.json',dict(expression='(D-A)-(B-C)',
            delta_F1_U=float(point.loc[D_NEW,'F1_U']-point.loc[A,'F1_U']-point.loc[B,'F1_U']+point.loc[C_NEW,'F1_U']),
            CI95=np.quantile(it,[.025,.975],method='linear').tolist(),exploratory=True,not_fifth_primary_comparison=True))
        extra=[];cost=[];t=targets.set_index(['policy_id','target'])
        for a in [A,B,C_NEW,D_NEW]:
            delta=u[:,arms.index(a)]-u[:,arms.index(BASELINE)]
            extra.append(dict(candidate=a,reference=BASELINE,delta_F1_U=float(point.loc[a,'F1_U']-point.loc[BASELINE,'F1_U']),
                CI95=np.quantile(delta,[.025,.975],method='linear').tolist(),descriptive_only=True))
            dc=float(point.loc[a,'F1_C']-point.loc[BASELINE,'F1_C'])
            dep={p:float(t.loc[(a,p),'F1_C']-t.loc[(BASELINE,p),'F1_C']) for p in PROTOCOLS}
            cost.append(dict(policy_id=a,delta_F1_C=dc,overall_pass=dc>=-.01,per_deployment=dep,
                each_deployment_pass=all(x>=-.02 for x in dep.values()),not_used_for_fallback=True,not_statistical_noninferiority=True))
        write(OUT/'comparisons/versus-Psmall-descriptive.json',extra)
        write(OUT/'scores/C-practical-cost.json',cost)
        flips=[];contrib=[]
        pairs=EFFECTS+[(a,BASELINE,'descriptive_vs_Psmall') for a in [A,B,C_NEW,D_NEW]]
        for a,b,name in pairs:
            aa=d[d.policy_id.eq(a)].set_index(['role_id','visit_id']).sort_index()
            bb=d[d.policy_id.eq(b)].set_index(['role_id','visit_id']).loc[aa.index]
            y,ce,br=per_visit(aa);yb,ceb,brb=per_visit(bb);require(np.array_equal(y,yb),'Paired evaluation labels')
            ac=aa.prediction.to_numpy()==y;bc=bb.prediction.to_numpy()==y
            states=np.where(ac,np.where(bc,'both_correct','repaired'),np.where(bc,'new_error','both_wrong'))
            f=aa[['target','group','outer','content_id','label_id','prediction']].reset_index()
            f['candidate']=a;f['reference']=b;f['comparison']=name;f['reference_prediction']=bb.prediction.to_numpy()
            f['state']=states;f['delta_CE']=ce-ceb;f['delta_Brier']=br-brb
            f['scope']=['U' if yi in MASKS[g] else 'C' for yi,g in zip(y,f.group)]
            f['candidate_pred_role']=['U' if yi in MASKS[g] else 'C' for yi,g in zip(f.prediction,f.group)]
            f['reference_pred_role']=['U' if yi in MASKS[g] else 'C' for yi,g in zip(f.reference_prediction,f.group)]
            flips.append(f)
            for (p,g),part in f.groupby(['target','group']):
                for scope in ['all','C','U']:
                    sub=part if scope=='all' else part[part.scope.eq(scope)]
                    for state in ['both_correct','repaired','new_error','both_wrong']:
                        q=sub[sub.state.eq(state)]
                        contrib.append(dict(candidate=a,reference=b,comparison=name,target=p,group=g,scope=scope,state=state,
                            count=len(q),total=len(sub),CE_contribution=float(q.delta_CE.sum()/len(sub)),
                            Brier_contribution=float(q.delta_Brier.sum()/len(sub))))
        save(pd.concat(flips,ignore_index=True),OUT/'scores/error-transitions.parquet')
        save(pd.DataFrame(contrib),OUT/'scores/probability-contributions.parquet')
        progress('AD1_scored',predictions=7200,primary_comparisons=4)
