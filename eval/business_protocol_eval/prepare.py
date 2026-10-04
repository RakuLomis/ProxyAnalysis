"""Q01-Q04 metadata, role and global content isolation; no model fitting."""
from collections import defaultdict
import pandas as pd
from common import *


def roles_for(cohort, experiment, fold, target=None):
    hold = cohort.fold.eq(fold)
    if experiment == 'E1':
        train, test = ~hold, hold
    elif experiment == 'E2':
        train = ~hold & ~cohort.protocol.eq(target)
        test = hold & cohort.protocol.eq(target)
    elif experiment == 'I0':
        train = ~hold & cohort.protocol.eq(target)
        test = hold & cohort.protocol.eq(target)
    else:
        raise ValueError(experiment)
    return {'train': sorted(cohort.loc[train,'session_id']),
            'test': sorted(cohort.loc[test,'session_id']),
            'unused': sorted(cohort.loc[~(train|test),'session_id'])}


def verify_roles(cohort, role, experiment, fold, target):
    ix = cohort.set_index('session_id')
    tr, te = ix.loc[role['train']], ix.loc[role['test']]
    assert not set(tr.index) & set(te.index)
    assert not set(tr.content_id) & set(te.content_id)
    assert tr.fold.ne(fold).all() and te.fold.eq(fold).all()
    expected = {'E1':(480,120), 'E2':(384,24), 'I0':(96,24)}[experiment]
    assert (len(tr),len(te)) == expected
    assert tr.label_id.nunique() == te.label_id.nunique() == 6
    if experiment == 'E2':
        assert tr.protocol.ne(target).all() and te.protocol.eq(target).all()
    for _, g in tr.groupby(['protocol','label_id']):
        assert len(g)==16 and g.content_id.nunique()==4


