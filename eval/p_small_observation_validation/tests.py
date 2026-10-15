"""Synthetic memory-only engineering checks; never open real PCAP files."""
from dataclasses import replace
import io
import ipaddress
import struct
import unittest
from .common import ROOT
from proxy_analysis.parsing.pcapng import CaptureRecord
from proxy_analysis.observation.physical_tcp import Endpoint, EndpointDecoder, Packet, epochs
from proxy_analysis.observation.window_stats import summarize
from proxy_analysis.observation.visit_histogram import aggregate, HIST
from .packages import validate_worker_package


LOCAL, REMOTE = "192.0.2.1", "203.0.113.10"
ENDPOINT = Endpoint(REMOTE, 443)


def pkt(t, seq=101, body=b"abcd", flags=16, direction=1, port=20000):
    return Packet(t, t+1, direction, LOCAL, port, REMOTE, 443, seq, 0, flags,
                  len(body), body, f"synthetic-{t}-{seq}-{port}")


def stat(packets, a=0, b=100):
    es = epochs(packets)
    return [summarize(e, a, b) for e in es]


def handshake():
    return [pkt(0, 100, b"", 2), pkt(1, 499, b"", 18, -1)]


def ipv4(payload, protocol=6, ident=1, offset=0, more=False, reverse=False):
    src, dst = (REMOTE, LOCAL) if reverse else (LOCAL, REMOTE)
    return struct.pack("!BBHHHBBH4s4s", 69, 0, 20+len(payload), ident,
                       offset//8 + (8192 if more else 0), 64, protocol, 0,
                       ipaddress.ip_address(src).packed, ipaddress.ip_address(dst).packed) + payload


def tcp(body=b"abcd", seq=101, flags=16, reverse=False, port=443):
    return struct.pack("!HHIIHHHH", port if reverse else 20000,
                       20000 if reverse else port, seq, 0, (5 << 12)+flags,
                       1024, 0, 0) + body


def rec(t, data, original=None):
    return CaptureRecord(0, 0, 101, t+1, t, len(data), original or len(data), data)


class Counters(unittest.TestCase):
    def test_retransmission_vs_packet_runs(self):
        s = stat(handshake()+[pkt(2), pkt(3, 500, b"xyz", direction=-1), pkt(4)])[0]
        self.assertTrue(s["valid"])
        self.assertEqual([s["statistics"][k] for k in ["W_up", "U_up", "P_up", "E_up", "FR_packet_runs", "R_unique_zero_runs"]], [8, 4, 2, 1, 3, 2])

    def test_partial_overlap(self):
        s = stat(handshake()+[pkt(2), pkt(3, 103, b"cdef")])[0]
        self.assertEqual(s["statistics"]["U_up"], 6)
        self.assertEqual(s["statistics"]["E_up"], 2)
        self.assertTrue(s["valid"])

    def test_out_of_order(self):
        s = stat(handshake()+[pkt(2, 105, b"ef"), pkt(3, 101, b"abcd")])[0]
        self.assertEqual(s["statistics"]["U_up"], 6)
        self.assertTrue(s["valid"])

    def test_conflict_rejected(self):
        s = stat(handshake()+[pkt(2), pkt(3, 102, b"XX")])[0]
        self.assertFalse(s["valid"])
        self.assertIn("overlap_content_conflict", s["reasons"])

    def test_cold_window_does_not_use_earlier_payload(self):
        s = stat(handshake()+[pkt(2), pkt(11)], 10, 20)[0]
        self.assertEqual(s["statistics"]["U_up"], 4)
        self.assertEqual(s["statistics"]["E_up"], 1)

    def test_half_open_window(self):
        s = stat(handshake()+[pkt(10), pkt(20, 105)], 10, 20)[0]
        self.assertEqual(s["statistics"]["W_up"], 4)

    def test_syn_fin_not_payload(self):
        s = stat([pkt(0, 100, b"abcd", 2), pkt(2, 105, b"", 1)])[0]
        self.assertEqual(s["statistics"]["U_up"], 4)

    def test_wrap(self):
        m = 1 << 32
        s = stat([pkt(0, m-3, b"", 2), pkt(2, m-2), pkt(3, 2, b"ef")])[0]
        self.assertEqual(s["statistics"]["U_up"], 6)
        self.assertTrue(s["valid"])

    def test_halfspace_ambiguity(self):
        s = stat(handshake()+[pkt(2), pkt(3, 101+(1 << 31))])[0]
        self.assertFalse(s["valid"])

    def test_window_payload_integrity(self):
        bad = replace(pkt(2), payload=b"a")
        self.assertFalse(stat(handshake()+[bad])[0]["valid"])

    def test_rst_does_not_remove_nonempty_connection(self):
        s = stat(handshake()+[pkt(2, flags=20)])[0]
        self.assertTrue(s["valid"])
        self.assertTrue(s["nonempty"])

    def test_direction_event_ties_ordinal(self):
        ps = handshake()+[replace(pkt(2), ordinal=20), replace(pkt(2, 500, direction=-1), ordinal=19)]
        s = stat(ps)[0]
        self.assertEqual(s["new_byte_events"][0]["direction"], -1)


