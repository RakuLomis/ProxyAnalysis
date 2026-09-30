import numpy as np
import pandas as pd
import pytest
from proxy_analysis.cross_business_calibration.common import NUMERIC,FEATURES,Bundle
from proxy_analysis.cross_business_calibration.export import frames
from proxy_analysis.cross_business_calibration.group import canonical,fit_group,torch

def test_eight_rotation_balance():
    counts=np.zeros((4,4),int)
    for t in range(4):
        for s in range(2):
            total=0
            for j in range(4):
                n=2 if (j+t)%4<2 else 1;total+=n
                for z in range(n):counts[j,(t+2*s+z)%4]+=1
            assert total==6
    assert (counts==3).all()

def test_group_rejects_paired_identity():
    pre=pd.DataFrame(columns=['content_id']+NUMERIC+['session_id']);post=pd.DataFrame(columns=['content_id']+FEATURES)
    with pytest.raises(AssertionError):canonical(pre,post)

def test_post_order_invariant_cuda():
    rng=np.random.default_rng(9);a=pd.DataFrame(rng.integers(1,1000,(12,7)),columns=NUMERIC);a['content_id']=np.repeat(['a','b','c'],4)
    b=pd.DataFrame(rng.integers(1,1000,(12,6)),columns=FEATURES);b['content_id']=a.content_id
    m,p,_=fit_group(a,b);n,q,_=fit_group(a.sample(frac=1,random_state=2),b.sample(frac=1,random_state=3))
    assert m.weight.is_cuda;torch.testing.assert_close(m.weight,n.weight,rtol=0,atol=0);pd.testing.assert_frame_equal(p,q)

def test_forbidden_numeric_poison_does_not_change_training():
    rows=[]
    for sid in ['c','u','h']:
        for side in ['pre','post']:rows.append({'session_id':sid,'content_id':sid,'protocol':'VLESS','repetition':1,'side':side,'label_id':sid,**{k:10 for k in NUMERIC}})
    p=pd.DataFrame(rows);before=frames(p,['c'],['u']);p.loc[(p.session_id=='h')|((p.session_id=='u')&(p.side=='post')),NUMERIC]=9000
    after=frames(p,['c'],['u'])
    for k in before:pd.testing.assert_frame_equal(before[k],after[k])
