"""C-only cross-content prediction and separate sealed-post scoring."""
from common import *
from probability import fit_paired,fit_group

def fit_predict():
    with stage('diagnostic_fit_predict'):
        require(read(OUT/'audits/information-and-permission-tests.json')['passed'],'Feature gate not passed')
        rows=[]; fits=0; errors=[]
        for index,r in enumerate(contract()['roles']):
            for i in range(4):
                root=rolepath(r)/'diagnostics'/f'i{i}'; dest=OUT/'diagnostics/models'/r['id']/f'i{i}'
                d=package(root/'paired.parquet','diag-fit')
                true={str(g):fit_paired(d,g) for g in range(4)}; del d
                pre=package(root/'group-pre.parquet','diag-group'); post=package(root/'group-post.parquet','diag-group')
                group={str(g):fit_group(pre,post,g) for g in range(4)}
                for g in range(4):
                    for axis in [0,1]:
                        err=float((true[str(g)]['counts'].sum(axis)-group[str(g)]['counts'].sum(axis)).abs().max())
                        require(err<1e-10,'True/group marginals unequal'); errors.append(err)
                put({'KP':true,'KG':group},dest/'kernels.pt',C_training_contents=sorted(set(r['C_contents'])-set(r['C_diagnostic_contents'][i])),
                    C_validation_contents=r['C_diagnostic_contents'][i],device='cuda:0',dtype='float64',classifier_fit=False)
                query=package(root/'query.parquet','diag-query')
                require(set(query)=={'pair_id',*[f's{g}' for g in range(4)]},'Diagnostic query schema')
                for g,k in enumerate(SIZES):
                    code=tensor(query[f's{g}'],torch.long); baseline=true[str(g)]['q']
                    for arm,bundle in [('M0',None),('KP',true[str(g)]),('KG',group[str(g)])]:
                        p=baseline.expand(len(query),-1) if bundle is None else bundle['matrix'][code]
                        t=pd.DataFrame(p.cpu().numpy(),columns=[f'p{b}' for b in range(k)])
                        t['pair_id']=query.pair_id.to_numpy(); t['role_id']=r['id']; t['inner']=i; t['block']=g; t['arm']=arm
                        t['unseen_pre_state']=False if bundle is None else (bundle['row_mass'][code]==0).cpu().numpy()
                        rows.append(t); fits+=1
            if (index+1)%12==0:progress('diagnostic_predictions',roles=index+1,total=60,tables=fits)
        require(fits==2880,'Finite diagnostic budget')
        p=OUT/'diagnostics/predictions/flows.parquet'; save(pd.concat(rows,ignore_index=True),p)
        write(p.with_name('complete.json'),{'sha256':sha(p),'tables':fits,'true_group_marginal_error':max(errors),
              'post_scoring_rows_read':0,'classifier_fits':0,'H_reads':0,'target_U_reads':0})

def score():
    with stage('diagnostic_score'):
        p=OUT/'diagnostics/predictions/flows.parquet'; checked(p,read(p.with_name('complete.json'))['sha256'],'diagnostic-predictions')
        pred=pd.read_parquet(p); rows=[]; responses=[]
        for index,r in enumerate(contract()['roles']):
            for i in range(4):
                d=package(rolepath(r)/'diagnostics'/f'i{i}'/'score.parquet','diag-score')
                sub=pred[pred.role_id.eq(r['id'])&pred.inner.eq(i)]
                for g,k in enumerate(SIZES):
                    for arm in ['M0','KP','KG']:
                        pp=sub[sub.block.eq(g)&sub.arm.eq(arm)].set_index('pair_id').loc[d.pair_id]
                        probability=pp[[f'p{b}' for b in range(k)]].to_numpy(); y=d[f's{g}'].to_numpy(int)
                        ce=-np.log(probability[np.arange(len(d)),y]); brier=((probability-np.eye(k)[y])**2).sum(1)
                        table=d[['content_id','content_visit_flow_mass']].copy()
                        table['CE_nats']=ce; table['Brier']=brier; table['unseen_pre']=pp.unseen_pre_state.to_numpy(float)
                        for content,part in table.groupby('content_id'):
                            w=part.content_visit_flow_mass.to_numpy(); require(abs(w.sum()-1)<1e-10,'Heldout content mass')
                            rows.append({'role_id':r['id'],'target':r['target'],'group':r['group'],'outer':r['outer'],
                                'inner':i,'content_id':content,'block':NAMES[g],'arm':arm,
                                'CE_nats':float(w@part.CE_nats),'CE_bits':float(w@part.CE_nats/np.log(2)),
                                'Brier':float(w@part.Brier),'unseen_pre':float(w@part.unseen_pre)})
                for direction in ['up','down']:
                    u=d['pre_U_'+direction].to_numpy(); e=d['pre_E_'+direction].to_numpy()
                    v=d['post_U_'+direction].to_numpy(); f=d['post_E_'+direction].to_numpy()
                    z=pd.DataFrame({'role_id':r['id'],'content_id':d.content_id,'direction':direction,
                        'pre_load_bin':np.searchsorted([1024,16384,262144],u,side='right'),
                        'pre_empty':e==0,'post_empty':f==0,'delta_U':v-u,'delta_E':f-e,
                        'pre_U_per_E':np.divide(u,e,out=np.full(len(e),np.nan),where=e>0),
                        'post_U_per_E':np.divide(v,f,out=np.full(len(f),np.nan),where=f>0),
                        'flow_mass':d.content_visit_flow_mass.to_numpy()})
                    responses.append(z)
            if (index+1)%12==0:progress('diagnostic_scoring',roles=index+1,total=60)
        save(pd.DataFrame(rows),OUT/'diagnostics/scores/content-scores.parquet')
        save(pd.concat(responses,ignore_index=True),OUT/'diagnostics/scores/native-C-responses.parquet')
        write(OUT/'diagnostics/scores/complete.json',{'content_rows':len(rows),'classifier_fits':0,
              'H_reads':0,'target_U_reads':0,'interpretation':'conditional predictive risk; not MI or physical protocol entropy'})

if __name__=='__main__':{'predict':fit_predict,'score':score}[sys.argv[1]]()
