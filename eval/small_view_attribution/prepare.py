"""Trusted package producer strips all C identity before marginal worker."""
from common import *
import objectives as O
import marginal as M

def pack(r,v):
    data={};seeds={}
    for side in ['pre','post']:
        d=package(ROOT/r['C_group_'+side],'marginal-pack');require(len(d)==64,'C member count')
        seed=int.from_bytes(hashlib.sha256(('SA20261010:'+r['id']+':'+side).encode()).digest()[:8],'little')
        ix=np.random.default_rng(seed).permutation(64)
        data[side]=(tensor(d[HIST].iloc[ix])-v['mu'])/v['scale'];data[side+'_mass']=tensor(d.fit_mass.iloc[ix])
        seeds[side]=seed
    M.schema(data);put(data,anonymous_path(r),role_id=r['id'],independent_permutation_seeds=seeds,
                      exact_identity_read=False,content_identity_in_worker=False,C_rows_per_side=64)

def build(r):
    v=artifact(oldviews(r));pre=package(rolepath(r)/'source-pre.parquet','train')
    require(len(pre)==288 and all(pre.groupby(['protocol','content_id','label_id']).size()==4),'Source multiplicities')
    raw=(tensor(pre[HIST])-v['mu'])/v['scale'];y=tensor(truths(pre),torch.long)
    require(torch.equal(y,v['P_y']) and torch.equal(v['P_mass'],v['G_mass']),'Source independent row order')
    if not anonymous_path(r).exists():pack(r,v)
    if not transformpath(r).exists():
        m,log=M.fit(artifact(anonymous_path(r)))
        put(m,transformpath(r),role_id=r['id'],mapping=log,input_sha256=sha(anonymous_path(r)))
    m=artifact(transformpath(r))
    views={'RawPre-small':(raw,y,v['P_mass']),
           'RawPost-small':(v['main_x'],v['main_y'],v['main_mass']),
           'Marginal-small':(M.apply(m,raw),y,v['P_mass'])}
    for a,(x,yy,mm) in views.items():
        if not newslot(r,a).exists():
            s=O.slot(v,x,yy,mm);require(len(s['x'])==928,'Weighted row count')
            put(s,newslot(r,a),role_id=r['id'],arm=a,beta=.1,source_rows=288,C_rows=64,
                class_mass=weighted(s['y'],s['mass'],6).cpu().tolist(),
                target_U_read=False,test_pre_read=False,additional_real_visits=0)

def run(pilot):
    name='prepare_pilot' if pilot else 'prepare_remaining'
    with stage(name):
        c=contract();rs=[r for r in c['roles'] if (r['id'] in c['pilot_roles'])==pilot]
        if not pilot:require(read(OUT/'pilot/promotion.json')['passed'],'Pilot not passed')
        for i,r in enumerate(rs):
            build(r)
            if (i+1)%12==0:progress(name,roles=i+1,total=len(rs))
        require(len(rs)==(12 if pilot else 48),'Prepare count')

if __name__=='__main__':run(sys.argv[1]=='pilot')
