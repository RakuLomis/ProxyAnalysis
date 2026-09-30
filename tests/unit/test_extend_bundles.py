import pandas as pd
import pytest
from proxy_analysis.extend_calibration.audit import write,file_hash
from proxy_analysis.extend_calibration.bundles import Bundle


def test_allowlist_and_integrity(tmp_path):
    path=tmp_path/'C_pre.parquet';pd.DataFrame({'session_id':['a'],'W_up':[1]}).to_parquet(path,index=False)
    write(tmp_path/'manifest.json',{'kind':'paired','files':{'C_pre':{'filename':path.name,'sha256':file_hash(path),'columns':['session_id','W_up']}}})
    b=Bundle(tmp_path,'paired');assert b.get('C_pre').W_up.tolist()==[1]
    for role in ['H_pre','H_post','U_post','../reference/U_post']:
        with pytest.raises(PermissionError):b.get(role)
    with pytest.raises(PermissionError):Bundle(tmp_path,'reference')
    pd.DataFrame({'session_id':['a'],'W_up':[2]}).to_parquet(path,index=False)
    with pytest.raises(AssertionError):b.get('C_pre')
