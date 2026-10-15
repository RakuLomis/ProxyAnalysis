from core import *

def run():
    c=C.start('identity-inventory');C.sealed_predictions()
    require(not (OUT/'input-manifest.json').exists(),'Inventory already registered')
    require((RUN/'failure.json').exists() and not (RUN/'completion.json').exists(),'Original terminal state')
    complete=C.read(REPORT/'complete.json')
    require(complete['report_analysis_complete'] and complete['independent_numeric_audit_passed'],'Report audit incomplete')
    require(C.sha(Path(E.__file__))==complete['evidence_builder_sha256'],'Prior verification implementation changed')
    fixed=[RUN/'failure.json',RUN/'progress.json',RUN/'manifests/experiment-contract.json',RUN/'manifests/numeric-policy.json',
           RUN/'selection/choices.json',RUN/'predictions/visits.parquet',RUN/'selection/inner-predictions.parquet',
           REPORT/'complete.json',REPORT/'integrity.json',REPORT/'independent-numeric-audit.json',Path(E.__file__)]
    fixed+=list((REPORT/'scores').glob('*.parquet'))+[REPORT/'comparisons/primary.json',REPORT/'comparisons/bootstrap.npz']
    fixed+=list((REPORT/'diagnostics').glob('*.parquet'))
    s=selected();coverage=[];index=[]
    for r in c['roles']:
        if r['inner'] is None:
            a,b=[C.chosen(r,v,s) for v in ['JA1','JA2']]
            coverage.append({'role_id':r['id'],'target':r['target'],'group':r['group'],'outer':r['outer'],
                'eta_JA1':a['eta'],'eta_JA2':b['eta'],'same_eta':a['eta']==b['eta'],'t_JA1':a['t'],'t_JA2':b['t']})
    for r,eta in pairs(c):
        ps=[C.mappath(r,a,eta) for a in ['JA1','JA2']]
        require(all(p.exists() and p.with_suffix('.json').exists() for p in ps),'Missing existing mapping')
        index.append({'role_id':r['id'],'eta':eta,'inner':r['inner'],'target':r['target'],'calibration':r['calibration'],
                      'group':r['group'],'paths':[C.rel(p) for p in ps]})
    require(len(index)==2929 and sum(v['same_eta'] for v in coverage)==49,'Candidate coverage changed')
    save(OUT/'matched-candidate-index.parquet',pd.DataFrame(index));save(OUT/'outer-eta-coverage.parquet',pd.DataFrame(coverage))
    write(OUT/'input-manifest.json',{'fixed_files':{C.rel(p):C.sha(p) for p in fixed},'plan_sha256':C.sha(PLAN),
        'core_sha256':C.sha(Path(__file__).with_name('core.py')),'registered_unix':time.time(),'original_contract_sha256':C.sha(RUN/'manifests/experiment-contract.json'),
        'process_precheck':'No python training/recovery process observed in Windows CIM at implementation start',
        'new_fits':0,'same_eta_inner_pairs':2880,'same_eta_outer_pairs':49,'different_eta_outer_roles':11,
        'environment':{'torch':torch.__version__,'cuda':torch.version.cuda,'gpu':torch.cuda.get_device_name(0),'dtype':'float64','CPU_fallback':False}})
    progress('inventory_complete',inner_pairs=2880,outer_pairs=49,new_fits=0)
if __name__=='__main__':run()
