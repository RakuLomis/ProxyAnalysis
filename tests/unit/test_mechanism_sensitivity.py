import numpy as np
import pytest

from proxy_analysis.crosscontent.mechanism_sensitivity import members, guard, content_scores
from proxy_analysis.crosscontent.business_splits import donors


def data():
    return [{'session_id':f'{p}-{c}-{r}','content_id':str(c),'label_id':'a','protocol':p,'repetition':r}
            for p in ('SS','VLESS') for c in range(5) for r in range(1,6)
            if not (p=='SS' and c==1 and r==3)]


@pytest.mark.parametrize('scheme',[0,1,2])
def test_299_match_source_only_and_keep_target_visits(scheme):
    rows=data(); assignment={str(c):c for c in range(5)}
    context={'task':'six_business','protocol':'SS','outer_fold':0,'scheme':scheme}
    available,train,test,target,part=members(rows,assignment,context)
    assert (len(available),len(train),len(test),len(target))==(19,18,5,5)
    mapping=donors(train,part)
    for i,j in enumerate(mapping):
        assert train[i]['content_id']!=train[j]['content_id']
        assert train[i]['repetition']==train[j]['repetition']
    context['protocol']='VLESS'; context['outer_fold']=1
    _,train,test,target,_=members(rows,assignment,context)
    assert (len(train),len(test),len(target))==(20,5,4)
    with pytest.raises(ValueError): guard(train+target,test,target,'VLESS')


def test_metrics_equalize_contents_not_visits():
    rows=[]
    for cid,n,p in [('a',4,[.8,.2]),('b',5,[.4,.6])]:
        for i in range(n):
            rows.append({'content_id':cid,'truth':0 if cid=='a' else 1,
                'probabilities':p,'loss_bits':-np.log2(p[0 if cid=='a' else 1])})
    result=content_scores(rows)
    assert result['log_loss_bits']==pytest.approx((-np.log2(.8)-np.log2(.6))/2)
    assert result['macro_f1']==1
