"""Post-only export; labels unavailable until every policy prediction sealed."""
from common import *
from weight_schedule import registry

def run():
    with stage('P5'):
        c=contract();e=pd.read_parquet(OUT/'manifests/endpoints.parquet');rows=[]
        for r in c['roles']:
            q=package(rolepath(r)/'query.parquet','query');raw=tensor(q[HIST]);ee=e[e.role_id.eq(r['id'])].set_index('policy_id')
            for p in registry():
                er=ee.loc[p['id']];m=artifact(ROOT/er.path,'inference-model')
                with torch.no_grad():
                    x=(raw-m['mu'])/m['scale'];z=x@m['weight'].T+m['bias'];lp=z.log_softmax(1);pp=z.softmax(1)
                require(z.is_cuda and z.dtype==torch.float64 and torch.isfinite(lp).all() and torch.isfinite(pp).all(),'Frozen output numerics')
                require(float((lp.exp()-pp).abs().max())<1e-12 and torch.equal(lp.argmax(1),pp.argmax(1)),'Probability/logprob replay')
                d=pd.DataFrame(pp.cpu().numpy(),columns=[f'p{i}' for i in range(6)])
                for j in range(6):d[f'logp{j}']=lp[:,j].cpu().numpy();d[f'logit{j}']=z[:,j].cpu().numpy()
                d['visit_id']=q.visit_id.to_numpy();d['prediction']=pp.argmax(1).cpu().numpy()
                d['role_id']=r['id'];d['policy_id']=p['id'];d['target']=r['target'];d['group']=r['group'];d['outer']=r['outer'];rows.append(d)
        d=pd.concat(rows,ignore_index=True)
        require(len(d)==56160 and d.visit_id.nunique()==480 and not d.duplicated(['role_id','policy_id','visit_id']).any(),'Prediction coverage')
        save(d,OUT/'predictions/visits.parquet')
        write(OUT/'predictions/complete.json',dict(sha256=sha(OUT/'predictions/visits.parquet'),rows=56160,unique_visits=480,policies=39,roles=60,H_labels_read=False,H_pre_reads=0))
        # Read historical predictions only now, solely to audit already fixed aliases.
        checked(TI/'predictions/visits.parquet',read(TI/'predictions/complete.json')['sha256'],'historical-probability-replay')
        checked(SA/'predictions/visits.parquet',read(SA/'predictions/complete.json')['sha256'],'historical-probability-replay')
        oldti=pd.read_parquet(TI/'predictions/visits.parquet');oldsa=pd.read_parquet(SA/'predictions/visits.parquet')
        maxerr=0.;pc=[f'p{i}' for i in range(6)]
        for p in registry():
            if not p['alias']:continue
            old=oldsa if p['source'] in ['RawPre','RawPost'] else oldti
            old=old[old.arm.eq(p['alias'])].set_index(['role_id','visit_id']);new=d[d.policy_id.eq(p['id'])].set_index(['role_id','visit_id']).loc[old.index]
            err=float(np.abs(new[pc].to_numpy()-old[pc].to_numpy()).max());require(err<1e-12,'Historical alias probability changed');maxerr=max(maxerr,err)
        write(OUT/'audits/historical-probability-replay.json',dict(passed=True,max_error=maxerr,read_only_after_all_models_and_predictions_sealed=True))

