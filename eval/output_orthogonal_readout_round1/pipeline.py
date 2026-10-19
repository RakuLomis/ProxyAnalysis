from common import *
from head import *
from solve import fit

def pilot():
    with stage('pilot'):
        require(read(OUT/'audits/unit-tests.json')['passed'],'Interface gate')
        r=contract()['roles'][0];logs=[fit(r,a,SEEDS[0]) for a in ARMS]
        used=read(OUT/'ledger.json')['fit_seconds'];projected=used+(132-5)*max(v['seconds'] for v in logs)
        write(OUT/'audits/pilot.json',dict(passed=projected<=2880,physical_fits=5,projected_fit_seconds=projected,fit_seconds_used=used))
        require(projected<=2880,'Pilot extrapolation exceeds 2880s; stop before query')

def train_all():
    with stage('train'):
        require(read(OUT/'audits/pilot.json')['passed'],'Pilot gate');eps=[]
        for i,r in enumerate(contract()['roles']):
            for arm in ARMS:
                for seed in ([SEEDS[0]] if arm in ['OR-X','OR-BIAS'] else SEEDS):
                    if not modelpath(r,arm,seed).exists():fit(r,arm,seed)
                for seed in SEEDS:eps.append(dict(role_id=r['id'],role_target=r['target'],query_deployment=r['calibration'],
                    arm=arm,seed=seed,model=rel(modelpath(r,arm,seed)),seed_alias=arm in ['OR-X','OR-BIAS']))
            progress('train_role_complete',roles=i+1,total=12,accepted=read(OUT/'ledger.json')['accepted_fits'])
        require(len(eps)==180 and len({v['model'] for v in eps})==132,'Head/endpoint counts')
        require(read(OUT/'ledger.json')['accepted_fits']==132,'All heads must qualify')
        for path,info in contract()['sources'].items():require(sha(ROOT/path)==info['sha256'],'Historical source mutated')
        write(OUT/'manifests/endpoints.json',eps)
        seal(OUT/'manifests/models-complete.json',list((OUT/'models').rglob('*pt'))+list((OUT/'models').rglob('*.json'))+
             list((OUT/'fit-logs').rglob('*.json'))+[OUT/'manifests/endpoints.json'],physical_fits=132,logical_endpoints=180)

def predict():
    with stage('predict'):
        verify(OUT/'manifests/models-complete.json');eps=read(OUT/'manifests/endpoints.json');parts=[];bases=[];diags=[]
        for i,r in enumerate(contract()['roles']):
            query=source_frame(ROOT/r['query'],'predict',r['id']);m=source_tensor(ROOT/r['base'],r['id'])
            require(set(query)=={'visit_id',*HIST} and len(query)==24 and query.visit_id.is_unique,'Post-only query')
            x=(tensor(query[HIST])-m['mu'])/m['scale'];z0=offset(x,m);q=basis();geo=geometry(z0,q)
            lp0=F.log_softmax(z0,1);base=pd.DataFrame(lp0.exp().cpu().numpy(),columns=PC)
            for k in range(6):base[f'l{k}']=lp0[:,k].cpu().numpy()
            base['role_id']=r['id'];base['visit_id']=query.visit_id.to_numpy();bases.append(base)
            alias={}
            for ep in [v for v in eps if v['role_id']==r['id']]:
                arm,seed=ep['arm'],ep['seed'];model=own(ROOT/ep['model'])
                g=None if arm in ['OR-X','OR-BIAS'] else source_tensor(ROOT/r['frozen_G'][f'{arm}-{seed}'],r['id'],arm)
                phi=features(x,g,arm);zz,h,delta=logits(model['W'],model['b'],phi,z0,model['Q'],geo)
                lp=F.log_softmax(zz,1);gcheck=geometry_errors(geo['s'],delta,geo['mask'])
                if ep['seed_alias']:
                    if arm in alias:require(torch.equal(lp,alias[arm]),'Seed alias not exact')
                    else:alias[arm]=lp.clone()
                df=pd.DataFrame(lp.exp().cpu().numpy(),columns=PC)
                for k in range(6):
                    df[f'l{k}']=lp[:,k].cpu().numpy();df[f'z0_{k}']=z0[:,k].cpu().numpy();df[f'delta{k}']=delta[:,k].cpu().numpy()
                for k in range(5):df[f'h{k}']=h[:,k].cpu().numpy()
                df['near_zero']=~geo['mask'].cpu().numpy();df['visit_id']=query.visit_id.to_numpy()
                for key in ['role_id','role_target','query_deployment','arm','seed']:df[key]=ep[key]
                parts.append(df);diags.append(dict(**ep,**gcheck,delta_RMS=float(delta.square().mean().sqrt()),
                    base_centered_norm=float(geo['s'].norm(dim=1).mean()),final_centered_norm=float((geo['s']+delta).norm(dim=1).mean())))
            progress('predict_role_complete',roles=i+1,total=12)
        d=pd.concat(parts,ignore_index=True);b=pd.concat(bases,ignore_index=True)
        require(len(d)==4320 and len(b)==288,'Prediction counts')
        # Original double baseline must reproduce historical probabilities exactly.
        old=source_frame(OLD/'predictions/base.parquet','control').set_index(['role_id','visit_id'])
        aligned=old.loc[pd.MultiIndex.from_frame(b[['role_id','visit_id']])]
        require(np.array_equal(aligned[PC+LC].to_numpy(),b[PC+LC].to_numpy()),'Original base replay not exact')
        save(OUT/'predictions/raw.parquet',d);save(OUT/'predictions/base.parquet',b)
        write(OUT/'diagnostics/raw-geometry.json',diags)
        seal(OUT/'predictions/raw-complete.json',[OUT/'predictions/raw.parquet',OUT/'predictions/base.parquet',OUT/'diagnostics/raw-geometry.json'],rows=4320,labels_read=0)
