import copy
import numpy as np
import pyarrow
import pytest
import torch

from proxy_analysis.crosscontent.group_anchor_reliability import (
    feature_groups, normalize_fit, normalized, crossfit, aggregate, inner_splits)
from proxy_analysis.crosscontent.group_anchor_models import group_losses, pretrain
from proxy_analysis.crosscontent.natural_pair_ssl_data import fingerprint


def test_groups_cover_and_have_no_duplicate_fr():
    groups = feature_groups()
    assert [len(g['indices']) for g in groups] == [4, 2, 4, 22, 24, 101]
    assert sorted(j for g in groups for j in g['indices']) == list(range(157))


def toy():
    rows = [{'session_id': f'{c}-{p}-{r}', 'content_id': str(c), 'label_id': 'a',
             'protocol': p, 'repetition': r} for c in range(4) for p in ('SS', 'VL') for r in (1, 2, 4, 5)]
    rng = np.random.default_rng(3); post = rng.normal(size=(len(rows), 157))
    pre = 2*post+3
    return rows, post, pre


def test_constant_missing_and_training_only_scaler():
    x = np.array([[1., np.nan, 1.], [1., np.nan, 3.]])
    s = normalize_fit(x)
    assert s['valid'] == [False, False, True]
    assert np.isfinite(normalized(x, s)).all()
    with pytest.raises(ValueError): normalize_fit([[np.inf]])


def test_crossfit_closed_partitions_and_wrong_donors():
    rows, post, pre = toy()
    true, _ = crossfit(rows, post, pre, 'true')
    wrong, _ = crossfit(rows, post, pre, 'mismatched')
    assert true['passed'] and min(true['reliability']) > .95
    assert sum(wrong['reliability']) < sum(true['reliability'])
    for split in wrong['splits']:
        assert not set(split['train_ids']) & set(split['validation_ids'])
        for part in ('train', 'validation'):
            assert set(split[part+'_ids']) == set(split[part+'_donor_ids'])
            assert all(a != b for a, b in zip(split[part+'_ids'], split[part+'_donor_ids']))
    changed = [{**r, 'label_id': 'renamed'} for r in rows]
    assert inner_splits(changed) == inner_splits(rows)


def test_reliability_has_no_test_data_dependency():
    rows, post, pre = toy()
    # Evaluation rows are deliberately explosive; selecting allowed IDs happens first.
    allowed = {r['session_id'] for r in rows}
    combined = rows + [{'session_id': 'test', 'content_id': 'unseen', 'label_id': 'secret'}]
    selected = [r for r in combined if r['session_id'] in allowed]
    assert selected == rows
    a, _ = crossfit(selected, post, pre, 'true')
    combined[-1]['label_id'] = 'changed'; combined[-1]['pre'] = float('inf')
    b, _ = crossfit([r for r in combined if r['session_id'] in allowed], post, pre, 'true')
    assert fingerprint(a) == fingerprint(b)


def test_group_loss_dimension_normalization_missing_and_gradient():
    groups = [{'indices': [0]}, {'indices': [1, 2, 3]}]
    predictions = [torch.ones(2, 1, dtype=torch.float64, requires_grad=True),
                   torch.ones(2, 3, dtype=torch.float64, requires_grad=True)]
    target = torch.zeros(2, 4, dtype=torch.float64); mask = torch.ones(2, 4, dtype=torch.bool)
    losses = group_losses(predictions, target, mask, groups)
    assert torch.allclose(losses, torch.tensor([.5, .5], dtype=torch.float64))
    losses.sum().backward()
    assert all(p.grad.abs().sum() > 0 for p in predictions)
    mask[:, 1:] = False
    assert float(group_losses(predictions, target, mask, groups)[1].detach()) == 0


@pytest.mark.parametrize('arm', ['R3', 'R4', 'R5', 'R6'])
def test_anchor_replay_and_initialization(arm):
    torch.set_num_threads(1)
    rng = np.random.default_rng(2)
    ssl = {'session_ids': list('abcd'), 'pre': rng.normal(size=(4, 157)).tolist(),
           'post': rng.normal(size=(4, 157)).tolist(), 'donor_indices': [1, 2, 3, 0]}
    anchor = {'session_ids': list('abcd'), 'target': ssl['pre'], 'target_mask': np.ones((4, 157), bool).tolist(),
              'target_scaler': {}, 'weights': {a: [1/6]*6 for a in ['R3', 'R4', 'R5', 'R6']}}
    cfg = {'steps': 2, 'learning_rate': .001, 'variance_eps': 1e-4, 'vicreg_weights': [25,25,1],
           'anchor_lambda': 1., 'mask_rate': .05}
    _, a, _ = pretrain(ssl, anchor, arm, 1, cfg)
    _, b, _ = pretrain(ssl, anchor, arm, 1, cfg)
    assert fingerprint(a) == fingerprint(b)
    assert a['row_view_exposures'] == 24
    assert a['donor_ids'] == (list('bcda') if arm in ('R5','R6') else list('abcd'))
    with pytest.raises(ValueError): pretrain({**ssl, 'labels': [0]*4}, anchor, arm, 1, cfg)


def test_no_valid_group_stops():
    rows, post, pre = toy()
    result, _ = crossfit(rows, post, np.zeros_like(pre), 'true')
    assert not result['passed'] and result['weights'] == [0.]*6
