import numpy as np
import pytest
from sklearn.linear_model import LogisticRegression

from proxy_analysis.crosscontent.business_features import resource_identity
from proxy_analysis.crosscontent.business_splits import outer_assignment, teacher_assignment, disjoint, donors, validate_donors
from proxy_analysis.crosscontent.privileged_learning import LinearStudent, matrix
from proxy_analysis.paired_information.reference_retrain import SCALAR_NAMES


def rows():
    return [{'session_id':f'{label}-{content}-{repeat}','label_id':label,'content_id':f'{label}:{content}',
             'protocol':'VLESS','repetition':repeat}
            for label in ('a','b') for content in range(5) for repeat in (1,2,4,5)]


def test_bing_redirect_bookkeeping_does_not_change_search_content():
    a='https://www.bing.com/search?q=hello+world'
    assert resource_identity(a)==resource_identity(a+'&rdr=1&rdrig=abc')
    assert resource_identity(a)!=resource_identity('https://www.bing.com/search?q=other')


def test_content_split_and_crossfit_donors_are_disjoint():
    data=rows(); assignment=outer_assignment(data,1)
    train=[r for r in data if assignment[r['content_id']]!=0]
    test=[r for r in data if assignment[r['content_id']]==0]
    assert len(train)==32 and len(test)==8
    disjoint(train,test)
    for scheme in range(3):
        partitions=teacher_assignment(train,scheme)
        mapping=donors(train,partitions)
        for i,j in enumerate(mapping):
            assert train[i]['content_id']!=train[j]['content_id']
            assert train[i]['repetition']==train[j]['repetition']
            teacher_train=[r for r in train if partitions[r['content_id']]!=partitions[train[i]['content_id']]]
            assert train[i]['content_id'] not in {r['content_id'] for r in teacher_train}
            assert train[j]['content_id'] not in {r['content_id'] for r in teacher_train}
        for seed in range(5):
            within=donors(train,partitions,'within_content',seed)
            assert all(train[i]['content_id']==train[j]['content_id'] and i!=j for i,j in enumerate(within))


def test_positive_controls_reject_leakage_and_wrong_strata():
    data=rows(); assignment=outer_assignment(data,1)
    train=[r for r in data if assignment[r['content_id']]!=0]
    with pytest.raises(ValueError,match='Overlap'): disjoint(train,[train[0]])
    with pytest.raises(ValueError,match='Duplicate'): disjoint([train[0],train[0]])
    partition=teacher_assignment(train,0); mapping=donors(train,partition)
    corrupted=[dict(r) for r in train]; corrupted[mapping[0]]['protocol']='SHADOWSOCKS'
    with pytest.raises(ValueError,match='protocol'): validate_donors(corrupted,partition,mapping,'cross_content')
    bad_partition=dict(partition); bad_partition[train[mapping[0]]['content_id']]=1-partition[train[0]['content_id']]
    with pytest.raises(ValueError,match='partition'): validate_donors(train,bad_partition,mapping,'cross_content')


@pytest.mark.parametrize('k',[2,6])
def test_hard_soft_target_training_equivalence(k):
    rng=np.random.default_rng(4); x=rng.normal(size=(60,14)); x[0,0]=np.nan; x[:,2]=np.nan
    y=np.arange(60)%k
    cfg={'model_C':1.,'max_iter':3000,'seed':1}
    student=LinearStudent(cfg).fit(x,np.eye(k)[y])
    z=student.preprocess.transform(x)
    reference=LogisticRegression(C=1,max_iter=3000,random_state=1).fit(z,y)
    np.testing.assert_allclose(student.predict(x),reference.predict_proba(z),atol=1e-10)
    q=.5*np.eye(k)[y]+.5*np.ones((60,k))/k
    soft=LinearStudent(cfg).fit(x,q)
    np.testing.assert_allclose(soft.predict(x).sum(axis=1),1)


def test_matrix_allowlist_ignores_identity_fields():
    row={'post':{**dict.fromkeys(SCALAR_NAMES,1),'ip_src':'secret','sni':'secret'},'label_id':'secret'}
    assert matrix([row],'post').shape==(1,14)
