"""240 content splits, two same-capacity maps each; predictions precede scores."""
from common import *
from anchors import arrays,rules
from affine import fit,apply,group_targets
from guard import project

def run():
    with stage('diagnostic_predict'):
        require(read(OUT/'audits/tests.json')['passed'],'Tests must pass')
        fits=[];predictions={}
        for ri,r in enumerate(contract()['roles']):
            for i in range(4):
                root=rolepath(r)/f'i{i}';dest=OUT/'diagnostics'/r['id']/f'i{i}'
                coord=artifact(root/'scaler.pt');mu=coord['mu'];sd=coord['scale']
                for arm in ['P','G']:
                    if arm=='P':
                        d=package(root/'P-fit.parquet','P-fit');a,b=arrays(d,True);ta=d.content_token.to_numpy();tb=None
                        require(len(a)==48,'C fit rows');x=(a-mu)/sd;y=(b-mu)/sd;constant=0.
                    else:
                        dp=package(root/'G-pre-fit.parquet','G-fit');db=package(root/'G-post-fit.parquet','G-fit')
                        a=arrays(dp);b=arrays(db);ta=dp.content_token.to_numpy();tb=db.content_token.to_numpy()
                        x=(a-mu)/sd;y,constant=group_targets(x,(b-mu)/sd,ta,tb)
                    rr=rules(a,b,ta,tb);write(dest/f'{arm}-rules.json',rr)
                    m,log=fit(x,y,r['eta'],constant)
                    put(m,dest/f'{arm}-map.pt',mapping=log,role_id=r['id'],inner=i,arm=arm)
                    fits.append({'role_id':r['id'],'inner':i,'arm':arm,**log})
                    q=package(root/('P-query.parquet' if arm=='P' else 'G-pre-validation.parquet'),arm+'-query')
                    qa=arrays(q);b0=apply(m,(qa-mu)/sd)*sd+mu
                    # Candidate per-block projections are sealed before validation targets determine the final set.
                    candidate=project(qa,b0,rr,active=range(10));train_guard=project(qa,b0,rr)
                    payload={'a':qa,'b0':b0,'candidate_guard':candidate,'train_guard':train_guard,'scale':sd,
                             'content_tokens':q.content_token.tolist(),'query_keys':q.query_key.tolist()}
                    p=dest/f'{arm}-predictions.pt';put(payload,p,role_id=r['id'],inner=i,arm=arm,C_validation_post_used=False)
                    predictions[rel(p)]=sha(p)
            if (ri+1)%12==0:progress('OOF_mapping_prediction',roles=ri+1,total=60,mapping_fits=len(fits))
        require(len(fits)==480,'Map budget')
        save(pd.DataFrame(fits),OUT/'diagnostics/accepted-maps.parquet')
        write(OUT/'diagnostics/predictions-complete.json',{'files':predictions,'maps':480,'classifier_fits':0,
              'C_validation_score_packages_read':0,'H_query_reads':0,'H_label_reads':0,'target_U_reads':0})

if __name__=='__main__':run()
