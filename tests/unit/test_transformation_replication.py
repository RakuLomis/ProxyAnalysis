import math
import pytest

from proxy_analysis.crosscontent.transformation_replication import values, summarize, category, identity


def test_strict_ratio_no_smoothing_and_js_divergence():
    a=dict(packet_count=10,transport_bytes=100,burst_count=0,fr_runs=2,
           length_hist=[1]+[0]*18,iat_hist=[1]+[0]*22)
    b=dict(a,packet_count=20,length_hist=[0,1]+[0]*17)
    result={r['metric']:r for r in values(a,b)}
    assert result['packet_count']['delta']==pytest.approx(math.log(2))
    assert result['burst_count']['delta'] is None
    assert result['length_js']['delta']==1
    assert result['iat_js']['delta']==0


def test_mad_iqr_and_asymmetric_log_band():
    rows=[{'metric':'packet_count','delta':v} for v in [0,1,2,3]]
    r=summarize(rows)
    assert r['median_delta']==1.5 and r['mad_delta']==1 and r['iqr_delta']==1.5
    assert category('packet_count',math.log(.9))=='within_0.9_1.1'
    assert category('packet_count',math.log(1.1))=='within_0.9_1.1'
    assert category('length_js',.05)=='within_0.05'
    assert category('iat_js',None)=='undefined'


def test_bing_url_encoding_identity_preserves_content():
    a='https://www.bing.com/search?q=network%20traffic%20analysis'
    b='https://www.bing.com/search?q=network+traffic+analysis'
    assert identity(a)==identity(b)
    assert identity(a)!=identity('https://www.bing.com/search?q=different')
