"""Post-P1 complete train-only fits, capability-isolated source/outer workers."""
from common import *
from data import fit_initial,fit_anchor
from worker import static,dynamic

def run(cap,phase,scope):
    configure(cap);barrier('P1-complete.json');require(scope in ['inner','outer'],'Scope')
    rs=contract()['inner_roles'] if scope=='inner' else contract()['roles']
    if scope=='outer':barrier('P3-complete.json')
    tag=f'{scope}-{phase}-{cap}-'+str(time.time_ns());hashes=code_seal(tag)
    try:
        jobs=[]
        if phase=='dynamic':
            if scope=='inner':
                jobs=[dict(role_id=r['id'],arm=arm,recipe=rec,seed=SEEDS[0]) for r in rs for rec in RECIPES for arm in DYNAMIC if capfor(arm)==cap]
            else:
                jobs=[j for j in read(OUT/'selections/outer-fit-jobs.json')['dynamic'] if capfor(j['arm'])==cap]
            dynamic(jobs)
        else:
            selected=read(OUT/'selections/outer-fit-jobs.json')['static'] if phase=='static' and scope=='outer' else None
            for i,r in enumerate(rs):
                if phase=='initial':
                    require(cap in ['G','E'],'Initial capability')
                    for g in GAMMAS:fit_initial(r,'post' if cap=='E' else 'pre',g)
                elif phase=='anchor':fit_anchor(r,cap)
                elif phase=='static':
                    require(cap in ['P','G'],'Static capability')
                    gs=GAMMAS if scope=='inner' else [j['gamma'] for j in selected if j['role_id']==r['id'] and j['arm']=='R-'+cap]
                    for g in gs:static(r,'R-'+cap,g)
                else:raise RuntimeError('Unknown fit phase')
                progress(scope+'_'+phase,capability=cap,completed=i+1,total=len(rs));flush_reads(tag)
        codecheck(hashes);flush_reads(tag)
        immutable(OUT/'workers'/(tag+'.json'),dict(passed=True,scope=scope,phase=phase,capability=cap,jobs=len(jobs)))
    except BaseException as e:failure(tag,e);raise

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--cap',choices=['P','G','E'],required=True);p.add_argument('--phase',choices=['initial','anchor','static','dynamic'],required=True);p.add_argument('--scope',choices=['inner','outer'],required=True)
    a=p.parse_args();run(a.cap,a.phase,a.scope)
