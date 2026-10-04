import unittest
import numpy as np
from diagnostic_models import wm, torch
from p3_model import CenterRidge, startup_beta, startup_center


@unittest.skipUnless(torch.cuda.is_available(),'CUDA required')
class P3Tests(unittest.TestCase):
    def setUp(self):
        self.a=np.array([[100+i*20,200+i*30,5+i,10+i,2,2] for i in range(20)],float)
        self.b=self.a.copy();self.b[:,:2]+=np.arange(20)[:,None]*3+40
        self.aux=np.zeros((20,8));self.aux[:,:2]=np.log1p([1,2])
    def test_D0_exact(self):
        old=wm.Ridge(self.a,wm.encode(self.b));new=CenterRidge(self.a,wm.encode(self.b))
        torch.testing.assert_close(new.predict(self.a),old.predict(self.a),atol=0,rtol=0)
    def test_zero_beta_restores_D1(self):
        x=CenterRidge(self.a,wm.encode(self.b),self.aux,self.a,True)
        y=CenterRidge(self.a,wm.encode(self.b),self.aux)
        torch.testing.assert_close(x.predict(self.a,self.aux),y.predict(self.a,self.aux),atol=0,rtol=0)
    def test_center_integer(self):
        beta=startup_beta(self.a,self.b,self.aux);x=startup_center(self.a,self.aux,beta)
        self.assertTrue(torch.equal(x,x.round()))
        self.assertTrue(torch.equal(x[:,2:],wm.tensor(self.a)[:,2:]))
    def test_capacity_stop(self):
        with self.assertRaisesRegex(ValueError,'capacity'):
            startup_center(self.a,self.aux,[1e10,1e10])
    def test_zero_direction(self):
        a=np.array([[50,0,2,0,1,0]],float);aux=np.zeros((1,8));aux[0,0]=np.log1p(1)
        x=startup_center(a,aux,[1,1000]);self.assertEqual(x[0,1].item(),0)


if __name__=='__main__':unittest.main()
