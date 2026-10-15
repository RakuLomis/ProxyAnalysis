# Qualified policy business experiment

Independent implementation of the user-approved original eligibility plus fixed fallback policy. This version repairs the preflight metadata lookup (`mapping.eta`) while preserving the failed run-01 code and artifacts.

Runtime: `D:/Tools/Anaconda/envs/Pytorch312/python.exe`, CUDA float64 only for model operations. No CPU model fallback.

Registered output: `outputs/dynamic-soft-drift-qualified-policy-business-20261013/run-02`.

Commands:

```powershell
& D:/Tools/Anaconda/envs/Pytorch312/python.exe eval/dynamic_soft_drift_qualified_policy_v2/run.py unit-test
& D:/Tools/Anaconda/envs/Pytorch312/python.exe eval/dynamic_soft_drift_qualified_policy_v2/run.py prepare
& D:/Tools/Anaconda/envs/Pytorch312/python.exe eval/dynamic_soft_drift_qualified_policy_v2/run.py execute
```

Preparation and execution refuse an already registered or stopped run; do not rerun these commands against the active run. The current execution is supervised by the one-shot task `ProxyAnalysis-qualified-policy-run02-20261013`; no recurring schedule or failure auto-retry is configured.

Original f0 endpoints are verified against P0 immutable hashes; the remaining 144 trajectories start at q=1. All 180 decisions must exist before final fitting. Exact fallback aliases use the frozen P-small/G-small models. All 600 logical endpoints must be sealed before H-post queries; all predictions must be sealed before H labels.

Optimization is limited to 20 cumulative hours including inherited f0 cost. Global interruption/resource stops leave roles undecided and block H. Ordinary completed qualification failures use fixed fallback. The policy never selects an intermediate best q or changes the scientific target, small proportion, regularization, masks, or original LR/implicit acceptance gates.
