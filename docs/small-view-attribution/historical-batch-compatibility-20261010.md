# 历史批次业务与表示兼容性

| batch | contents | current_96D_ready | identity_overlap_contents | labels | matching_current_labels | missing_current_labels | protocols | repetitions | status | visits |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0914 | 14 | False | 4 | 14 | 5 | youtube.com::search_results_view | SHADOWSOCKS; VLESS | 1; 2; 3; 4; 5 | 业务覆盖不兼容且需重新构造表示 | 140 |
| 0916 | 30 | False | 30 | 6 | 6 |  | SHADOWSOCKS; VLESS | 1; 2; 4; 5 | 业务标签兼容，需重新构造并审核96维表示 | 240 |

## 历史业务与内容覆盖

| label_id | contents | visits | batch |
| --- | --- | --- | --- |
| arxiv.org::paper_abstract_view | 1 | 10 | 0914 |
| bing.com::search_results_view | 1 | 10 | 0914 |
| cloudflare.com::homepage_view | 1 | 10 | 0914 |
| developer.mozilla.org::document_view | 1 | 10 | 0914 |
| example.com::static_control_view | 1 | 10 | 0914 |
| github.com::repository_view | 1 | 10 | 0914 |
| openstreetmap.org::map_view | 1 | 10 | 0914 |
| rottentomatoes.com::movie_info_view | 1 | 10 | 0914 |
| tradingview.com::chart_view | 1 | 10 | 0914 |
| unsplash.com::image_feed_view | 1 | 10 | 0914 |
| vimeo.com::video_info_view | 1 | 10 | 0914 |
| weather.com::weather_view | 1 | 10 | 0914 |
| wikipedia.org::article_view | 1 | 10 | 0914 |
| youtube.com::video_playback | 1 | 10 | 0914 |
| bing.com::search_results_view | 5 | 40 | 0916 |
| developer.mozilla.org::document_view | 5 | 40 | 0916 |
| github.com::repository_view | 5 | 40 | 0916 |
| wikipedia.org::article_view | 5 | 40 | 0916 |
| youtube.com::search_results_view | 5 | 40 | 0916 |
| youtube.com::video_playback | 5 | 40 | 0916 |

## 跨批次资源重叠

| batch | historical_content | canonical_content | exact_string_match | global_training_exclusion_required |
| --- | --- | --- | --- | --- |
| 0914 | https://developer.mozilla.org/en-US/docs/Web/HTTP | https://developer.mozilla.org/en-US/docs/Web/HTTP | True | True |
| 0914 | https://en.wikipedia.org/wiki/Computer_network | https://en.wikipedia.org/wiki/Computer_network | True | True |
| 0914 | https://github.com/RakuLomis/TrafficTracer | https://github.com/RakuLomis/TrafficTracer | True | True |
| 0914 | https://www.youtube.com/watch?v=sAWK0mgrMp4 | youtube_video:sAWK0mgrMp4 | False | True |
| 0916 | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API | True | True |
| 0916 | https://developer.mozilla.org/en-US/docs/Web/HTTP | https://developer.mozilla.org/en-US/docs/Web/HTTP | True | True |
| 0916 | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching | True | True |
| 0916 | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies | True | True |
| 0916 | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | True | True |
| 0916 | https://en.wikipedia.org/wiki/Computer_network | https://en.wikipedia.org/wiki/Computer_network | True | True |
| 0916 | https://en.wikipedia.org/wiki/Domain_Name_System | https://en.wikipedia.org/wiki/Domain_Name_System | True | True |
| 0916 | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol | True | True |
| 0916 | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | https://en.wikipedia.org/wiki/Transmission_Control_Protocol | True | True |
| 0916 | https://en.wikipedia.org/wiki/Transport_Layer_Security | https://en.wikipedia.org/wiki/Transport_Layer_Security | True | True |
| 0916 | https://github.com/RakuLomis/TrafficTracer | https://github.com/RakuLomis/TrafficTracer | True | True |
| 0916 | https://github.com/numpy/numpy | https://github.com/numpy/numpy | True | True |
| 0916 | https://github.com/pallets/flask | https://github.com/pallets/flask | True | True |
| 0916 | https://github.com/python/cpython | https://github.com/python/cpython | True | True |
| 0916 | https://github.com/scikit-learn/scikit-learn | https://github.com/scikit-learn/scikit-learn | True | True |
| 0916 | https://www.bing.com/search?q=beginner+guitar+chords | https://www.bing.com/search?q=beginner+guitar+chords | True | True |
| 0916 | https://www.bing.com/search?q=indoor+plant+care | https://www.bing.com/search?q=indoor+plant+care | True | True |
| 0916 | https://www.bing.com/search?q=network+traffic+analysis | https://www.bing.com/search?q=network+traffic+analysis | True | True |
| 0916 | https://www.bing.com/search?q=solar+system+facts | https://www.bing.com/search?q=solar+system+facts | True | True |
| 0916 | https://www.bing.com/search?q=sourdough+bread+recipe | https://www.bing.com/search?q=sourdough+bread+recipe | True | True |
| 0916 | https://www.youtube.com/results?search_query=astronomy+documentary | https://www.youtube.com/results?search_query=astronomy+documentary | True | True |
| 0916 | https://www.youtube.com/results?search_query=bicycle+maintenance | https://www.youtube.com/results?search_query=bicycle+maintenance | True | True |
| 0916 | https://www.youtube.com/results?search_query=bread+baking | https://www.youtube.com/results?search_query=bread+baking | True | True |
| 0916 | https://www.youtube.com/results?search_query=piano+practice | https://www.youtube.com/results?search_query=piano+practice | True | True |
| 0916 | https://www.youtube.com/results?search_query=watercolor+tutorial | https://www.youtube.com/results?search_query=watercolor+tutorial | True | True |
| 0916 | youtube_video:R6MlUcmOul8 | youtube_video:R6MlUcmOul8 | True | True |
| 0916 | youtube_video:aircAruvnKk | youtube_video:aircAruvnKk | True | True |
| 0916 | youtube_video:aqz-KE-bpKQ | youtube_video:aqz-KE-bpKQ | True | True |
| 0916 | youtube_video:eRsGyueVLvQ | youtube_video:eRsGyueVLvQ | True | True |
| 0916 | youtube_video:sAWK0mgrMp4 | youtube_video:sAWK0mgrMp4 | True | True |

只统一显式YouTube video ID别名，其他URL不任意删查询参数。0916六类标签吻合不意味着资源独立或表示可直接迁移；0914缺当前YouTube搜索类，不能强行重标。历史缓存与新96维输入需要单独登记重构。当前没有新特征提取、PCAP扫描或跨批次拟合。
