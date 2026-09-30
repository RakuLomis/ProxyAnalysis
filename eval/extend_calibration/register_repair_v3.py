"""One-time repair registration: inspect generation only; preserve every original artifact."""
from collections import Counter
from formal_common import *
from formal_generate import valid

def main():
    target=OUT/'repair-02/compatibility.json';assert not target.exists(),'Registration is immutable'
    assert not (OUT/'runner.lock').exists()
    oldpath=OUT/'execution-contract.json';old=read(oldpath);oldhash=sha(oldpath)
    failure=OUT/'generation-failure.json';f=read(failure)
    assert f=={'classification_started':False,'error':'''AttributeError("'str' object has no attribute 'open'")''',
               'kind':'paired','scenario':'W-shadowsocks-f0-g0-r0'}
    assert not (OUT/'classifiers').exists() and not (OUT/'restricted-prediction-seal.json').exists()
    before=OUT/'repair-02/before'
    changed=[]
    for path,h in old['files'].items():
        if sha(path)!=h:
            assert Path(path).name in ['formal_common.py','formal_generate.py','formal_classify.py']
            assert sha(before/Path(path).name)==h
            changed.append({'path':path,'before_sha256':h,'after_sha256':sha(path)})
    seals={};files={};counts=Counter();rows=0
    for p in sorted((OUT/'generation').glob('*/*/complete.json')):
        done=read(p);assert done['contract']==oldhash and done['cuda'] and done['roundtrip_passed']
        name=p.parent.name;kind=p.parent.parent.name;track=metadata(name)['track'];counts[(track,kind)]+=1
        assert done['scenario']==name and done['kind']==kind
        assert done['redraws']==done['fallbacks']==0
        for path,h in done['files'].items():
            q=Path(path);assert q.resolve().parent==p.parent.resolve() and sha(q)==h
            files[str(q)]={'sha256':h,'mtime_ns':q.stat().st_mtime_ns}
        bundle=Bundle(PREP/'packages'/kind/name,kind);query=bundle.get('U_pre')
        arms={'center','marginal','paired','cyclic'} if kind=='paired' else {'group'}
        for seed in SEEDS:
            frame=pd.read_parquet(p.parent/f'samples-{seed}.parquet')
            assert set(frame.arm)==arms and set(frame.session_id)==set(query.session_id)
            assert len(frame)==72*8*len(arms) and not frame.duplicated(['arm','session_id','view']).any()
            assert frame.groupby(['arm','session_id']).view.apply(lambda x:set(x)==set(range(8))).all()
            valid(frame[FEATURES[track]].to_numpy(),track,frame.F.to_numpy() if track=='T' else None)
            if track=='T':assert frame.F.eq(frame.session_id.map(query.set_index('session_id').F)).all()
            rows+=len(frame)
        seals[str(p.resolve())]=sha(p)
        files[str(p)]={'sha256':sha(p),'mtime_ns':p.stat().st_mtime_ns}
    assert dict(counts)=={('T','group'):480,('T','paired'):480,('W','group'):121,('W','paired'):121}
    write(OUT/'repair-02/preserved-files.json',files)
    write(target,{'passed':True,'old_contract_sha256':oldhash,'resolved_failure_sha256':sha(failure),
          'generation_seals':seals,'changed_sources':changed,'validated_scenarios':601,'validated_sample_rows':rows,
          'counts':{f'{a}/{b}':n for (a,b),n in counts.items()},'preserved_files_sha256':sha(OUT/'repair-02/preserved-files.json'),
          'only_generation_compatible':True,'scientific_changes':False})
    freeze()
    print('Repair registered; validated 601 scenarios and',rows,'generated rows',flush=True)

if __name__=='__main__':main()
