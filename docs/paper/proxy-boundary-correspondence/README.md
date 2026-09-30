# Across the Proxy Boundary — reference draft

English IEEEtran journal-style draft, September 2026. This is not a submission-ready or accepted manuscript. Authors and venue are deliberately not fabricated. See `review/` for author decisions and Chinese writing notes.

## Main files

- `main.tex`: main manuscript; modular sections under `sections/`.
- `supplement.tex`: supplementary methods, complete controls and results.
- `build/main.pdf`, `build/supplement.pdf`: locally compiled reading copies.
- `figures/source/`: editable draw.io diagrams.
- `figures/generated/`: vector PDF diagrams and Python empirical plots.
- `figures/preview/`: raster previews of empirical figures.
- `tables/`: machine-generated LaTeX tables.
- `evidence/`: JSON plot data, claim map, artifact/source SHA-256 hashes.

## Build

From the repository root, with Pytorch312:

```powershell
python eval/proxy_boundary_paper/build_all.py
python eval/proxy_boundary_paper/plot_transformations.py
python eval/proxy_boundary_paper/make_diagrams.py
python eval/proxy_boundary_paper/feature_appendix.py
python eval/proxy_boundary_paper/finish_evidence.py
python -m pytest eval/proxy_boundary_paper/tests -q -p no:cacheprovider
```

The figure build expects the existing frozen `outputs/` tree. It never trains a model or modifies its sources. Small JSON snapshots under `evidence/figure_data` support manual verification but do not replace the formal experiment outputs.

For a full local build, pass installed or portable executable paths to `eval/proxy_boundary_paper/build_paper.ps1`. Official Tectonic 0.17.0 and draw.io desktop 31.4.5 portable releases were selected for this machine; neither is committed to the repository or installed into conda. Tectonic downloads public TeX resources into its cache on the first build; manuscript contents are compiled locally, not uploaded to an online editor.

Alternatively use a standard IEEEtran-capable LaTeX environment with `pdflatex`, BibTeX, and two further `pdflatex` passes. The `.drawio` files must be exported as cropped PDF first; pre-generated PDFs are included. Run from the paper directory when using conventional LaTeX tools.

For PDF review use `eval/proxy_boundary_paper/render_qa.py` with the bundled runtime containing PDFium, pypdf, and Pillow. It renders every page and writes contact sheets and basic text checks under `build/qa`. Visual review remains necessary; text checks alone do not validate layout.

## Scope

No new collection, fitting, target-based selection, Git push, or data release accompanies this draft. Historical test counts are explicitly attributed to earlier audits, not claimed as rerun by the manuscript build. Main evidence uses the conservative 0916 six-class cohort; 0914 is historical context and the 299 cohort overlaps the primary data.
