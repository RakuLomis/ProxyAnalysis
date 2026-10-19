# ST1 fixed map shape source attribution

Implements the frozen source-inner plan at
`plan/ST1-shape-source-downstream-attribution-plan-20261016.md`.

Run from repository root in Pytorch312:

```powershell
python -u eval/shape_source_task_attribution/run.py all
```

Each stage also has an explicit command: `register`, `prepare`, `train`,
`predict`, `score`, `verify`, `report`. A stopped run cannot silently resume.
The registration seals all implementation code. Complete all source edits
before registration; do not modify sealed code to make failed gates pass.

The four arms are PP, PG, GP and GG. Projections act in raw histogram units.
All 192 LR models fit fresh with unchanged v4 CUDA float64 numerical policy.
The fixed 16-model engineering pilot is included in those 192 fits.
No G training, new maps, temperature fitting, actual target H/U, query pre,
native data, packet files or mixed feedback containers are permitted.

All models are sealed before query input, and all 4608 predictions are sealed
before source-inner label access. The bootstrap uses the same content counts
across all protocols, masks and arms. This is retrospective, fixed-model
source-inner analysis, not external validation or authorization for a new
60-role experiment.
