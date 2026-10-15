# Paired identity decomposition and additive JA closeout

This implementation never imports the scientific training runner or calls a fit.
It keeps the original JA failure, sources, models, choices and predictions unchanged.
CT5 directory-level metadata is authenticated through the already frozen historical
contract. All inference and tensor diagnostics require CUDA float64 in Pytorch312.

Run in order: `inventory.py`, `tests.py`, `closeout.py`, `decompose.py`, `project.py`,
`plots.py`, `synthesize.py`, `review.py`, `verify.py`. Completed stages refuse accidental reruns.
Each stage has a 30-minute limit and an exclusive lock. Terminal diagnostic failures
must be inspected before any explicit revision; no automatic retry is provided.

Outputs are local and large intermediate artifacts are not intended for Git.
Mapped held-out pre readouts are offline diagnostics, never post-only attack scores.
There is no new model selection or primary statistical test in this analysis.
