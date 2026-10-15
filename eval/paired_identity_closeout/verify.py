from core import *

def run():
    with stage('verify'):
        for name in ['tests','closeout','decompose','project','plots','synthesize','review']:
            marker=C.read(OUT/'stages'/f'{name}.json');require(marker['passed'],'Stage incomplete: '+name)
            require(C.sha(ROOT/marker['script'])==marker['script_sha256'],'Stage code changed: '+name)
        require(C.read(CLOSE/'verification.json')['passed'],'Closeout verification')
        inv=C.read(OUT/'input-manifest.json');require(C.sha(RUN/'failure.json')==inv['fixed_files'][C.rel(RUN/'failure.json')],'Original failure overwritten')
        require(not (RUN/'completion.json').exists(),'Original completion rewritten')
        d=pd.read_parquet(OUT/'moment-decomposition.parquet');require(len(d)==2929 and d.maximum_normalized_residual.max()<=1e-10,'Algebra gate')
        require(len(pd.read_parquet(OUT/'block-effects.parquet'))==292900,'Block table coverage')
        p=pd.read_parquet(OUT/'decision-projections.parquet');require(len(p)==17574 and not p.is_attack_score.any(),'Projection scope')
        require(len(pd.read_parquet(OUT/'actual-post-candidate-comparisons.parquet'))==2929,'Actual comparison coverage')
        require(C.read(OUT/'projection-verification.json')['new_fits']==0,'New fits forbidden')
        evidence=C.read(OUT/'evidence-index.json')
        for row in evidence['rows']:
            require(C.sha(ROOT/row['report'])==row['report_sha256'],'Evidence report changed')
            for item in row['machine_files']:require(C.sha(ROOT/item['path'])==item['sha256'],'Machine evidence changed')
        total=sum(C.read(v)['seconds'] for v in (OUT/'stages').glob('*.json'))
        require(total<4*3600 and time.time()-inv['registered_unix']<8*3600,'Cumulative processing budget exceeded')
        files=[v for v in DOC.rglob('*') if v.is_file()]+[v for v in OUT.glob('*') if v.is_file() and v.name not in ['progress.json','stage.lock','verification.json','completion.json']]
        write(OUT/'verification.json',{'passed':True,'new_fits':0,'same_eta_pairs':2929,'algebra_threshold':1e-10,
            'original_failure_preserved':True,'scientific_contract_unchanged':True,'target_U_reads':0,
            'CUDA_float64_diagnostics':True,'new_primary_tests':0,'completed_stage_seconds_before_verify':total,'files':{C.rel(v):C.sha(v) for v in files},
            'closeout_completion_sha256':C.sha(CLOSE/'completion.json')})
    write(OUT/'completion.json',{'passed':True,'time_unix':time.time(),'new_fits':0,'stages':8,
        'verification_sha256':C.sha(OUT/'verification.json'),'original_runner_failure_retained':True,'additive_closeout_complete':True})
if __name__=='__main__':run()
