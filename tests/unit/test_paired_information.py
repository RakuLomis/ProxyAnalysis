from pathlib import Path

import numpy as np
import pytest

from proxy_analysis.paired_information.pairing import pairing, matrix
from proxy_analysis.paired_information.prepare import guarded, canonical, assert_replay
from proxy_analysis.paired_information.extensions import temperature
from proxy_analysis.paired_information.report import audit_predictions


def sample_rows():
    return [{'session_id': f'{u}-{p}-{r}', 'target_url': u, 'protocol': p,
             'repetition': r, 'pre': {'x': r+1}, 'post': {'x': (r+1)*2}}
            for u in ['url1', 'url2'] for p in ['SS', 'VLESS'] for r in range(5)]


def test_pairing_is_partition_local_bijection():
    rows = sample_rows()
    donors, mapping = pairing(rows, 9, True)
    assert sorted(donors) == list(range(len(rows)))
    assert all(i != j for i, j in enumerate(donors))
    assert donors == pairing(rows, 9, True)[0]
    for i, j in enumerate(donors):
        assert (rows[i]['target_url'], rows[i]['protocol']) == (rows[j]['target_url'], rows[j]['protocol'])
    assert {m['receiver_session_id'] for m in mapping} == {m['donor_session_id'] for m in mapping}


def test_loro_test_cannot_pair():
    with pytest.raises(ValueError, match='singleton'):
        pairing([r for r in sample_rows() if r['repetition'] == 1], 1, True)


def test_wrong_delta_is_recomputed():
    rows = sample_rows()
    spec = [{'id':'x', 'family':'workload', 'transform':'log_ratio', 'unit':'count'}]
    true, _ = matrix(rows, spec, 'delta_scalar')
    wrong, _ = matrix(rows, spec, 'delta_scalar', seed=8, wrong=True)
    assert np.allclose(true, np.log(2))
    assert not np.allclose(wrong, true)


def test_wrong_js_recomputed_from_histograms():
    rows = sample_rows()[:5]
    for i, row in enumerate(rows):
        row['pre']['length_hist'] = [i+1, 6-i]
        row['post']['length_hist'] = [i+1, 6-i]
    spec = [{'id':'length_js', 'family':'packetization', 'transform':'distance', 'unit':'bits'}]
    true, _ = matrix(rows, spec, 'delta_distribution')
    wrong, _ = matrix(rows, spec, 'delta_distribution', seed=8, wrong=True)
    assert np.allclose(true, 0)
    assert (wrong > 0).all()


def test_source_gate(tmp_path):
    good = tmp_path/'run'; good.mkdir()
    source = good/'x'; source.write_text('x')
    assert guarded(source, good) == source
    with pytest.raises(ValueError, match='non-0914'):
        guarded(source, tmp_path/'elsewhere')
    mixed = good/'comparison'; mixed.mkdir(); (mixed/'x').write_text('x')
    with pytest.raises(ValueError, match='mixed'):
        guarded(mixed/'x', good)


def test_replay_detects_null_and_numeric_errors():
    row = dict(metric='x', reason=None, scope='exclusive_page', selection='observed',
               pre=1., post=2., delta=np.log(2), delta_smoothed=np.log(1.5))
    assert_replay([row], [row])
    with pytest.raises(ValueError, match='numeric'):
        assert_replay([row], [{**row, 'delta': 10.}])
    with pytest.raises(ValueError, match='null'):
        assert_replay([row], [{**row, 'delta': None}])


def test_windows_long_path_canonical():
    if Path('.').resolve().drive:
        path = str(Path('.').resolve())
        assert canonical('\\\\?\\'+path) == canonical(path)


def test_temperature_finite_and_decisions_unchanged():
    from scipy.special import expit, logit
    p = np.asarray([.01, .3, .6, .95])
    t = temperature([0, 1, 0, 1], p)
    assert np.isfinite(t) and t > 0
    assert np.array_equal(expit(logit(p)/t) >= .5, p >= .5)


def test_prediction_audit_rejects_wrong_fold():
    registry = {'s': {'session_id':'s', 'target_url':'u', 'protocol':'VLESS'}}
    row = {'session_id':'s', 'fold':'u', 'truth':1, 'prob_vless':.8}
    audit_predictions([row], registry)
    with pytest.raises(ValueError, match='fold'):
        audit_predictions([{**row, 'fold':'other'}], registry)


def test_perturbation_only_changes_outer_test_pairing():
    from proxy_analysis.paired_information.experiments import evaluate
    from proxy_analysis.paired_information.report import audit_map
    rows=sample_rows()
    rows += [{**r, 'session_id':'extra-'+r['session_id'], 'target_url':'extra-'+r['target_url']}
             for r in sample_rows()]
    spec=[{'id':'x','family':'workload','transform':'log_ratio','unit':'count'}]
    cfg={'classification_C':[1.0],'seed':1}
    pred,maps,_=evaluate(rows,spec,'delta_scalar',cfg,1,False,limit=1,test_wrong=True)
    assert all(r['wrong']==(r['role']=='outer_test') for r in maps)
    assert all(not r['wrong'] and r['test_wrong'] for r in pred)
    audit_map(maps,{r['session_id']:r for r in rows})


def test_sensitivity_membership_not_silently_filtered():
    from proxy_analysis.paired_information.sensitivity import choose_rows
    rows=[{**r,'scope':'exclusive_page','selection':'observed'} for r in sample_rows()]
    assert len(choose_rows(rows,rows,'observed',2))==12
    with pytest.raises(ValueError,match='cohort mismatch'):
        choose_rows(rows[:-1],rows,'observed',2)
