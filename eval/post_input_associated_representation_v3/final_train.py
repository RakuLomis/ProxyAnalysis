"""All endpoints fixed before any target H post read."""
from common import *
from teacher import fit_batch as teachers
from train import fit_batch as residuals

def run():
    with stage('P3_final_train',training=True):
        verifyseal(OUT/'manifests/engineering-code.json');verifyseal(OUT/'selections/complete.json')
        decisions=read(OUT/'selections/decisions.json');lookup={(v['role_id'],v['arm']):v for v in decisions}
        endpoints=[]
        for r in contract()['roles']:
            budget();active=any(lookup[(r['id'],a)]['enabled'] for a in ['A1','A2','A3'])
            # Teacher only needed for an actually associated nonzero selected target.
            if any(lookup[(r['id'],a)]['enabled'] and lookup[(r['id'],a)]['lambda_value']>0 for a in ['A2','A3']):teachers([r])
            jobs=[]
            for arm in ['A1','A2','A3']:
                d=lookup[(r['id'],arm)]
                if d['enabled']:
                    lam=d['lambda_value'];canon=cfg_arm(arm,lam)
                    for seed in SEEDS:
                        j=(r,canon,lam,seed)
                        if j not in jobs:jobs.append(j)
            if jobs:residuals(jobs)
            for arm in ['A0','A1','A2','A3']:
                decision=None if arm=='A0' else lookup[(r['id'],arm)]
                for seed in SEEDS:
                    path=None
                    if decision is not None and decision['enabled']:
                        lam=decision['lambda_value'];path=rel(OUT/'models'/r['id']/tag(cfg_arm(arm,lam),lam,seed)/'terminal.pt')
                    endpoints.append(dict(role_id=r['id'],arm=arm,seed=seed,base_path=rel(PARENT/'base-models'/r['id']/'P-small.pt'),
                                          residual_path=path,fallback=path is None,lambda_value=None if decision is None else decision['lambda_value']))
        require(len(endpoints)==720,'Endpoint count')
        write(OUT/'manifests/endpoints.json',endpoints)
        files={ROOT[e['base_path']] for e in endpoints}|{ROOT[e['residual_path']] for e in endpoints if e['residual_path']}
        seal(OUT/'manifests/models-complete.json',list(files)+[OUT/'manifests/endpoints.json'],passed=True,endpoints=720)

if __name__=='__main__':run()
