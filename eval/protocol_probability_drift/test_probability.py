"""Boundaries, FR, group marginals, information and pre-only inference checks."""
import unittest
import numpy as np
import pandas as pd
import torch
from bins import encode, size, labels
from weights import mass
from features import event_summary
from kernels import fit_tables, predict, smooth, tensor, native_tables
from information import information


class ProbabilityChecks(unittest.TestCase):
    def test_bins(self):
        np.testing.assert_array_equal(encode([0, 1, 255, 256, 1048575, 1048576, 10**9], 'U_up'), [0, 1, 1, 2, 7, 8, 8])
        np.testing.assert_array_equal(encode([0, 1, 2, 3, 4, 7, 8, 127, 128], 'P_up'), [0, 1, 2, 3, 4, 4, 5, 8, 9])
        for f in ['U_up', 'P_up']:
            self.assertEqual(len(labels(f, True)), size(f, True))
        with self.assertRaises(ValueError): encode([-1], 'U_up')
        with self.assertRaises(ValueError): encode([np.nan], 'U_up')

    def test_weights(self):
        f = pd.DataFrame({'content_id': ['a']*4+['b']*2, 'session_id': ['1','1','1','2','3','3']})
        f['w'] = mass(f)
        np.testing.assert_allclose(f.groupby('content_id').w.sum(), [1,1])

    def test_original_fr(self):
        f = pd.DataFrame({'timestamp_ns': [1,2,3,4,5], 'raw_packet_ordinal': [1,2,3,4,5],
                          'entity_id':['x']*4+['y'], 'direction':[1,1,-1,1,-1], 'payload_bytes':[10]*5})
        r = event_summary(f, 'entity_id', 'payload_bytes')
        self.assertEqual(r['x']['runs_up'] + r['x']['runs_down'], 3)
        self.assertEqual(r['y']['runs_down'], 1)

    def test_information(self):
        for n in [tensor([[1,1],[1,1]]), tensor([[0,2],[2,0]])]:
            s = information(n)
            self.assertAlmostEqual((s['entropy_delta'] - s['H_B_given_A'] + s['H_A_given_B']).item(), 0., places=12)
        self.assertAlmostEqual(information(tensor([[1,1],[1,1]]))['MI'].item(), 0., places=12)
        self.assertAlmostEqual(information(tensor([[0,2],[2,0]]))['MI'].item(), 1., places=12)

    def test_empty_backoff(self):
        qb, k = smooth(tensor([[0,0],[1,0]]))
        torch.testing.assert_close(qb, k[0]); self.assertTrue(bool((k>0).all()))

    def test_group_and_pre_only(self):
        pre = pd.DataFrame({'content_id':['a','a','b','b'], 'pre_P_up':[1,2,3,4],
                            'pre_U_up':[1,2,3,4], 'pre_U_down':[0,0,0,0]})
        post = pd.DataFrame({'content_id':['a','a','b','b'], 'post_P_up':[4,3,2,1]})
        gp = pre.copy(); gb = post.iloc[[3,1,0,2]].copy(); gp['fit_mass']=.5; gb['fit_mass']=.5
        bundle = fit_tables(pre, post, gp, gb, [.5]*4, 'P_up')
        torch.testing.assert_close(bundle['true_counts'].sum(0), bundle['group_counts'].sum(0))
        torch.testing.assert_close(bundle['true_counts'].sum(1), bundle['group_counts'].sum(1))
        query = pre[['pre_P_up','pre_U_up','pre_U_down']]
        self.assertEqual(predict(bundle, query)['M1'].shape, (4,10))
        q = native_tables(pre, post, gp, gb, [.5]*4, 'P_up')
        self.assertEqual(q['M1'].shape, (10,5))
        self.assertTrue(bool((q['M1'][:,1:]>=q['M1'][:,:-1]).all()))


if __name__ == '__main__':
    unittest.main()
