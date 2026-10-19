"""Trusted role-filtered integer histograms; separate P, G and E capability packages."""
from common import *
import pyarrow.dataset as ds

def weights(meta,r):
    y=meta.label_id.map(dict(zip(LABELS,range(6)))).to_numpy(int);src=meta.protocol.isin(r['sources']).to_numpy()
    w=np.zeros(len(meta));groups=[src&np.isin(y,r['missing']),src&~np.isin(y,r['missing']),~src]
    for mask in groups:
        for yy in sorted(set(y[mask])):
            by=mask&(y==yy);ps=sorted(meta.loc[by,'protocol'].unique())
            for proto in ps:
                bp=by&meta.protocol.eq(proto).to_numpy();us=sorted(meta.loc[bp,'content_id'].unique())
                for u in us:
                    ix=bp&meta.content_id.eq(u).to_numpy();require(ix.sum()==4,'Incomplete repetition group')
                    w[ix]=1/(3*len(set(y[mask]))*len(ps)*len(us)*4)
    require(max(abs(w[m].sum()-1/3) for m in groups)<1e-12,'Three resource masses')
    require(abs(w.sum()-1)<1e-12 and max(abs(w[y==yy].sum()-1/6) for yy in range(6))<1e-12,'Class masses')
    return y,w

def build(r):
    rid=r['id'];dest=OUT/'packages'/rid
    marker=dest/'complete.json'
    if marker.exists():verifyseal(marker);return read(dest/'audit.json')
    post=pd.concat([external(PREP/'packages'/rid/'source-post.parquet',rid,'source-post'),external(PREP/'packages'/rid/'C-post.parquet',rid,'C-post')],ignore_index=True)
    prebag=external(PREP/'packages'/rid/'source-pre.parquet',rid,'source-pre')
    b0=external(ASSOC/'base-models'/rid/'P-small.pt',rid,'base');inner=r['inner'] is not None;n=192 if inner else 352
    require(len(post)==n and post.visit_id.is_unique,'Real post identities')
    require(set(post.content_id)<=set(r['train_contents']) and not set(post.content_id)&set(r['validation_contents']),'Post outside training')
    require(not ((post.protocol==r['calibration'])&post.content_id.isin(r['U_contents'])).any(),'Forbidden U post')
    allowed=((ds.field('protocol').isin(r['sources']))&ds.field('content_id').isin(r['train_contents']))|((ds.field('protocol')==r['calibration'])&ds.field('content_id').isin(r['C_contents']))
    cols=['session_id','protocol','content_id','label_id','fold','pair_id','repetition']+[s+'_'+f for s in ['pre','post'] for f in FEATURES]
    raw=ds.dataset(NATIVE,format='parquet').to_table(columns=cols,filter=allowed).to_pandas()
    READS.append(dict(path=rel(NATIVE),role_id=rid,kind='trusted-filtered-native',rows=len(raw),sha256=contract()['files'][rel(NATIVE)]['sha256'],
        filter=dict(sources=r['sources'],train_contents=r['train_contents'],calibration=r['calibration'],C_contents=r['C_contents'])))
    require(raw.pair_id.is_unique and raw.repetition.isin([1,2,3,4]).all(),'Native pair/repetition')
    require(not set(raw.content_id)&set(r['validation_contents']) and not ((raw.protocol==r['calibration'])&raw.content_id.isin(r['U_contents'])).any(),'Native permission failure')
    if inner:require(not raw.protocol.eq(r['target']).any(),'Actual target numeric rows in inner')
    raw['visit_id']=raw.session_id.map(lambda x:hashlib.sha256(('business-query-v1:'+x).encode()).hexdigest())
    meta=raw[['visit_id','session_id','protocol','content_id','label_id','fold','repetition']].drop_duplicates()
    require(len(meta)==n and meta.visit_id.is_unique and set(meta.visit_id)==set(post.visit_id),'Authoritative parents differ')
    meta=meta.set_index('visit_id').loc[post.visit_id].reset_index()
    for k in ['protocol','content_id','label_id','fold']:require(meta[k].tolist()==post[k].tolist(),'Metadata association mismatch')
    start=time.perf_counter();ix=raw.visit_id.map({u:i for i,u in enumerate(post.visit_id)}).to_numpy(int)
    den=np.bincount(ix,minlength=n);require((den>0).all(),'Empty registered access')
    counts={s:np.zeros((n,96),dtype=np.int64) for s in ['pre','post']}
    pos=0
    for j,f in enumerate(FEATURES):
        edges=[1,256,1024,4096,16384,65536,262144,1048576] if j<4 else [1,2,3,4,8,16,32,64,128]
        for side in ['pre','post']:
            v=raw[side+'_'+f].to_numpy();require(np.isfinite(v).all() and (v>=0).all() and (v==np.floor(v)).all(),'Noninteger native feature')
            bi=np.searchsorted(edges,v,side='right')
            counts[side][:,pos:pos+SIZES[j]]=np.bincount(ix*SIZES[j]+bi,minlength=n*SIZES[j]).reshape(n,SIZES[j])
        pos+=SIZES[j]
    freq={s:v/den[:,None] for s,v in counts.items()}
    posterr=float(np.max(abs(freq['post']-post[HIST].to_numpy())))
    require(posterr<=1e-14,'Raw post histogram replay')
    ns=len(prebag);ap=meta[['protocol','content_id','label_id']].iloc[:ns].copy();ap[HIST]=freq['pre'][:ns]
    keys=['protocol','content_id','label_id',*HIST]
    preerr=float(np.max(abs(ap.sort_values(keys)[HIST].to_numpy()-prebag.sort_values(keys)[HIST].to_numpy())))
    require(preerr<=1e-14,'Raw pre anonymous multiset replay')
    y,w=weights(meta,r);a=tensor(freq['pre']);b=tensor(freq['post']);yt=tensor(y,torch.long);wt=tensor(w)
    # Conditional IDs contain no repetition identity and never enter inference.
    condkeys=[(p,yy) for p in r['sources']+[r['calibration']] for yy in range(6) if p!=r['calibration'] or yy not in r['missing']]
    ci=np.array([condkeys.index((p,int(yy))) for p,yy in zip(meta.protocol,y)]);cit=tensor(ci,torch.long)
    require(len(condkeys)==(16 if inner else 22) and np.unique(np.bincount(ci)).tolist()==[12 if inner else 16],'Conditional support')
    gi,_=pd.factorize([hashlib.sha256(('deproxy-group:'+p+':'+u).encode()).hexdigest() for p,u in zip(meta.protocol,meta.content_id)],sort=True)
    require(pd.Series(gi).value_counts().eq(4).all(),'Four-repeat anonymous groups')
    group=tensor(gi,torch.long);enc=F.one_hot(group,int(group.max())+1).double();centers=((enc.T@a)/4)[group]
    mu=a.mean(0);sd=a.std(0,unbiased=False);scale=torch.where(sd<=1e-12,torch.ones_like(sd),sd)
    C=F.one_hot(cit,len(condkeys)).double().T;pi=C@wt;cw=C*wt[None]/pi[:,None]
    mom1=cw@a;mom2=torch.einsum('cn,ni,nj->cij',cw,a,a)
    gap=tensor([(condkeys.index((r['calibration'],yy)),condkeys.index((p,yy))) for p in r['sources'] for yy in range(6) if yy not in r['missing']],torch.long)
    # Independent random order on each side; permutations remain trusted-only.
    seed=int(hashlib.sha256(rid.encode()).hexdigest()[:8],16)
    pa=np.random.default_rng(seed+103).permutation(n);pb=np.random.default_rng(seed+209).permutation(n)
    ia=tensor(pa,torch.long);ib=tensor(pb,torch.long)
    require(not np.array_equal(pa,pb),'Independent group permutations')
    for side in ['pre','post']:
        for j in range(10):require(np.all(counts[side][:,block(j)].sum(1)==den),'Integer block denominator')
    torch.cuda.synchronize();debit('raw-package-numeric',time.perf_counter()-start,contexts=1,role_id=rid)
    common=dict(role_id=rid)
    put(dest/'paired/train.pt',dict(a=a,b=b,y=yt,w=wt,ci=cit),capability='P',**common)
    put(dest/'group/pre.pt',dict(a=a[ia],y=yt[ia],w=wt[ia],ci=cit[ia],group=group[ia]),capability='G',**common)
    put(dest/'group/post.pt',dict(b=b[ib],y=yt[ib],w=wt[ib],ci=cit[ib],group=group[ib]),capability='G',**common)
    put(dest/'group/targets.pt',dict(target=centers[ib],mom1=mom1,mom2=mom2,pi=pi,gap=gap),capability='G',**common)
    put(dest/'paired/moments.pt',dict(mom1=mom1,mom2=mom2,pi=pi,gap=gap),capability='P',**common)
    put(dest/'post/train.pt',dict(b=b,y=yt,w=wt),capability='E',**common)
    put(dest/'scales/pre.pt',dict(mu=mu,scale=scale,low_variance=sd<=1e-12),capability='pre',**common)
    put(dest/'scales/post.pt',dict(mu=b0['mu'],scale=b0['scale']),capability='post',**common)
    put(dest/'base.pt',b0,capability='shared',**common)
    put(OUT/'trusted'/rid/'integer-counts.pt',dict(pre_counts=torch.from_numpy(counts['pre']),post_counts=torch.from_numpy(counts['post']),denominator=torch.from_numpy(den)),capability='trusted',**common)
    meta['post_row']=np.arange(n);meta['pre_permutation_inverse']=np.argsort(pa);meta['post_permutation_inverse']=np.argsort(pb)
    meta['mass']=w;meta['condition_index']=ci;meta['group']=gi
    save(OUT/'trusted'/rid/'paired-train-ledger.parquet',meta)
    audit=dict(role_id=rid,visits=n,contents=meta.content_id.nunique(),native_rows=len(raw),post_replay_error=posterr,
        pre_multiset_error=preerr,groups=int(group.max())+1,conditions=len(condkeys),pair_rule='session_id -> business-query-v1 SHA256 -> registered training visit_id',
        target_U_numeric_rows=0,H_numeric_rows=0,group_identity_exported=False,pre_source='integer native feature counts, not inverse standardized teacher',
        class_mass=[float(w[y==yy].sum()) for yy in range(6)],numeric_seconds=time.perf_counter()-start)
    immutable(dest/'audit.json',audit);seal(marker,list(dest.rglob('*.pt'))+[dest/'audit.json'],passed=True,role_id=rid)
    return audit

