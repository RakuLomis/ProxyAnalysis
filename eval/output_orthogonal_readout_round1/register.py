from common import *

def run():
    require(not OUT.exists(),'Preserve existing OR1 run');configure()
    old=read(OLD/'manifests/experiment-contract.json')
    require(read(OLD/'completion.json')['passed'],'Old readout incomplete')
    require(sha(OLD/'manifests/experiment-contract.json')==read(OLD/'manifests/contract-seal.json')['sha256'],'Old contract')
    for path in ['manifests/code.json','manifests/models-complete.json','predictions/complete.json','scores/complete.json']:verify(OLD/path)
    require(read(TEMP/'completion.json')['passed'],'Temperature pilot incomplete')
    for path in ['registration-seal','temperatures-complete','predictions-complete','scores-complete']:verify(TEMP/f'manifests/{path}.json')
    ct=read(PREP/'manifests/package-manifest.json');roles=[];sources={};rows=[]
    oldinputs=read(TEMP/'manifests/contract.json')['old_inputs']
    historical=dict(oldinputs)
    for p in [OLD/'completion.json',TEMP/'completion.json',TEMP/'audits/independent-verification.json',
              TEMP/'audits/extended-quality.json',TEMP/'manifests/contract.json',
              ROOT/'eval/post_associated_temperature_calibration/run.py']:
        historical[rel(p)]=sha(p)
    for p,h in historical.items():require(sha(ROOT/p)==h,'Historical input changed')
    def bind(p,kind,rid=None,expected=None,**kw):
        h=sha(p);require(expected is None or h==expected,'Source binding mismatch')
        sources[rel(p)]=dict(kind=kind,role_id=rid,sha256=h,**kw)
    for oldr in old['roles']:
        r=dict(oldr);rid=r['id'];roles.append(r);r['frozen_G']={}
        for field,kind in [('classification','classification'),('base','base')]:
            side=read((ROOT/r[field]).with_suffix('.json'));require(side['role_id']==rid,'Tensor identity')
            bind(ROOT/r[field],kind,rid,side['sha256'])
        for field,kind in [('query','query-post'),('labels','query-label')]:
            info=old['sources'][r[field]]
            # Reuse sealed bindings; no deferred bytes decoded here.
            sources[r[field]]=dict(info,kind=kind)
        for arm in ['OR-R','OR-G','OR-P']:
            for seed in SEEDS:
                p=OLD/'frozen-G'/rid/f'{arm[-1]}-seed{seed}.pt';meta=read(p.with_suffix('.json'))
                require(meta['role_id']==rid and meta['arm']==arm[-1] and meta['source']==r['g_assets'][f'{arm[-1]}-{seed}'],'G lineage')
                bind(p,'g-'+arm[-1],rid,meta['sha256']);r['frozen_G'][f'{arm}-{seed}']=rel(p)
        root=PREP/'packages'/rid;pack={}
        for filename,kind in [('source-post.parquet','source-post'),('source-pre.parquet','source-pre'),('C-post.parquet','C-post')]:
            p=root/filename;info=ct[rel(p)];require(info['scope']['id']==rid and info['kind']==kind,'Metadata role')
            bind(p,kind,rid,info['sha256']);pack[kind]=pd.read_parquet(p)
        ancestors={}
        for kind,p in [('CT1',PREP/'slots'/rid/'CT1.pt'),('CT2',PREP/'slots'/rid/'CT2.pt'),
                       ('JA1',JA/'slots'/rid/f'JA1-eta{r["eta"]:g}.pt')]:
            side=read(p.with_suffix('.json'));require(side['role_id']==rid,'Ancestor role')
            bind(p,kind,rid,side['sha256']);ancestors[kind]=torch.load(p,map_location=device(),weights_only=True)
        s=torch.load(ROOT/r['classification'],map_location=device(),weights_only=True)
        m=torch.load(ROOT/r['base'],map_location=device(),weights_only=True)
        require(s['x'].shape==(480,96) and s['real_x'].shape==(192,96),'Slot shapes')
        require(torch.equal(s['mu'],m['mu']) and torch.equal(s['scale'],m['scale']),'Coordinate mismatch')
        require(abs(float(s['mass'].sum())-1)<1e-12 and float((F.one_hot(s['y'],6).double().T@s['mass']-1/6).abs().max())<1e-12,'Slot/class weights')
        post,pre,cp=pack['source-post'],pack['source-pre'],pack['C-post']
        require(len(post)==len(pre)==144 and len(cp)==48 and 'visit_id' not in pre,'Frozen anonymous source pre')
        require(set(post.protocol)<=set(r['sources']) and set(pre.protocol)<=set(r['sources']) and set(cp.protocol)=={r['calibration']},'Deployment permission')
        require(set(cp.content_id)<=set(r['C_contents']) and not set(cp.content_id)&set(r['U_contents']),'C permission')
        for p in [post,pre,cp]:require(set(p.content_id)<=set(r['train_contents']) and not set(p.content_id)&set(r['validation_contents']),'Training content permission')
        standard=(tensor(post[HIST])-s['mu'])/s['scale'];cstandard=(tensor(cp[HIST])-s['mu'])/s['scale']
        require(torch.equal(s['x'][:144],standard) and torch.equal(s['x'][432:],cstandard),'Post order')
        require(torch.equal(s['x'][144:288],ancestors['CT2']['x'][144:288]),'CORAL order')
        require(torch.equal((tensor(pre[HIST])-s['mu'])/s['scale'],ancestors['CT1']['x'][144:288]),'Anonymous pre order')
        require(float((s['x'][288:432]-ancestors['JA1']['x'][144:288]).abs().max())<1e-12,'Mapped slot lineage')
        require(torch.equal(s['real_x'],torch.cat([standard,cstandard])),'192 real visits')
        index={v:i for i,v in enumerate(LABELS)}
        for start,p,view in [(0,post,'source-real-post'),(144,post,'source-CORAL-post'),(288,pre,'anonymous-pre-mapped'),(432,cp,'C-real-post')]:
            require(np.array_equal(s['y'][start:start+len(p)].cpu().numpy(),p.label_id.map(index).to_numpy()),'Slot labels order')
            for j,row in enumerate(p.itertuples(index=False)):
                i=start+j;anonymous=view=='anonymous-pre-mapped'
                rows.append(dict(role_id=rid,role_target=r['target'],query_deployment=r['calibration'],row_index=i,
                    row_key=hashlib.sha256(f'{rid}:{sources[r["classification"]]["sha256"]}:{i}'.encode()).hexdigest(),
                    input_view=view,slot_type=view,label=int(s['y'][i]),sample_mass=float(s['mass'][i]),
                    content_key=row.content_id,protocol=row.protocol,
                    source_package=rel(root/('source-pre.parquet' if anonymous else 'C-post.parquet' if start==432 else 'source-post.parquet')),
                    source_package_row_index=j,parent_visit_key=None if anonymous else row.visit_id,
                    parent_identity_status='anonymous_by_original_contract' if anonymous else 'registered_visit',
                    input_row_sha256=hashlib.sha256(s['x'][i].cpu().numpy().tobytes()).hexdigest()))
    for kind,p in [('old-prediction',OLD/'predictions/visits.parquet'),('old-prediction',OLD/'predictions/base.parquet'),
                   ('old-temperature',TEMP/'fits/temperatures.json'),('old-calibrated',TEMP/'predictions/visits.parquet'),
                   ('old-score',TEMP/'scores/summary.json')]:bind(p,kind)
    c=dict(version='OR1-v1',authorization='User authorized sync and OR1 execution on 2026-10-15',
           implementation_source='User pasted specification; ZIP unavailable, not executed or claimed reviewed',
           plan_sha256=sha(PLAN),roles=roles,sources=sources,historical=historical,
           arms=ARMS,seeds=SEEDS,eta=.01,tau=1e-12,physical_fit_cap=132,endpoints=180,
           max_iter=2000,max_eval=10000,gradient_gate=1e-5,replay_gate=1e-10,fit_seconds_cap=3600,
           H_forbidden=True,actual_U_forbidden=True,teacher_G_updates_forbidden=True,
           old_temperature_code_sha256=sha(ROOT/'eval/post_associated_temperature_calibration/run.py'),
           primary='Same-opportunity content-cross-fitted calibrated metrics; raw metrics descriptive geometry',
           CE_margin=.002,C_overall_F1_cost=.01,C_deployment_F1_cost=.02)
    write(OUT/'manifests/contract.json',c);write(OUT/'manifests/contract-seal.json',dict(sha256=sha(OUT/'manifests/contract.json')))
    save(OUT/'manifests/training-row-ledger.parquet',pd.DataFrame(rows));require(len(rows)==5760,'Row ledger size')
    seal(OUT/'manifests/code.json',list(CODE.glob('*.py')))
    seal(OUT/'manifests/provenance-complete.json',[OUT/'manifests/training-row-ledger.parquet',OUT/'manifests/contract.json'])
    mutable(OUT/'ledger.json',dict(attempted_fits=0,accepted_fits=0,fit_seconds=0.,G_fits=0,teacher_fits=0,base_fits=0,temperature_fits=0))
    write(OUT/'stages/register.json',dict(passed=True,roles=12,rows=5760,anonymous_parent_rows=1728,
          numeric_rows_rebuilt=0,query_decoded_rows=0,H_reads=0,actual_U_reads=0))
    progress('register_complete',roles=12,physical_fits=132)
