"""Single-role OOF hard direction; positive frozen class-balanced weights."""
import sys
from common import *

def main(inner):
    c=start('weight-build'); directions=[]; summaries=[]; contents=[]; source_rows=[]
    choices={}
    if not inner:
        seal=read(OUT/'selection/complete.json'); require(seal['choices_sha256']==sha(OUT/'selection/choices.json'),'Selection seal')
        choices={(v['outer'],v['protocol'],v['arm']):v['setting'] for v in read(OUT/'selection/choices.json')}
    for r in c['roles']:
        if (r['inner'] is not None)!=inner: continue
        h=package(r,'train-post','weight-build'); oo=package(r,'train-OOF','weight-build')
        require(oo.visit_id.tolist()==h.visit_id.tolist() and set(oo.content_id)==set(r['train_contents']),'OOF role order')
        y=tensor(truths(h),torch.long); d=tensor(oo.d_post); meta={'outer':r['outer'],'inner':r['inner'],'protocol':r['protocol']}
        dst=folder('weights',r); dst.mkdir(parents=True,exist_ok=True)
        for arm in ARMS[2:]:
            p=folder('packages',r)/(arm+'.pt'); checked(p,c['packages_sha256'],'weight-build-gamma')
            gpack=torch.load(p,map_location=device(),weights_only=True); g=gpack['gamma']
            require(gpack['visit_id']==h.visit_id.tolist(),'Gamma order')
            hard,rr=direction(d,y,g)
            require(arm!='RW2' or hard in [1,None],'RW2 high CE direction violated')
            info={**meta,'arm':arm,'R0_OOF':float(rr[0]),'R1_OOF':float(rr[1]),'difference':float(rr[1]-rr[0]),
              'hard':hard,'tie':hard is None,'visits':len(h),'contents':h.content_id.nunique(),
              'CF_source_contents':12 if inner else 18,'OOF_sha256':sha(folder('packages',r)/'train-OOF.parquet'),
              'gamma_sha256':sha(p),'source_count':oo.source.nunique()}
            directions.append(info)
            for source,ix in oo.groupby('source').groups.items():
                idx=tensor(list(ix),torch.long); sr=[]
                # A CF source may lack a class/state cell; mark its diagnostic NA.
                for k in range(2):
                    cells=[]
                    for label in range(6):
                        mask=y[idx]==label; mass=g[idx,k][mask].sum()
                        cells.append(float((d[idx][mask]*g[idx,k][mask]).sum()/mass) if float(mass)>0 else None)
                    sr.append(sum(cells)/6 if all(v is not None for v in cells) else None)
                source_rows.append({**meta,'arm':arm,'source':source,'R0':sr[0],'R1':sr[1],
                  'difference':sr[1]-sr[0] if all(v is not None for v in sr) else None})
            settings=RATIOS if inner else [choices[(r['outer'],r['protocol'],arm)]]
            for ratio in settings:
                w=weights(g,hard,ratio); validate_gamma(g,y)
                require(bool(torch.isfinite(w).all()) and float(w.min())>=.4-1e-12 and float(w.max())<=1.6+1e-12,'Weight bounds')
                means=[float(w[y==j].mean()) for j in range(6)]
                require(max(abs(v-1) for v in means)<1e-12 and abs(float(w.mean())-1)<1e-12,'Weight class/global mean')
                ess=float(w.sum().square()/w.square().sum())
                require(ess>=len(w)*25/34-1e-10,'Bounded weight ESS algebra')
                summary={**meta,'arm':arm,'setting':ratio,'hard':hard,'alias':bool(torch.equal(w,torch.ones_like(w))),
                  'minimum':float(w.min()),'maximum':float(w.max()),'mean':float(w.mean()),
                  'q25':float(w.quantile(.25)),'median':float(w.quantile(.5)),'q75':float(w.quantile(.75)),
                  'ESS':ess,'soft_tie_visits':int(((g[:,0]>0)&(g[:,0]<1)).sum()),'max_class_mean_error':max(abs(v-1) for v in means)}
                summaries.append(summary)
                for label in range(6):
                    visits=torch.where(y==label)[0]; classmass=w[visits].sum(); masses=[]
                    for content in sorted(h.loc[truths(h)==label,'content_id'].unique()):
                        idx=tensor(np.flatnonzero(h.content_id.to_numpy()==content),torch.long); mass=w[idx].sum(); masses.append(mass)
                        contents.append({**meta,'arm':arm,'setting':ratio,'business':LABELS[label],
                          'content_id':content,'weight_mass':float(mass),'class_share':float(mass/classmass)})
                    mass=torch.stack(masses)
                    require(float((mass/classmass).max())<=(1.6/(3 if inner else 4))+1e-12,'Content share algebra')
                    summary[f'class{label}_mass']=float(classmass)
                    summary[f'class{label}_max_content_share']=float((mass/classmass).max())
                    summary[f'class{label}_effective_contents']=float(classmass.square()/mass.square().sum())
                torch.save({'visit_id':h.visit_id.tolist(),'w':w,'gamma':g,'hard':hard,'setting':ratio,
                  'direction':info},dst/f'{arm}-r{ratio:g}.pt')
        complete(dst,role=r,OOF_sha256=sha(folder('packages',r)/'train-OOF.parquet'),directions=directions[-3:])
    part='inner' if inner else 'outer'; dst=OUT/'weights'; dst.mkdir(parents=True,exist_ok=True)
    save(pd.DataFrame(directions),dst/f'{part}-directions.parquet'); save(pd.DataFrame(summaries),dst/f'{part}-summary.parquet')
    save(pd.DataFrame(contents),dst/f'{part}-content-masses.parquet'); save(pd.DataFrame(source_rows),dst/f'{part}-CF-source-diagnostics.parquet')
    write(dst/f'{part}-seal.json',{'time_unix':time.time(),'sha256':{p.name:sha(p) for p in dst.glob(part+'-*.parquet')},
      'role_seals':{rel(folder('weights',r)/'complete.json'):sha(folder('weights',r)/'complete.json') for r in c['roles'] if (r['inner'] is not None)==inner}})
    finish('RW08-RW10' if inner else 'RW17-RW18',directions=len(directions),weight_vectors=len(summaries))
if __name__=='__main__': main(sys.argv[1]=='inner')
