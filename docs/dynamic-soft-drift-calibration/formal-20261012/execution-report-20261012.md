# 动态软约束漂移正式业务实验执行报告

更新日期：2026年10月12日。当前状态：`stop_formal_gate_failure`。

本轮保持extend四部署、六业务、五折全局内容划分和原P-small资源口径，以充分求解LR后的隐式梯度学习十块漂移幅度。新臂为D-P、T-P、D-G；七类旧参照不重新训练或选择。

## 执行状态

{
  "H_scored": false,
  "formal_complete": false,
  "passed": false,
  "reason": "Weights only load failed. This file can still be loaded, to do so you have two options, \u001b[1mdo those steps only if you trust the source of the checkpoint\u001b[0m. \n\t(1) Re-running `torch.load` with `weights_only` set to `False` will likely succeed, but it can result in arbitrary code execution. Do it only if you got the file from a trusted source.\n\t(2) Alternatively, to load with `weights_only=True` please check the recommended steps in the following error message.\n\tWeightsUnpickler error: Unsupported global: GLOBAL numpy._core.multiarray.scalar was not an allowed global by default. Please use `torch.serialization.add_safe_globals([scalar])` to allowlist this global if you trust this class/function.\n\nCheck the documentation of torch.load to learn more about types accepted by default with weights_only https://pytorch.org/docs/stable/generated/torch.load.html.",
  "stage": "batch_one",
  "status": "stop_formal_gate_failure"
}

## 计算账本

|   cache_hits |   implicit |   logical_forward |   new_final_LR |   new_source_LR |   q_updates |   refinement |   validation |
|-------------:|-----------:|------------------:|---------------:|----------------:|------------:|-------------:|-------------:|
|            0 |        504 |               264 |              1 |             252 |          20 |          504 |          252 |

训练和数值微分使用Pytorch312、CUDA float64。实际目标U两侧、测试pre和PCAP均不进入本流程。所有600端点封存后才允许H-post查询；全部14400行预测封存后才允许H标签评分。

## registration

```json
{
  "OOF_predictions": 480,
  "numeric_H_reads": 0,
  "numeric_U_reads": 0,
  "old_models": 420,
  "passed": true,
  "resource": {
    "estimated_remaining": 10363469824,
    "free": 358707777536,
    "required": 26095648768
  },
  "roles": 60,
  "source_episodes": 720,
  "source_maps": 1440
}
```

## audits permission-tests

```json
{
  "Adam_replay_error": 0.0,
  "Adam_steps": 20,
  "H_numeric_reads": 0,
  "negative_checks": 10,
  "passed": true
}
```

## audits OOF-replay

```json
{
  "H_reads": 0,
  "U_reads": 0,
  "coefficient_sets": 120,
  "group_all_combinations": true,
  "max_explicit_error": 1.2860823517257813e-12,
  "new_mapping_fits": 0,
  "passed": true,
  "predictions": 480
}
```

## audits q-one-replay

```json
{
  "H_reads": 0,
  "U_reads": 0,
  "final_caches": 120,
  "new_maps": 0,
  "outer_mapped_error": 0.0,
  "passed": true,
  "source_maps_reused": 1440,
  "source_tasks": 1440
}
```

## 业务评价边界

正式评分尚未执行，不能根据已接受数值解、源内CE或部分q轨迹判断D-P是否优于P-small、T-P或D-G。

## 停止原因

- batch_one：Weights only load failed. This file can still be loaded, to do so you have two options, [1mdo those steps only if you trust the source of the checkpoint[0m. 
	(1) Re-running `torch.load` with `weights_only` set to `False` will likely succeed, but it can result in arbitrary code execution. Do it only if you got the file from a trusted source.
	(2) Alternatively, to load with `weights_only=True` please check the recommended steps in the following error message.
	WeightsUnpickler error: Unsupported global: GLOBAL numpy._core.multiarray.scalar was not an allowed global by default. Please use `torch.serialization.add_safe_globals([scalar])` to allowlist this global if you trust this class/function.

Check the documentation of torch.load to learn more about types accepted by default with weights_only https://pytorch.org/docs/stable/generated/torch.load.html.。
  证据：`outputs/dynamic-soft-drift-business-formal-20261012/run-01/failures/batch_one-1791806255431794400.json`。
- main/f0/shadowsocks/G0/outer：见失败资产。
  证据：`outputs/dynamic-soft-drift-business-formal-20261012/run-01/failures/meta-T-P-1791806255426794500.json`。

失败版本保留；不会自动增加预算、放宽验收门、跳过任务或改用先前梯度。后续修订需独立版本。

## 复现入口

`D:/Tools/Anaconda/envs/Pytorch312/python.exe eval/dynamic_soft_drift_formal/run.py prepare`

`D:/Tools/Anaconda/envs/Pytorch312/python.exe eval/dynamic_soft_drift_formal/run.py formal`

阶段命令不覆盖已完成产物；formal拒绝已登记的失败版本。报告可以用独立report命令更新。
