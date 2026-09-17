from proxy_analysis.crosscontent.audit_capture import content_key


def test_youtube_video_identity_ignores_noncontent_query_parameters():
    target = {'domain': 'youtube.com', 'run_label': 'video_playback',
              'url': 'https://www.youtube.com/watch?v=abc&feature=shared'}
    assert content_key(target) == 'youtube_video:abc'


def test_bilibili_part_is_preserved():
    target = {'domain': 'bilibili.com', 'run_label': 'video_playback',
              'url': 'https://www.bilibili.com/video/BV123/?p=2'}
    assert content_key(target).endswith(':p=2')
    target['url'] = 'https://www.bilibili.com/video/BV123/'
    assert content_key(target).endswith(':p=1')


def test_search_query_is_part_of_content_identity():
    target = {'domain': 'youtube.com', 'run_label': 'search_results_view',
              'url': 'https://www.youtube.com/results?search_query=piano'}
    first = content_key(target)
    target['url'] = 'https://www.youtube.com/results?search_query=bread'
    assert content_key(target) != first
