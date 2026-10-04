import unittest
from local_rules import local_rule_checks, quic_varint_length


class DiagnosticTests(unittest.TestCase):
    def test_rules(self):
        self.assertTrue(all(local_rule_checks().values()))
    def test_varint_invalid(self):
        for value in [-1,2**62]:
            with self.assertRaises(ValueError):quic_varint_length(value)


if __name__ == '__main__':unittest.main()
