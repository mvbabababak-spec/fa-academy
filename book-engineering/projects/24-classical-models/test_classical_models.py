import unittest
import numpy as np
from sklearn.neighbors import KNeighborsClassifier
from classical_models import knn_predict, split_data, build_search

class Tests(unittest.TestCase):
    def test_knn_matches_library_without_distance_tie(self):
        rows=[([0.0],0),([1.0],0),([3.0],1)]
        lib=KNeighborsClassifier(n_neighbors=3).fit([x for x,y in rows],[y for x,y in rows])
        self.assertEqual(knn_predict(rows,[0.4],3),int(lib.predict([[0.4]])[0]))
    def test_vote_tie_prefers_smaller_label(self):
        self.assertEqual(knn_predict([([0],1),([2],0)],[1],2),0)
    def test_bad_input(self):
        for rows,q,k in [([], [0],1),([([1],1)],[1],2),([([1,2],0)],[1],1)]:
            with self.assertRaises(ValueError): knn_predict(rows,q,k)
    def test_invalid_knn_label(self):
        for label in ['one', 1.5, np.int64(1)]:
            with self.assertRaises(ValueError): knn_predict([([1.],label)],[1.],1)
    def test_search_and_train_scaler(self):
        Xtr,Xte,ytr,yte=split_data();s=build_search().fit(Xtr,ytr)
        np.testing.assert_allclose(s.best_estimator_.named_steps['scale'].mean_,Xtr.mean(axis=0))
        self.assertEqual(len(s.predict(Xte)),len(yte))
        self.assertEqual(len(s.cv_results_['mean_test_score']),18)
    def test_split_shape(self):
        a,b,c,d=split_data(); self.assertEqual((len(a),len(b)),(300,100));self.assertEqual(a.shape[1],8)
    def test_cv_is_stratified(self): self.assertEqual(build_search().cv.n_splits,4)
if __name__=='__main__':unittest.main()
