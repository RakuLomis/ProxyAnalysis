import pandas as pd
import numpy as np
import pytest
from proxy_analysis.calibration_budget.common import TrainingBundle,NUMERIC
from proxy_analysis.calibration_budget.export import train_frames
from proxy_analysis.conditional_drift.model import Ridge

def fixture():
    rows=[]
    for i in range(10):
      for side in ['pre','post']:
        rows.append({'session_id':str(i),'content_id':str(i//2),'protocol':'SS','repetition':i%2,
          'side':side,'label_id':'a',**{k:10+i for k in NUMERIC}})
    return pd.DataFrame(rows)

def test_export_has_no_U_post_or_H():
    frames=train_frames(fixture(),['0','1','2','3'],['4','5','6','7'])
    assert set(frames)=={'C_pre','C_post','U_pre','labels'}
    assert set(frames['C_post'].session_id)=={'0','1','2','3'}
    assert not any(c.endswith('_post') for c in frames['U_pre'].columns)

def test_poison_hidden_values_preserves_cuda_fit():
    d=fixture();C=['0','1','2','3'];U=['4','5','6','7']
    original=train_frames(d,C,U)
    d.loc[(d.side=='post')&d.session_id.isin(U),NUMERIC]=999999
    d.loc[d.session_id.isin(['8','9']),NUMERIC]=0
    altered=train_frames(d,C,U)
    for k in original:pd.testing.assert_frame_equal(original[k],altered[k])
    fitted=[]
    for x in [original,altered]:
        a=x['C_pre'][NUMERIC[:-1]].to_numpy(float);b=x['C_post'][NUMERIC[:-1]].to_numpy(float)
        fitted.append(Ridge(a,b,x['C_pre'].F.to_numpy()).weight.detach().cpu().numpy())
    np.testing.assert_array_equal(*fitted)

@pytest.mark.parametrize('role',['U_post','H_pre','H_post','H_labels','../raw'])
def test_deny_before_filesystem_access(role):
    bundle=TrainingBundle.__new__(TrainingBundle)
    with pytest.raises(PermissionError):bundle.get(role)
