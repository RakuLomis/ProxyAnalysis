"""Trusted read-only reuse auditor; seals all code before new real directions."""
import platform
import sys
from common import *
from tests import main as tests

def main():
    configure(); require(not (OUT/'manifests/experiment-contract.json').exists(),'Never overwrite registration')
    old=read(DSR/'manifests/experiment-contract-amended-v1.json')
    amendment=read(DSR/'manifests/engineering-repair-v1/amendment-seal.json')
    require(sha(DSR/'manifests/experiment-contract-amended-v1.json')==amendment['contract_sha256'],'DSR amendment chain')
    require(sha(DSR/'manifests/experiment-contract.json')==old['engineering_revision']['original_contract_sha256'],'DSR original chain')
    require(read(DSR/'verification.json')['pass'],'DSR verification required')
    baseline_map={**old['baseline_sha256'],**old['packages_sha256'],**old['source_sha256']}
    rendering=read(DSR/'manifests/zero-selection-report-rendering.json')
    adapter=ROOT/'eval/drift_state_group_risk/report_zero.py'
    require(sha(adapter)==rendering['entry_sha256'],'DSR report-only adapter chain')
    baseline_map[rel(adapter)]=sha(adapter)
    for p,h in baseline_map.items(): require(sha(ROOT/p)==h,'Frozen DSR source changed '+p)
    # Preserve both prior experiments, including original/amended contracts and repaired reports.
    for root in [DSR,OLD]:
        for p in root.rglob('*'):
            if p.is_file() and '__pycache__' not in p.parts: baseline_map[rel(p)]=sha(p)
    for p in [PLAN,Q/'features/paired-flow-features.parquet',Q/'cohorts/folds.parquet']:
        baseline_map[rel(p)]=sha(p)
    df=pd.read_parquet(Q/'features/paired-flow-features.parquet')
    require(len(df)==23566 and df.session_id.nunique()==480 and df.content_id.nunique()==30 and df.pair_id.is_unique,'Fixed cohort')
    for key in ['pair_id','session_id','logical_id','carrier_id','registered_epoch_proxy','content_id']:
        require(df.groupby(key).fold.nunique().max()==1,'Registered entity split '+key)
    roles=old['roles']; require(len(roles)==100,'Role count'); packages={}; reuse=[]
    sources={s['id']:s for s in old['sources']}
    for q in old['queries']:
        s=sources[q['source']]; parent=q['parent']; a=set(s['train_contents']); bset=set(q['query_contents']); whole=set(parent['train_contents'])
        validate_scope(a,bset,whole); require(len(a)==(18 if parent['inner'] is None else 12),'CF scope size')
    frames={part:pd.read_parquet(DSR/f'states/{part}-CF-scores.parquet') for part in ['inner','outer']}
    for r in roles:
        part='outer' if r['inner'] is None else 'inner'; n=96 if part=='outer' else 72
        src=DSR/'packages/main'/rolekey(r); dst=folder('packages',r); dst.mkdir(parents=True,exist_ok=True)
        h=pd.read_parquet(src/'train-post.parquet'); query=pd.read_parquet(src/'query-post.parquet'); validate_query(query)
        labels=pd.read_parquet(src/'score-labels.parquet')
        require(len(h)==n and len(query)==24 and h.visit_id.is_unique and query.visit_id.is_unique,'Role rows')
        require(set(h.content_id)==set(r['train_contents']) and set(labels.content_id)==set(r['validation_contents']) and not set(h.visit_id)&set(query.visit_id),'Role train/query membership')
        frame=frames[part]; sub=frame[(frame.outer==r['outer'])&(frame.protocol==r['protocol'])&((frame.inner==r['inner']) if part=='inner' else frame.inner.isna())]
        require(len(sub)==n and sub.visit_id.is_unique and set(sub.content_id)==set(r['train_contents']),'OOF scope')
        sub=sub.set_index('visit_id').loc[h.visit_id].reset_index()
        require(sub.label_id.tolist()==h.label_id.tolist(),'OOF label/order')
        yy=tensor(truths(h),torch.long)
        # Replay saved CF difficulty from predictions and train-only query labels.
        for q in [q for q in old['queries'] if rolekey(q['parent'])==rolekey(r)]:
            pp=DSR/'CF-predictions/cf'/q['id']/'post-probabilities.parquet'
            require(read(pp.parent/'complete.json')['sha256'][pp.name]==sha(pp),'CF prediction seal')
            probs=pd.read_parquet(pp).set_index('visit_id'); ss=sub[sub.CF_fold==q['held']]
            p=tensor(probs.loc[ss.visit_id,[f'p{i}' for i in range(6)]]); y=tensor(truths(ss),torch.long)
            ce=-p[torch.arange(len(y),device=device()),y].log()
            require(float((ce-tensor(ss.d_post)).abs().max())<1e-12,'OOF difficulty replay')
        save(h,dst/'train-post.parquet'); save(query,dst/'query-post.parquet'); save(labels,dst/'score-labels.parquet')
        save(sub[['visit_id','content_id','label_id','d_post','source','CF_fold']],dst/'train-OOF.parquet')
        for newarm,oldarm,col in [('RW2','DSR2','d_post'),('RW3','DSR3','d_group'),('RW4','DSR4','d_true')]:
            p=DSR/'states/main'/rolekey(r)/(oldarm+'.pt')
            require(read(p.parent/'complete.json')['sha256'][p.name]==sha(p),'State seal')
            g=torch.load(p,map_location=device(),weights_only=True)
            require(g['visit_id']==h.visit_id.tolist(),'Gamma row order'); validate_gamma(g['gamma'],yy)
            require(torch.equal(g['gamma'],partition(tensor(sub[col]),yy)),'State partition replay')
            torch.save(g,dst/(newarm+'.pt'))
            reuse.append({'role':rolekey(r),'arm':newarm,'source':rel(p),'sha256':sha(p),'visits':n,'contents':n//4})
        for p in dst.iterdir(): packages[rel(p)]=sha(p)
    ix=np.load(DSR/'comparisons/bootstrap-indices.npy'); order=pd.read_parquet(DSR/'comparisons/content-order.parquet')
    rng=np.random.default_rng(20261005); expected=np.concatenate([rng.choice(np.arange(j*5,(j+1)*5),size=(10000,5),replace=True) for j in range(6)],axis=1)
    require(np.array_equal(ix,expected) and len(order)==30,'Shared bootstrap exact reproduction')
    tests()
    write(OUT/'manifests/environment.json',{'python':sys.version,'platform':platform.platform(),'torch':torch.__version__,
      'CUDA':torch.version.cuda,'GPU':torch.cuda.get_device_name(0),'dtype':'float64','deterministic':True,'TF32':False})
    save(pd.DataFrame(reuse),OUT/'manifests/reuse.parquet')
    c={'registered_unix':time.time(),'roles':roles,'sources':old['sources'],'queries':old['queries'],
      'source_sha256':{rel(p):sha(p) for p in Path(__file__).parent.iterdir() if p.suffix in ['.py','.md']},
      'baseline_sha256':baseline_map,'packages_sha256':packages,'ratios':RATIOS,'L2_settings':L2_SETTINGS,
      'eta':ETA,'rho':.001,'direction_tolerance_nat':EPS,'fit_max_iter':500,'fit_max_gradient':1e-5,
      'labels':LABELS,'features':HIST,'cohort_pairs':23566,'visits':480,'contents':30,'main_family':3,
      'bootstrap_seed':20261005,'bootstrap_reuse_indices_sha256':sha(DSR/'comparisons/bootstrap-indices.npy'),
      'bootstrap_reuse_order_sha256':sha(DSR/'comparisons/content-order.parquet'),
      'practical_gain_vs_RW1':.01,'new_fit_budget_upper':780,'permission_whitelist_not_OS_sandbox':True,
      'selection_rule':'pooled inner full-six-class macro-F1; tie 1e-12 then min ratio',
      'zero_alias_exact':True,'source_kernel_or_CF_fit_count':0,'stop_after_report':True}
    write(OUT/'manifests/experiment-contract.json',c)
    finish('RW00-RW07',source_files=len(c['source_sha256']),baseline_files=len(baseline_map),roles=100,tests_pass=True)
if __name__=='__main__': main()
