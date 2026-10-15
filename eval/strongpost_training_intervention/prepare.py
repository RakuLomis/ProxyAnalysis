"""TI06--TI11: weighted bags, never row-match independently ordered source sides."""
from common import *

def mapping(r,arm,mu,scale):
    old=oldmap(r,arm,r['eta'])
    if old.exists():
        m=artifact(old);info=read(old.with_suffix('.json'))
        require(info['mapping']['accepted'],'Map not accepted')
        require(torch.equal(mu,m['mu']) and torch.equal(scale,m['scale']),'Mapping coordinates')
        return m,rel(old)
    require(arm=='JA1' and r['inner'] is None,'Only registered missing P maps may be fitted')
    p=OUT/'mappings'/r['id']/f'JA1-eta{r["eta"]:g}.pt'
    if p.exists():return artifact(p),rel(p)
    d=package(ROOT/r['C_paired'],'paired-map')
    x=(tensor(d[['pre_'+h for h in HIST]])-mu)/scale
    y=(tensor(d[['post_'+h for h in HIST]])-mu)/scale
    m,log=affine().fit(x,y,tensor(d.fit_mass),r['eta'],'JA1')
    m.update(mu=mu,scale=scale)
    put(m,p,mapping=log,role_id=r['id'],fit_package=r['C_paired'],target_U_read=False)
    return m,rel(p)

def build(r):
    if viewpath(r).exists():return artifact(viewpath(r))
    source=package(rolepath(r)/'source-post.parquet','train')
    pre=package(rolepath(r)/'source-pre.parquet','train')
    cp=package(rolepath(r)/'C-post.parquet','train')
    columns=['protocol','content_id','label_id']
    left=source.groupby(columns).size();right=pre.groupby(columns).size()
    require(left.equals(right),'Source side member multiplicities differ')
    require(all(left==4),'Four visits per content and source deployment')
    oldS=artifact(PREP/'slots'/r['id']/'CT2.pt')
    oldP=artifact(PREP/'slots'/r['id']/'CT1.pt')
    mu,scale=scaler(torch.cat([tensor(source[HIST]),tensor(cp[HIST])]))
    require(torch.equal(oldS['mu'],mu) and torch.equal(oldS['scale'],scale),'Frozen scaler mismatch')
    mS,yS=weights().loss_weights(source,cp,r['missing'])
    mP,yP=weights().loss_weights(pre,cp,r['missing'])
    n=len(source);c=len(cp);z=(tensor(source[HIST])-mu)/scale;zc=(tensor(cp[HIST])-mu)/scale
    coralmetadata=cp.copy();coralmetadata[HIST]=zc.cpu().numpy()
    S,parameters=weights().coral(z,source,coralmetadata,r['missing'])
    require(residual(torch.cat([z,S,zc]),oldS['x'])<1e-12,'CORAL replay')
    require(torch.equal(mS,oldS['mass']) and torch.equal(yS,oldS['y']),'S mass/label replay')
    masspre=mP[n:2*n];yp=tensor(truths(pre),torch.long)
    require(torch.equal(oldP['y'][n:2*n],yp) and torch.equal(oldP['mass'][n:2*n],masspre),'Pre row weights')
    require(torch.equal(oldP['mu'],mu) and torch.equal(oldP['scale'],scale),'Pre coordinate mismatch')
    px=(tensor(pre[HIST])-mu)/scale
    v={'mu':mu,'scale':scale,'main_x':z,'main_y':yS[:n],'main_mass':mS[:n],
       'C_x':zc,'C_y':yS[2*n:],'C_mass':mS[2*n:],
       'S_x':S,'S_y':yS[n:2*n],'S_mass':mS[n:2*n],
       'P_y':yp,'P_mass':masspre,'G_y':yp,'G_mass':masspre}
    paths={}
    for arm,short in [('JA1','P'),('JA2','G')]:
        m,path=mapping(r,arm,mu,scale);paths[short]=path
        v[short+'_x']=affine().apply(m,px)
        old=oldslot(r,arm,r['eta'])
        if old.exists():
            prior=artifact(old)
            require(residual(v[short+'_x'],prior['x'][n:2*n])<1e-12,'Mapped auxiliary replay')
            require(torch.equal(prior['mass'][n:2*n],masspre) and torch.equal(prior['y'][n:2*n],yp),'Aux weights replay')
    meta={'role_id':r['id'],'source_visits':n,'C_visits':c,'mappings':paths,'eta':r['eta'],'t':r['t'],
          'source_membership':'hash-bound previously verified independent-order source bags; content/deployment/class multiplicities replayed',
          'source_sides_row_matched':False,'target_U_read':False,'test_pre_read':False,
          'source_post_package':rel(rolepath(r)/'source-post.parquet'),
          'source_pre_package':rel(rolepath(r)/'source-pre.parquet')}
    put(v,viewpath(r),**meta);return v

def run():
    with stage('prepare'):
        c=contract();rows=[]
        for i,r in enumerate(c['roles']+c['pilot_roles']):
            build(r);rows.append(read(viewpath(r).with_suffix('.json')))
            if (i+1)%12==0:progress('prepare_views',roles=i+1,total=72)
        require(len(list((OUT/'mappings').rglob('*.pt')))==11,'Unexpected added mapping count')
        write(OUT/'manifests/views-complete.json',{'roles':72,'new_mapping_fits':11,
                    'metadata':rows,'target_U_reads':0,'test_pre_reads':0})

if __name__=='__main__':run()
