# Six-deployment migration: qualification commands

Use `D:/Tools/Anaconda/envs/Pytorch312/python.exe`. These entry points perform
offline qualification only; none trains a model or changes files in Datasets.

1. `audit.py --config configs/extend-calibration-20260930.yaml`
   inventories all selected sessions and attempts, audits registered artifacts,
   sanitised runtime semantics, request routing, entity identities, and bounded
   shared-carrier traces. It writes `run-01` and refuses to overwrite a completed run.
2. `review.py --review-name g1-review-v2`
   independently checks the sealed inventory and records unresolved document/socket
   evidence and proposed recovered-navigation label acceptances. It does not apply
   those acceptances.
3. `forensic.py`
   records the subsequent explicit user decision, accepts six recovered-navigation
   **labels only**, and examines seven document/socket conflicts using direct
   NetLog dependencies, exact flow tuples, bounded proxy traces and 14 raw PCAPs.
   Its proposed lineage overlay is **not applied**.
4. `lineage_audit.py`
   repeats the direct primary-document dependency diagnostic across all 600 fixed
   non-Hy2 visits. It examines all successful target documents, not a favorable
   choice of attempts. Unsupported/ambiguous dependencies remain unresolved.
5. `extract.py --pilot`, then `extract.py --workers 4`
   applies the explicitly approved seven-case local lineage sidecar, freezes the
   600-visit cohort, and saves raw-window W / observed-unique exclusive TCP T
   events and summaries. Resumes completed sessions only if source hashes match.
6. `verify_extraction.py`
   independently recounts saved events, checks CUDA integer round trips without
   fitting, and prepares candidate content folds. Raw ID-string reuse is only an
   audit flag; see the subsequent epoch/alias interpretation before calling it leakage.
7. `review_extraction.py`
   writes `hold-review-02` using each held session's bounded raw trace. The earlier
   `hold-review-01` used a shared-protocol-only lifecycle table and is superseded
   for exclusive-protocol lifecycle evidence (not for its unchanged hold counts).
8. `catalog_features.py`
   exports quality-labelled audit tables. All rows remain training-ineligible;
   AnyTLS non-applicable zero T rows are excluded from the convenient T catalog.

The completed v1 extraction has 559/600 W coverage passes and 41 holds. These
commands do not release training or create C/U/H permission packages. See
`docs/extend-calibration-20260930/extraction-gate-report.md` before proceeding.

## Approved v2 measurement adaptation

- `extract_v2.py --pilot`, then `extract_v2.py --workers 4`: strict IPv4 reassembly
  with provenance and same-scope/direction W union. Unaffected v1 events are
  inherited only after rehashing raw inputs. No T ownership waiver.
- `audit_epochs_v2.py`: targeted SYN/sequence/lifecycle and conditional capture
  clock evidence. A time-contained bind is not automatic packet ownership.
- `audit_boundary_events_v2.py`: all bounded connect/dial/bind/close evidence for
  the nine remaining held visits.
- `verify_v2.py`: independent event counts, raw fragment byte replay, CUDA exact
  round trips and quality-labelled candidate exports. No model fitting.

v2 has 591/600 W coverage passes; all candidate rows still forbid training.
The nine remaining cases require a capture-scope decision and clock validation,
not a missing-packet waiver. See `docs/extend-calibration-20260930/extraction-v2-report.md`.

## Approved v3 common observation interval

`prepare_v3.py` pins collector/Chromium clock sources and prepares all 600
intervals. The actual collector records `stopped` AFTER process exit, so the
conservative end is `browser_quiescent`, before the recorded successful capture
health check and shutdown. Start is max(tun ready, physical ready).

Run `extract_v3.py --pilot`, then `extract_v3.py --workers 4`; all 600 visits are
recomputed. `audit_clock_anchors_v3.py` independently brackets TCP handshakes
using each session's NetLog offset. `verify_v3.py` recomputes events, replays
fragments and checks CUDA round trips.

`audit_isolation_v3.py` checks carrier/raw hashes and SYN/positive-packet
fingerprints. Its raw SYN-completeness flag remains false for five paths.
`audit_missing_syn_v3.py` and `qualify_identity_v3.py` provide separate,
source-qualified stable-carrier evidence; they do NOT invent missing SYNs.

`prepare_packages_v3.py` exports 1,080 C/U/H scenarios into 4,320 role folders
and checks forbidden access. `smoke_v3.py` performs two training-only CUDA
engineering runs, without H/reference reads. `seal_preparation_v3.py` freezes
the scientific budget and package hashes. Production generator/classifier/scorer
workers still need their own frozen execution contracts before formal training.

Completed outputs are immutable checkpoints. The first command accepts a config
with a new output directory; the review accepts a versioned review name. The two
targeted scripts currently reference this frozen run and must be versioned for a
new experiment rather than silently overwriting existing records.

Tests:

```powershell
& D:/Tools/Anaconda/envs/Pytorch312/python.exe -m pytest tests/unit/test_extend_calibration.py tests/unit/test_extend_forensic.py -q -p no:cacheprovider --basetemp outputs/extend-tests-new-unique-directory
```

Use a fresh dedicated test directory: pytest may clean its explicit basetemp.
Do not point it at an existing experiment directory.

## Boundaries

- Domain names and connection IDs are audit identities, never model features.
- A browser NetLog `direct://` proxy setting is not evidence of bypassing a TUN proxy.
- A shared carrier's physical packet count is not a document-specific byte count.
- A label acceptance does not waive routing, capture coverage, or split isolation.
- Seven verified corrections do not establish correctness for all other mappings.
- Hy2 remains measurement-only under the approved decision.
- Generation, CUDA training and held-out scoring are still gated on qualification.
