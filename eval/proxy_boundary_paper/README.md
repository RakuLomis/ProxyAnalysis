# Frozen-result paper build

Run from the repository root with Pytorch312:

```powershell
python eval/proxy_boundary_paper/build_all.py
python -m pytest eval/proxy_boundary_paper/tests -q
```

No estimator is fitted. Inputs under `outputs/` are read-only. The build records SHA-256 hashes and copies the small JSON evidence used for figures. Missing sources fail rather than silently substituting report text. All empirical figures are generated with Matplotlib; diagrams use editable draw.io XML. See the paper README for compilation and diagram export.
