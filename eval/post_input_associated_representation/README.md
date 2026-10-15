# post输入关联表征残差分支

批准计划：`plan/post-input-associated-representation-residual-plan-20261014.md`。

环境为Pytorch312，CUDA为硬要求。历史实验只读；Stage B未授权。

顺序为inventory.py、prepare.py、run.py。run.py仅跳过已有通过阶段，失败阶段不自动重试。工程先导超预算或数值门失败时终止，不缩减业务、角色或seed。

deploy.py是独立post推理入口，仅依赖torch和给定模型参数，不读取教师、标签、内容/协议身份或配对表。
