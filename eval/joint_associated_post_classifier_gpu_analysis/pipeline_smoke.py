"""Synthetic-only scoring/permission interface smoke test, no actual query data."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'joint_associated_post_classifier'))
from common import *
from workflow import ARMS,LABELS,package
from evaluate import bootstrap,metric

def run():
    configure();started=time.perf_counter();rows=[]
    for arm in ARMS:
        for p in PROTOCOLS:
            for g in MASKS:
                for seed in SEEDS:
                    for content in range(30):
                        y=content//5
                        for rep in range(4):
                            row=dict(arm=arm,target=p,group=g,seed=seed,content_id=f'synthetic-{content}',
                                     label_id=LABELS[y],prediction=y)
                            prob=np.full(6,.05);prob[y]=.75
                            row.update({f'p{i}':prob[i] for i in range(6)});row.update({f'l{i}':float(np.log(prob[i])) for i in range(6)})
                            rows.append(row)
    d=pd.DataFrame(rows);m,_,_=metric(d[(d.arm=='JP')&(d.target=='vless')&(d.group=='G0')&(d.seed==SEEDS[0])],'G0')
    require(abs(m['F1_U']-1)<1e-12 and abs(m['CE']+np.log(.75))<1e-12,'Synthetic metrics failed')
    _,_,values,error=bootstrap(d);require(np.max(abs(values-1))<1e-12,'Perfect-prediction bootstrap fixture failed')
    # These calls must stop before file decode because global seals do not exist.
    blocked=[]
    for kind in ['query','labels']:
        try:package(contract()['roles'][0],kind,True)
        except RuntimeError as e:
            require('Global phase barrier' in str(e),'Wrong permission failure');blocked.append(kind)
        else:raise RuntimeError('Premature H reader unexpectedly allowed')
    p=OUT/'engineering/pipeline-synthetic-smoke.json'
    immutable(p,dict(passed=True,synthetic_rows=len(d),no_actual_query_reads=True,no_H_U_reads=True,
          blocked_outer_readers=blocked,bootstrap_replay_error=error,seconds=time.perf_counter()-started,
          code_sha256=sha(Path(__file__))))
    print(read(p),flush=True)

if __name__=='__main__':run()
