"""Independent metrics, alias checks, forward replay and full provenance closeout."""
from common import *
from formal import historical,base
from deploy import base_logp,branch_logp,mixture

def run():
    configure('inference');barrier('P5-scores-complete.json');barrier('P4-models-complete.json');hashes=code_seal('P6-verify')
    d=pd.read_parquet(OUT/'predictions/post-only.parquet');eps=read(OUT/'manifests/outer-endpoints.json');worst=0.
    for r in contract()['roles']:
        query=historical(r,'query');raw=tensor(query[HIST]);sub=d[d.role_id==r['id']].set_index(['pipeline','seed','visit_id'])
        with compute('final-post-replay',role_id=r['id']),torch.no_grad():
            lp0=base_logp(raw,base(r));cache={None:lp0}
            for e in [x for x in eps if x['role_id']==r['id']]:
                path=e['export_path']
                if path not in cache:cache[path]=branch_logp(raw,own(ROOT/path,r['id']))
                lp=mixture(lp0,cache[path],e['beta']);old=tensor(sub.loc[(e['pipeline'],e['seed'])].loc[query.visit_id,[f'l{k}' for k in range(6)]])
                err=float((lp-old).abs().max());worst=max(worst,err)
                require(torch.allclose(lp,old,atol=1e-9,rtol=1e-8),'Frozen H inference replay')
                if e['beta']==0:require(torch.equal(lp,lp0) and torch.equal(lp,old),'beta0 was not exact frozen B0 alias')
        flush_reads('P6')
    scenes=pd.read_parquet(OUT/'scores/scenarios.parquet');labeled=pd.read_parquet(OUT/'scores/labeled-predictions.parquet');replay_error=0.
    for keys,part in labeled.groupby(['pipeline','target','group','seed']):
        # Independent one-vs-rest counts, not the original confusion-matrix helper.
        y=part.label_id.map(dict(zip(LABELS,range(6)))).to_numpy();z=part.prediction.to_numpy();f=[]
        for k in range(6):
            tp=np.sum((y==k)&(z==k));den=np.sum(y==k)+np.sum(z==k);f.append(2*tp/den if den else 0.)
        f=np.array(f);ref=scenes
        for col,key in zip(['pipeline','target','group','seed'],keys):ref=ref[ref[col]==key]
        require(len(ref)==1,'Independent score stratum')
        ce=-part[[f'l{k}' for k in range(6)]].to_numpy()[np.arange(len(y)),y]
        check={'F1_U':f[MASKS[keys[2]]].mean(),'F1_C':np.delete(f,MASKS[keys[2]]).mean(),'F1_all':f.mean(),'CE':ce.mean()}
        for k,v in check.items():replay_error=max(replay_error,abs(float(ref.iloc[0][k])-float(v)))
    require(replay_error<=1e-12,'Independent score mismatch')
    # Byte-level verification includes the originally bound native table but no
    # capture content. Deferred query/labels are now legal and can be rehashed.
    for p,info in contract()['files'].items():require(sha(ROOT/p)==info['sha256'],'Historical file changed at closeout: '+p)
    require(read(OUT/'budget.json')['used_seconds']<=144000,'Activity budget overrun')
    immutable(OUT/'tests/P6-independent-verification.json',dict(passed=True,post_logp_max_error=worst,independent_metric_error=replay_error,
        historical_hashes_verified=len(contract()['files']),query_pre_reads=0,target_U_training_reads=0,PCAP_reads=0,
        statistical_independence_unit='global content, not visit/role/seed',bootstrap_is_conditional=True))
    codecheck(hashes);flush_reads('P6');seal(OUT/'manifests/P6-complete.json',[OUT/'tests/P6-independent-verification.json',OUT/'manifests/P5-scores-complete.json'],passed=True)
    progress('P6_verified',max_logp_error=worst)
