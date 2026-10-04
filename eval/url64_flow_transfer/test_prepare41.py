import copy
import unittest

from prepare41 import public_post_index, select_post


class PostOnlyTests(unittest.TestCase):
    def flow(self):
        return {'egress_outcome': 'proxy', 'proxy_semantics': {'protocol': 'ss'},
                'pre_flow': {'secret': 'unavailable'}, 'match': {'status': 'failed'},
                'request_ids': ['hidden'], 'carrier_binding': {
                    'carrier_id': 'c1', 'mode': 'exclusive', 'physical_paths': [{
                        'network': 'tcp', 'complete': True, 'src_ip': '192.0.2.1',
                        'src_port': 1234, 'dst_ip': '192.0.2.2', 'dst_port': 443}]}}

    def test_pre_and_matching_mutations_cannot_change_post(self):
        a = self.flow(); b = copy.deepcopy(a)
        del b['pre_flow']; b['match'] = {'status': 'matched'}; del b['request_ids']
        self.assertEqual(select_post(public_post_index([a], 'shadowsocks')),
                         select_post(public_post_index([b], 'shadowsocks')))

    def test_duplicate_logical_rows_do_not_duplicate_carrier(self):
        f = self.flow()
        result = select_post(public_post_index([f, copy.deepcopy(f)], 'shadowsocks'))
        self.assertEqual(len(result), 1)
        self.assertEqual(len(result['c1']), 1)

    def test_no_shared_or_direct_fallback(self):
        f = self.flow(); f['carrier_binding']['mode'] = 'shared'
        self.assertEqual(select_post(public_post_index([f], 'shadowsocks')), {})
        f = self.flow(); f['egress_outcome'] = 'direct'
        self.assertEqual(public_post_index([f], 'shadowsocks'), [])


if __name__ == '__main__': unittest.main()
