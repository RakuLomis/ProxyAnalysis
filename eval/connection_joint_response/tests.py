"""Positive and negative retention and interface checks, no fitting or H labels."""
from common import *
from representation import summarize, schema, predict

def synthetic(swap=False):
    d=pd.DataFrame(np.zeros((2,10),dtype='int64'),columns=FEATURES)
    d['W_up']=d['U_up']=[512,8192]; d['P_up']=8
    d['E_up']=[8,1] if swap else [1,8]
    d['FR_packet_runs']=d['R_unique_zero_runs']=1; return d

def run():
    with stage('tests'):
        a,_=summarize(synthetic()); b,_=summarize(synthetic(True)); rows=[]
        def check(name,ok):require(ok,name); rows.append({'test':name,'passed':True})
        check('same marginal counterexample',np.array_equal(a['M'],b['M']))
        check('same product counterexample',np.array_equal(a['I'],b['I']))
        check('joint distinguishes same-marginal connections',not np.array_equal(a['J'],b['J']))
        z,_=summarize(synthetic().iloc[::-1])
        check('whole-row permutation invariant',all(np.array_equal(a[k],z[k]) for k in a))
        for g in range(4):
            j=a['J'][96+slice_joint(g).start:96+slice_joint(g).stop]
            v=a['I'][96+slice_joint(g).start:96+slice_joint(g).stop]
            jp=j[1:] if SIZES[g]==17 else j; vp=v[1:] if SIZES[g]==17 else v
            check('block marginals equal '+NAMES[g],np.allclose(jp.reshape(4,4).sum(0),vp.reshape(4,4).sum(0)) and
                  np.allclose(jp.reshape(4,4).sum(1),vp.reshape(4,4).sum(1)))
        bad=synthetic(); bad['protocol']='vless'
        try:schema(bad)
        except RuntimeError:rejected=True
        else:rejected=False
        check('metadata injection rejected',rejected)
        for r in contract()['roles']:
            for rep in INPUTS:
                root=rolepath(r)/rep; q=package(root/'query.parquet','query')
                cols=INPUTS[rep]; check('query numeric whitelist '+r['id']+rep,set(q)=={'visit_id',*cols})
                source=package(root/'source-post.parquet','train'); cp=package(root/'C-post.parquet','train')
                pre=package(root/'source-pre.parquet','train')
                check('source and C scope '+r['id']+rep,set(source.content_id)<=set(r['train_contents']) and
                      set(cp.content_id)==set(r['C_contents']) and not set(cp.content_id)&set(r['U_contents']))
                check('source pre has no shared visit identity '+r['id']+rep,'visit_id' not in pre)
                for frame in [source,cp,pre,q]:
                    x=frame[cols].to_numpy(); check('finite normalized blocks '+r['id']+rep+str(len(frame)),
                        np.isfinite(x).all() and (x>=0).all())
                    if rep!='M':
                        for g in range(4):check('unit block '+r['id']+rep+str(g)+str(len(frame)),
                            np.allclose(x[:,96+slice_joint(g).start:96+slice_joint(g).stop].sum(1),1,atol=1e-12,rtol=0))
                mu,scale=scaler(torch.cat([tensor(source[cols]),tensor(cp[cols])]))
                random=torch.Generator(device='cuda').manual_seed(20261010)
                model={'mu':mu,'scale':scale,'weight':torch.randn((6,len(cols)),generator=random,
                       device=device(),dtype=torch.float64)*.01,'bias':torch.zeros(6,device=device(),dtype=torch.float64)}
                original=predict(model,q,rep); shuffled=q.sample(frac=1,random_state=20261010)
                changed=predict(model,shuffled,rep).set_index('visit_id').loc[original.visit_id]
                check('CUDA query order independent '+r['id']+rep,
                      np.allclose(original[[f'p{i}' for i in range(6)]],changed[[f'p{i}' for i in range(6)]],rtol=0,atol=1e-14))
                injected=q.copy(); injected['test_pre']=np.arange(len(q))
                try:predict(model,injected,rep)
                except RuntimeError:rejected=True
                else:rejected=False
                check('test-pre injection rejected '+r['id']+rep,rejected)
                try:package(rolepath(r)/'labels.parquet','score')
                except RuntimeError:rejected=True
                else:rejected=False
                check('H labels blocked before all predictions '+r['id']+rep,rejected)
            paired=package(rolepath(r)/'C-paired.parquet','paired-map')
            for side in ['pre','post']:
                group=package(rolepath(r)/f'C-group-{side}.parquet','group-map')
                check('group identity stripped '+r['id']+side,set(group)=={'content_token','fit_mass',*INPUTS['J']})
                anon=package(rolepath(r)/f'C-marginal-{side}.parquet','marginal-map')
                check('marginal identity and content stripped '+r['id']+side,set(anon)=={'fit_mass',*INPUTS['J']})
            joint=package(rolepath(r)/'J'/'source-post.parquet','train')
            check('new blocks not all training-constant '+r['id'],
                  all((joint[JOINT[slice_joint(g)]].var(ddof=0)>0).any() for g in range(4)))
        write(OUT/'audits/information-and-permission-tests.json',{'passed':True,'checks':rows,
             'classifier_fits':0,'H_pre_input_exists':False,'target_U_worker_rows':0,'PCAP_reads':0})
        progress('tests_passed',checks=len(rows),classifier_fits=0)

if __name__=='__main__':run()
