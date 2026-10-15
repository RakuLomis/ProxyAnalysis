"""Source feedback and final weighted caches, train-only frozen coordinates."""
from common import *

def build(r,kind):
    arm='D-G' if kind=='G' else 'D-P';purpose='source-train' if r['inner'] is not None else 'final-train'
    root=PREP/'packages'/r['id'];source=package(root/'source-post.parquet',purpose,arm,r)
    pre=package(root/'source-pre.parquet',purpose,arm,r);cp=package(root/'C-post.parquet',purpose,arm,r)
    require(source.groupby(['protocol','content_id','label_id']).size().equals(pre.groupby(['protocol','content_id','label_id']).size()),'Independent side bags')
    s=artifact(PREP/'slots'/r['id']/'CT2.pt','shared',arm,r);raw=artifact(PREP/'slots'/r['id']/'CT1.pt','shared',arm,r)
    mu,scale=scaler(torch.cat([tensor(source[HIST]),tensor(cp[HIST])]))
    require(torch.equal(mu,s['mu']) and torch.equal(scale,s['scale']),'Frozen scaler replay')
    n=len(source);a=(tensor(pre[HIST])-mu)/scale
    require(torch.equal(a,raw['x'][n:2*n]),'Independent pre ordering')
    if r['inner'] is not None:mp=JA/'maps'/r['id']/f'JA{1 if kind=="P" else 2}-eta{r["eta"]:g}.pt'
    else:mp=ROOT/r['reuse_maps'][kind]
    model=artifact(mp,kind,arm,r);require(torch.equal(mu,model['mu']) and torch.equal(scale,model['scale']),'Map coordinates')
    b0=a@model['matrix'].T+model['bias']
    v=dict(mu=mu,scale=scale,main_x=s['x'][:n],main_y=s['y'][:n],main_mass=s['mass'][:n],
           S_x=s['x'][n:2*n],S_y=s['y'][n:2*n],S_mass=s['mass'][n:2*n],
           pre_x=a,pre_y=raw['y'][n:2*n],pre_mass=raw['mass'][n:2*n],mapped_x=b0,
           C_x=s['x'][2*n:],C_y=s['y'][2*n:],C_mass=s['mass'][2*n:])
    amp,u,_,rec=production();slot=u.pack(v,arm,torch.ones(10,device=device(),dtype=torch.float64))
    require(len(slot['x'])==(480 if r['inner'] is not None else 928),'Slot row counts')
    require(abs(float(slot['mass'].sum())-1)<1e-12 and float((weighted(slot['y'],slot['mass'],6)-1/6).abs().max())<1e-12,'Class mass replay')
    require(abs(float(v['pre_mass'].sum())*.1-1/30)<1e-12,'Small mapped total mass')
    if r['inner'] is not None:
        old=artifact(JA/'slots'/r['id']/f'JA{1 if kind=="P" else 2}-eta{r["eta"]:g}.pt',kind,arm,r)
        require(float((b0-old['x'][n:2*n]).abs().max())<1e-12 and torch.equal(v['pre_y'],old['y'][n:2*n]) and torch.equal(v['pre_mass'],old['mass'][n:2*n]),'q=1 legacy mapping/labels/mass')
        query=package(root/'query.parquet','source-feedback',arm,r);labels=package(root/'labels.parquet','source-feedback',arm,r)
        lookup=labels.set_index('visit_id');require(set(query.visit_id)==set(lookup.index),'Source query-label membership')
        yy=truths(lookup.loc[query.visit_id].reset_index());ix=np.isin(yy,r['missing']);require(ix.sum()==8,'Uncovered feedback visits')
        v.update(query_x=((tensor(query[HIST])-mu)/scale)[tensor(ix,torch.bool)],query_y=tensor(yy[ix],torch.long),query_mass=torch.full((8,),1/8,device=device(),dtype=torch.float64))
    # At q=1 only, own train matrix; no whole-range bound or finite unroll.
    aug=torch.cat([slot['x'],torch.ones_like(slot['x'][:,:1])],1)
    h=aug.T@(aug*slot['mass'][:,None])/6+torch.diag(torch.cat([torch.full((96,),.001*(1+r['t']),device=device(),dtype=torch.float64),tensor([0.])]))
    L=torch.linalg.cholesky(h);inv=torch.linalg.solve_triangular(L,torch.eye(97,device=device(),dtype=torch.float64),upper=False)
    return v,inv

def run():
    with stage('episodes'):
        rows=[]
        for i,r in enumerate(contract()['inner_roles']+contract()['roles']):
            for kind in ['P','G']:
                v,inv=build(r,kind)
                put(dict(view=v,inv=inv),OUT/'tasks'/r['id']/(kind+'.pt'),role_id=r['id'],kind=kind,train_only=True,q_coordinate_frozen_at_one=True,original_W_L2=True,rows=480 if r['inner'] is not None else 928)
                rows.append(dict(role_id=r['id'],kind=kind,inner=r['inner'],rows=480 if r['inner'] is not None else 928,query_rows=8 if r['inner'] is not None else 0,source_sides_row_matched=False))
            if (i+1)%60==0:progress('training_caches_prepared',roles=i+1,total=780)
        # Trusted compatibility auditor may read the sealed combined old view; G worker never does.
        maxerr=0.
        for r in contract()['roles']:
            old=artifact(ROOT/r['reuse_views'],'shared','D-P',r)
            for kind in ['P','G']:
                v=own(OUT/'tasks'/r['id']/(kind+'.pt'))['view']
                err=float((v['mapped_x']-old[kind+'_x']).abs().max());maxerr=max(maxerr,err)
                require(err<1e-12 and torch.equal(v['pre_y'],old[kind+'_y']) and torch.equal(v['pre_mass'],old[kind+'_mass']),'Outer q=1 old small view replay')
                for key in ['main_x','main_y','main_mass','S_x','S_y','S_mass','C_x','C_y','C_mass','mu','scale']:require(torch.equal(v[key],old[key]),'Final source/C replay')
        save(pd.DataFrame(rows),OUT/'manifests/episode-index.parquet')
        write(OUT/'audits/q-one-replay.json',dict(passed=True,source_tasks=1440,final_caches=120,source_maps_reused=1440,new_maps=0,outer_mapped_error=maxerr,H_reads=0,U_reads=0))

if __name__=='__main__':run()
