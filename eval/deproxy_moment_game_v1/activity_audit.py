"""Conservative worker-wall complement, including otherwise untimed reuse/load math."""
from common import *

def audit():
    barrier('P1-numeric-complete.json');b=read(OUT/'budget.json');rows=[]
    require(not any(v['kind']=='P1-worker-wall-complement' for v in b['items']),'Complement cannot be charged twice')
    markers=list((OUT/'workers').glob('*.json'))
    # Preserve the initial guard failure; it also consumed real startup/load and
    # replay work outside the individually timed original-coordinate fits.
    markers+=list((OUT/'failures').glob('initial-G-1792151315422787400-*.json'))
    for marker in markers:
        failed=marker.parent.name=='failures'
        if failed:tag='initial-G-1792151315422787400';phase='initial';cap='G'
        else:
            tag=marker.stem;v=read(marker);phase=v['phase'];cap=v['capability']
        start=(OUT/'code'/tag/'seal.json').stat().st_mtime;end=marker.stat().st_mtime
        covered=0.;events=0
        for e in b['items']:
            point=None
            if e['kind']=='convex-head':
                path=ROOT/e['path'];side='pre' if cap=='G' else 'post'
                matches=(phase=='initial' and '/initial-classifiers/' in path.as_posix() and path.parent.name==side) or (
                    phase=='static' and '/R-'+cap+'/' in path.as_posix()) or (
                    phase=='dynamic' and any('/'+arm+'/' in path.as_posix() for arm in DYNAMIC if capfor(arm)==cap))
                if matches:point=path.with_suffix('.quality.json')
            elif e['kind']=='inverse-anchor' and phase=='anchor' and e['capability']==cap:
                point=OUT/'anchors'/e['role_id']/(cap+'.json')
            elif e['kind']=='dynamic-Adam' and phase=='dynamic' and e['capability']==cap:
                j=e['batch_jobs'][0];point=OUT/'models'/j['role_id']/j['arm']/j['recipe']['id']/str(j['seed'])/'terminal.json'
            if point is not None and point.exists() and start<=point.stat().st_mtime<=end:
                covered+=e['seconds'];events+=1
        wall=max(0.,end-start);gap=max(0.,wall-covered)
        rows.append(dict(worker=tag,retained_failure=failed,phase=phase,capability=cap,wall_seconds=wall,
            individually_charged_seconds=covered,numerical_events=events,complement_upper_bound_seconds=gap,
            includes_metadata_IO_and_process_overhead=True))
    require(len(rows)==10,'Nine successful workers plus retained first initialization guard stop')
    save(OUT/'tests/P1-worker-activity-audit.parquet',pd.DataFrame(rows));gap=sum(v['complement_upper_bound_seconds'] for v in rows)
    debit('P1-worker-wall-complement',gap,includes_non_numeric_overhead=True,conservative_not_exact_GPU_time=True)
    immutable(OUT/'tests/P1-activity-audit.json',dict(passed=True,workers=len(rows),additional_upper_bound_seconds=gap,
        method='sum of worker filesystem wall intervals minus individually charged fits/anchors/Adam in the same intervals',
        IO_kept_in_complement_conservatively=True,old_failure_retained=True,training_replays_not_assumed_free=True))

if __name__=='__main__':audit()
