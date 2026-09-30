# Draft delivery status — 2026-09-21

## Delivered

- IEEEtran journal-style English main manuscript: 12 pages including references.
- Supplementary manuscript: 4 pages.
- Nine figures: two editable draw.io frameworks and seven Python empirical figure panels.
- Source-generated LaTeX tables, 157-dimension representation documentation, and nine-claim evidence ledger.
- Result snapshots with original paths and SHA-256 digests; no model fitting, new capture, or parameter search.
- Seven paper-specific tests passed (result consistency, unique selection, paired contrasts, three algebra/geometry checks, diagram references).

## Rendering and compilation

Compiled locally with portable Tectonic 0.17.0; draw.io desktop 31.4.5 portable exported cropped vector diagrams. Both tools reside in the user's temporary tool directory, not in conda or the repository. No system PATH or Pytorch312 packages were changed. TeX package cache was populated on first compile. No manuscript or trace upload to an online editor was performed.

Official release archives downloaded:

- Tectonic Windows archive SHA-256: `F61CE51F0B0ADE1015B7DE7EF368541C5424E9756ECBD0D7AF97D6D48030845F`.
- draw.io Windows archive SHA-256: `D2C6F1EB4ED39FAC9BB70FE6A1D359B8B9B01778145D65A68D29554994414207`.

These are locally recorded download hashes, not an assertion of independent signature verification.

All 16 pages were rendered with PDFium and reviewed in contact sheets; chart and diagram previews were also examined. The workflow corrected crossing diagram arrows, a covered chart legend, a long equation, and unbreakable histogram-boundary arrays. Final logs contain no overfull boxes or unresolved citations/references. There are remaining underfull spacing notices and an input-PDF version warning from XeTeX's image reader; the emitted main document is PDF 1.7 and both diagram pages render correctly. No blank pages or `??` references were detected.

## Research boundaries

The manuscript retains pooled/deployment differences, negative controls, historical MLP positive evidence, probability-floor semantics, and retrospective selection limitations. It is a reference draft, not submission-ready: author/venue/ethics/release decisions and a broader focused novelty review remain open in `unresolved_items.md`. The eight verified references are an initial technical bibliography, not an exhaustive related-work survey.

No Git commit or push was performed. Existing experiment code and large local outputs were not modified. Figures and source files are under the requested paper directory; plotting/build code is under `eval/proxy_boundary_paper/`.
