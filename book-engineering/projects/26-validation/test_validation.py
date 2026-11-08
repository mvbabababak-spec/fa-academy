import unittest
import numpy as np
from sklearn.preprocessing import PolynomialFeatures
from validation import ridge_objective,dataset,build_search

class Tests(unittest.TestCase):
    def test_objective(self):self.assertAlmostEqual(ridge_objective([[1],[2]],[1,2],[0],2),5.)
    def test_bad_objective(self):
        with self.assertRaises(ValueError):ridge_objective([[1]],[1],[1],-1)
        with self.assertRaises(ValueError):ridge_objective([[1,2]],[1],[1],1)
    def test_split(self):
        a,b,c,d=dataset();self.assertEqual((len(a),len(b)),(120,40))
    def test_cv(self):
        s=build_search();a,b,c,d=dataset();s.fit(a,c);self.assertEqual(len(s.cv_results_['mean_test_score']),9)
        poly=PolynomialFeatures(degree=s.best_params_['poly__degree'],include_bias=False).fit_transform(a)
        np.testing.assert_allclose(s.best_estimator_.named_steps['scale'].mean_,poly.mean(axis=0))
        self.assertEqual(len(s.predict(b)),40)
    def test_deterministic(self):
        a,b,c,d=dataset();s=build_search().fit(a,c);t=build_search().fit(a,c)
        self.assertEqual(s.best_params_,t.best_params_);np.testing.assert_allclose(s.predict(b),t.predict(b))
    def test_folds_do_not_overlap(self):
        a,_,_,_=dataset()
        for tr,va in build_search().cv.split(a):self.assertFalse(set(tr)&set(va))
if __name__=='__main__':unittest.main()
