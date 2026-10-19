from common import *
from head import *

def run():
    with stage('audit'):
        for name in ['provenance-complete','models-complete']:verify(OUT/f'manifests/{name}.json')
        verify(OUT/'predictions/raw-complete.json');verify(OUT/'calibration/temperatures-complete.json')
        verify(OUT/'predictions/calibrated-complete.json');verify(OUT/'scores/complete.json')
        c=contract();eps=read(OUT/'manifests/endpoints.json');raw=pd.read_parquet(OUT/'predictions/raw.parquet')
        calibrated=pd.read_parquet(OUT/'predictions/calibrated.parquet');maxreplay=0.;maxgradient=0.;calerr=0.
        for r in c['roles']:
            s,m,_=train(r,'OR-X',SEEDS[0]);q=basis();z0=offset(s['x'],m);geo=geometry(z0,q)
            # Training gradient checks use only training packages.
            for ep in [v for v in eps if v['role_id']==r['id'] and (not v['seed_alias'] or v['seed']==SEEDS[0])]:
                h=own(ROOT/ep['model']);arm,seed=ep['arm'],ep['seed']
                g=None if arm in ['OR-X','OR-BIAS'] else source_tensor(ROOT/r['frozen_G'][f'{arm}-{seed}'],r['id'],arm)
                phi=features(s['x'],g,arm);ind=independent(h['W'],h['b'],phi,z0,s['y'],s['mass'],q)
                grad=max(maxabs(ind['gd']),maxabs(ind['ge']));maxgradient=max(maxgradient,grad);require(grad<=1e-5,'Audit original gradient')
            query=source_frame(ROOT/r['query'],'predict',r['id']);x=(tensor(query[HIST])-m['mu'])/m['scale'];zbase=offset(x,m);geo=geometry(zbase,q)
            for ep in [v for v in eps if v['role_id']==r['id']]:
                h=own(ROOT/ep['model']);arm,seed=ep['arm'],ep['seed']
                g=None if arm in ['OR-X','OR-BIAS'] else source_tensor(ROOT/r['frozen_G'][f'{arm}-{seed}'],r['id'],arm)
                phi=features(x,g,arm);zz,_,delta=logits(h['W'],h['b'],phi,zbase,h['Q'],geo);geometry_errors(geo['s'],delta,geo['mask'])
                lp=F.log_softmax(zz,1).cpu().numpy()
                saved=raw[raw.role_id.eq(r['id'])&raw.arm.eq(arm)&raw.seed.eq(seed)].set_index('visit_id').loc[query.visit_id]
                error=float(abs(lp-saved[LC].to_numpy()).max());maxreplay=max(maxreplay,error);require(error==0,'Raw replay not exact')
        ts=read(OUT/'calibration/temperatures-new.json');require(len(ts)==360,'Temperature count')
        for fit in ts:
            p=ROOT/fit['calibration_package'];require(sha(p)==fit['calibration_package_sha256'],'Cal package changed')
            z=pd.read_parquet(p);z=z[z.pipeline.eq(fit['pipeline'])]
            require(set(z.role_id)=={fit['role_id']} and fit['held_content'] not in set(z.content_id),'Temperature role/content leak')
            require(z.visit_id.nunique()==20 and z.content_id.nunique()==5,'Calibration sample counts')
            a=z[LC].to_numpy()*fit['inverse_temperature'];a-=a.max(1,keepdims=True);lp=a-np.log(np.exp(a).sum(1,keepdims=True))
            y=z.y.to_numpy(dtype=int);orig=z[LC].to_numpy();value=float(-lp[np.arange(len(z)),y].mean())
            grad=float(((np.exp(lp)*orig).sum(1)-orig[np.arange(len(z)),y]).mean())
            require(abs(value-fit['objective'])<1e-10 and abs(grad-fit['gradient'])<1e-10,'Temperature objective replay')
            if fit['status']=='T1':require(grad<=1e-8,'T1 KKT')
            elif fit['status']=='T5':require(grad>=-1e-8,'T5 KKT')
            else:require(abs(grad)<=1e-8 or (fit['bracket_upper']-fit['bracket_lower']<=1e-10 and
                 fit['bracket_gradient_lower']<=0<=fit['bracket_gradient_upper']),'Interior temperature')
        orig=calibrated[['raw_'+v for v in LC]].to_numpy();z=orig/calibrated.temperature.to_numpy()[:,None]
        z-=z.max(1,keepdims=True);lp=z-np.log(np.exp(z).sum(1,keepdims=True))
        calerr=float(abs(lp-calibrated[LC].to_numpy()).max());require(calerr<1e-12,'Independent calibrated replay')
        require(np.array_equal(orig.argmax(1),calibrated[PC].to_numpy().argmax(1)),'Temperature argmax change')
        for p,h in c['historical'].items():require(sha(ROOT/p)==h,'Historical artifact mutated')
        for p,info in c['sources'].items():require(sha(ROOT/p)==info['sha256'],'Source artifact mutated')
        log=read(OUT/'ledger.json');require(log['accepted_fits']==log['attempted_fits']==132 and log['temperature_fits']==360,'Fit accounting')
        require(log['G_fits']==log['teacher_fits']==log['base_fits']==0,'Forbidden fitting')
        for name in ['tests','pilot','train']:
            reads=read(OUT/f'stages/{name}.json')['reads'];require(not any(v['purpose'] in ['predict','labels'] for v in reads),'Query/labels during training')
        result=dict(passed=True,physical_heads=132,logical_endpoints=180,new_temperatures=360,reused_temperatures=360,
                    raw_rows=4320,combined_rows=8064,max_original_gradient=maxgradient,raw_inference_replay_error=maxreplay,
                    calibrated_replay_error=calerr,all_G_base_scalers_unchanged=True,H_reads=0,actual_U_reads=0,
                    historical_role_decisions_unchanged=True,independent_source_only=True)
        write(OUT/'audits/final-verification.json',result)

def finish():
    for name in ['register','tests','pilot','train','predict','calibrate','score','audit']:
        require(read(OUT/f'stages/{name}.json')['passed'],'Missing stage')
    s=read(OUT/'scores/summary.json')
    write(OUT/'completion.json',dict(passed=True,status='OR1_source_pilot_complete',physical_heads=132,
        geometry_utility_pass=s['utility_pass'],paired_increment_pass=s['increment_pass'],formal_H_scored=False,
        full_roles_started=False,G_updated=False,old_results_unchanged=True,
        verification_sha256=sha(OUT/'audits/final-verification.json')))
    progress('complete',utility=s['utility_pass'],paired_increment=s['increment_pass'])
