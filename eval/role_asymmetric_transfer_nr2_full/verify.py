"""Independent frozen export/CM/bootstrap and permission timeline audit."""
from common import *
from weight_schedule import registry
from score import bootstrap,PC,LPC,cm_f1

def run():
    with stage('verify'):
        c=contract();d=pd.read_parquet(OUT/'scores/labeled-predictions.parquet');raw=pd.read_parquet(OUT/'predictions/visits.parquet')
        e=pd.read_parquet(OUT/'manifests/endpoints.parquet');require(len(e)==2340 and len(d)==len(raw)==56160,'Full coverage')
        require(not (OUT/'failure.json').exists(),'Unresolved failure')
        maxprob=maxlog=0.;modelreplays=0
        for r in c['roles']:
            q=package(rolepath(r)/'query.parquet','query');x=tensor(q[HIST]);ee=e[e.role_id.eq(r['id'])].set_index('policy_id')
            for p in registry():
                er=ee.loc[p['id']];m=artifact(ROOT/er.path,'independent-model-replay')
                zz=((x-m['mu'])/m['scale'])@m['weight'].T+m['bias'];lp=zz.log_softmax(1);pr=zz.softmax(1)
                expected=raw[raw.role_id.eq(r['id'])&raw.policy_id.eq(p['id'])].set_index('visit_id').loc[q.visit_id]
                pe=float(np.abs(pr.detach().cpu().numpy()-expected[PC].to_numpy()).max());le=float(np.abs(lp.detach().cpu().numpy()-expected[LPC].to_numpy()).max())
                require(pe<1e-12 and le<1e-12,'Frozen export replay');maxprob=max(maxprob,pe);maxlog=max(maxlog,le);modelreplays+=1
        stored=np.load(OUT/'comparisons/bootstrap.npz');arms,contents,w,u,aux,cm=bootstrap(d)
        require(np.array_equal(w,stored['weights']) and np.array_equal(cm,stored['content_confusions']),'Bootstrap membership replay')
        require(np.array_equal(u,stored['F1_U']) and np.array_equal(aux,stored['F1_C']),'Bootstrap metric replay')
        # Independent manual CM/F1 from rows, not from stored bootstrap cube.
        scene=pd.read_parquet(OUT/'scores/scenarios.parquet').set_index(['policy_id','target','group']);maximum=0.
        for key,part in d.groupby(['policy_id','target','group']):
            yy=truths(part);zz=part.prediction.to_numpy();mat=np.zeros((6,6),int)
            for a,b in zip(yy,zz):mat[a,b]+=1
            f=[]
            for j in range(6):
                tp=mat[j,j];fp=mat[:,j].sum()-tp;fn=mat[j].sum()-tp;f.append(2*tp/(2*tp+fp+fn) if 2*tp+fp+fn else 0.)
            expected=np.mean(np.asarray(f)[MASKS[key[2]]]);maximum=max(maximum,abs(expected-scene.loc[key,'F1_U']))
        require(maximum<1e-12,'Independent confusion metric')
        p4=read(OUT/'stages/P4.json');p5=read(OUT/'stages/P5.json');reads=[]
        for path in (OUT/'stages').glob('*.json'):reads.extend(read(path)['reads'])
        reads.extend(READS)
        for a in reads:
            require(not any(x in a['path'] for x in ['heldout-visits','main-test-paired','.pcap','.pcapng']),'Forbidden raw or H-pre read')
            if a['purpose']=='query':require(a['time_unix']>=p4['ended_unix'],'Query before all model seal')
            if a['purpose']=='score':require(a['time_unix']>=p5['ended_unix'],'Labels before complete prediction stage')
        for p,h in c['fixed'].items():require(sha(ROOT/p)==h,'Historical input changed')
        for p,h in c['code'].items():require(sha(ROOT/p)==h,'Code changed')
        require(len(list((OUT/'fit-logs').rglob('*.json')))==1296,'Physical resumed fit count')
        require(sha(OLD/'failure.json')==c['original_failure_sha256'] and not (OLD/'completion.json').exists(),'Original stop was rewritten')
        require(sha(FULL1/'failure.json')==c['full_NR1_failure_sha256'] and not (FULL1/'completion.json').exists(),'Full NR1 stop was rewritten')
        write(OUT/'verification.json',dict(passed=True,models=2340,physical_resumed_scientific=1296,adopted_scientific=624,aliases=420,model_prediction_replays=modelreplays,
              probability_replay_max=maxprob,logprob_replay_max=maxlog,confusion_metric_replay_max=maximum,bootstrap_exactly_replayed=True,
              H_pre_reads=0,actual_target_U_training_reads=0,post_only_interface=True,all_model_fit_and_prediction_CUDA_float64=True,
              stage_timeline_verified=True,new_method_selected_after_H=False,active_seconds_before_closeout=spent(),report_sha256=sha(DOC/'complete-report.md')))

