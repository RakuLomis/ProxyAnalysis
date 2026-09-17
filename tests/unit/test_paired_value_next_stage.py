import copy

import numpy as np
import pytest

from proxy_analysis.paired_information.reference_retrain import (
    SCALAR_NAMES, assert_partition, build_matrix, inner_indices, loss_bits,
)


def spec():
    return [{'id': name, 'transform': 'log_ratio' if i < 8 or i >= 12 else 'difference'}
            for i, name in enumerate(SCALAR_NAMES)]


def test_reference_metadata_and_identity_fields_do_not_enter_matrix():
    row = {'pre': dict.fromkeys(SCALAR_NAMES, 2), 'post': dict.fromkeys(SCALAR_NAMES, 4)}
    altered = copy.deepcopy(row)
    altered.update(session_id='secret', protocol='changed', target_url='secret')
    for side in ('pre', 'post'):
        altered[side].update(ip_src='secret', sni='secret', captured_bytes=999999)
    for view in ('pre', 'post', 'joint_scalar', 'delta_scalar'):
        np.testing.assert_equal(build_matrix([row], spec(), view),
                                build_matrix([altered], spec(), view))


def test_zero_log_operand_is_missing_not_smoothed():
    row = {'pre': dict.fromkeys(SCALAR_NAMES, 0), 'post': dict.fromkeys(SCALAR_NAMES, 2)}
    result = build_matrix([row], spec(), 'delta_scalar')[0]
    assert np.isnan(result[0])
    assert result[8] == 2


def test_overlap_positive_control():
    row = {'session_id': 'a', 'target_url': 'u'}
    with pytest.raises(ValueError, match='overlap'):
        assert_partition([row], [], [row])
    with pytest.raises(ValueError, match='target_url'):
        assert_partition([row], [{'session_id': 'b', 'target_url': 'u'}], [])


def test_seeded_inner_partitions_are_grouped_balanced_and_reproducible():
    rows = [{'session_id': f'{u}-{r}', 'target_url': f'u{u}'} for u in range(13) for r in range(10)]
    folds = list(inner_indices(rows, 1101))
    sizes = []
    for (tr, va), (tr2, va2) in zip(folds, inner_indices(rows, 1101)):
        np.testing.assert_equal(tr, tr2)
        np.testing.assert_equal(va, va2)
        assert_partition([rows[i] for i in tr], [rows[i] for i in va], [])
        sizes.append(len({rows[i]['target_url'] for i in va}))
    assert sorted(sizes) == [4, 4, 5]
    assert sorted(i for _, va in folds for i in va) == list(range(130))


def test_bit_loss_units():
    np.testing.assert_allclose(loss_bits([0, 1], [.5, .5]), [1, 1])


def test_bootstrap_copies_keep_original_url_and_pairing_population():
    from proxy_analysis.paired_information.uncertainty import url_bootstrap, expansion
    from proxy_analysis.paired_information.pairing import pairing
    rows = [{'session_id': f'{u}-{p}-{r}', 'target_url': f'u{u}',
             'protocol': p, 'repetition': r}
            for u in range(13) for p in ('SHADOWSOCKS', 'VLESS') for r in range(5)]
    counts, attempts = url_bootstrap(rows, 70001)
    assert sum(counts.values()) == 13
    assert attempts >= 1
    unique = [r for r in rows if r['target_url'] in counts]
    for tr, va in inner_indices(unique, 1101):
        a, b = [unique[i] for i in tr], [unique[i] for i in va]
        assert_partition(a, b, [])
        donors, mapping = pairing(a, 99, True)
        assert len(mapping) == len(a)
        assert all(i != donor for i, donor in enumerate(donors))
        expanded = [a[i] for i in expansion(a, counts)]
        assert {r['target_url'] for r in expanded}.isdisjoint({r['target_url'] for r in b})
