"""Twelve source pseudo-targets only; no H-conditioned fallback."""
from common import *

def metric(d,pcols,missing):
    y=d.truth.to_numpy(int);p=d[pcols].to_numpy();m,_,_=base.metrics(y,p,missing)
    use=np.isin(y,missing);m['CE_U']=float(-np.log(p[np.arange(len(y)),y][use]).mean())
    return m

def run():
    with stage('P2_selection'):
        verifyseal(OUT/'manifests/engineering-code.json');verifyseal(OUT/'inner-predictions/complete.json')
        d=pd.read_parquet(OUT/'inner-predictions/post-only.parquet');rs=contract()['inner_roles'];labels={}
        for r in rs:
            l=oldpackage(PREP/'packages'/r['id']/'labels.parquet',r,'inner-score')
            labels[r['id']]=dict(zip(l.visit_id,truths(l)))
        d['truth']=[labels[rid][vid] for rid,vid in zip(d.role_id,d.visit_id)]
        pcs=[f'p{i}' for i in range(6)];bcs=[f'bp{i}' for i in range(6)];rows=[];decisions=[]
        for r in contract()['roles']:
            sub=d[d.outer.eq(r['outer'])&d.actual_target.eq(r['target'])&d.group.eq(r['group'])]
            for arm in ['A1','A2','A3']:
                choices=[]
                for lam in ([0.] if arm=='A1' else [0.,.1,1.]):
                    s=sub[sub.arm.eq('A1' if lam==0 else arm)&sub['lambda'].eq(lam)]
                    metrics=[]
                    for (pseudo,seed),z in s.groupby(['calibration','seed']):
                        require(len(z)==96,'Four complete inner folds')
                        a=metric(z,pcs,r['missing']);b=metric(z,bcs,r['missing'])
                        metrics.append(dict(pseudo=pseudo,seed=seed,CE_U=a['CE_U'],base_CE_U=b['CE_U'],
                                            F1_U=a['F1_uncovered'],base_F1_U=b['F1_uncovered'],
                                            F1_C=a['F1_aux'],base_F1_C=b['F1_aux']))
                    t=pd.DataFrame(metrics);require(len(t)==9,'Three pseudo deployments and seeds')
                    ce=float(t.CE_U.mean());dc=float((t.CE_U-t.base_CE_U).mean());du=float((t.F1_U-t.base_F1_U).mean())
                    cc=float((t.F1_C-t.base_F1_C).mean());by=t.assign(delta=t.F1_C-t.base_F1_C).groupby('pseudo').delta.mean()
                    gates=dict(CE_U=dc<=-.002,F1_U=du>=0,C_overall=cc>=-.01,C_deployment=bool((by>=-.02).all()))
                    row=dict(role_id=r['id'],arm=arm,lambda_value=lam,CE_U=ce,delta_CE_U=dc,delta_F1_U=du,
                             delta_F1_C=cc,worst_delta_F1_C=float(by.min()),gates=gates,qualified=all(gates.values()))
                    rows.append(row);choices.append(row)
                good=[v for v in choices if v['qualified']]
                if good:
                    best=min(v['CE_U'] for v in good);choice=min([v for v in good if v['CE_U']<=best+1e-6],key=lambda v:v['lambda_value'])
                    decisions.append(dict(role_id=r['id'],arm=arm,enabled=True,fallback=False,lambda_value=choice['lambda_value'],decision=choice))
                else:decisions.append(dict(role_id=r['id'],arm=arm,enabled=False,fallback=True,lambda_value=None,reason='no_source_qualified_candidate'))
        require(len(decisions)==180,'All strategy decisions')
        write(OUT/'selections/candidate-metrics.json',rows);write(OUT/'selections/decisions.json',decisions)
        seal(OUT/'selections/complete.json',[OUT/'selections/candidate-metrics.json',OUT/'selections/decisions.json'],passed=True,H_reads=0)
        progress('P2_selection_decisions',enabled=sum(v['enabled'] for v in decisions),fallback=sum(v['fallback'] for v in decisions))

if __name__=='__main__':run()
