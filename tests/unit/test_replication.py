import pytest

from proxy_analysis.reproducibility.registry import ordered_attempts


@pytest.mark.parametrize('selected', [1, 2])
def test_selected_attempt_is_not_assumed_last(selected):
    run = {'session_ids': [f's{selected}'], 'prior_session_ids': [f's{3-selected}'],
           'selected_attempt': selected, 'attempts': [
               {'ordinal': n, 'session_ids': [f's{n}'], 'selected': n == selected} for n in [1, 2]]}
    ordered = ordered_attempts(run, {})
    assert [(n, sid) for n, sid, _ in ordered] == [(1, 's1'), (2, 's2')]


def test_contradictory_selected_rejected():
    run = {'session_ids': ['b'], 'prior_session_ids': ['a'], 'selected_attempt': 1,
           'attempts': [{'ordinal': 1, 'session_ids': ['a']}, {'ordinal': 2, 'session_ids': ['b']}]}
    with pytest.raises(ValueError, match='selected_attempt'):
        ordered_attempts(run, {})


def test_legacy_chronology_requires_evidence():
    with pytest.raises(ValueError, match='chronology'):
        ordered_attempts({'session_ids': ['b'], 'prior_session_ids': ['a']}, {'a': {}, 'b': {}})
