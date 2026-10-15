"""K03-K04: trusted packaging; fixed histograms, opaque post-only queries."""
from common import *

def run():
    require(not (OUT/'manifests/experiment-contract.json').exists(),'Cannot repackage sealed experiment')
    require(read(OUT/'manifests/cohort-audit.json')['passed'],'Inventory gate required')
    x=pd.read_parquet(OLD/'features/paired-flow-features.parquet')
    hashes={}
    roles=[]
    for fold in range(5):
      for p in PROTOCOLS:
        f=x[x.protocol.eq(p)]
        tr,te=f[f.fold.ne(fold)].copy(),f[f.fold.eq(fold)].copy()
        folder=rolefolder(fold,p)
        meta=['pair_id','session_id','content_id','label_id']
        for side in ['pre','post']:
            data=tr[meta+[side+'_'+f for f in FEATURES]].copy()
            data['fit_mass']=mass(data)
            saveparquet(data,folder/f'fit-{side}.parquet')
        names,h=visits_histogram(tr,'post')
        train=pd.DataFrame(h.cpu().numpy(),columns=HIST)
        train['session_id']=names
        m=tr[['session_id','content_id','label_id']].drop_duplicates()
        train=train.merge(m,on='session_id',validate='one_to_one')
        require(len(train)==96 and len(names)==96,'Train access coverage changed')
        saveparquet(train,folder/'fit-post-hist.parquet')
        mapping={s:hashlib.sha256(('business-query-v1:'+s).encode()).hexdigest() for s in te.session_id.unique()}
        query=te[['session_id']+['post_'+f for f in FEATURES]].copy()
        query['visit_id']=query.session_id.map(mapping)
        query=query.drop(columns='session_id')
        require(set(query)=={'visit_id',*['post_'+f for f in FEATURES]},'Forbidden query columns')
        saveparquet(query,folder/'query-post-flow.parquet')
        names,h=visits_histogram(query,'post','visit_id')
        q=pd.DataFrame(h.cpu().numpy(),columns=HIST)
        q['visit_id']=names
        saveparquet(q,folder/'query-post-hist.parquet')
        score=te[['session_id','content_id','label_id','repetition','fold','protocol']].drop_duplicates().copy()
        score['visit_id']=score.session_id.map(mapping)
        require(len(score)==24 and set(score.visit_id)==set(q.visit_id),'Score/query coverage changed')
        saveparquet(score,folder/'score-labels.parquet')
        for path in folder.glob('*.parquet'):
            hashes[rel(path)]=sha(path)
        roles.append({'fold':fold,'protocol':p,'train_contents':sorted(tr.content_id.unique()),
                      'test_contents':sorted(te.content_id.unique()),'train_visits':96,'test_visits':24,
                      'train_pairs':len(tr),'test_pairs':len(te)})
    write(OUT/'manifests/package-manifest.json',{'sha256':hashes,'roles':roles})
    write(OUT/'manifests/access-contract.json',{'trusted_packaging_reads_both_sides_for_fixed_eligibility':True,
         'fit_roles_read_training_only':True,'inference_numeric_input':HIST,'inference_metadata':['opaque visit_id','known deployment route'],
         'inference_no_test_pre_no_labels_no_content_no_SNI_IP_port':True,
         'given_access_and_dual_side_qualified_connection_set':True,'OS_security_sandbox_claimed':False})
    print('Prepared 20 roles; 480 test visits; 96 post histogram coordinates',flush=True)

if __name__=='__main__':
    run()
