# StrongPost auxiliary view training intervention

Approved plan: `plan/strongpost-auxiliary-view-training-intervention-plan-20261009.md`.

This independent entry point leaves CT v4, JA and their contracts unchanged.
It replaces auxiliary CE mass, not feature vectors. Only the fixed source-inner
numeric pilot may execute before promotion. Target H labels, target training U,
test pre and optional half-C fitting are unavailable at this stage.

Run from the repository root using Pytorch312:

```powershell
& 'D:/Tools/Anaconda/envs/Pytorch312/python.exe' eval/strongpost_training_intervention/inventory.py
& 'D:/Tools/Anaconda/envs/Pytorch312/python.exe' eval/strongpost_training_intervention/tests.py
& 'D:/Tools/Anaconda/envs/Pytorch312/python.exe' eval/strongpost_training_intervention/prepare.py
& 'D:/Tools/Anaconda/envs/Pytorch312/python.exe' eval/strongpost_training_intervention/numeric_pilot.py fit
& 'D:/Tools/Anaconda/envs/Pytorch312/python.exe' eval/strongpost_training_intervention/numeric_pilot.py gate
```

All numerical work requires CUDA float64. Accepted artifacts and completed
stages cannot be overwritten. If `pilot/promotion.json` has `passed: false`,
stop and seek user direction. No precision, epsilon, mapping or classifier
selection changes are permitted by this runner. The finite-difference pilot
contains 60 diagnostic fits, outside the 240 formal endpoint cap.

## Authorized finite continuation

The user authorized continuing finite interventions without repairing or
promoting the failed influence-function pilot. The additive record is
`manifests/continuation.json`; the original pilot/pause records stay unchanged.
Both new scripts are hash-bound before any formal prediction or target scoring.

```powershell
& 'D:/Tools/Anaconda/envs/Pytorch312/python.exe' eval/strongpost_training_intervention/formal.py register
& 'D:/Tools/Anaconda/envs/Pytorch312/python.exe' eval/strongpost_training_intervention/formal.py train
& 'D:/Tools/Anaconda/envs/Pytorch312/python.exe' eval/strongpost_training_intervention/formal.py predict
& 'D:/Tools/Anaconda/envs/Pytorch312/python.exe' eval/strongpost_training_intervention/formal.py score
& 'D:/Tools/Anaconda/envs/Pytorch312/python.exe' eval/strongpost_training_intervention/formal.py diagnose
& 'D:/Tools/Anaconda/envs/Pytorch312/python.exe' eval/strongpost_training_intervention/formal_report.py
& 'D:/Tools/Anaconda/envs/Pytorch312/python.exe' eval/strongpost_training_intervention/formal.py verify
```

Do not rerun completed stages. Formal continuation fixes 199 new classifier
fits plus 41 compatible reused full endpoints and 60 frozen StrongPost models.
It does not change beta, eta, t, preprocessing, objective, optimizer policy or
permissions. Local influence tables are explicitly unvalidated retrospective
approximations and never supply training weights or model-selection signals.
