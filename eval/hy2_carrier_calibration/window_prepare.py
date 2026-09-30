"""Explicit user-approved tail exception; freeze packages before any fitting."""
import itertools
from experiment import *
def main():
    review=read(OUT/'window-review.json');gate=read(OUT/'window-gate.json')
    assert review['unobserved_members']==1 and review['old_carrier_packets_included_in_later_main_input']==0
    assert gate['reasons']=={'members_without_window_packets':1} and gate['main_carrier_reused']==0
    acceptance={'passed':True,'user_confirmed':True,'rule':'actual observed packets only; retain visit; no fabricated events',
       'exception_session':'1d5e7275-4ff2-4836-a1ed-fda753879679',
       'exception_member':'c310dd91-14f2-4ad3-b9bc-b2a4ac174c16','missingness_as_model_input':False,
       'original_gate_hash':sha(OUT/'window-gate.json'),'review_hash':sha(OUT/'window-review.json')}
    write(OUT/'accepted-window-gate.json',acceptance)
    v=pd.read_parquet(PRIOR/'candidate-visits.parquet');summary=pd.read_parquet(OUT/'side-summaries.parquet')
    classes=sorted(v.label_id.unique());groups=list(itertools.combinations(classes,2));write(OUT/'business-groups.json',{'classes':classes,'groups':groups})
    roles=[]
    for fold in range(5):
      for bg,new in enumerate(groups):
       for rot in range(6):
        name=f'HYSTERIA2-f{fold}-g{bg}-r{rot}';train=v[v.fold!=fold];held=v[v.fold==fold]
        chosen=[]
        for label in classes:
            if label in new:continue
            contents=sorted(train[train.label_id==label].content_id.unique());assert len(contents)==4
            # Config registration uses its class position, not result-dependent order.
            ordered=['github.com::repository_view','youtube.com::search_results_view','wikipedia.org::article_view','youtube.com::video_playback','developer.mozilla.org::document_view']
            chosen+=list(list(itertools.combinations(contents,2))[(rot+ordered.index(label))%6])
        cal=train[train.content_id.isin(chosen)];u=train[~train.content_id.isin(chosen)]
        assert (len(cal),len(u),len(held))==(24,56,20)
        for role,frame in [('C',cal),('U',u),('H',held)]:
            for r in frame.to_dict('records'):roles.append({k:r[k] for k in ['session_id','content_id','label_id','repetition']}|{'scenario':name,'role':role,'fold':fold,'business_group':bg,'rotation':rot})
        identity=['session_id','content_id','repetition']
        def side(frame,s):return frame[identity].merge(summary[summary.side==s][['session_id',*FEATURES]],on='session_id',validate='one_to_one').sort_values('session_id').reset_index(drop=True)
        cp=side(cal,'pre');cq=side(cal,'post');up=side(u,'pre')
        for kind in ['paired','group']:
            dest=OUT/'bundles'/kind/name;dest.mkdir(parents=True,exist_ok=True)
            tables={'C_pre':cp,'C_post':cq,'U_pre':up}
            if kind=='group':tables={**tables,'C_pre':cp[['content_id',*FEATURES]].sort_values(['content_id',*FEATURES]),'C_post':cq[['content_id',*FEATURES]].sort_values(['content_id',*FEATURES])}
            else:tables['labels']=train[['session_id','label_id']]
            for key,f in tables.items():f.to_parquet(dest/(key+'.parquet'),index=False)
            meta={'kind':kind,'scenario':name,'fold':fold,'business_group':bg,'rotation':rot,'new_labels':list(new),
                  'hashes':{key:sha(dest/(key+'.parquet')) for key in tables}}
            if kind=='paired':meta.update(C_sessions=sorted(cal.session_id),C_contents=sorted(chosen),U_contents=sorted(u.content_id.unique()))
            write(dest/'manifest.json',meta)
        for where,tables in [('evaluation',{'H_post':side(held,'post'),'H_labels':held[['session_id','content_id','label_id']]}),('reference',{'U_post':side(u,'post')})]:
            dest=OUT/where/name;dest.mkdir(parents=True,exist_ok=True)
            for key,f in tables.items():f.to_parquet(dest/(key+'.parquet'),index=False)
    role=save('roles',roles);assert len(role)==30000
    for _,g in role.groupby('scenario'):
        assert g.session_id.nunique()==100
        assert g.groupby('content_id').role.nunique().eq(1).all()
    files=[*Path(__file__).parent.glob('window_*.py'),Path(__file__).with_name('experiment.py'),ROOT/'configs/hy2-carrier-calibration-0916.yaml',OUT/'accepted-window-gate.json',OUT/'roles.parquet',OUT/'business-groups.json']
    contract={'files':{str(p):sha(p) for p in files},'scenarios':300,'restricted_models':5400,'reference_models':900,'cuda_required':True}
    if (OUT/'learning-contract.json').exists():assert read(OUT/'learning-contract.json')==contract
    else:write(OUT/'learning-contract.json',contract)
    write(OUT/'permission-gate.json',{'passed':True,'scenarios':300,'group_post_identity_removed':True,'U_post_separate':True,'H_pre_not_exported':True})
    print('300 scenarios frozen; no fitting performed',flush=True)
if __name__=='__main__':main()
