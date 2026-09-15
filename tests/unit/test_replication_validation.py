import pytest
import json
from proxy_analysis.replication.validate import unique
from proxy_analysis.information_validation.data import build_labels
from proxy_analysis.replication.contract import target_contract


def test_same_url_different_repeat_is_not_a_duplicate():
    rows=[{'url':'u','repetition':r} for r in [1,2]]
    unique(rows,['url','repetition'])
    with pytest.raises(ValueError,match='duplicate'):
        unique(rows,['url'])


def test_same_domain_home_and_video_remain_distinct(tmp_path):
    sites=target_contract({'pipeline_id':'p','targets':[
        {'index':0,'domain':'example.org','url':'https://example.org/'},
        {'index':1,'domain':'example.org','url':'https://example.org/watch?v=1','playback':{'seconds':25}}]})
    assert len({r['content_key'] for r in sites['sites']})==2
    registry=[];routes={}
    for i,target in enumerate(sites['sites']):
        sid=str(i);path=tmp_path/sid/'analysis';path.mkdir(parents=True)
        (path/'summary.json').write_text(json.dumps({'session_id':sid,'navigation_outcome':{'state':'passed'}}))
        registry.append({'is_final':True,'session_id':sid,'session_path':str(path.parent),
            'target_domain':target['domain'],'target_url':target['url'],'protocol':'VLESS','repetition':1,'activity_id':target['content_key']})
        routes[sid]={'page_context_candidate':True,'main_document_proxy_candidate':True}
    labels=build_labels(registry,routes,sites)
    assert [r['intended_activity'] for r in labels]==['page_load','video_playback']
    assert not any(r['playback_verified'] for r in labels)
    assert all(r['verified_activity']=='page_load' for r in labels)
