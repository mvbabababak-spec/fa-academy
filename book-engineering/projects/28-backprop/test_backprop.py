import unittest
import numpy as np
import torch
from backprop import X,y,parameters,loss_grad,numerical

class Tests(unittest.TestCase):
    def test_numerical_every_parameter(self):
        p=parameters();_,g=loss_grad(X,y,p);n=numerical(X,y,p)
        for k in p:np.testing.assert_allclose(g[k],n[k],atol=1e-8,rtol=1e-6)
    def test_torch_autograd(self):
        p=parameters();_,g=loss_grad(X,y,p)
        q={k:torch.tensor(v,requires_grad=True,dtype=torch.float64) for k,v in p.items()}
        xx=torch.tensor(X);yy=torch.tensor(y);h=torch.tanh(xx@q['W1']+q['b1']);z=h@q['W2']+q['b2']
        loss=torch.nn.functional.binary_cross_entropy_with_logits(z,yy);loss.backward()
        for k in p:np.testing.assert_allclose(g[k],q[k].grad.detach().numpy(),atol=1e-12)
    def test_descent(self):
        p=parameters();loss,g=loss_grad(X,y,p);new={k:p[k]-0.1*g[k] for k in p}
        self.assertLess(loss_grad(X,y,new)[0],loss)
    def test_invalid_data(self):
        with self.assertRaises(ValueError):loss_grad(X,np.array([1,0,1]),parameters())
        with self.assertRaises(ValueError):loss_grad(X,np.array([[1],[3],[0]]),parameters())
    def test_no_mutation(self):
        p=parameters();before={k:v.copy() for k,v in p.items()};numerical(X,y,p)
        for k in p:np.testing.assert_array_equal(p[k],before[k])
    def test_bad_epsilon(self):
        with self.assertRaises(ValueError):numerical(X,y,parameters(),0)
if __name__=='__main__':unittest.main()
