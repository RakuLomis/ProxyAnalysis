"""Source-only pilot material, with independent P and G readers."""
from common import *
import recovery as R
import unroll as U

def build(r,arm):
    kind='G' if arm=='D-G' else 'P';root=PREP/'packages'/r['id']
    source=package(root/'source-post.parquet','train',arm,r)
    pre=package(root/'source-pre.parquet','train',arm,r)
    cp=package(root/'C-post.parquet','train',arm,r)
    require(source.groupby(['protocol','content_id','label_id']).size().equals(
            pre.groupby(['protocol','content_id','label_id']).size()),'Independent source bag membership')
    S=artifact(PREP/'slots'/r['id']/'CT2.pt',arm=arm)
    raw=artifact(PREP/'slots'/r['id']/'CT1.pt',arm=arm)
    mu,scale=scaler(torch.cat([tensor(source[HIST]),tensor(cp[HIST])]))
    require(torch.equal(S['mu'],mu) and torch.equal(S['scale'],scale),'Frozen scale replay')
    n=144
    a=(tensor(pre[HIST])-mu)/scale
    require(torch.equal(a,raw['x'][n:2*n]),'Source pre order replay')
    M=artifact(oldmap(r,kind),kind,arm)
    require(torch.equal(mu,M['mu']) and torch.equal(scale,M['scale']),'Map coordinate mismatch')
    b0=a@M['matrix'].T+M['bias']
    old=artifact(oldslot(r,kind),kind,arm)
    require(float((b0-old['x'][n:2*n]).abs().max())<1e-12,'q=1 legacy auxiliary replay')
    require(torch.equal(raw['y'][n:2*n],old['y'][n:2*n]) and
            torch.equal(raw['mass'][n:2*n],old['mass'][n:2*n]),'Source pre label/mass order')
    query=package(root/'query.parquet','meta-query',arm,r)
    labels=package(root/'labels.parquet','meta-labels',arm,r)
    lookup=labels.set_index('visit_id');require(set(query.visit_id)==set(lookup.index),'Meta query labels')
    yy=truths(lookup.loc[query.visit_id].reset_index())
    ix=np.isin(yy,r['missing']);require(ix.sum()==8,'Eight uncovered meta rows')
    qx=((tensor(query[HIST])-mu)/scale)[tensor(ix,torch.bool)]
    qy=tensor(yy[ix],torch.long)
    v=dict(mu=mu,scale=scale,main_x=S['x'][:n],main_y=S['y'][:n],main_mass=S['mass'][:n],
           S_x=S['x'][n:2*n],S_y=S['y'][n:2*n],S_mass=S['mass'][n:2*n],
           pre_x=a,pre_y=raw['y'][n:2*n],pre_mass=raw['mass'][n:2*n],mapped_x=b0,
           C_x=S['x'][2*n:],C_y=S['y'][2*n:],C_mass=S['mass'][2*n:],
           query_x=qx,query_y=qy,query_mass=torch.full((8,),1/8,device=device(),dtype=torch.float64))
    full=U.pack(v,kind,tensor(np.ones(10)))
    require(abs(float(full['mass'].sum())-1)<1e-12 and float((weighted(full['y'],full['mass'],6)-1/6).abs().max())<1e-12,'P-small class mass')
    require(abs(float(v['pre_mass'].sum())*.1-1/30)<1e-12,'Auxiliary ten percent meaning')
    require(float((full['x'][:n]-old['x'][:n]).abs().max())<1e-12,'Legacy main rows')
    v['conditioning']=U.initialize(v,r['t'])
    # Shared normalization is anonymous even in the paired reader.
    gb=package(ROOT/r['C_group_post'],'group-recovery',arm,r)
    gbz=(tensor(gb[HIST])-mu)/scale
    s,rawvar=R.anonymous_variance(gbz,tensor(gb.fit_mass))
    if kind=='P':
        paired=package(ROOT/r['C_paired'],'paired-recovery',arm,r)
        ca=(tensor(paired[['pre_'+h for h in HIST]])-mu)/scale
        cb=(tensor(paired[['post_'+h for h in HIST]])-mu)/scale
        w=tensor(paired.fit_mass);variance=None
        fixture={'a':ca,'b':cb,'w':w}
    else:
        gp=package(ROOT/r['C_group_pre'],'group-recovery',arm,r)
        ca=(tensor(gp[HIST])-mu)/scale
        gpz=gp.copy();gbc=gb.copy();gpz[HIST]=ca.cpu().numpy();gbc[HIST]=gbz.cpu().numpy()
        cb,variance=R.group_center_targets(gpz,gbc);w=tensor(gp.fit_mass)
        fixture={'a':ca,'b':cb,'w':w,'variance':variance,
                 'pre_tokens':list(gp.content_token),'post_tokens':list(gb.content_token),'post':gbz,
                 'post_mass':tensor(gb.fit_mass)}
    cb0=ca@M['matrix'].T+M['bias'];fixture['b0']=cb0
    coeff=R.coefficients(ca,cb0,cb,w,variance);coeff.update(s=s,raw_variance=rawvar)
    return v,coeff,fixture,old

def run():
    with stage('prepare'):
        rows=[];conditioning=[]
        for r in contract()['pilot_roles']:
            for arm in ['D-P','D-G']:
                v,c,fixture,old=build(r,arm)
                dst=OUT/'pilot/tasks'/r['id']/f'{arm}.pt'
                put({'view':v,'coeff':c,'fixture':fixture},dst,role_id=r['id'],arm=arm,
                    calibration=r['calibration'],actual_target_numeric_read=False,
                    recovery_fixture_is_in_sample=True,formal_C_OOF_coefficients=False)
                # q=1 exact loss-mass identity, independently evaluated at a fixed nonzero model.
                th=torch.arange(582,device=device(),dtype=torch.float64).reshape(6,97)/10000
                slot=U.pack(v,arm,tensor(np.ones(10)))
                wanted=U.original_objective(th,{'x':Sx(v),'y':Sy(v),'mass':Sm(v)},r['t'])
                aux=ce(th,v['mapped_x'],v['pre_y'],v['pre_mass'])-ce(th,v['S_x'],v['S_y'],v['S_mass'])
                err=abs(float(U.original_objective(th,slot,r['t'])-wanted-.1*aux))
                require(err<1e-10,'Original P-small objective replay')
                rows.append(dict(role_id=r['id'],arm=arm,rows=len(slot['x']),class_mass_error=float((weighted(slot['y'],slot['mass'],6)-1/6).abs().max()),
                                 objective_replay_error=err,source_sides_row_matched=False,meta_queries=8))
                conditioning.append(dict(role_id=r['id'],arm=arm,t=r['t'],step=float(v['conditioning']['step']),
                                         curvature_upper=float(v['conditioning']['curvature_upper']),shared_S_preconditioner=True))
            progress('source_pilot_prepared',roles=len(rows)//2,total=12)
        save(pd.DataFrame(rows),OUT/'audits/q-one-replay.parquet')
        save(pd.DataFrame(conditioning),OUT/'audits/conditioning-audit.parquet')

def Sx(v):return torch.cat([v['main_x'],v['S_x'],v['C_x']])
def Sy(v):return torch.cat([v['main_y'],v['S_y'],v['C_y']])
def Sm(v):return torch.cat([v['main_mass'],v['S_mass'],v['C_mass']])
def ce(th,x,y,m):
    z=x@th[:,:96].T+th[:,96]
    return (m*(torch.logsumexp(z,1)-z.gather(1,y[:,None]).squeeze(1))).sum()

if __name__=='__main__':run()
