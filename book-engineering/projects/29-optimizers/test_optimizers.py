import unittest
import numpy as np
import torch
from optimizers import GRADS,manual,library

class Tests(unittest.TestCase):
    def test_all_steps_match_library(self):
        for name in ['sgd','adam','adamw']:np.testing.assert_allclose(manual(name,GRADS),library(name,GRADS),atol=1e-12)
    def test_first_sgd(self):self.assertAlmostEqual(manual('sgd',[.3])[0],.997)
    def test_decay_difference(self):self.assertNotEqual(manual('adam',GRADS)[-1],manual('adamw',GRADS)[-1])
    def test_bad_options(self):
        with self.assertRaises(ValueError):manual('wrong',[1])
        with self.assertRaises(ValueError):manual('adam',[1],lr=0)
        with self.assertRaises(ValueError):manual('adam',[1],b1=1)
    def test_dropout_eval(self):
        m=torch.nn.Dropout(.5);m.eval();x=torch.ones(20);torch.testing.assert_close(m(x),x)
    def test_dropout_train_reproducible(self):
        m=torch.nn.Dropout(.5);m.train();torch.manual_seed(42);a=m(torch.ones(20));torch.manual_seed(42);b=m(torch.ones(20));torch.testing.assert_close(a,b);self.assertTrue(torch.all((a==0)|(a==2)))
    def test_batchnorm_running(self):
        m=torch.nn.BatchNorm1d(2);m.train();m(torch.tensor([[1.,3.],[3.,5.]]));before=m.running_mean.clone();m.eval();m(torch.tensor([[4.,9.],[8.,5.]]));torch.testing.assert_close(m.running_mean,before)
if __name__=='__main__':unittest.main()
