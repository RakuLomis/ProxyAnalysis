import unittest
from registry import normalize_derived
from mechanisms import qualify_rule
from common import relative_child, ROOT, read_json


class RegistrySemanticsTests(unittest.TestCase):
    def test_anytls_zero_remains_option_zero(self):
        fields = {'idle_session_timeout_seconds': {'state': 'known', 'value': 0}}
        result = normalize_derived('anytls', fields)
        self.assertEqual(fields['idle_session_timeout_seconds']['value'], 0)
        self.assertEqual(result[0]['source_derived_value'], 30)
        self.assertFalse(result[0]['runtime_timer_observed'])

    def test_vision_false_is_inactive_not_unknown(self):
        rule = {'requirements': {'vision': True}}
        self.assertEqual(qualify_rule(rule, {'vision': {'state': 'known', 'value': False}})
                         ['applicability'], 'inactive_configuration_branch')
        self.assertEqual(qualify_rule(rule, {})['applicability'], 'configuration_unresolved')

    def test_auto_does_not_become_aes(self):
        result = normalize_derived('vmess', {'cipher': {'state': 'known', 'value': 'auto'}})
        self.assertIsNone(result[0]['value'])
        self.assertEqual(result[0]['status'], 'insufficient')

    def test_local_rule_does_not_claim_observed_counts(self):
        result = qualify_rule({'requirements': {'tls': True}}, {'tls': {'state': 'known', 'value': True}})
        self.assertFalse(result['internal_counts_observed'])
        self.assertEqual(result['capture_prediction_grade'], 'empirical-only')

    def test_path_escape_and_capture_reads_rejected(self):
        for value in ['../other.json', '/other.json', 'C:/other.json']:
            with self.assertRaises(ValueError):
                relative_child(ROOT, value)
        with self.assertRaises(ValueError):
            read_json(ROOT / 'never-open.pcap')


if __name__ == '__main__':
    unittest.main()