class Lifecycle(unittest.TestCase):
    def test_duplicate_syn_same_epoch(self):
        self.assertEqual(len(epochs([pkt(0, 100, b"", 2), pkt(1, 100, b"", 2), pkt(2)])), 1)

    def test_port_reuse_distinct_isn_after_rst(self):
        es = epochs(handshake()+[pkt(2), pkt(3, 105, b"", 4), pkt(4, 1000, b"", 2), pkt(5, 1001)])
        self.assertEqual(len(es), 2)
        self.assertFalse(any(e.reasons for e in es))
        self.assertNotEqual(es[0].token, es[1].token)

    def test_new_syn_without_terminal_is_hold(self):
        es = epochs(handshake()+[pkt(2), pkt(4, 1000, b"", 2)])
        self.assertTrue(all(e.reasons for e in es))

    def test_midstream_unproven(self):
        self.assertIn("midstream_epoch_identity_unproven", epochs([pkt(3)])[0].reasons)

    def test_single_fin_not_terminal(self):
        self.assertFalse(epochs(handshake()+[pkt(3, 105, b"", 1)])[0].terminated)

    def test_late_previous_epoch_payload_hold(self):
        es = epochs(handshake()+[pkt(2), pkt(3, 105, b"", 4), pkt(4, 1000, b"", 2), pkt(5)])
        self.assertTrue(all("payload_may_belong_to_previous_epoch" in e.reasons for e in es))


class Decoder(unittest.TestCase):
    def decoder(self):
        return EndpointDecoder([ENDPOINT], 0, 100)

    def test_direction_from_endpoint(self):
        d = self.decoder()
        d.feed(rec(0, ipv4(tcp(b"", 100, 2))))
        d.feed(rec(2, ipv4(tcp())))
        d.feed(rec(3, ipv4(tcp(seq=500, reverse=True), reverse=True)))
        es, failures = d.finish()
        self.assertFalse(failures)
        self.assertEqual([p.direction for p in es[0].packets], [1, 1, -1])

    def test_wrong_endpoint_port(self):
        d = self.decoder()
        d.feed(rec(2, ipv4(tcp(port=444))))
        self.assertFalse(d.finish()[0])

    def test_udp_not_tcp_feature(self):
        d = self.decoder()
        d.feed(rec(2, ipv4(struct.pack("!HHHH", 20000, 443, 8, 0), protocol=17)))
        self.assertFalse(d.finish()[0])

    def test_payload_truncation(self):
        d = self.decoder()
        full = ipv4(tcp())
        d.feed(rec(2, full[:-2], len(full)))
        self.assertIn("endpoint_packet_truncated", d.finish()[1])

    def test_malformed_unknown_scope_hold(self):
        d = self.decoder()
        d.feed(rec(2, b"\x45\0"))
        self.assertIn("unclassifiable_packet", d.finish()[1])

    def test_ipv4_fragment_complete_completion_time(self):
        d = self.decoder()
        data = tcp(b"abcdefghij")
        d.feed(rec(2, ipv4(data[:24], more=True)))
        d.feed(rec(3, ipv4(data[24:], offset=24)))
        es, failures = d.finish()
        self.assertFalse(failures)
        self.assertEqual(es[0].packets[0].timestamp_ns, 3)
        self.assertEqual(es[0].packets[0].payload, b"abcdefghij")

    def test_orphan_fragment_no_resync(self):
        d = self.decoder()
        d.feed(rec(2, ipv4(b"ijklmn", offset=24)))
        self.assertIn("orphan_nonzero_fragment", d.finish()[1])

    def test_fragment_incomplete_no_padding(self):
        d = self.decoder()
        d.feed(rec(2, ipv4(tcp(b"abcd"), more=True)))
        self.assertIn("incomplete_datagrams", d.finish()[1])

    def test_fragment_window_boundary_not_carried(self):
        d = EndpointDecoder([ENDPOINT], 10, 100)
        data = tcp(b"abcdefghij")
        d.feed(rec(2, ipv4(data[:24], more=True)))
        d.feed(rec(11, ipv4(data[24:], offset=24)))
        self.assertIn("orphan_nonzero_fragment", d.finish()[1])

    def test_ipv6_fragment_hold(self):
        d = EndpointDecoder([Endpoint("2001:db8::2", 443)], 0, 100)
        fragment = struct.pack("!BBHI", 6, 0, 1, 10)+tcp()
        ip = struct.pack("!IHBB16s16s", 6 << 28, len(fragment), 44, 64,
                         ipaddress.ip_address("2001:db8::1").packed,
                         ipaddress.ip_address("2001:db8::2").packed)+fragment
        d.feed(rec(2, ip))
        self.assertIn("unsupported_ipv6_fragments", d.finish()[1])

    def test_outside_payload_not_retained(self):
        d = EndpointDecoder([ENDPOINT], 10, 100)
        d.feed(rec(2, ipv4(tcp())))
        self.assertIsNone(d.packets[0].payload)


