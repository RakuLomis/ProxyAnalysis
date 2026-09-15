from proxy_analysis.replication.activity_confirmation import resolve_activity


def test_manual_confirmation_is_scoped_and_preserves_telemetry():
    row={'batch':'repeat','target_url':'https://www.bilibili.com/video/v/','target_domain':'bilibili.com',
         'video_capture_valid':False,'verified_activity':'page_load'}
    confirmations=[{'batch':'repeat','url':row['target_url'],'main_content_playback':True,
                    'activity':'video_playback','page_kind':'video_resource'}]
    revised=resolve_activity(row,confirmations)
    assert revised['effective_video_capture_valid']
    assert not revised['video_capture_valid']
    assert revised['effective_label_id']=='bilibili.com::video_playback'
    assert not resolve_activity({**row,'target_url':'https://www.bilibili.com/'},confirmations)['effective_video_capture_valid']
    assert not resolve_activity({**row,'batch':'broad'},confirmations)['effective_video_capture_valid']


def test_vimeo_description_is_not_playback():
    row={'batch':'repeat','target_url':'https://vimeo.com/513177164','target_domain':'vimeo.com',
         'video_capture_valid':False,'verified_activity':'page_load'}
    r=resolve_activity(row,[{'batch':'repeat','url':row['target_url'],'main_content_playback':False,
                            'activity':'page_load','page_kind':'video_description'}])
    assert r['effective_activity']=='page_load'
    assert not r['effective_video_capture_valid']
    assert r['manual_page_kind']=='video_description'
