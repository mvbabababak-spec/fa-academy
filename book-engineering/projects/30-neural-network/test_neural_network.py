import unittest,tempfile
from pathlib import Path
import numpy as np
import torch
from neural_network import data,init,loss_grad,numerical_gradient,train_pair,logits,reload_weights

class Tests(unittest.TestCase):
    def test_gradient_all_parameters(self):
        (X,y),_,_=data();p=init();_,g=loss_grad(X[:4],y[:4],p);ng=numerical_gradient(X[:4],y[:4],p)
        for k in p:np.testing.assert_allclose(g[k],ng[k],atol=1e-8)
    def test_train_and_framework_agreement(self):
        (X,y),_,(Xt,yt)=data();p,model,first,last=train_pair(X,y,steps=80)
        self.assertLess(last,first)
        with torch.no_grad():np.testing.assert_allclose(logits(Xt,p),model(torch.from_numpy(Xt)).numpy(),atol=1e-12)
    def test_save_reload(self):
        (X,y),_,(Xt,yt)=data();p,model,_,_=train_pair(X,y,steps=5)
        with tempfile.TemporaryDirectory() as d:
            model2=reload_weights(model,Path(d)/'w.pt')
            with torch.no_grad():torch.testing.assert_close(model(torch.from_numpy(Xt)),model2(torch.from_numpy(Xt)))
    def test_splits(self):
        tr,val,te=data();self.assertEqual([len(tr[0]),len(val[0]),len(te[0])],[180,60,60])
        self.assertEqual(len({tuple(x) for xx,_ in (tr,val,te) for x in xx}),300)
    def test_bad_inputs(self):
        with self.assertRaises(ValueError):loss_grad(np.ones((2,3)),np.ones((2,1)),init())
        (X,y),_,_=data()
        with self.assertRaises(ValueError):train_pair(X,y,steps=0)
        with self.assertRaises(ValueError):numerical_gradient(X[:2],y[:2],init(),0)
    def test_reproducible(self):
        (X,y),_,_=data();a,_,_,_=train_pair(X,y,steps=5);b,_,_,_=train_pair(X,y,steps=5)
        for k in a:np.testing.assert_array_equal(a[k],b[k])
if __name__=='__main__':unittest.main()