class Histogram(unittest.TestCase):
    def test_dimensions_blocks_and_zero_direction(self):
        r = aggregate(stat(handshake()+[pkt(2)]), coverage_verified=True)
        self.assertEqual(len(r["x"]), 96)
        self.assertEqual(r["x"]["h01_00"], 1)
        self.assertEqual(r["x"]["h00_01"], 1)

    def test_edge_goes_right(self):
        r = aggregate(stat(handshake()+[pkt(2, body=b"x"*256)]), coverage_verified=True)
        self.assertEqual(r["x"]["h00_02"], 1)

    def test_equal_connection_not_byte_weight(self):
        cs = stat(handshake()+[pkt(2)])+stat([pkt(0, 100, b"", 2, port=20001), pkt(2, body=b"x"*256, port=20001)])
        r = aggregate(cs, coverage_verified=True)
        self.assertEqual(r["x"]["h00_01"], .5)
        self.assertEqual(r["x"]["h00_02"], .5)

    def test_empty_not_zero_vector(self):
        r = aggregate(stat(handshake()), coverage_verified=True)
        self.assertEqual(r["status"], "empty_window")
        self.assertIsNone(r["x"])

    def test_invalid_connection_not_deleted(self):
        cs = stat(handshake()+[pkt(2)])+stat([pkt(0, body=b"x", port=20001)])
        r = aggregate(cs, coverage_verified=True)
        self.assertEqual(r["status"], "invalid_observation")
        self.assertEqual(r["nonempty_connections"], 2)
        self.assertIsNone(r["x"])

    def test_coverage_failure(self):
        self.assertEqual(aggregate(stat(handshake()+[pkt(2)]), coverage_verified=False)["status"], "invalid_observation")


class Permissions(unittest.TestCase):
    def test_metadata_reader_refuses_raw_and_indices(self):
        from .common import safe_read_path
        for name in ["phys.pcap", "tun.pcap", "netlog.json", "cdp.json", "flow-index.json", "mihomo-trace.jsonl"]:
            with self.subTest(name=name), self.assertRaises(PermissionError):
                safe_read_path(ROOT / name)

    def test_worker_refuses_labels_pair_and_pre_fields(self):
        p = {"visit_token": "a"*64, "physical_path": "phys.pcap", "endpoints": [{"address": REMOTE, "port": 443}],
             "windows": [{"version": "O1", "start_ns": 0, "end_ns": 100, "coverage_verified": False}]}
        self.assertTrue(validate_worker_package(p))
        for f in ["label_id", "pair_id", "pre", "content_id", "url"]:
            with self.subTest(field=f), self.assertRaises(PermissionError):
                validate_worker_package({**p, f: "forbidden"})


def run():
    suite = unittest.defaultTestLoader.loadTestsFromModule(__import__(__name__, fromlist=["*"]))
    stream = io.StringIO()
    result = unittest.TextTestRunner(stream=stream, verbosity=2).run(suite)
    return {"passed": result.wasSuccessful(), "tests": result.testsRun,
            "failures": len(result.failures), "errors": len(result.errors),
            "log": stream.getvalue(), "real_PCAP_reads": 0,
            "classifier_fits": 0, "engineering_scope": "synthetic_packets_only"}


if __name__ == "__main__":
    result = run()
    print(result["log"])
    raise SystemExit(0 if result["passed"] else 1)
