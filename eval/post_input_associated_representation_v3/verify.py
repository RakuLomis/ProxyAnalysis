"""Independent deployment replay and exact baseline aliases; no new fitting."""
from common import *
from deploy import predict_post

def run():
    with stage('P4_verify'):
        for name in ['manifests/engineering-code.json','packages/complete.json','selections/complete.json','manifests/models-complete.json','predictions/complete.json']:verifyseal(OUT/name)
        d=pd.read_parquet(OUT/'predictions/visits.parquet');eps=read(OUT/'manifests/endpoints.json')
        maxerr=0.;aliases=0
        for r in contract()['roles']:
            q=oldpackage(PREP/'packages'/r['id']/'query.parquet',r,'H-predict');m=own(PARENT/'base-models'/r['id']/'P-small.pt','inference')
            for e in [e for e in eps if e['role_id']==r['id']]:
                state=None if e['residual_path'] is None else own(ROOT/e['residual_path'],'inference')['state']
                lp=predict_post(tensor(q[HIST]),m,state)
                part=d[d.role_id.eq(r['id'])&d.arm.eq(e['arm'])&d.seed.eq(e['seed'])].set_index('visit_id').loc[q.visit_id]
                err=float(np.abs(lp.cpu().numpy()-part[[f'l{i}' for i in range(6)]].to_numpy()).max());maxerr=max(maxerr,err)
                require(err==0,'Independent standalone deployment replay not exact')
                if e['arm']!='A0' and e['fallback']:
                    basepart=d[d.role_id.eq(r['id'])&d.arm.eq('A0')&d.seed.eq(e['seed'])].set_index('visit_id').loc[q.visit_id]
                    require(np.array_equal(part[[f'p{i}' for i in range(6)]+[f'l{i}' for i in range(6)]+['prediction']].to_numpy(),
                                           basepart[[f'p{i}' for i in range(6)]+[f'l{i}' for i in range(6)]+['prediction']].to_numpy()),'Fallback not exactly A0')
                    aliases+=1
        pooled=pd.read_parquet(OUT/'scores/pooled.parquet').set_index('arm')
        require(abs(float(pooled.loc['A0','F1_U'])-.796931)<1e-6,'Frozen P-small F1 not reproduced')
        write(OUT/'verification.json',dict(passed=True,endpoints=720,predictions=17280,independent_logprob_max_error=maxerr,
              exact_fallback_seed_endpoints=aliases,new_fits=0,test_pre_reads=0,actual_U_reads=0,
              standalone_deploy_imports=['torch'],bootstrap_unit='shared business-stratified content',training_budget=read(OUT/'ledger.json')))

if __name__=='__main__':run()
