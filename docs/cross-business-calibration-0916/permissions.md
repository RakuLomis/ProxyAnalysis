# XBC0–XBC2 权限与角色

|   business_group | new_labels                                                         |
|-----------------:|:-------------------------------------------------------------------|
|                0 | github.com::repository_view / youtube.com::search_results_view     |
|                1 | wikipedia.org::article_view / bing.com::search_results_view        |
|                2 | youtube.com::video_playback / developer.mozilla.org::document_view |

240个scenario，C=24访问，U=72访问，其中new=32。8轮换全部均衡；C无new业务。双侧历史资格依赖保留；不等于无需捕获U_post。组级worker无校准配对身份，参考臂另包隔离。污染、禁止访问、flow/capture互斥检查通过。
