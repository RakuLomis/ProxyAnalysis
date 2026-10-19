from common import *

def temperature_module():
    p=ROOT/'eval/post_associated_temperature_calibration/run.py'
    require(sha(p)==contract()['old_temperature_code_sha256'],'Frozen temperature backend changed')
    spec=importlib.util.spec_from_file_location('or1_frozen_temperature_backend',p)
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    return m

def run():
    with stage('calibrate'):
        verify(OUT/'predictions/raw-complete.json');c=contract()
        oldtc=read(TEMP/'manifests/contract.json');content=oldtc['contents'];require(len(content)==6,'Six global content folds')
        frozen=source_frame(TEMP/'predictions/visits.parquet','control')
        oldfits=read(TEMP/'fits/temperatures.json');check_source(TEMP/'fits/temperatures.json','control')
        wanted=['base','X_eta0p01','R_eta0p01','G_eta0p01','P_eta0p01']
        controls=frozen[frozen.pipeline.isin(wanted)].copy()
        reused=[v for v in oldfits if v['pipeline'] in wanted];require(len(reused)==360 and len(controls)==3744,'Old-control budgets')
        raw=pd.read_parquet(OUT/'predictions/raw.parquet');parts=[];jobs=[];ll=[];yy=[];ww=[];newpackages=[]
        for ri,r in enumerate(c['roles']):
            labels=source_frame(ROOT/r['labels'],'labels',r['id'])
            require(set(labels.content_id)==set(content)==set(r['validation_contents']) and labels.visit_id.is_unique,'Content membership')
            require(not set(content)&set(r['train_contents']),'Held content in model training')
            labels['y']=labels.label_id.map({v:i for i,v in enumerate(LABELS)})
            require(not labels.y.isna().any() and labels.groupby('content_id').size().eq(4).all(),'Source label rows')
            oldrole=next(v for v in oldtc['roles'] if v['id']==r['id'])
            prior=pd.read_parquet(ROOT/oldrole['scoring_labels'])
            require(labels[['visit_id','content_id','y']].set_index('visit_id').sort_index().equals(
                    prior[['visit_id','content_id','y']].set_index('visit_id').sort_index()),'Old temperature label compatibility')
            sp=OUT/f'calibration/packages/r{ri:02d}/scoring-labels.parquet'
            save(sp,labels[['visit_id','content_id','protocol','y']]);newpackages.append(sp)
            z=raw[raw.role_id.eq(r['id'])].merge(labels[['visit_id','content_id']],on='visit_id',validate='many_to_one')
            z['pipeline']=z.arm;z['calibration_fold']=z.content_id.map({v:i for i,v in enumerate(content)})
            for fold,held in enumerate(content):
                cal=z[z.content_id.ne(held)].merge(labels[['visit_id','y']],on='visit_id',validate='many_to_one')
                pack=OUT/f'calibration/packages/r{ri:02d}/h{fold}.parquet'
                save(pack,cal[['role_id','pipeline','seed','visit_id','content_id','y',*LC]])
                newpackages.append(pack)
                for arm in ARMS:
                    sub=cal[cal.pipeline.eq(arm)].sort_values(['visit_id','seed'])
                    require(len(sub)==60 and sub.visit_id.nunique()==20 and sub.content_id.nunique()==5 and held not in set(sub.content_id),'Fit exclusion')
                    require(sub.groupby('visit_id').size().eq(3).all(),'Seed-balanced weight')
                    ll.append(sub[LC].to_numpy());yy.append(sub.y.to_numpy());ww.append(np.full(60,1/60))
                    jobs.append(dict(id=f'r{ri:02d}/{arm}/h{fold}',role_id=r['id'],pipeline=arm,fold=fold,held_content=held,
                                     calibration_package=rel(pack),calibration_package_sha256=sha(pack),
                                     calibration_contents=sorted(set(sub.content_id)),calibration_visits=sorted(set(sub.visit_id))))
            parts.append(z)
        require(len(jobs)==360,'New temperature count')
        write(OUT/'calibration/task-index.json',jobs)
        seal(OUT/'calibration/packages-complete.json',newpackages+[OUT/'calibration/task-index.json'])
        backend=temperature_module();l=tensor(np.stack(ll));y=tensor(np.stack(yy),torch.int64);w=tensor(np.stack(ww))
        start=time.perf_counter();sol=backend.solve(l,y,w);torch.cuda.synchronize();seconds=time.perf_counter()-start
        records=[]
        for i,job in enumerate(jobs):
            v={key:(arr[i].item() if hasattr(arr[i],'item') else str(arr[i])) for key,arr in sol.items()}
            z=ll[i]*v['inverse_temperature'];z-=z.max(1,keepdims=True);lp=z-np.log(np.exp(z).sum(1,keepdims=True))
            obj=float((-lp[np.arange(60),yy[i]]*ww[i]).sum())
            grad=float((((np.exp(lp)*ll[i]).sum(1)-ll[i][np.arange(60),yy[i]])*ww[i]).sum())
            require(abs(obj-v['objective'])<=1e-10 and abs(grad-v['gradient'])<=1e-10,'Temperature independent replay')
            records.append(dict(**job,**v,qualified=True,objective_replay_error=abs(obj-v['objective']),gradient_replay_error=abs(grad-v['gradient'])))
        write(OUT/'calibration/temperatures-new.json',records);write(OUT/'calibration/temperatures-reused.json',reused)
        write(OUT/'calibration/quality.json',dict(passed=True,new_fits=360,reused=360,cuda_seconds=seconds,
              backend_sha256=c['old_temperature_code_sha256'],temperature_range=[1,5]))
        ledger(temperature_fits=360)
        seal(OUT/'calibration/temperatures-complete.json',[OUT/'calibration/temperatures-new.json',OUT/'calibration/temperatures-reused.json',OUT/'calibration/quality.json'])
        # All temperatures sealed before any calibrated held-content output.
        idx={(v['role_id'],v['pipeline'],v['fold']):v for v in records};new=[]
        for z in parts:
            ts=np.array([idx[(r,a,int(f))]['temperature'] for r,a,f in zip(z.role_id,z.pipeline,z.calibration_fold)])
            old=tensor(z[LC]);lp=F.log_softmax(old/tensor(ts)[:,None],1)
            require(np.array_equal(lp.argmax(1).cpu().numpy(),z[PC].to_numpy().argmax(1)),'Temperature altered classification')
            out=z.rename(columns={k:'raw_'+k for k in PC+LC});out['temperature']=ts
            for k in range(6):out[f'l{k}']=lp[:,k].cpu().numpy();out[f'p{k}']=lp[:,k].exp().cpu().numpy()
            new.append(out)
        new=pd.concat(new,ignore_index=True)
        baseindex={r['id']:r for r in c['roles']}
        controls['role_target']=[baseindex[v]['target'] for v in controls.role_id]
        controls['query_deployment']=[baseindex[v]['calibration'] for v in controls.role_id]
        columns=['role_id','role_target','query_deployment','pipeline','seed','visit_id','content_id','calibration_fold','temperature',
                 *PC,*LC,*['raw_'+v for v in PC+LC]]
        joined=pd.concat([new[columns],controls[columns]],ignore_index=True)
        require(len(joined)==8064 and len(new)==4320,'Combined new/control predictions')
        save(OUT/'predictions/calibrated.parquet',joined)
        seal(OUT/'predictions/calibrated-complete.json',[OUT/'predictions/calibrated.parquet'],rows=8064,
             new_rows=4320,control_rows=3744,temperature_class_changes=0)
