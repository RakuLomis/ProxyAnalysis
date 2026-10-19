# NER1 numerical-execution repair pilot

This is an independent, bounded engineering pilot for DP-GAN1-M v1.
It does not contain a full-experiment entrypoint or a query/H/U reader.

## Frozen scientific definition

The original 96 coordinates, capability-specific raw training packages,
three classifier regularizers, six Adam recipes, 2,000 Adam updates,
float64 CUDA math, original-coordinate gradient gate (1e-5), independent
replay gate (1e-10), and strict iteration/evaluation budgets are unchanged.
An optimizer reaching 2,000 iterations or 10,000 function evaluations is
rejected even if its final gradient is small.

`lbfgs_local.py` contains the installed PyTorch LBFGS step with an accepted-point
callback and explicit exit logging. Its recursion, line search and native
small-change tests are preserved. The callback uses the gradient selected by
strong Wolfe, not the gradient left by a possibly rejected last closure.
The final six-class objective and gradient are checked independently.

## Sequence

1. `register.py`: bind historical seals, twelve legal roles, 232 original head
   problems and 88 dynamic jobs. No tensor decoding.
2. `seal.py`: append a source version, installed-step diff and pure-math bindings.
3. `pilot.py controls`, then `hard`, then `serial --cap G/P/E`: controls and
   25 fixed convex problems. A failed numerical gate stops progression.
4. `driver.py`: only after R1 has passed. Runs uniform-lr synthetic and legacy
   replay, fixed C1/C4/C8 head benchmarks, one new-policy integrated P1 and
   metadata closeout. Each capability executes in a separate subprocess.

Use `D:/Tools/Anaconda/envs/Pytorch312/python.exe`. Do not rerun these commands
over an existing run as an implicit retry. Immutable assets and old stops are
retained. Explicit engineering recovery is recorded separately.

## Concurrency and accounting

Each head owns its parameters, optimizer, line search, stopping counters and
CUDA stream. Inputs are prepared read-only by the coordinator. Per-head
synchronization is stream-local; the coordinator is the sole activity-ledger
writer. Adam uses at most 32 models, eight streams and one learning rate per
bucket. No multi-head summed LBFGS objective is used.

The repair increment is capped at four hours within the original cumulative
24-hour guard. Whole subprocess wall time is reconciled with worker stage
accounting. Uncaptured pre-driver work is covered by an explicit conservative
elapsed-wall reserve, not misrepresented as measured training time.

All results are in `outputs/deproxy-moment-game-v1-20261016/numeric-repair-01`.
Passing engineering checks does not authorize a full experiment. A forecast
with insufficient queue/conditioning evidence remains undetermined.
