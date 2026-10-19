"""Independent endpoint gradients, predictions, confusion matrices and bootstrap."""
from common import *
from prepare import loss_audit
from evaluate import scored_predictions,aggregate_content,bootstrap_counts,bootstrap_independent,METRIC_NAMES

def verify():
    with stage('P5'):
        verify_seal(OUT/'slots-complete.json');verify_seal(OUT/'models-complete.json')
        verify_seal(OUT/'predictions-complete.json');verify_seal(OUT/'scores-complete.json')
        predictions=pd.read_parquet(OUT/'predictions.parquet');audits=[];pred_error=0.
        for r in contract()['roles']:
            q=package(PREP/'packages'/r['id']/'query.parquet',r,'query')
            with compute('independent-endpoint-check-'+r['id']):
                for arm in ARMS:
                    s=own(OUT/'slots'/r['id']/(arm+'.pt'));m=own(OUT/'models'/r['id']/(arm+'.pt'))
                    audit=loss_audit(m,s,r['t']);log=read(OUT/'fit-logs'/r['id']/f'{arm}-t{r["t"]:g}.json')
                    objective_error=abs(audit['objective']-log['objective']);gradient_error=abs(audit['gradient']-log['max_gradient'])
                    require(audit['gradient']<=1e-5 and objective_error<1e-10 and gradient_error<1e-10,'Independent endpoint acceptance')
                    # Expanded affine raw-input formula, distinct from prediction helper.
                    raw=tensor(q[HIST]);w=m['weight']/m['scale'][None,:]
                    z=raw@w.T+(m['bias']-w@m['mu']);lp=z-torch.logsumexp(z,1)[:,None];p=lp.exp()
                    original=predictions[(predictions.role_id==r['id'])&(predictions.arm==arm)].set_index('visit_id').loc[q.visit_id]
                    pe=float((p-tensor(original[[f'p{i}' for i in range(6)]])).abs().max());require(pe<1e-10,'Independent post-only probability replay')
                    require(np.array_equal(cpu(p.argmax(1)),original.prediction.to_numpy()),'Class replay conflict')
                    pred_error=max(pred_error,pe)
                    audits.append(dict(role_id=r['id'],arm=arm,objective=audit['objective'],max_gradient=audit['gradient'],
                         objective_replay_error=objective_error,gradient_replay_error=gradient_error,probability_replay_error=pe))
        save(pd.DataFrame(audits),'independent-endpoint-checks')
        d=scored_predictions();old=pd.read_parquet(OUT/'scored-predictions.parquet')
        require(d[['role_id','arm','visit_id','y']].equals(old[['role_id','arm','visit_id','y']]),'Scoring identities replay')
        cmout=pd.read_parquet(OUT/'confusion-matrices.parquet');metricout=pd.read_parquet(OUT/'metrics-by-role-group.parquet')
        metric_error=0.
        for keys,g in d.groupby(['role_target','query_deployment','group','arm']):
            target,dep,group,arm=keys
            # Independent additive confusion table from individual categorical comparisons.
            cm=np.array([[int(((g.y==y)&(g.prediction==p)).sum()) for p in range(6)] for y in range(6)])
            cmold=cmout[(cmout.role_target==target)&(cmout.query_deployment==dep)&(cmout.group==group)&(cmout.arm==arm)].sort_values(['truth','prediction'])['count'].to_numpy().reshape(6,6)
            require(np.array_equal(cm,cmold),'Confusion matrix replay')
            f=[]
            for y in range(6):
                tp=cm[y,y];fp=cm[:,y].sum()-tp;fn=cm[y,:].sum()-tp;f.append(2*tp/(2*tp+fp+fn))
            row=metricout[(metricout.role_target==target)&(metricout.group==group)&(metricout.arm==arm)].iloc[0]
            ne=max(abs(np.mean([f[y] for y in MASKS[group]])-row.F1_U),abs(np.mean([f[y] for y in range(6) if y not in MASKS[group]])-row.F1_C))
            metric_error=max(metric_error,ne);require(ne<1e-12,'Pooled metric replay')
        contents,labels,cm,risks,counts,masks=aggregate_content(d)
        boot=np.load(OUT/'bootstrap.npz',allow_pickle=False);weights=bootstrap_counts(labels)
        require(np.array_equal(weights,boot['counts']) and contents==boot['contents'].tolist(),'Bootstrap resampling replay')
        with compute('independent-bootstrap-10000'):
            independent=bootstrap_independent(cm,risks,counts,masks,weights)
        be=float(np.max(np.abs(independent-boot['draws'])));require(be<1e-11,'Independent bootstrap replay')
        comparisons=read(OUT/'primary-comparisons.json');interval_error=0.
        for ca,re in COMPARISONS:
            delta=independent[:,ARMS.index(ca),0]-independent[:,ARMS.index(re),0]
            ci=np.quantile(delta,[.025/3,1-.025/3]);oldci=comparisons[ca+'-'+re]['F1_U_family_CI']
            interval_error=max(interval_error,float(np.max(np.abs(ci-oldci))))
        require(interval_error<1e-11,'Family interval replay')
        # Rehash every registered input, including deferred query/labels, once at closeout.
        for path,info in contract()['files'].items():require(sha(ROOT/path)==info['sha256'],'Historical asset modified '+path)
        reads=[]
        for path in (OUT/'ledgers').glob('*.json'):reads.extend(read(path)['reads'])
        reads.extend(READS)
        for x in reads:
            require(x['path'] in contract()['files'],'Unregistered recorded read')
            require(x['kind'] not in {'query','labels'} or x['stage'] in ({'P3','P5'} if x['kind']=='query' else {'P4','P5'}),'Barrier violation')
            require('/feedback-cache/' not in x['path'] and '/heldout-visits/' not in x['path'] and '/native' not in x['path'],'Forbidden mixed cache read')
        result=dict(passed=True,models=192,objective_max_error=max(x['objective_replay_error'] for x in audits),
             gradient_max_error=max(x['gradient_replay_error'] for x in audits),original_gradient_max=max(x['max_gradient'] for x in audits),
             probability_max_error=pred_error,metric_max_error=metric_error,bootstrap_max_error=be,family_interval_max_error=interval_error,
             registered_input_hashes=len(contract()['files']),all_registered_inputs_unchanged=True,read_events=len(reads),
             actual_H_reads=0,actual_U_reads=0,query_pre_reads=0,native_reads=0,pcap_reads=0,mixed_feedback_cache_reads=0,
             audit_scope='enforced ST1 IO adapter and source inspection; not OS-level syscall auditing')
        write(OUT/'verification.json',result)
        write(OUT/'ledger.json',dict(reads=reads,execution_order=['all training slots sealed','all 192 models sealed','all 4608 post predictions sealed','source-inner scoring labels read'],
               actual_H_U_authorized=False,old_artifacts_changed=False))