def main():
    assert not (OUT/'gate-A.json').exists(), 'Preparation is frozen'
    paths = [OLD/'extraction-01/metadata-qualified-pool.parquet',
             EXTRACT/'full-W-features.parquet', EXTRACT/'training-preparation-01/roles.parquet',
             EXTRACT/'full-gate.json', EXTRACT/'clock-anchors-01/summary.json',
             EXTRACT/'identity-source-evidence/qualification.json', EXTRACT/'isolation-01/summary.json',
             EXTRACT/'verification-01/verification.json', EXTRACT/'training-preparation-01/preregistration.json']
    assert read(paths[3])['W_passed']==600
    assert read(paths[4])['bracket_failed']==0
    assert read(paths[5])['qualified_for_registered_entity_grouping']
    assert read(paths[7])['independent_event_counts']
    old_isolation=read(paths[6])
    for key in ['cross_fold_SYN_signatures','cross_fold_positive_IP_packet_hash_matches',
                'cross_fold_registered_carriers','repeated_raw_file_hashes','overlapping_windows']:
        assert old_isolation[key]==0
    # Verify frozen source hashes for the files used rather than trusting new hashes alone.
    prereg=read(paths[8]); registered=prereg['source_hashes']
    for p in paths:
        key=str(p.relative_to(ROOT))
        if key in registered: assert file_hash(p)==registered[key]
    visits=pd.read_parquet(paths[0]); w=pd.read_parquet(paths[1]); old=pd.read_parquet(paths[2])
    assert len(visits)==600 and visits.session_id.is_unique
    assert set(visits.protocol)==set(PROTOCOLS) and set(visits.repetition)=={1,2,3,4}
    assert visits.content_id.nunique()==30 and visits.label.nunique()==6
    assert visits.groupby(['protocol','content_id']).repetition.agg(set).map(lambda a:a=={1,2,3,4}).all()
    assert len(w)==1200 and not w.duplicated(['session_id','side']).any()
    assert set(w.side)=={'pre','post'} and set(w.session_id)==set(visits.session_id)
    valid_w(w[FEATURES].to_numpy())
    old=old[old.track.eq('W')]
    test=old[old.role.eq('H')][['session_id','content_id','fold','label_id']].drop_duplicates()
    assert len(test)==600 and test.session_id.is_unique
    assert test.groupby('content_id').fold.nunique().eq(1).all()
    cohort=visits[['session_id','protocol','content_id','repetition','label']].merge(
        test,on=['session_id','content_id'],validate='one_to_one')
    assert cohort.label.eq(cohort.label_id).all()
    assert set(cohort.fold)==set(range(5))
    assert cohort.groupby(['fold','label_id']).content_id.nunique().eq(1).all()
    # Every prior role, not just one rotation, must agree with the global fold.
    check=old.merge(cohort[['session_id','fold']].rename(columns={'fold':'global_fold'}),on='session_id',validate='many_to_one')
    assert check.role.eq('H').eq(check.fold.eq(check.global_fold)).all()
    cohort=cohort.drop(columns='label').sort_values(['protocol','content_id','repetition']).reset_index(drop=True)
    OUT.mkdir(parents=True,exist_ok=True)
    cohort.to_parquet(OUT/'cohort.parquet',index=False)
    cohort[['content_id','label_id','fold']].drop_duplicates().to_parquet(OUT/'global-folds.parquet',index=False)
    # Rebuild registered carrier/raw-file membership using frozen session scopes.
    entities=defaultdict(set); used_session_hashes={}
    for sid in cohort.session_id:
        folder=EXTRACT/'sessions'/sid
        scope=read(folder/'scope.json'); done=read(folder/'complete.json')
        for carrier in scope['carriers']:entities['carrier:'+carrier].add(sid)
        for name in ['raw/tun.pcap','raw/phys.pcap']:entities['raw:'+done['input_hashes'][name]].add(sid)
        for name in ['scope.json','complete.json']:
            p=folder/name;used_session_hashes[str(p.relative_to(ROOT))]=file_hash(p)
    conflicts=[]; scenarios=[]
    for experiment in ['E1','E2','I0']:
        for target in ([None] if experiment=='E1' else PROTOCOLS):
            for fold in range(5):
                name=f'{experiment}-{target or "all"}-f{fold}'
                role=roles_for(cohort,experiment,fold,target)
                verify_roles(cohort,role,experiment,fold,target)
                forbidden=set(role['test'])
                if experiment=='E2':
                    forbidden |= set(cohort.loc[cohort.protocol.eq(target)|cohort.fold.eq(fold),'session_id'])
                training=set(role['train'])
                for entity,members in entities.items():
                    if members & training and members & forbidden:conflicts.append({'scenario':name,'entity':entity})
                source=sorted(cohort[cohort.session_id.isin(training)].protocol.unique())
                meta={'scenario':name,'experiment':experiment,'target':target,'fold':fold,
                      'source_protocols':source,**role,'training_allowed':False}
                write(OUT/'roles'/f'{name}.json',meta)
                scenarios.append({'scenario':name,'experiment':experiment,'target':target,'fold':fold,
                                  'train':len(training),'test':len(role['test']),'unused':len(role['unused'])})
    assert not conflicts,conflicts
    pd.DataFrame(scenarios).to_parquet(OUT/'scenarios.parquet',index=False)
    generator_jobs=[]
    for fold in range(5):
        train=cohort[cohort.fold.ne(fold)]
        content_group={}
        for _,g in train.groupby('label_id'):
            ordered=sorted(g.content_id.unique(),key=lambda c:digest(['business-protocol-crossfit-v1',fold,c]))
            assert len(ordered)==4
            content_group.update({c:i for i,c in enumerate(ordered)})
        for protocol in PROTOCOLS:
            p=train[train.protocol.eq(protocol)]
            for group in range(4):
                query=p[p.content_id.map(content_group).eq(group)]
                fit=p[~p.session_id.isin(query.session_id)]
                assert len(query)==24 and len(fit)==72
                assert query.content_id.nunique()==6 and fit.content_id.nunique()==18
                assert not set(query.content_id)&set(fit.content_id)
                loco=[]
                for content in sorted(fit.content_id.unique()):
                    inner=fit[fit.content_id.ne(content)]
                    assert len(inner)==68 and inner.content_id.nunique()==17
                    loco.append({'held_content':content,'fit_sessions':sorted(inner.session_id),
                                 'held_sessions':sorted(fit.loc[fit.content_id.eq(content),'session_id'])})
                name=f'{protocol}-f{fold}-q{group}'
                job={'job':name,'protocol':protocol,'fold':fold,'query_group':group,
                     'fit_sessions':sorted(fit.session_id),'query_sessions':sorted(query.session_id),
                     'query_contents':sorted(query.content_id.unique()),'loco':loco}
                write(OUT/'generator-roles'/f'{name}.json',job);generator_jobs.append(name)
    assert len(generator_jobs)==100 and len(scenarios)==55
    write(OUT/'source-lock.json',{'inputs':{str(p.relative_to(ROOT)):file_hash(p) for p in paths},
                                'session_evidence':used_session_hashes})
    write(OUT/'gate-A.json',{'passed':True,'Q01_Q04_complete':True,'visits':600,'contents':30,'W_rows':1200,
          'scenarios':55,'E1':5,'E2':25,'I0':25,'generator_jobs':100,'inner_LOCO_jobs':1800,
          'cross_role_registered_entity_conflicts':conflicts,'old_role_rows_verified':len(check),
          'historical_unobserved_SYN_rows_retained':old_isolation['tcp_path_side_rows_without_SYN'],
          'complete_TCP_birth_reconstruction_claimed':False,'models_trained':0,'training_allowed':False,
          'script_sha256':file_hash(Path(__file__))})
    print(read(OUT/'gate-A.json'))


if __name__=='__main__':main()
