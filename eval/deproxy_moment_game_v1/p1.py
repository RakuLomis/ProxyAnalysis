"""Fixed P1, capability-isolated workers, no query loading or scientific score gate."""
from common import *
import subprocess

def command(args):
    remaining()
    result=subprocess.run([sys.executable,*args],cwd=ROOT)
    require(result.returncode==0,'P1 subprocess stopped; inspect preserved failure, no automatic retry')

def finish():
    # Metadata-only collection. Actual fits are performed by separate workers.
    rs=pilot_roles();rows=[];files=[]
    for r in rs:
        for side in ['pre','post']:
            for g in GAMMAS:
                p=OUT/'initial-classifiers'/r['id']/side/(gamma_tag(g)+'.quality.json');v=read(p)
                require(v['passed'],'Unaccepted initial head');rows.append(dict(role=r['id'],arm=side,category='initial',**v));files.append(p)
        for cap in ['P','G']:
            p=OUT/'anchors'/r['id']/(cap+'.pt');require(p.exists(),'Missing inverse anchor');files.append(p)
    for r in rs:
        for arm in ['R-P','R-G']:
            for g in GAMMAS:
                p=OUT/'models'/r['id']/arm/gamma_tag(g)/str(SEEDS[0]);verifyseal(p/'complete.json')
                v=read(p/'head.quality.json');rows.append(dict(role=r['id'],category='static',**v));files.append(p/'complete.json')
    # Count exactly the predetermined H01 plus fixed two-role recipe extension.
    for r in rs:
        recs=RECIPES if (r['target'],r['group']) in [('shadowsocks','G0'),('vmess','G2')] else RECIPES[:1]
        for rec in recs:
            for arm in DYNAMIC:
                p=OUT/'models'/r['id']/arm/rec['id']/str(SEEDS[0]);verifyseal(p/'complete.json')
                v=read(p/'head.quality.json');rows.append(dict(role=r['id'],category='dynamic-refit',**v));files.append(p/'complete.json')
    require(len(rows)==232,'P1 232 convex heads')
    save(OUT/'tests/P1-head-quality.parquet',pd.DataFrame(rows));files.append(OUT/'tests/P1-head-quality.parquet')
    seal(OUT/'manifests/P1-numeric-complete.json',files,heads=232,dynamic_paths=88,anchors=24,query_reads=0,H_U_reads=0)
    progress('P1_numeric_complete',heads=232,dynamic_paths=88,anchors=24)

def run():
    barrier('P0-complete.json')
    # The first initialization process completed all heads but its final source
    # seal detected the development of the dispatcher. Keep that stop record.
    # Every saved head is replayed against the same original-coordinate
    # objective by classifier.fit before reuse; no training is repeated.
    immutable(OUT/'manifests/P1-engineering-revision-01.json',dict(
        retained_stops=['P1-math-01','P1-math-02','initial-G-1792151315422787400'],
        changes=['deterministic fixed prefix sums instead of unsupported CUDA cumsum',
            'correct local tensor variable names in prefix implementation',
            'dispatcher completed while first initialization ran; its source-guard stop is retained',
            'saved initial heads independently replay original loss and original-coordinate gradient before reuse',
            'sole-worker activity allowance cached per fit rather than re-reading growing JSON per closure'],
        model_loss_permissions_thresholds_unchanged=True,refit_old_heads=False,
        CUDA_replay='tests/P1-CUDA-01/replay.json',math='tests/P1-math-03/math.json'))
    for cap,phase in [('G','initial'),('E','initial'),('P','anchor'),('G','anchor'),('P','static'),('G','static'),('P','dynamic'),('G','dynamic'),('E','dynamic')]:
        command([str(CODE/'worker.py'),'--cap',cap,'--phase',phase])
    finish()

if __name__=='__main__':
    try:run()
    except BaseException as e:failure('P1-schedule',e);raise
