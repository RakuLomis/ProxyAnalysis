"""Reuse frozen content-role assignments, export six-class C/U/H permissions."""
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
import sys
import pandas as pd

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'src'))
from proxy_analysis.extend_calibration.audit import read,write,file_hash
from proxy_analysis.extend_calibration.bundles import Bundle
BASE=ROOT/'outputs/extend-calibration-20260930/run-01';NEW=BASE/'extraction-03';OUT=NEW/'training-preparation-01'
FEATURES={'W':['W_up','W_down','P_up','P_down','R_up','R_down'],'T':['U_up','U_down','E_up','E_down','R_up','R_down','F']}


def export_one(task):
    track,protocol,scenario,group=task
    features=FEATURES[track];post_targets=features if track=='W' else features[:-1]
    data=pd.read_parquet(NEW/f'full-{track}-features.parquet')
    pre=data[data.side.eq('pre')].set_index('session_id');post=data[data.side.eq('post')].set_index('session_id')
    ids={role:group.loc[group.role.eq(role),'session_id'].tolist() for role in ['C','U','H']}
    assert [len(ids[r]) for r in ['C','U','H']]==[24,72,24]
    assert all(not set(ids[a])&set(ids[b]) for a,b in [('C','U'),('C','H'),('U','H')])
    assert group.groupby('content_id').role.nunique().eq(1).all()
    def frame(role,side):
        return group[group.role.eq(role)][['session_id','content_id','repetition']].merge(
            (pre if side=='pre' else post)[features],left_on='session_id',right_index=True,validate='one_to_one').sort_values('session_id').reset_index(drop=True)
    c,cp,u,h=frame('C','pre'),frame('C','post'),frame('U','pre'),frame('H','post')
    labels=group[group.role.isin(['C','U'])][['session_id','label_id']].sort_values('session_id')
    packages={'paired':{'C_pre':c,'C_post':cp,'U_pre':u,'labels':labels},
        'group':{'G_pre':c[['content_id',*features]],'G_post':cp[['content_id',*post_targets]],'U_pre':u},
        'reference':{'U_post':frame('U','post')},
        'scoring':{'H_post':h[['session_id',*features]],
                   'H_labels':group[group.role.eq('H')][['session_id','content_id','repetition','label_id','business_role']]}}
    for kind,frames in packages.items():
        folder=OUT/'packages'/kind/scenario;folder.mkdir(parents=True,exist_ok=True)
        assert not (folder/'manifest.json').exists()
        files={}
        for name,f in frames.items():
            path=folder/f'{name}.parquet';f.to_parquet(path,index=False)
            files[name]={'filename':path.name,'sha256':file_hash(path),'columns':list(f.columns),'rows':len(f)}
        manifest={'kind':kind,'scenario':scenario,'track':track,'protocol':protocol,'files':files,
            'numeric_classifier_features':features,'repetitions':[1,2,3,4],'formal_training_allowed':False,
            'group_identity_fields_removed':kind=='group','reference_requires_restricted_prediction_seal':kind=='reference'}
        if kind!='group':manifest.update({role+'_sessions':ids[role] for role in ['C','U','H']})
        # Group manifest never carries paired post row identities.
        write(folder/'manifest.json',manifest)
    b=Bundle(OUT/'packages/paired'/scenario,'paired')
    for role in ['U_post','H_pre','H_post']:
        try:b.get(role)
        except PermissionError:pass
        else:raise AssertionError('forbidden role readable')
    g=Bundle(OUT/'packages/group'/scenario,'group')
    assert set(g.get('G_pre'))=={'content_id',*features} and set(g.get('G_post'))=={'content_id',*post_targets}
    try:g.get('labels')
    except PermissionError:pass
    else:raise AssertionError('group reads labels')
    assert set(b.get('labels').session_id)==set(ids['C']+ids['U'])
    return {'scenario':scenario,'track':track,'protocol':protocol,'C':24,'U':72,'H':24,'permission_negative_tests_passed':True}


def main():
    OUT.mkdir(exist_ok=True);assert not (OUT/'package-gate.json').exists()
    assert read(NEW/'full-gate.json')['W_passed']==600
    assert read(NEW/'clock-anchors-01/summary.json')['bracket_failed']==0
    assert read(NEW/'identity-source-evidence/qualification.json')['qualified_for_registered_entity_grouping']
    assert read(NEW/'verification-01/verification.json')['independent_event_counts']
    pool=pd.read_parquet(BASE/'extraction-01/metadata-qualified-pool.parquet')
    original=ROOT/'outputs/cross-business-calibration-0916/run-01/roles.parquet'
    old=pd.read_parquet(original);template=old[old.protocol.eq('SHADOWSOCKS')]
    fields=['business_group','rotation','role','business_role','fold','split','content_id','label_id']
    template=template[fields].drop_duplicates()
    tasks=[];roles=[]
    for track in ['W','T']:
        for protocol,visits in pool.groupby('protocol'):
            if track=='T' and protocol=='anytls':continue
            linked=template.merge(visits[['session_id','content_id','repetition','label']],on='content_id',validate='many_to_many')
            assert linked.label.eq(linked.label_id).all()
            for (fold,business,rotation),g in linked.groupby(['fold','business_group','rotation']):
                scenario=f'{track}-{protocol}-f{fold}-g{business}-r{rotation}'
                g=g.copy();g['scenario']=scenario;g['protocol']=protocol;g['track']=track
                assert len(g)==120 and g.session_id.is_unique and g.label_id.nunique()==6
                roles.append(g.drop(columns='label'));tasks.append((track,protocol,scenario,g))
    assert len(tasks)==1080
    pd.concat(roles,ignore_index=True).to_parquet(OUT/'roles.parquet',index=False)
    results=[]
    with ProcessPoolExecutor(max_workers=4) as ex:
        for i,r in enumerate(ex.map(export_one,tasks),1):
            results.append(r)
            if i%120==0:print(f'Permission packages {i}/1080',flush=True)
    pd.DataFrame(results).to_parquet(OUT/'scenario-audit.parquet',index=False)
    write(OUT/'package-gate.json',{'passed':True,'W_scenarios':600,'T_scenarios':480,'package_directories':4320,
        'permission_negative_tests':1080*4,'role_template_sha256':file_hash(original),
        'training_repetitions':[1,2,3,4],'test_pre_exported':False,'U_post_in_restricted_packages':False,
        'group_post_identity_exported':False,'OS_security_sandbox_claimed':False,'formal_training_allowed':False})


if __name__=='__main__':main()
