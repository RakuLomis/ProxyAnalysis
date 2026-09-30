import importlib.util
from pathlib import Path
import pytest

spec=importlib.util.spec_from_file_location('paper_build',Path(__file__).parents[1]/'build_all.py')
build=importlib.util.module_from_spec(spec)
spec.loader.exec_module(build)

def test_frozen_sources():
    build.validate(build.load())

def test_selection_requires_unique_row():
    with pytest.raises(ValueError):build.select([{'a':1},{'a':1}],a=1)
    with pytest.raises(ValueError):build.select([],a=1)

def test_effect_matches_metrics():
    d=build.load()
    for r in d['cross_contrasts']:
        if r.get('domain')!='target':continue
        a,b=r['contrast'].split('-')
        ra=build.select(d['cross'],arm=a,domain='target',source_protocol=r['source_protocol'])
        rb=build.select(d['cross'],arm=b,domain='target',source_protocol=r['source_protocol'])
        assert r['macro_f1_gain']==pytest.approx(ra['macro_f1']-rb['macro_f1'])
        assert r['ce_bits_gain']==pytest.approx(rb['ce_bits']-ra['ce_bits'])
