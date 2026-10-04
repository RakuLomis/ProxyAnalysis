"""Synthetic safety checks; no experiment data required."""
import unittest

from qualify import content_key, flow_candidate, route_evidence, window_candidate


class QualificationTests(unittest.TestCase):
    def test_url_identity_keeps_content(self):
        self.assertNotEqual(content_key("https://www.youtube.com/watch?v=a"),
                            content_key("https://www.youtube.com/watch?v=b"))
        self.assertNotEqual(content_key("https://example.com/a"), content_key("https://example.com/b"))

    def test_successful_primary_not_background_route(self):
        requests = [{"resource_type": "Document", "url": "https://example.com/",
                     "connection_id": "main", "response_status": 200},
                    {"resource_type": "Script", "url": "https://cdn.test/a",
                     "connection_id": "aux", "response_status": 200}]
        conns = [{"connection_id": "main", "egress": {"mode": "direct"}},
                 {"connection_id": "aux", "egress": {"mode": "proxy"}}]
        decision, _ = route_evidence(requests, conns, {"url": "https://example.com/"}, {})
        self.assertEqual(decision, "direct_success")

    def test_shared_carrier_is_not_exclusive_flow(self):
        f = {"egress_outcome": "proxy", "carrier_binding": {"mode": "shared"},
             "post_flow": {"network": "tcp", "complete": True},
             "post_flow_disposition": "with_post_flow"}
        self.assertFalse(flow_candidate(f))
        f["carrier_binding"]["mode"] = "exclusive"
        self.assertTrue(flow_candidate(f))  # No SNI is required.
        f["egress_outcome"] = "direct"
        self.assertFalse(flow_candidate(f))

    def test_failed_coverage_is_not_candidate(self):
        self.assertFalse(window_candidate({}))
        self.assertFalse(window_candidate({"packet_coverage": {"status": "passed", "errors": ["x"]}}))
        self.assertTrue(window_candidate({"packet_coverage": {"status": "passed", "errors": []}}))


if __name__ == "__main__":
    unittest.main()
