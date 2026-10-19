"""Trusted train-only producer; group learner never reads paired assets."""
from common import *

def basis_for(base):
    w=base['weight']-base['weight'].mean(0,keepdim=True)
    u,s,vh=torch.linalg.svd(w,full_matrices=False); tol=max(1e-12,1e-10*float(s[0])); k=int((s>tol).sum())
    require(0<k<=5,'Effective decision rank'); q=vh[:k].T.contiguous()
    orth=float((q.T@q-torch.eye(k,device='cuda',dtype=torch.float64)).abs().max())
    err=float((w-w@q@q.T).abs().max())/max(1.,float(w.abs().max()))
    require(max(orth,err)<=1e-10,'Decision basis reconstruction')
    return q,dict(rank=k,singular_values=cpu(s).tolist(),threshold=tol,orthogonal_error=orth,weight_reconstruction_error=err)

def prep(r):
    rid=r['id']; p=OUT/'packages'/rid
    slot=external(ASSOC/'packages'/rid/'classification.pt',rid,'classification')
    base=external(ASSOC/'base-models'/rid/'P-small.pt',rid,'base')
    mp=external(ROOT/'outputs/joint-affine-transfer-20261007/run-01/maps'/rid/f'JA1-eta{r["eta"]:g}.pt',rid,'map')
    pre=external(PREP/'packages'/rid/'source-pre.parquet',rid,'source-pre')
    post=external(PREP/'packages'/rid/'source-post.parquet',rid,'source-post'); cp=external(PREP/'packages'/rid/'C-post.parquet',rid,'C-post')
    require(len(pre)==len(post)==144 and len(cp)==48 and len(slot['x'])==480,'Fixed source shape')
    mu,sc=base['mu'],base['scale']; sx=(tensor(pre[HIST])-mu)/sc; sy=tensor(yvalues(pre),torch.long)
    require(torch.equal(mu,slot['mu']) and torch.equal(sc,slot['scale']),'Base scale exact')
    require(torch.equal(slot['y'][288:432],sy),'Source anonymous row labels')
    require(torch.equal(slot['x'][:144],(tensor(post[HIST])-mu)/sc),'Real post exact')
    require(torch.equal(slot['x'][432:],(tensor(cp[HIST])-mu)/sc),'C post exact')
    require(float((sx@mp['matrix'].T+mp['bias']-slot['x'][288:432]).abs().max())<=1e-12,'Original forward map replay')
    w=slot['mass']; require(abs(float(w.sum())-1)<1e-12 and float((F.one_hot(slot['y'],6).double().T@w-1/6).abs().max())<1e-12,'CE class masses')
    masses=[float(w[a:b].sum()) for a,b in [(0,144),(144,288),(288,432),(432,480)]]
    require(np.allclose(masses,[1/3,.3,1/30,1/3],atol=1e-12,rtol=0),'Slot masses')
    q,bq=basis_for(base)
    require(torch.equal(slot['x'][288:432]+torch.zeros_like(sx),slot['x'][288:432]),'ZERO exact')
    # Original W/c equation at the frozen base, independent from solver.
    logits=slot['x']@base['weight'].T+base['bias']; prob=logits.softmax(1); ey=(prob-F.one_hot(slot['y'],6))*w[:,None]
    grad=max(float((ey.T@slot['x']+.001*(1+r['t'])*base['weight']).abs().max()),float(ey.sum(0).abs().max()))
    require(grad<=1e-5,'Frozen B0 objective incompatible')
    shared=dict(sx=sx,sy=sy,Q=q,M=mp['matrix'],bias=mp['bias'],mapped=slot['x'][288:432],mu=mu,scale=sc)
    put(p/'shared.pt',shared,role_id=rid,capability='shared'); put(p/'base.pt',base,role_id=rid,capability='base')
    put(p/'classification.pt',{k:slot[k] for k in ['x','y','mass','mu','scale']},role_id=rid,capability='classification')
    paired=external(RAW/'packages'/rid/'paired/train.pt',rid,'raw-paired/train.pt'); mask=paired['ci']>=12
    ledger=external(RAW/'trusted'/rid/'paired-train-ledger.parquet',rid,'trusted-ledger').iloc[144:]
    require(int(mask.sum())==48 and len(ledger)==48,'C count')
    for key in ['visit_id','content_id','protocol','label_id']:
        require(ledger[key].tolist()==cp[key].tolist(),'C trusted identity/order mismatch '+key)
    require(float((paired['b'][mask]-tensor(cp[HIST])).abs().max())<=1e-14,'Original integer/post-table replay')
    cx=(paired['a'][mask]-mu)/sc; cb=(paired['b'][mask]-mu)/sc; cy=paired['y'][mask]
    for yy in r['missing']: require(not bool((cy==yy).any()),'U entered calibration')
    put(p/'P.pt',dict(cx=cx,target=cb,post=cb,cy=cy,post_y=cy),role_id=rid,capability='P')
    ga=external(RAW/'packages'/rid/'group/pre.pt',rid,'raw-group/pre.pt'); gb=external(RAW/'packages'/rid/'group/post.pt',rid,'raw-group/post.pt')
    ia=ga['ci']>=12; ib=gb['ci']>=12; require(int(ia.sum())==int(ib.sum())==48,'G C shape')
    gx=(ga['a'][ia]-mu)/sc; gz=(gb['b'][ib]-mu)/sc; gy=ga['y'][ia]; py=gb['y'][ib]
    ag,bg=ga['group'][ia],gb['group'][ib]; gt=torch.empty_like(gx)
    for token in ag.unique():
        require(int((ag==token).sum())==int((bg==token).sum())==4,'Anonymous four repeats')
        # Validate complete groups; construct centers with explicit dimensions below.
    enc=F.one_hot(bg,int(bg.max())+1).double();centers=enc.T@gz/4;gt=centers[ag]
    put(p/'G.pt',dict(cx=gx,target=gt,post=gz,cy=gy,post_y=py),role_id=rid,capability='G')
    # Only training provenance in the row ledger. Source pre remains anonymous.
    led=[]
    for name,d,start in [('source-post',post,0),('CORAL',post,144),('mapped-pre',pre,288),('C-post',cp,432)]:
        for j,item in enumerate(d.itertuples()):
            ix=start+j;led.append(dict(role_id=rid,row_key=f'{rid}/{name}/{j}',input_view=name,label=int(slot['y'][ix]),sample_mass=float(w[ix]),
                content_key=item.content_id,parent_visit_key=None if name=='mapped-pre' else item.visit_id,anonymous_pre_row=j if name=='mapped-pre' else None))
    save(p/'row-ledger.parquet',led)
    seal(p/'complete.json',list(p.glob('*.pt'))+[p/'row-ledger.parquet'],role_id=rid)
    return dict(role_id=rid,role_target=r['target'],query_deployment=r['calibration'],slot_masses=masses,zero_exact=True,
        paired_C_only=True,base_original_gradient=grad,**bq)

def run():
    configure('trusted'); codecheck(); rows=[]
    for i,r in enumerate(roles()):
        deadline();rows.append(prep(r));flush('P0');progress('P0_packages',completed=i+1,total=48)
    save(OUT/'manifests/P0-audit.parquet',rows)
    seal(OUT/'manifests/P0-complete.json',[OUT/'packages'/r['id']/'complete.json' for r in roles()]+[OUT/'manifests/P0-audit.parquet'],roles=48,query_pre_reads=0,actual_H_U_reads=0)

if __name__=='__main__':run()