def prepare():
    configure('trusted');hashes=code_seal('P0');rows=[]
    require(sha(NATIVE)==contract()['files'][rel(NATIVE)]['sha256'],'Native changed')
    started=time.perf_counter()
    try:
        for i,r in enumerate(roles()):
            rows.append(build(r))
            if (i+1)%20==0:flush_reads('P0');progress('P0_raw_packages',contexts=i+1,total=780)
        save(OUT/'manifests/raw-package-audit.parquet',pd.DataFrame(rows))
        seal(OUT/'manifests/P0-complete.json',[OUT/'packages'/r['id']/'complete.json' for r in roles()]+[OUT/'manifests/raw-package-audit.parquet']+
            list((OUT/'trusted').rglob('*.pt'))+list((OUT/'trusted').rglob('*.parquet')),
            passed=True,contexts=780,raw_counts_authoritative=True,H_pre_reads=0,target_U_numeric_rows=0)
        immutable(OUT/'manifests/training-authorization.json',dict(P0_passed=True,allowed_phase='P1 only until engineering/budget passes',contract_sha256=sha(OUT/'manifests/contract.json')))
        progress('P0_complete',contexts=780,seconds=time.perf_counter()-started,max_post_error=max(x['post_replay_error'] for x in rows))
    except BaseException as e:failure('P0',e);raise
    finally:flush_reads('P0');codecheck(hashes)
