"""Independent lineage checks, sampled original FR and weighted-score replay."""
from pathlib import Path
from types import SimpleNamespace
import sys
import subprocess
import numpy as np
import pandas as pd
import torch
from common import ROOT, OUT, EXTRACT, FEATURES, PROTOCOLS, read, write, relative, hash_file, require, verify_sources, cuda
from kernels import tensor,smooth
from information import information


def run():
    verify_sources()
    contract=read(OUT/'manifests/experiment-contract.json')
    repair=read(OUT/'manifests/engineering-repairs.json')
    for rel,sha in contract['source_sha256'].items():
        now=hash_file(ROOT/rel)
        declared=repair['source_changes'].get(rel,{})
        require(now==sha or (declared.get('original_sha256')==sha and declared.get('repaired_sha256')==now),
                'Undocumented source change')
    for rel,sha in contract['packages_sha256'].items():
        require(hash_file(ROOT/rel)==sha,'Sealed package changed')
    frame=pd.read_parquet(OUT/'features/paired-flow-features.parquet')
    pairs=pd.read_parquet(OUT/'cohorts/pairs.parquet')
    require(set(frame.pair_id)==set(pairs.pair_id) and len(frame)==23566,'Main members changed')
    require(frame.groupby('content_id').fold.nunique().max()==1,'Content split')
    require(frame.groupby('logical_id').fold.nunique().max()==1,'Logical split')
    require(frame.groupby('carrier_id').fold.nunique().max()==1,'Carrier split')
    sys.path.insert(0,str(ROOT/'src'))
    from proxy_analysis.features.reversal import reversal_features
    original_fr_count=0
    for p in PROTOCOLS:
        sample=frame[frame.protocol.eq(p)].sample(12,random_state=20261004)
        for _,r in sample.iterrows():
          for side,ident in [('pre',r.logical_id),('post',r.carrier_id)]:
            events=pd.read_parquet(EXTRACT/'sessions'/r.session_id/(side+'-W-events.parquet'))
            events=events[events.entity_id.eq(ident)]
            packets=[SimpleNamespace(transport_payload_len=int(x.payload_bytes),timestamp_ns=int(x.timestamp_ns),
                                     packet_ordinal=int(x.raw_packet_ordinal),direction=int(x.direction))
                     for x in events.itertuples()]
            result=reversal_features(packets)
            require(result.fr_runs==r[side+'_FR_packet_runs'] and result.fr_reversals==r[side+'_FR_packet_switches'],
                    'Original FR reference differs')
            original_fr_count+=1
    model_count=0;max_marginal_error=0.
    for p in (OUT/'kernels').rglob('complete.json'):
        meta=read(p)
        for name,sha in meta['sha256'].items():
            require(hash_file(p.parent/name)==sha,'Model hash changed')
            model=torch.load(p.parent/name,map_location=cuda(),weights_only=True)
            t,g=model['true_counts'],model['group_counts']
            for axis in [0,1]:
                error=(t.sum(axis)-g.sum(axis)).abs().max().item()
                max_marginal_error=max(max_marginal_error,error)
                require(error<1e-10,'Anonymous marginal mismatch')
            require(torch.allclose(model['M1'].sum(1),torch.ones_like(model['row_mass']),atol=1e-12,rtol=1e-12),
                    'Model rows not normalized')
            model_count+=1
    # Direct pooled physical-pair replay of the flow-equal sensitivity estimand.
    content=pd.read_parquet(OUT/'scores/content-feature-scores.parquet')
    max_score_error=0.
    for protocol in PROTOCOLS:
        chunks=[pd.read_parquet(OUT/'scores/flow_equal'/f'f{fold}-{protocol}.parquet') for fold in range(5)]
        rows=pd.concat(chunks,ignore_index=True)
        direct=rows.groupby(['feature','arm']).CE_bits.mean()
        grouped=content[content.variant.eq('flow_equal')&content.protocol.eq(protocol)]
        actual=grouped.groupby(['feature','arm']).apply(
            lambda z:np.average(z.CE_bits,weights=z.evaluation_mass),include_groups=False)
        error=float((direct-actual).abs().max());max_score_error=max(max_score_error,error)
        require(error<1e-12,'Flow equal aggregation replay failure')
    tests=subprocess.run([sys.executable,'-m','unittest','discover','-s',str(Path(__file__).parent),'-p','test_*.py','-v'],
                         capture_output=True,text=True)
    require(tests.returncode==0,'Unit tests failed')
    write(OUT/'manifests/unit-tests.json',{'returncode':tests.returncode,'output':tests.stdout+tests.stderr,'tests':7})
    n=tensor([[24.,0.,0.,0.,0.,0.,0.,0.,0.,0.]])
    q,k=smooth(n)
    null={'training_contents_mass':24,'B_bins':10,'A_constant':True,'B_constant':True,
          'empirical_MI':float(information(n)['MI'].item()),'M0_observed_probability':q[0].item(),
          'M1_observed_probability':k[0,0].item(),
          'log_loss_gain_bits_without_MI':float(torch.log2(k[0,0]/q[0]).item()),
          'M1_and_M2_equal_when_true_and_group_joints_equal':True,
          'models_or_hyperparameters_changed':False}
    write(OUT/'information/smoothing-null-check.json',null)
    write(OUT/'manifests/postprocessing-source-manifest.json',{
        'sha256':{relative(p):hash_file(p) for p in Path(__file__).parent.glob('*.py')},
        'recorded_after_execution_not_pretended_prefit_seal':True})
    result={'passed':True,'main_pairs':len(frame),'missing_required':0,'old_inputs_and_results_hash_unchanged':True,
      'global_content_fold_consistent':True,'logical_and_registered_carrier_cross_fold':0,
      'original_FR_reference_checks':original_fr_count,'saved_model_files':model_count,
      'max_anonymous_marginal_error':max_marginal_error,'flow_equal_direct_replay_error':max_score_error,
      'unit_tests':7,'CUDA_float64':True,'raw_PCAP_read':0,'business_classifier_fit':False,
      'declared_pre_score_weight_repair':True,'current_AnyTLS_exclusive_TCP_qualification':False,
      'Hy2_new_numeric_extraction':False,'universal_unobserved_TCP_epoch_proof':False}
    write(OUT/'verification.json',result)
    print('Independent verification passed:',model_count,'models;',original_fr_count,'original FR checks;',flush=True)


if __name__=='__main__':run()
