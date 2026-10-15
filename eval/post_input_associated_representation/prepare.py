"""Trusted packer applies role filter before decoding native numeric arrays."""
from common import *

def build(r):
    p=taskpath(r);source=oldpackage(PREP/'packages'/r['id']/'source-post.parquet',r,'prepare')
    prebag=oldpackage(PREP/'packages'/r['id']/'source-pre.parquet',r,'prepare')
    cp=oldpackage(PREP/'packages'/r['id']/'C-post.parquet',r,'prepare')
    v=old(ROOT/r['old_task'],'train-only-cache')['view']
    forbidden={'query_x','query_y','query_mass'};v={k:x for k,x in v.items() if k not in forbidden}
    require(len(source)==(144 if r['inner'] is not None else 288),'Source count')
    post=pd.concat([source,cp],ignore_index=True);n=len(source)
    require(post.visit_id.is_unique,'Training visit IDs unique')
    allow=((ds.field('protocol').isin(r['sources'])) & ds.field('content_id').isin(r['train_contents'])) | (
           (ds.field('protocol')==r['calibration']) & ds.field('content_id').isin(r['C_contents']))
    cols=['session_id','protocol','content_id','label_id','fold','pair_id','repetition',
          *['pre_'+f for f in FEATURES],*['post_'+f for f in FEATURES]]
    require(sha(NATIVE)==contract()['bindings'][rel(NATIVE)],'Native changed')
    raw=ds.dataset(NATIVE,format='parquet').to_table(columns=cols,filter=allow).to_pandas()
    require(raw.pair_id.is_unique and raw.repetition.isin([1,2,3,4]).all(),'Native identities')
    require(set(raw.content_id)<=set(r['train_contents']) and not set(raw.content_id)&set(r['validation_contents']),'Read outside training')
    require(not ((raw.protocol==r['calibration']) & raw.content_id.isin(r['U_contents'])).any(),'Target U decoded')
    raw['visit_id']=raw.session_id.map(base.visitid)
    meta=raw[['visit_id','session_id','protocol','content_id','label_id','fold']].drop_duplicates()
    require(len(meta)==len(post) and meta.visit_id.is_unique and set(meta.visit_id)==set(post.visit_id),'Native/source parents differ')
    meta=meta.set_index('visit_id').loc[post.visit_id].reset_index()
    for key in ['protocol','content_id','label_id','fold']:require(meta[key].tolist()==post[key].tolist(),'Parent metadata mismatch')
    ids={u:i for i,u in enumerate(post.visit_id)};idx=tensor(raw.visit_id.map(ids),torch.long)
    counts=torch.bincount(idx,minlength=len(post)).to(torch.float64);a=torch.empty((len(post),96),device=device(),dtype=torch.float64)
    pos=0;posterr=0.
    for j,f in enumerate(FEATURES):
        for side in ['pre','post']:
            z=torch.zeros((len(post),size(j)),device=device(),dtype=torch.float64)
            z.index_put_((idx,bins(raw[side+'_'+f],j)),torch.ones_like(idx,dtype=torch.float64),accumulate=True)
            z=z/counts[:,None]
            if side=='pre':a[:,pos:pos+size(j)]=z
            else:posterr=max(posterr,float((z-tensor(post[HIST[pos:pos+size(j)]])).abs().max()))
        pos+=size(j)
    require(posterr<1e-14,'Authoritative post hist replay')
    precheck=meta[['protocol','content_id','label_id','fold']].iloc[:n].copy();precheck[HIST]=a[:n].cpu().numpy()
    keys=['protocol','content_id','label_id',*HIST]
    err=float(np.abs(precheck.sort_values(keys)[HIST].to_numpy()-prebag.sort_values(keys)[HIST].to_numpy()).max())
    require(err<1e-14,'Authoritative pre multiset differs; cannot guess identity')
    mu,scale=v['mu'],v['scale'];realx=torch.cat([v['main_x'],v['C_x']])
    require(torch.equal(realx,(tensor(post[HIST])-mu)/scale),'Post order/coordinates')
    y=torch.cat([v['main_y'],v['C_y']]);mass=torch.cat([2*v['main_mass'],v['C_mass']])
    require(abs(float(mass.sum())-1)<1e-12 and float((weighted(y,mass,6)-1/6).abs().max())<1e-12,'Teacher/real class mass')
    groups=[hashlib.sha256(('representation-group:'+pr+':'+u).encode()).hexdigest() for pr,u in zip(post.protocol,post.content_id)]
    gi,_=pd.factorize(groups,sort=True);group=tensor(gi,torch.long)
    require(pd.Series(gi).value_counts().eq(4).all(),'Four visits per group')
    s=dict(x=torch.cat([v['main_x'],v['S_x'],v['mapped_x'],v['C_x']]),
           y=torch.cat([v['main_y'],v['S_y'],v['pre_y'],v['C_y']]),
           mass=torch.cat([v['main_mass'],.9*v['S_mass'],.1*v['pre_mass'],v['C_mass']]),
           real_x=realx,real_mass=mass,mu=mu,scale=scale)
    require(len(s['x'])==(480 if r['inner'] is not None else 928),'Small rows')
    require(abs(float(s['mass'].sum())-1)<1e-12 and float((weighted(s['y'],s['mass'],6)-1/6).abs().max())<1e-12,'Small class mass')
    oldbase=old(ROOT/r['base_path'],'frozen-base')
    if r['inner'] is not None:
        require(torch.equal(oldbase['q'],torch.ones(10,device=device(),dtype=torch.float64)),'Wrong q cache')
        th=oldbase['theta_f'];m=dict(weight=th[:,:96],bias=th[:,96],mu=mu,scale=scale)
    else:m=oldbase
    require(torch.equal(mu,m['mu']) and torch.equal(scale,m['scale']),'Base scaler')
    audit=loss_audit(m,s,r['t'])
    put(s,p/'classification.pt',role_id=r['id'],kind='post-classification',rows=len(s['x']))
    put(dict(x=(a-mu)/scale,y=y,mass=mass),p/'teacher/fit.pt',role_id=r['id'],kind='pre-teacher',rows=len(a))
    put(dict(group=group),p/'trusted/groups.pt',role_id=r['id'],kind='trusted-group-builder')
    put(m,OUT/'base-models'/r['id']/'P-small.pt',role_id=r['id'],kind='base',source=r['base_path'],audit=audit)
    return dict(role_id=r['id'],inner=r['inner'],native_rows=len(raw),training_visits=len(a),post_hist_error=posterr,
                pre_multiset_error=err,original_gradient=audit['gradient_max'],source_pair_IDs=sha(NATIVE),
                pair_rule='native session_id -> SHA256 business-query-v1 -> registered post visit ID',
                H_pre_reads=0,H_post_reads=0,target_U_rows=0,registered_pair_ids_unique=True)

def run():
    with stage('P0_prepare'):
        rows=[]
        for i,r in enumerate(contract()['inner_roles']+contract()['roles']):
            rows.append(build(r))
            if (i+1)%30==0:progress('P0_training_pair_packages',roles=i+1,total=780)
        save(pd.DataFrame(rows),OUT/'manifests/pair-join-audit.parquet')
        seal(OUT/'packages/complete.json',list((OUT/'packages').rglob('*.pt'))+list((OUT/'base-models').rglob('*.pt')),roles=780,passed=True)
        write(OUT/'audits/P0-complete.json',dict(passed=True,roles=780,base_models_reused=780,new_fits=0,
              H_numeric_reads=0,actual_U_decoded_rows=0,pair_rule='registered parent identities, never source bag row order'))

if __name__=='__main__':run()
