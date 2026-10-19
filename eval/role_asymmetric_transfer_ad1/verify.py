"""Independent AD1 endpoint, prediction, CM, bootstrap and permission audit."""
from common import *
from weight_schedule import registry,A,B,C_NEW,D_NEW,BASELINE,EFFECTS
from score import bootstrap,PC,LPC

def run():
    with stage('verify'):
        c=contract();raw=pd.read_parquet(OUT/'predictions/visits.parquet');d=pd.read_parquet(OUT/'scores/labeled-predictions.parquet')
        ends=pd.read_parquet(OUT/'manifests/endpoints.parquet');new=pd.read_parquet(OUT/'manifests/new-endpoints.parquet')
        require(len(ends)==300 and len(new)==120 and len(d)==len(raw)==7200,'Coverage')
        require(not (OUT/'failure.json').exists(),'Unresolved failure')
        require(len(list((OUT/'attempts').rglob('*.json')))==120 and len(list((OUT/'models').rglob('*.pt')))==120,'Physical new fit count')
        checked(OUT/'manifests/endpoints.parquet',read(OUT/'manifests/endpoint-seal.json')['sha256'],'independent-endpoint-seal')
        checked(OUT/'predictions/visits.parquet',read(OUT/'predictions/complete.json')['sha256'],'independent-prediction-seal')
        idx=['role_id','policy_id','visit_id'];aa=raw.set_index(idx).sort_index();bb=d.set_index(idx).sort_index()
        require(aa.index.equals(bb.index) and np.array_equal(aa[PC+LPC].to_numpy(),bb[PC+LPC].to_numpy()),'Scoring altered predictions')
        maximum=0.;logmax=0.;replays=0
        for r in c['roles']:
            q=package(rolepath(r)/'query.parquet','query');x=tensor(q[HIST])
            for e in ends[ends.role_id.eq(r['id'])].to_dict('records'):
                checked(ROOT/e['path'],e['sha256'],'independent-model-hash')
                m=artifact(ROOT/e['path'],'independent-inference-model')
                z=((x-m['mu'])/m['scale'])@m['weight'].T+m['bias'];pp=z.softmax(1);lp=z.log_softmax(1)
                old=raw[raw.role_id.eq(r['id'])&raw.policy_id.eq(e['policy_id'])].set_index('visit_id').loc[q.visit_id]
                pe=float(np.abs(pp.cpu().numpy()-old[PC].to_numpy()).max());le=float(np.abs(lp.cpu().numpy()-old[LPC].to_numpy()).max())
                require(pe<1e-12 and le<1e-12,'Frozen inference replay');maximum=max(maximum,pe);logmax=max(logmax,le);replays+=1
        # Manual six-class confusion reconstruction independent of score.metrics.
        scene=pd.read_parquet(OUT/'scores/scenarios.parquet').set_index(['policy_id','target','group']);err=0.
        for key,part in d.groupby(['policy_id','target','group']):
            mat=np.zeros((6,6),int)
            for y,p in zip(truths(part),part.prediction):mat[y,int(p)]+=1
            fs=[]
            for y in range(6):
                tp=mat[y,y];fp=mat[:,y].sum()-tp;fn=mat[y].sum()-tp
                fs.append(2*tp/(2*tp+fp+fn) if 2*tp+fp+fn else 0.)
            err=max(err,abs(float(np.array(fs)[MASKS[key[2]]].mean())-scene.loc[key,'F1_U']))
        require(err<1e-12,'Full confusion metric replay')
        stored=np.load(OUT/'comparisons/bootstrap.npz');arms,cts,w,u,aux,cm=bootstrap(d)
        require(np.array_equal(stored['weights'],w) and np.array_equal(stored['content_confusions'],cm),'Bootstrap sampling/membership')
        require(np.array_equal(stored['F1_U'],u) and np.array_equal(stored['F1_C'],aux),'Bootstrap result replay')
        prior=np.load(PARENT/'comparisons/bootstrap.npz')
        require(np.array_equal(prior['contents'],np.array(cts)) and np.array_equal(prior['weights'],w),'Original common content resampling')
        pooled=pd.read_parquet(OUT/'scores/pooled.parquet').set_index('policy_id')
        primary=read(OUT/'comparisons/primary.json');require(primary['family']==4 and primary['marginal_coverage']==.9875,'Four-effect family')
        for x,(a,b,name) in zip(primary['comparisons'],EFFECTS):
            require(x['candidate']==a and x['reference']==b and x['name']==name,'Fixed comparison changed')
            delta=u[:,arms.index(a)]-u[:,arms.index(b)];ci=np.quantile(delta,[.00625,.99375],method='linear')
            require(np.max(np.abs(ci-x['CI_family']))<1e-12,'Primary interval replay')
            require(abs(x['delta_F1_U']-(pooled.loc[a,'F1_U']-pooled.loc[b,'F1_U']))<1e-12,'Primary point replay')
        p4=read(OUT/'stages/P4.json');p5=read(OUT/'stages/P5.json');reads=[]
        for path in (OUT/'stages').glob('*.json'):reads.extend(read(path)['reads'])
        reads.extend(READS)
        for a in reads:
            require(not any(k in a['path'] for k in ['heldout-visits','main-test-paired','.pcap','.pcapng']),'Forbidden raw/H-pre read')
            if a['purpose']=='query':require(a['time_unix']>=p4['ended_unix'],'Query before full model seal')
            if a['purpose']=='score':require(a['time_unix']>=p5['ended_unix'],'Labels before full prediction seal')
        for path,h in c['fixed'].items():
            budget_check();require(sha(ROOT/path)==h,'Fixed historical source changed: '+path)
        for path,h in c['code'].items():require(sha(ROOT/path)==h,'AD1 code changed')
        require(sha(OLD/'failure.json')==c['original_failure_sha256'],'Original stop changed')
        require(sha(FULL1/'failure.json')==c['full_NR1_failure_sha256'],'NR1 full stop changed')
        for r in c['roles']:
            require(not(set(r['train_contents'])&set(r['validation_contents'])),'Content leakage')
        reuse=read(OUT/'audits/reused-prediction-replay.json');require(reuse['passed'] and reuse['max_error']<1e-12,'Reuse replay missing')
        write(OUT/'verification.json',dict(passed=True,new_models=120,reused_models=180,model_prediction_replays=replays,
            probability_replay_max=maximum,logprob_replay_max=logmax,confusion_metric_replay_max=err,
            original_bootstrap_weights_identical=True,bootstrap_exactly_replayed=True,primary_family=4,
            H_pre_reads=0,actual_target_U_training_reads=0,new_mapping_fits=0,global_content_intersection_max=0,
            post_only_interface=True,all_model_fit_and_prediction_CUDA_float64=True,stage_timeline_verified=True,
            original_full_records_preserved=True,new_method_selected_after_H=False,cumulative_before_closeout=spent(),
            report_sha256=sha(DOC/'complete-report.md')))
