"""The fixed empirical-Bayes backoff can improve M0 even for constant variables."""
import unittest
from kernels import tensor,smooth
from information import information


class SmoothingNullCheck(unittest.TestCase):
    def test_constant_variable_not_information_gain(self):
        n=tensor([[24.,0.,0.,0.,0.,0.,0.,0.,0.,0.]])
        q,k=smooth(n)
        self.assertAlmostEqual(information(n)['MI'].item(),0.,places=12)
        self.assertGreater(k[0,0].item(),q[0].item())
        self.assertAlmostEqual(k[0,0].item(),(24+(24+.1)/25)/25,places=12)


if __name__=='__main__':unittest.main()
