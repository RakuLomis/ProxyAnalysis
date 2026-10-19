"""Append-only R5 queue forecast from completed NER1 metadata, no model reads."""
from pathlib import Path
import sys,heapq,math
sys.path.insert(0,str(Path(__file__).resolve().parent/'deproxy_moment_game_v1_numeric_repair'))
from common import *

def queue(costs,workers):
    total=0.
    for start in range(0,len(costs),32):
        slots=[0.]*workers
        for duration in costs[start:start+32]:
            t=heapq.heappop(slots);heapq.heappush(slots,t+duration)
        total+=max(slots)
    return total

def main():
    configure('coordinator');begin('R5-queue-forecast')
    try:
        completion=read(OUT/'completion.json');require(completion['integrated_pilot_verified'],'Only a completed engineering pilot can have a full queue forecast')
        codecheck();source_hash=sha(Path(__file__))
        choice=read(OUT/'tests/backend-choice.json');workers=choice['workers']
        df=pd.read_parquet(OUT/'tests/integrated-P1-inventory.parquet')
        phases={}
        for p in (OUT/'tests').glob('R4-*.json'):
            if 'export' not in p.name:phases[p.stem]=read(p)
        costs={}
        for (kind,arm,g),part in df.groupby(['kind','arm','gamma']):
            a=part.seconds.to_numpy();costs[(kind,arm,float(g))]=dict(n=len(a),median=float(np.median(a)),p90=float(np.quantile(a,.9)),maximum=float(a.max()))
        synth=[]
        for p in (OUT/'tests').glob(f'R3-synthetic-r*-C{workers}.parquet'):synth.extend(pd.read_parquet(p).to_dict('records'))
        sf=pd.DataFrame(synth);sf['rows']=sf.problem_key.map(lambda s:int(s.split('-')[1]));shape={}
        for g in GAMMAS:
            for kind,small,large in [('initial',192,352),('refit',384,704)]:
                a=sf[(sf.gamma==g)&(sf.rows==small)].seconds.median();b=sf[(sf.gamma==g)&(sf.rows==large)].seconds.median()
                shape[(kind,g)]=max(352/192,float(b/a))
        def t(kind,arm,g,mode,outer=False):
            profile=costs[(kind,arm,g)];v=profile[mode]
            return v*(shape[('initial' if kind=='initial' else 'refit',g)] if outer else 1.)
        # Calibrate queue overhead against actual integrated initial/static phases.
        overhead={};measured={}
        for kind,caps in [('initial',['G','E']),('static',['P','G'])]:
            for cap in caps:
                arm=('pre' if cap=='G' else 'post') if kind=='initial' else 'R-'+cap
                part=df[(df.kind==kind)&(df.arm==arm)]
                simulation=queue(part.seconds.tolist(),workers)
                actual=phases[f'R4-{kind}-{cap}'];meta_time=sum(i['seconds'] for i in read(OUT/'budget.json')['items'] if i['stage']==f'R4-{kind}-{cap}')
                overhead[(kind,cap)]=max(1.,meta_time/max(simulation,1e-12));measured[f'{kind}-{cap}']=dict(heads=len(part),queue_seconds=simulation,phase_seconds=meta_time,overhead_factor=overhead[(kind,cap)])
        # Dynamic residual is intentionally conservative: it includes capture,
        # diagnostics, data preparation, persistence, and head queue overhead.
        pathrates={}
        for cap in ['P','G','E']:
            part=df[(df.kind=='refit')&df.arm.map(lambda a:capfor(a)==cap)]
            sim=queue(part.seconds.tolist(),workers)
            sec=sum(i['seconds'] for i in read(OUT/'budget.json')['items'] if i['stage']==f'R4-dynamic-{cap}')
            n=len(part);residual=max(0.,sec-sim)
            require(residual>0,'No positive separately attributable dynamic residual; forecast undetermined')
            pathrates[cap]=residual/n;measured['dynamic-'+cap]=dict(paths=n,phase_seconds=sec,head_queue_seconds=sim,nonhead_residual_seconds=residual,seconds_per_path=residual/n)
        old=read(OLD/'manifests/contract.json');rs=old['inner_roles'];outer=old['roles']
        done={(j['role_id'],j['arm'],j['recipe']['id'],j['seed']) for j in registration()['jobs']}
        pilotids={r['id'] for r in roles()};components=[]
        for mode in ['median','p90']:
            margin=1. if mode=='median' else 1.25
            for side,cap in [('pre','G'),('post','E')]:
                vals=[];ni=no=0
                for r in rs:
                    if r['id'] in pilotids:continue
                    for g in GAMMAS:vals.append(t('initial',side,g,mode));ni+=1
                for r in outer:
                    for g in GAMMAS:vals.append(t('initial',side,g,mode,True));no+=1
                components.append(dict(mode=mode,component='initial-'+side,inner=ni,outer=no,seconds=margin*queue(vals,workers)*overhead[('initial',cap)]))
            for arm,cap in [('R-P','P'),('R-G','G')]:
                vals=[];ni=no=0
                for r in rs:
                    if r['id'] in pilotids:continue
                    for g in GAMMAS:vals.append(t('static',arm,g,mode));ni+=1
                worst=max(t('static',arm,g,mode,True) for g in GAMMAS)
                for r in outer:
                    for policy in range(2):vals.append(worst);no+=1
                components.append(dict(mode=mode,component='static-'+arm,inner=ni,outer=no,seconds=margin*queue(vals,workers)*overhead[('static',cap)]))
            # Explicit capability/lr queues. Tail batches do not get divided by c.
            for cap in ['P','G','E']:
                vals=[];ni=no=0
                for lr in [.0003,.001]:
                    for r in rs:
                        for rec in RECIPES:
                            if rec['lr']!=lr:continue
                            for arm in DYNAMIC:
                                if capfor(arm)!=cap or (r['id'],arm,rec['id'],SEEDS[0]) in done:continue
                                vals.append(t('refit',arm,rec['gamma'],mode));ni+=1
                for r in outer:
                    for policy in range(2):
                        for seed in SEEDS:
                            for arm in DYNAMIC:
                                if capfor(arm)==cap:vals.append(max(t('refit',arm,g,mode,True) for g in GAMMAS));no+=1
                components.append(dict(mode=mode,component='refit-'+cap,inner=ni,outer=no,seconds=margin*queue(vals,workers)))
                # Adam is already model-parallel. Its measured per-path rate is
                # never divided by head concurrency or stream count.
                components.append(dict(mode=mode,component='Adam-capture-diagnostics-'+cap,inner=ni,outer=no,
                    seconds=margin*pathrates[cap]*(ni+(352/192)*no)))
            anchor=[i['seconds'] for i in read(OLD/'budget.json')['items'] if i.get('kind')=='inverse-anchor']
            require(len(anchor)==24,'Original anchor accounting')
            rate=float(np.median(anchor) if mode=='median' else np.quantile(anchor,.9))
            components.append(dict(mode=mode,component='remaining-anchors',inner=1416,outer=120,seconds=margin*rate*(1416+(352/192)*120)))
        # Queue extrapolation is metadata based, not a measured full run. Account
        # the original replay/inference allowance and a future process floor.
        b=read(OUT/'budget.json');center=sum(c['seconds'] for c in components if c['mode']=='median')*1.05+60+b['used_seconds']
        conservative=sum(c['seconds'] for c in components if c['mode']=='p90')*1.05+60+b['used_seconds']
        forecast=dict(version=2,qualified=True,feasible=conservative<=69120,workers=workers,source_sha256=source_hash,
            center_seconds=center,conservative_seconds=conservative,center_hours=center/3600,conservative_hours=conservative/3600,
            gate_seconds=69120,activity_used_before_forecast=b['used_seconds'],components=components,measured_queue_checks=measured,
            head_profiles=[dict(kind=k[0],arm=k[1],gamma=k[2],**v) for k,v in costs.items()],
            outer_shape_factors=[dict(kind=k[0],gamma=k[1],factor=v) for k,v in shape.items()],
            empirical_policy_not_runtime_bound=True,real_outer_conditioning_observed=False,
            limitations=['Dynamic phase residual includes all nonhead overhead; rate depends on bucket fill.',
                'Outer gamma/lr are not selected; use worst gamma head time and at least 352/192 shape factor.',
                'Two-role extended-recipe strata are small; P90 plus 25% is an engineering policy, not a confidence bound.',
                'Future full scheduler must preserve the same 32-head admission, stream and accounting policy.'],
            full_experiment_enabled=False,query_read=False,H_scored=False,supersedes=rel(OUT/'cost-forecast-revised.json'))
        write(OUT/'cost-forecast-revision-02.json',forecast,True)
        revised=dict(completion,full_scope_budget_feasible=forecast['feasible'],forecast_status='policy_estimate_feasible' if forecast['feasible'] else 'policy_estimate_over_budget',
            cost_revision=rel(OUT/'cost-forecast-revision-02.json'),supersedes=rel(OUT/'completion.json'))
        write(OUT/'completion-revision-02.json',revised,True)
        write(OUT/'completion-current.json',dict(path=rel(OUT/'completion-revision-02.json'),sha256=sha(OUT/'completion-revision-02.json')),True)
        progress('R5_queue_forecast_complete',center_hours=center/3600,conservative_hours=conservative/3600,full_experiment_enabled=False)
    except BaseException as e:failure('R5-queue-forecast',e);raise
    finally:end('R5-queue-forecast')

if __name__=='__main__':main()
