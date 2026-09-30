# 跨批次比较：仅作参考

精确资源重合不代表实际 workload、采集时长、部署路由相同；不将两批次拼接为新增重复。下面保留相同资源候选及活动标签差异。数值明细见 cross-dataset-comparison.parquet，未作跨批次显著性或可重复性推断。

| 0914子集 | 目标资源 | 0914活动 | 0916活动 | 活动兼容 | 比较资格 |
| --- | --- | --- | --- | --- | --- |
| 0914-broad | https://www.bilibili.com/video/BV1hu4m1P7Mu/ | bilibili.com::video_playback | bilibili.com::video_playback | 1 | same_resource_activity_descriptive_only |
| 0914-broad | https://www.bilibili.com/video/BV1HEf2YWEvs/ | bilibili.com::video_playback | bilibili.com::video_playback | 1 | same_resource_activity_descriptive_only |
| 0914-broad | https://www.youtube.com/watch?v=sAWK0mgrMp4 | youtube.com::video_playback | youtube.com::video_playback | 1 | same_resource_activity_descriptive_only |
| 0914-broad | https://en.wikipedia.org/wiki/Computer_network | wikipedia.org::page_load | wikipedia.org::article_view | 1 | same_resource_activity_descriptive_only |
| 0914-broad | https://developer.mozilla.org/en-US/docs/Web/HTTP | developer.mozilla.org::page_load | developer.mozilla.org::document_view | 1 | same_resource_activity_descriptive_only |
| 0914-broad | https://github.com/RakuLomis/TrafficTracer | github.com::page_load | github.com::repository_view | 1 | same_resource_activity_descriptive_only |
| 0914-repeat | https://en.wikipedia.org/wiki/Computer_network | wikipedia.org::page_load | wikipedia.org::article_view | 1 | same_resource_activity_descriptive_only |
| 0914-repeat | https://developer.mozilla.org/en-US/docs/Web/HTTP | developer.mozilla.org::page_load | developer.mozilla.org::document_view | 1 | same_resource_activity_descriptive_only |
| 0914-repeat | https://github.com/RakuLomis/TrafficTracer | github.com::page_load | github.com::repository_view | 1 | same_resource_activity_descriptive_only |
| 0914-repeat | https://www.bing.com/search?q=network+traffic+analysis | bing.com::page_load | bing.com::search_results_view | 1 | same_resource_activity_descriptive_only |
| 0914-repeat | https://www.bilibili.com/video/BV1hu4m1P7Mu/ | bilibili.com::video_playback | bilibili.com::video_playback | 1 | same_resource_activity_descriptive_only |
| 0914-repeat | https://www.youtube.com/watch?v=sAWK0mgrMp4 | youtube.com::video_playback | youtube.com::video_playback | 1 | same_resource_activity_descriptive_only |


生成 8279 条分特征、侧别、部署与范围的描述性对比。标签命名的细化（如 page_load → document_view）仅在原始 activity_kind 一致且目标确切相同时允许进入描述性候选；绝不据此断言任务负载完全相同。
