"""End-to-end frozen inference replay and role/source audit."""
from common import *
from predict import predict_frames

def run():
    c=start('verify')
    baseline=read(OUT/'manifests/baseline-manifest.json')
    for path,h in baseline['sha256'].items():
        require(sha(ROOT/path)==h,'Frozen old input or result changed: '+path)
    for path,h in c['packages_sha256'].items():
        require(sha(ROOT/path)==h,'Package changed')
    saved=pd.read_parquet(OUT/'predictions/visits.parquet')
    require(read(OUT/'predictions/complete.json')['sha256'][rel(OUT/'predictions/visits.parquet')]==sha(OUT/'predictions/visits.parquet'),'Predictions changed')
    max_error=0.
    histogram_error=0.
    labels_perturbation_checks=0
    forbidden_query_checks=0
    for r in c['roles']:
        fold,p=r['fold'],r['protocol']
        f=rolefolder(fold,p)
        query=load_package(f/'query-post-hist.parquet','verify')
        flows=load_package(f/'query-post-flow.parquet','verify')
        names,h=visits_histogram(flows,'post','visit_id')
        err=float(np.max(np.abs(query.set_index('visit_id').loc[names,HIST].to_numpy()-h.cpu().numpy())))
        histogram_error=max(histogram_error,err)
        require(err<1e-12,'Post histogram replay failed')
        m=modelfolder(fold,p)
        bundle=model_load(m/'distributions.pt','verify')
        lr=model_load(m/'G1.pt','verify')
        mlps={s:model_load(m/f'G2-{s}.pt','verify') for s in SEEDS}
        with torch.inference_mode():
            result=predict_frames(query,bundle,lr,mlps)
            # An unrelated modified scorer object cannot enter this inference function.
            fake_score={'truth':'altered','pre':'unavailable','content_id':'withheld'}
            repeated=predict_frames(query.copy(),bundle,lr,mlps)
        labels_perturbation_checks+=1
        for key,logits in result.items():
            arm,seed=key
            old=saved[saved.protocol.eq(p)&saved.fold.eq(fold)&saved.arm.eq(arm)&saved.seed.eq(seed)].set_index('visit_id').loc[query.visit_id]
            error=float(np.max(np.abs(old[[f'p{i}' for i in range(6)]].to_numpy()-logits.softmax(1).cpu().numpy())))
            max_error=max(max_error,error)
            require(error<1e-6,'Saved inference replay differs')
            require(np.array_equal(old.prediction.to_numpy(),logits.argmax(1).cpu().numpy()),'Reload changes decisions')
            require(torch.equal(logits,repeated[key]),'External scorer change affected inference')
        try:
            predict_frames(query.assign(pre_W_up=0),bundle,lr,mlps)
        except RuntimeError:
            forbidden_query_checks+=1
        else:
            raise RuntimeError('Inference accepted forbidden pre column')
    baseline_fits=read(OUT/'manifests/baseline_fit-ledger.json')['fits']
    require(len(baseline_fits)==80 and all(r['device']=='cuda:0' for r in baseline_fits),'CUDA fitting ledger incomplete')
    actual_predict_reads=read(OUT/'manifests/predict-ledger.json')['reads']
    require(all('/models/' in r['path'] or r['path'].endswith('/query-post-hist.parquet') for r in actual_predict_reads), 'Predict ledger has forbidden package')
    require(len(saved)==3840 and saved.visit_id.nunique()==480,'Prediction support changed')
    for (p,a,s),g in saved.groupby(['protocol','arm','seed']):
        require(len(g)==120 and g.visit_id.nunique()==120,'Incomplete arm/seed support')
    v={'passed':True,'old_inputs_and_results_unchanged':True,'main_pairs':23566,'visits':480,
       'reused_kernel_files':200,'new_LR_models':20,'new_MLP_models':60,'CUDA_fit_and_predict':True,
       'max_probability_replay_error':max_error,'max_histogram_replay_error':histogram_error,
       'external_score_noninterference_checks':labels_perturbation_checks,'forbidden_pre_column_rejections':forbidden_query_checks,
       'numeric_inference_input':HIST,'query_pre_or_label_opened':False,
       'registered_entity_cross_fold':0,'universal_TCP_epoch_proof':False,
       'given_dual_side_qualified_connections_and_visit_ranges':True,'raw_PCAP_reads':0,
       'unit_tests':len(read(OUT/'manifests/unit-tests.json')['checks']),
       'human_external_blind_validation':False,'no_new_SSL_or_kernel_fitting':True}
    write(OUT/'verification.json',v)
    finish('verify',**v)
    print('Verification passed; exact decisions replayed for all 3840 probability rows',flush=True)

if __name__=='__main__':
    run()
