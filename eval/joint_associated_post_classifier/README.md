# JAT1 joint classifier and CUDA engineering implementation

Complete trainable classifier: `W*x + V*G(x) + c`, with G 96→16→8.
There is no frozen logit offset, 0.1 output multiplier or hard projection.
W/V/c and losses are CUDA float64; G is CUDA float32. Adam state and
gradient clipping remain independent for every model.

The initial engineering-only revision is retained in immutable engineering
snapshots. The user-approved execution extension now implements P1–P5:
fixed 12-task pilot; all 720 source tasks; finite six-recipe selection; 60
outer teachers; three-seed outer fits and matched freeze branches; globally
sealed post-only prediction; four-comparison shared-content bootstrap; and
independent replay/export/report. Target-U training sides and H-pre remain
forbidden. H-post opens only after all outer model endpoints are sealed.

The adopted backend is 32 independent models, up to eight CUDA streams,
and CUDA Graph. The tensorized BMM backend failed the fixed numerical gate
and is not used, regardless of its speed. No training objective, numerical
tolerance or scientific gate was relaxed to improve GPU occupancy.

Commands in Pytorch312, from repository root:

```powershell
python -u eval/joint_associated_post_classifier/run.py register
python -u eval/joint_associated_post_classifier/run.py tests --tag numeric-01
python -u eval/joint_associated_post_classifier/run.py profile --tag gpu-01
python -u eval/joint_associated_post_classifier/run.py tests --tag numeric-05
python -u eval/joint_associated_post_classifier/run.py all
```

An existing tag is immutable. Failed numerical backends are retained and are
not selected by throughput. A profile is never a scientific fit or business
result. Engineering copies use only the fixed twelve legal source tasks;
their repeated inputs do not create additional independent visits.

Selection should maximize validated throughput with safe memory headroom,
not allocate padding to fill VRAM. nvidia-smi utilization includes the Windows
desktop and other processes; PyTorch allocated/reserved peaks are logged
separately. CUDA Graph setup time is separate from steady-state throughput.

`all` first freezes a separate execution authorization and code snapshot.
It does not overwrite the original engineering contract or historical stops.
P1 reads no query/labels and is accepted on engineering and the predeclared
19.2-hour forecast ceiling, not local classification gain. The cumulative
training-activity cap is 24 hours; IO/hash/report wall time is separate.
Physical fits, midpoint warm paths, aliases, teacher fits and model updates
are separately accounted. Global budget exhaustion stops unrun work; it
never silently marks it as fallback.

Live state: `outputs/joint-associated-post-classifier-20261016/run-01/progress.json`.
Activity budget: `budget.json`; phase barriers: `manifests/*complete.json`.
Failed execution records: `audits/stop-*.json`; they are never deleted or
automatically retried. Completed checkpoints are reusable only under their
exact role/recipe/seed identity and unchanged source/code contracts.
