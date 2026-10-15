"""Additional in-memory IO and conservative lifecycle checks."""
import io
import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch

from .pilot_worker import ReadBudget, HashingReader, lifecycle_guard
from .tests import pkt, handshake
from proxy_analysis.observation.physical_tcp import epochs


class PilotTests(unittest.TestCase):
    def test_hash_single_stream(self):
        b = ReadBudget([("phys.pcap", 4)], 4)
        r = HashingReader(io.BytesIO(b"abcd"), b, 4)
        self.assertEqual(r.read(2)+r.read(2), b"abcd")
        self.assertEqual(b.bytes, 4)
        self.assertEqual(r.size, 4)

    def test_budget_limit(self):
        b = ReadBudget([("phys.pcap", 3)], 3)
        with self.assertRaises(PermissionError):
            HashingReader(io.BytesIO(b"abcd"), b, 3).read()

    def test_unregistered_path(self):
        b = ReadBudget([("phys.pcap", 4)], 4)
        for p in ["tun.pcap", "other/phys.pcap", "netlog.json"]:
            with self.assertRaises(PermissionError):
                b.authorize(p)

    def test_budget_manifest(self):
        with self.assertRaises(ValueError):
            ReadBudget([("phys.pcap", 4)], 5)

    def test_same_isn_after_rst_is_ambiguous(self):
        e = epochs(handshake()+[pkt(2), pkt(3, 105, b"", 4), pkt(4, 100, b"", 2)])[0]
        lifecycle_guard(e)
        self.assertIn("bare_syn_after_terminal_same_isn_ambiguous", e.reasons)

    def test_same_isn_before_terminal_is_retransmission(self):
        e = epochs([pkt(0, 100, b"", 2), pkt(1, 100, b"", 2), pkt(2)])[0]
        lifecycle_guard(e)
        self.assertFalse(e.reasons)

    def test_same_isn_after_two_fins_is_ambiguous(self):
        e = epochs(handshake()+[pkt(2, 105, b"", 1), pkt(3, 500, b"", 1, -1), pkt(4, 100, b"", 2)])[0]
        lifecycle_guard(e)
        self.assertTrue(e.reasons)

    def test_distinct_isn_after_rst_stays_separate(self):
        es = epochs(handshake()+[pkt(2), pkt(3, 105, b"", 4), pkt(4, 1000, b"", 2)])
        for e in es:
            lifecycle_guard(e)
        self.assertEqual(len(es), 2)
        self.assertFalse(any(e.reasons for e in es))

    def test_no_second_raw_pass(self):
        b = ReadBudget([("phys.pcap", 4)], 4)
        fake = unittest.mock.Mock()
        fake.stat.return_value.st_size = 4
        with patch("eval.p_small_observation_validation.pilot_worker.io_path", return_value=fake):
            b.authorize("phys.pcap")
            with self.assertRaises(PermissionError):
                b.authorize("phys.pcap")


def run():
    stream = io.StringIO()
    r = unittest.TextTestRunner(stream=stream, verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(PilotTests))
    return {"passed": r.wasSuccessful(), "tests": r.testsRun, "failures": len(r.failures),
            "errors": len(r.errors), "log": stream.getvalue(), "real_PCAP_reads": 0}
