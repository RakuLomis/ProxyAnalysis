"""Pre-score fixed P1 cost decision. No query or target U/H access."""
from common import *
from cuda_checks import synthetic
from engine import Engine

def bench():
    configure('tests');barrier('P1-numeric-complete.json');tag='P1-outer-shape-01';hashes=code_seal(tag);t=time.perf_counter();rows=[]
    try:
        for n,c in [(192,16),(352,22)]:
            d=synthetic(n,c)
            head=dict(W=torch.zeros((6,96),device='cuda',dtype=torch.float64),c=torch.zeros(6,device='cuda',dtype=torch.float64))
            jobs=[dict(arm='F-P',recipe=RECIPES[0],seed=SEEDS[0]+i) for i in range(32)]
            eng=Engine([d]*32,jobs,[head]*32,streams=True);eng.capture();eng.advance(10)
            torch.cuda.synchronize();ts=time.perf_counter();eng.advance(100);torch.cuda.synchronize();sec=time.perf_counter()-ts
            rows.append(dict(rows=n,conditions=c,models=32,streams=8,steps=100,seconds=sec,seconds_per_model_step=sec/3200,
                allocated_MiB=torch.cuda.memory_allocated()/1048576,reserved_MiB=torch.cuda.memory_reserved()/1048576))
            del eng;torch.cuda.empty_cache()
        immutable(OUT/'tests/P1-shape-benchmark.json',dict(passed=True,synthetic=True,formal_paths=0,benchmarks=rows));codecheck(hashes)
    except BaseException as e:failure(tag,e);raise
    finally:debit('synthetic-shape-benchmark',time.perf_counter()-t,formal_paths=0);flush_reads(tag)

def forecast():
    barrier('P1-numeric-complete.json');require(read(OUT/'tests/P1-shape-benchmark.json')['passed'],'Shape benchmark')
    require(read(OUT/'tests/P1-CUDA-01/replay.json')['passed'] and read(OUT/'tests/P1-math-03/math.json')['passed'],'Math/CUDA acceptance')
    d=pd.read_parquet(OUT/'tests/P1-head-quality.parquet');budget=read(OUT/'budget.json');components=[]
    # Inner estimates are stratified by side/arm and gamma. Outer work uses the
    # observed shape factor (at least 352/192) and worst gamma because selections
    # have not yet been made and no validation data may guide this forecast.
    br=read(OUT/'tests/P1-shape-benchmark.json')['benchmarks'];ratio=max(352/192,br[1]['seconds']/br[0]['seconds'])
    def row(name,v,inner_n,outer_n):
        require(len(v)>0,'Missing cost stratum '+name)
        med=float(np.median(v));p90=float(np.quantile(v,.9));mx=float(np.max(v))
        components.append(dict(component=name,samples=len(v),median_seconds=med,p90_seconds=p90,max_seconds=mx,
            remaining_inner_problems=int(inner_n),remaining_outer_problems=int(outer_n),outer_factor=ratio,
            center_seconds=med*(inner_n+ratio*outer_n),conservative_seconds=1.25*p90*(inner_n+ratio*outer_n)))
    for side in ['pre','post']:
        for g in GAMMAS:
            v=d[(d.category=='initial')&(d.arm==side)&(d.gamma==g)]
            row('initial-'+side+'-'+gamma_tag(g),v.seconds,720-12,60)
    for arm in ['R-P','R-G']:
        part=d[(d.category=='static')&(d.arm==arm)]
        for g in GAMMAS:
            v=part[part.gamma==g];row('static-'+arm+'-'+gamma_tag(g),v.seconds,720-12,0)
        worst=part.groupby('gamma').seconds.quantile(.9).idxmax();row('outer-static-'+arm,part[part.gamma==worst].seconds,0,120)
    for arm in DYNAMIC:
        part=d[(d.category=='dynamic-refit')&(d.arm==arm)]
        for g in GAMMAS:
            v=part[part.gamma==g];row('refit-'+arm+'-'+gamma_tag(g),v.seconds,1440-len(v),0)
        worst=part.groupby('gamma').seconds.quantile(.9).idxmax();row('outer-refit-'+arm,part[part.gamma==worst].seconds,0,360)
    dynamic=[v for v in budget['items'] if v['kind']=='dynamic-Adam'];require(sum(v['paths'] for v in dynamic)==88,'88 pilot Adam paths')
    rates=[v['seconds']/v['paths'] for v in dynamic]
    row('Adam-2000-path',rates,17280-88,1440)
    anchor=[v['seconds'] for v in budget['items'] if v['kind']=='inverse-anchor'];row('inverse-anchor-bundle',anchor,1440-24,120)
    center=sum(v['center_seconds'] for v in components);upper=sum(v['conservative_seconds'] for v in components)
    # Five percent numerical replay/prediction allowance plus one minute floor.
    center_total=budget['used_seconds']+center*1.05+60;upper_total=budget['used_seconds']+upper*1.05+60
    good=upper_total<=69120
    out=dict(passed=good,activity_used_seconds=budget['used_seconds'],center_total_seconds=center_total,conservative_total_seconds=upper_total,
        center_total_hours=center_total/3600,conservative_total_hours=upper_total/3600,automatic_promotion_limit_seconds=69120,activity_cap_seconds=86400,
        remaining_scope='all arms, 720 inner contexts; up to 60 outer roles and both policy recipes, three seeds',
        counts=dict(P1_heads=232,P1_dynamic_paths=88,full_heads_upper=27960,full_dynamic_paths_upper=18720),
        outer_shape_factor=ratio,components=components,query_labels_read=False,H_U_read=False,
        decision='promote_full' if good else 'stop_budget_forecast_requires_user',
        estimates_are_not_runtime_guarantees=True,no_scope_reduction=True)
    immutable(OUT/'manifests/P1-cost-forecast.json',out)
    if good:
        seal(OUT/'manifests/P1-complete.json',[OUT/'manifests/P1-cost-forecast.json',OUT/'manifests/P1-numeric-complete.json',OUT/'tests/P1-CUDA-01/replay.json',OUT/'tests/P1-math-03/math.json',OUT/'tests/P1-shape-benchmark.json'],passed=True,query_reads=0)
        progress('P1_accepted',forecast_hours=upper_total/3600)
    else:progress('stop_budget_forecast_requires_user',forecast_hours=upper_total/3600,limit_hours=19.2,query_reads=0)
    return out

if __name__=='__main__':
    try:bench();forecast()
    except BaseException as e:failure('P1-cost',e);raise
