"""Independent replays before completion; qualifications never auto-promote."""
from common import *
import objectives as O
import marginal as M
from score import labeled,bootstrap,tables,PC,COLS

def run():
    with stage('verify'):
        c=contract()
        for name in ['tests','prepare_pilot','fit_pilot','pilot_gate','prepare_remaining','fit_remaining',
                     'seal_models','predict','score','concentration','compatibility','observation_audit','report']:
            require(read(OUT/'stages'/(name+'.json'))['passed'],'Stage incomplete '+name)
        require(not (OUT/'failure.json').exists(),'Unresolved failure')
        refs={(v['role_id'],v['arm']):v for v in c['references']}
        pred=pd.read_parquet(OUT/'predictions/visits.parquet');rows=[];maxerr=0.;transform_error=0.
        for i,r in enumerate(c['roles']):
            v=artifact(oldviews(r));query=package(rolepath(r)/'query.parquet','query')
            anonymous=artifact(anonymous_path(r));stored=artifact(transformpath(r));rebuilt,log=M.fit(anonymous)
            err=max(residual(stored[k],rebuilt[k]) for k in stored);require(err<1e-12,'Marginal replay');transform_error=max(transform_error,err)
            for a in ARMS:
                if a in ARMS[:3]:p=ROOT/refs[(r['id'],a)]['model_path'];s=O.reference(v,a)
                else:p=newmodel(r,a);s=artifact(newslot(r,a))
                m=artifact(p);meta=read(p.with_suffix('.json'))['optimizer'];audit=O.audit(m,s,r['t'],meta)
                expected=pred[pred.role_id.eq(r['id'])&pred.arm.eq(a)].set_index('visit_id')
                replay=predict(m,query).set_index('visit_id').loc[expected.index]
                diff=float(np.abs(replay[PC].to_numpy()-expected[PC].to_numpy()).max())
                require(diff<1e-12,'Prediction replay');maxerr=max(maxerr,diff)
                rows.append({'role_id':r['id'],'arm':a,'probability_max_error':diff,**audit})
            if (i+1)%12==0:progress('verify_models',roles=i+1,total=60)
        d=labeled();contents,w,u,aux=bootstrap(d);stored=np.load(OUT/'comparisons/bootstrap.npz')
        require(np.array_equal(w,stored['weights']) and np.array_equal(u,stored['uncovered']) and
                np.array_equal(aux,stored['auxiliary']) and np.array_equal(np.array(contents),stored['contents']),'Exact bootstrap replay')
        primary=read(OUT/'comparisons/primary.json');dfs,_=tables(d);point=dfs['pooled'].set_index('arm')
        for v in primary['comparisons']:
            delta=u[:,ARMS.index(v['candidate'])]-u[:,ARMS.index(v['reference'])]
            require(np.array_equal(np.quantile(delta,[.05/6,1-.05/6]),np.array(v['CI_98_333333'])),'CI replay')
            pp=float(point.loc[v['candidate'],'F1_uncovered']-point.loc[v['reference'],'F1_uncovered'])
            require(pp==v['delta_F1_uncovered'],'Point replay')
        require(len(rows)==360 and len(list((OUT/'models').rglob('*.pt')))==180 and
                len(list((OUT/'fit-logs').rglob('*.json')))==180 and len(list((OUT/'transforms').rglob('*.pt')))==60,'Formal budget counts')
        reads=[a for p in (OUT/'stages').glob('*.json') for a in read(p).get('reads',[])]+ACCESS
        require(not any('heldout-visits' in a['path'] or 'main-test-paired' in a['path'] or
                    Path(a['path']).suffix.lower() in ['.pcap','.pcapng','.cap'] for a in reads),'Forbidden raw/test-pre read')
        for p,h in c['fixed_files'].items():require(sha(ROOT/p)==h,'Old input changed during run')
        save(pd.DataFrame(rows),OUT/'scores/independent-model-audit.parquet')
        files=[p for p in DOC.rglob('*') if p.is_file()]+[OUT/'predictions/visits.parquet',
             OUT/'comparisons/primary.json',OUT/'comparisons/bootstrap.npz',OUT/'manifests/new-endpoints.parquet',
             OUT/'audits/historical-compatibility.json',OUT/'audits/physical-post-qualification.json']
        write(OUT/'verification.json',{'passed':True,'attribution_complete':True,'numerical_acceptance':True,
            'new_classifier_fits':180,'reused_classifiers':180,'new_marginal_transforms':60,
            'independent_transform_replays':60,'classifier_replays':360,'probability_max_error':maxerr,
            'marginal_replay_error':transform_error,'bootstrap_exactly_replayed':True,'old_family_unchanged':True,
            'target_U_training_reads':0,'test_pre_reads':0,'PCAP_reads':0,'all_model_fit_and_prediction_CUDA_float64':True,
            'physical_input_qualified':False,'historical_direct_transfer_qualified':False,
            'historical_compatibility_status':'Requires representation and business/content qualification',
            'physical_observation_status':'Window independence and full physical reconstruction not verified',
            'files':{rel(p):sha(p) for p in files}})
    write(OUT/'completion.json',{'passed':True,'attribution_complete':True,'numerical_acceptance':True,
          'new_classifier_fits':180,'new_marginal_transforms':60,'historical_direct_transfer_qualified':False,
          'physical_input_qualified':False,'target_U_training_reads':0,'test_pre_reads':0,
          'verification_sha256':sha(OUT/'verification.json'),'time_unix':time.time()})

if __name__=='__main__':run()
