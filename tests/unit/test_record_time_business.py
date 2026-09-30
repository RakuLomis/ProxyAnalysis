import numpy as np
import pandas as pd
import pytest
from proxy_analysis.crosscontent.record_time_business.data import canon,eligibility

def record(end=47):return pd.DataFrame({'end':[end]})

def test_complete_eligibility():
    assert eligibility('contiguous','syntax_prefix_complete',record(),47,True)

@pytest.mark.parametrize('status,reason,rows,total,valid',[
    ('contiguous','partial_record_body',record(),80,True),
    ('gap_or_unobserved_prefix','syntax_prefix_complete',record(),47,True),
    ('contiguous','syntax_prefix_complete',record(),48,True),
    ('contiguous','syntax_prefix_complete',record(),47,False),
    ('contiguous','syntax_prefix_complete',record(),np.nan,False),
    ('empty','empty_prefix',pd.DataFrame(),0,True),
    ('contiguous','invalid_header_no_resynchronization',record(),47,True),
])
def test_qualification_does_not_fill_or_accept_partial(status,reason,rows,total,valid):
    assert not eligibility(status,reason,rows,total,valid)

def test_windows_path_identity():
    assert canon('F:\\Path\\File.pcap')==canon('f:/path/file.pcap')
    assert canon('\\\\?\\F:\\Path\\File.pcap')==canon('f:/path/file.pcap')
