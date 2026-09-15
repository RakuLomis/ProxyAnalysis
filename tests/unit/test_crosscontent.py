from collections import Counter
from copy import deepcopy
from pathlib import Path

import pytest
import yaml

from proxy_analysis.crosscontent.prepare import (
    content_slots, prepare, readiness, schedule, validate_contents, validate_design,
)


@pytest.fixture
def config():
    return yaml.safe_load(Path('configs/activity-crosscontent-v1/design.yaml').read_text())


def test_matrix_and_reproducibility(config):
    contents = content_slots(config)
    assert len(contents) == 92
    pilot = schedule(config, contents, 'pilot')
    assert len(pilot) == 72
    assert pilot == schedule(config, list(reversed(contents)), 'pilot')
    formal = schedule(config, contents, 'formal')
    assert len({r['planned_unit_id'] for r in formal}) == 960
    assert Counter(r['partition'] for r in formal) == {
        'development': 432, 'unseen_content_test': 288,
        'unseen_date_diagnostic': 144, 'joint_locked_test': 96}
    for block in (1, 2):
        block_rows = [r for r in pilot if r['block_id'] == block]
        orders = Counter(tuple(r['protocol'] for r in block_rows[i:i+3])
                         for i in range(0, len(block_rows), 3))
        assert len(orders) == 6 and set(orders.values()) == {2}
    assert all(r['requires_model_lock'] == (r['block_id'] == 4) for r in formal)


def test_no_fake_readiness(config):
    result = readiness(config, content_slots(config))
    assert result['status'] == 'blocked'
    assert not result['capture_ready']
    assert len(result['unresolved_pilot_slots']) == 12


def test_duplicate_group_rejected(config):
    rows = content_slots(config)
    rows[0]['content_group_id'] = rows[-1]['content_group_id'] = 'shared-content'
    with pytest.raises(ValueError, match='duplicate content group'):
        validate_contents(config, rows)


@pytest.mark.parametrize('url', ['http://www.bilibili.com/video/1',
                                'https://bilibili.com.evil.example/video/1',
                                'https://user:secret@bilibili.com/video/1'])
def test_invalid_urls(config, url):
    rows = content_slots(config)
    rows[0]['target_url'] = url
    with pytest.raises(ValueError, match='HTTPS URL'):
        validate_contents(config, rows)


def test_assignment_cannot_change(config):
    rows = content_slots(config)
    rows[0]['split_role'] = 'locked'
    with pytest.raises(ValueError, match='assignment'):
        validate_contents(config, rows)


def test_invalid_config(config):
    bad = deepcopy(config)
    bad['observation']['stop_at_playback_goal'] = True
    with pytest.raises(ValueError):
        validate_design(bad)


def test_write_and_refuse_overwrite(tmp_path):
    config_path = Path('configs/activity-crosscontent-v1/design.yaml')
    output = tmp_path / 'prepared'
    result = prepare(config_path, output)
    assert result['actual_captures'] == 0
    assert (output / 'readiness.json').is_file()
    with pytest.raises(FileExistsError):
        prepare(config_path, output)
