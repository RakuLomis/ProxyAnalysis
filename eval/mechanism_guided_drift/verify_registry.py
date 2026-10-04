"""Independent persisted-output verification, no fitting and no capture payload reads."""
from collections import Counter
import json
import re
from pathlib import Path

from common import ROOT, OUT, DOC, read_json, file_hash
from safe_profile import FIELDS, valid_value


def verify():
    audit = read_json(OUT / 'registry-audit.json')
    profiles = read_json(OUT / 'protocol-profile-registry.json')['profiles']
    ledger = read_json(OUT / 'session-profile-ledger.json')
    sources = read_json(OUT / 'mechanism-contract.json')['rules']
    ids = {p['profile_id'] for p in profiles}
    assert len(ids) == len(profiles) == 6 and audit['engineering_passed']
    assert len(ledger) == audit['selected_sessions'] == 1974
    assert len({r['session_id'] for r in ledger}) == len(ledger)
    assert sum(r['main_cohort'] for r in ledger) == 600
    assert Counter(r['profile_id'] for r in ledger) == Counter({p['profile_id']: p['selected_sessions'] for p in profiles})
    for row in ledger:
        assert row['profile_id'] in ids and row['status'] != 'conflicting'
        if row['main_cohort']:
            assert row['cached_deployment_evidence'] == 'verified'
    for profile in profiles:
        for layer in ['configured', 'effective']:
            for field, node in profile['fields'][layer].items():
                assert field in FIELDS
                assert node['state'] != 'known' or valid_value(field, node['value'])
                assert node['state'] == 'known' or node['value'] is None
        assert len(profile['evidence']) == profile['selected_sessions']
    for rule in sources:
        assert not rule['exact_observed_visit_overhead_claimed']
        for reference in rule['sources']:
            filename = ROOT / reference['local_path']
            assert file_hash(filename) == reference['sha256']
            lines = filename.read_text(encoding='utf-8').splitlines()
            assert all(reference['marker'] in lines[i - 1] for i in reference['line_numbers'])
    for filename, expected in read_json(OUT / 'baseline-manifest.json')['sha256'].items():
        assert file_hash(ROOT / filename) == expected, 'frozen_input_changed'
    for reference in read_json(OUT / 'evidence-inventory.json')['records']:
        assert file_hash(ROOT / reference['path']) == reference['sha256'], 'metadata_changed'
    documents = list(DOC.glob('*.md'))
    for document in documents:
        for target in re.findall(r'\]\(([^)]+)\)', document.read_text(encoding='utf-8')):
            if not target.startswith('https://'):
                assert (document.parent / target).exists(), 'missing_document_link'
    assert not audit['G1_accepted'] and not audit['next_stage_authorized']
    assert not audit['classification_performed'] and not audit['regression_performed']
    assert audit['capture_payload_files_opened'] == 0
    result = {'passed': True, 'selected_rows': len(ledger), 'main_rows': 600,
              'profiles': 6, 'mechanism_rules': len(sources), 'G1_pending': True,
              'frozen_input_hashes_rechecked': True, 'metadata_hashes_rechecked': True}
    print(json.dumps(result, indent=2))
    return result


if __name__ == '__main__':
    verify()
