import unittest
import numpy as np
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error
from regression import sigmoid, loss_and_gradient, fit_gradient, data

class Tests(unittest.TestCase):
    def test_gradient_finite_difference(self):
        X=np.array([[1.,-1.],[1.,0.5],[1.,2.]])
        for task,y in [('linear',np.array([1.,0.,2.])),('logistic',np.array([0.,1.,1.]))]:
            w=np.array([0.2,-0.4]); _,g=loss_and_gradient(X,y,w,task); eps=1e-6
            for j in range(2):
                d=np.zeros(2);d[j]=eps
                numeric=(loss_and_gradient(X,y,w+d,task)[0]-loss_and_gradient(X,y,w-d,task)[0])/(2*eps)
                self.assertAlmostEqual(g[j],numeric,places=6)
    def test_library_agreement(self):
        x,yr,yc,tr,te=data(); X=np.column_stack((np.ones(len(x)),x))
        wl=fit_gradient(X[tr],yr[tr],'linear'); lib=LinearRegression().fit(x[tr,None],yr[tr])
        np.testing.assert_allclose(X[te]@wl,lib.predict(x[te,None]),atol=1e-5)
        w=fit_gradient(X[tr],yc[tr],'logistic'); lib2=LogisticRegression(penalty=None,max_iter=2000,tol=1e-9).fit(x[tr,None],yc[tr])
        np.testing.assert_allclose(sigmoid(X[te]@w),lib2.predict_proba(x[te,None])[:,1],atol=1e-4)
    def test_known_metrics(self):
        self.assertEqual(mean_absolute_error([1,2],[2,4]),1.5)
        self.assertEqual(mean_squared_error([1,2],[2,4]),2.5)
    def test_splits(self):
        *_,tr,te=data(); self.assertFalse(set(tr)&set(te));self.assertEqual(len(tr)+len(te),240)
    def test_reject_bad_input(self):
        with self.assertRaises(ValueError): loss_and_gradient(np.ones((1,2)),np.array([2]),np.zeros(2),'logistic')
        with self.assertRaises(ValueError): fit_gradient(np.ones((2,1)),np.ones(2),'linear',steps=0)
        with self.assertRaises(ValueError): loss_and_gradient(np.empty((0,1)),np.array([]),np.zeros(1),'linear')
    def test_saturation_limits(self):
        values=sigmoid(np.array([-1000.,0.,1000.]))
        self.assertTrue(np.isfinite(values).all())
        self.assertGreater(values[0],0.0)
        self.assertAlmostEqual(values[1],0.5)
        self.assertEqual(values[2],1.0)
        X=np.ones((1,1)); _,g=loss_and_gradient(X,np.array([1.]),np.array([-1000.]),'logistic')
        self.assertAlmostEqual(g[0],-1.0)  # confidently wrong can have nonzero logit gradient
    def test_stable_sigmoid(self): self.assertTrue(np.isfinite(sigmoid(np.array([-1000.,1000.]))).all())
if __name__=='__main__': unittest.main()
