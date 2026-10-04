import json
import unittest
from safe_profile import extract_layer, valid_value, normalize_protocol


class SafeProfileTests(unittest.TestCase):
    def test_nested_secret_and_free_text_not_copied(self):
        raw = {'cipher': {'state': 'known', 'value': 'aes-256-gcm',
                          'endpoint': 'secret.example:443', 'password': 'DO_NOT_EXPORT'},
               'plugin': {'state': 'unknown', 'reason': 'DO_NOT_EXPORT'},
               'password': {'state': 'known', 'value': 'DO_NOT_EXPORT'},
               'tls': {'state': 'known', 'value': True},
               'obfs': {'state': 'known', 'value': {'password': 'DO_NOT_EXPORT'}}}
        result, counts = extract_layer(raw)
        text = json.dumps(result)
        self.assertNotIn('DO_NOT_EXPORT', text)
        self.assertNotIn('secret.example', text)
        self.assertNotIn('endpoint', text)
        self.assertEqual(counts['non_allowlisted_fields'], 1)
        self.assertEqual(counts['invalid_typed_values'], 1)

    def test_false_unknown_and_not_applicable(self):
        result, _ = extract_layer({'tls': {'state': 'known', 'value': False},
            'reality': {'state': 'unknown'}, 'plugin_tls': {'state': 'not_applicable'}})
        self.assertIs(result['tls']['value'], False)
        self.assertEqual(result['tls']['status'], 'confirmed')
        self.assertEqual(result['reality']['status'], 'insufficient')
        self.assertEqual(result['plugin_tls']['status'], 'not_applicable')

    def test_strict_types_and_ranges(self):
        self.assertFalse(valid_value('tls', 1))
        self.assertFalse(valid_value('udp_mtu', True))
        self.assertFalse(valid_value('udp_mtu', float('nan')))
        self.assertFalse(valid_value('udp_mtu', -1))
        self.assertFalse(valid_value('transport', 'https://secret.example'))
        self.assertFalse(valid_value('alpn', ['h3', 'secret.example']))
        self.assertFalse(valid_value('cipher', {'key': 'secret'}))
        self.assertTrue(valid_value('udp_mtu', 1197))

    def test_unknown_never_exports_an_attached_value(self):
        result, _ = extract_layer({'cipher': {'state': 'unknown', 'value': 'DO_NOT_EXPORT'}})
        self.assertIsNone(result['cipher']['value'])

    def test_protocol_alias_is_explicit_not_fuzzy(self):
        self.assertEqual(normalize_protocol('ss'), 'shadowsocks')
        self.assertEqual(normalize_protocol('shadowsocks'), 'shadowsocks')
        self.assertIsNone(normalize_protocol('vless-secret.example'))
        self.assertIsNone(normalize_protocol(None))


if __name__ == '__main__':
    unittest.main()
