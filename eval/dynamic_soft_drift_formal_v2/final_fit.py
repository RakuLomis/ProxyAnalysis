"""Zero-init original final LR, original mass/coordinates, no H queries."""
from common import *

def fit(r,arm):
    kind='G' if arm=='D-G' else 'P';v=own(OUT/'tasks'/r['id']/(kind+'.pt'))['view'];q=own(OUT/'q'/r['id']/(arm+'.pt'))['q']
    a,u,_,rec=production();s=u.pack(v,arm,q)
    require(len(s['x'])==928 and abs(float(s['mass'].sum())-1)<1e-12 and float((weighted(s['y'],s['mass'],6)-1/6).abs().max())<1e-12,'Final slot policy')
    put(s,OUT/'final-slots'/r['id']/(arm+'.pt'),role_id=r['id'],arm=arm,rows=928,q_path=rel(OUT/'q'/r['id']/(arm+'.pt')))
    ledger(new_final_LR=1)
    m,log=solver().fit_preconditioned(s['x'],s['y'],s['mass'],r['t'],dict(role_id=r['id'],arm=arm))
    m.update(mu=v['mu'],scale=v['scale']);p=OUT/'models'/r['id']/(arm+'.pt');put(m,p,role_id=r['id'],arm=arm,t=r['t'],optimizer=log)
    raw=a.adjust(v['pre_x'],v['mapped_x'],q)*v['scale']+v['mu'];stats=[]
    for j in range(10):
        b=raw[:,block(j)];stats.append(dict(role_id=r['id'],arm=arm,block=FEATURES[j],negative_rows=int((b<0).any(1).sum()),block_sum_max_error=float((b.sum(1)-1).abs().max()),q=float(q[j]),rows=len(b)))
    save(pd.DataFrame(stats),OUT/'audits/format'/r['id']/(arm+'.parquet'))
    return dict(role_id=r['id'],arm=arm,model_path=rel(p),model_sha256=sha(p),seconds=log['seconds'],max_gradient=log['max_gradient'])

