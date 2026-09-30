from types import SimpleNamespace
import numpy as np
from proxy_analysis.crosscontent.business_0914 import split_ids,clipped_groups,raw_matrix,ACTIVITIES


def test_whole_visit_repeat_split():
    rows=[{'session_id':f'{c}-{p}-{r}','label_id':c,'protocol':p,'repetition':r} for c in ACTIVITIES for p in ['SS','VL'] for r in range(1,6)]
    tests=[]
    for fold in range(1,6):
        a,b=split_ids(rows,fold)
        assert len(a)==112 and len(b)==28
        assert {r['repetition'] for r in b}=={fold}
        assert not {r['session_id'] for r in a}&{r['session_id'] for r in b}
        tests.extend(r['session_id'] for r in b)
    assert len(tests)==len(set(tests))==140


def test_prefix_preserves_flow_groups_and_half_open_boundary():
    groups=[[SimpleNamespace(timestamp_ns=10),SimpleNamespace(timestamp_ns=8000000010)],
            [SimpleNamespace(timestamp_ns=5000000010)]]
    out,start,end=clipped_groups(groups,8)
    assert (start,end)==(10,8000000010)
    assert list(map(len,out))==[1,1]
    assert out[1][0] is groups[1][0]


def test_metadata_not_model_input():
    row={'full_x':[1.,2.],'domain':'a','label_id':'a','protocol':'SS','configured_seconds':60}
    altered={**row,'domain':'secret','label_id':'different','protocol':'VL','configured_seconds':8}
    assert np.array_equal(raw_matrix([row],'full'),raw_matrix([altered],'full'))
    assert raw_matrix([row],'configured_duration')[0,0]==60
