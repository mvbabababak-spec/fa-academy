import unittest
import numpy as np
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from unsupervised import kmeans_manual,pca_manual

class Tests(unittest.TestCase):
    def setUp(self): self.X=np.array([[0.,0.],[0.,2.],[10.,10.],[10.,12.]])
    def test_centers(self):
        centers,labels=kmeans_manual(self.X,[[0,0],[10,10]])
        np.testing.assert_allclose(centers,[[0,1],[10,11]])
        np.testing.assert_array_equal(labels,[0,0,1,1])
    def test_kmeans_matches_library(self):
        init=np.array([[0.,0.],[10.,10.]])
        c,l=kmeans_manual(self.X,init)
        model=KMeans(n_clusters=2,init=init,n_init=1,random_state=42).fit(self.X)
        np.testing.assert_allclose(c,model.cluster_centers_);np.testing.assert_array_equal(l,model.labels_)
    def test_pca_subspace_and_variance(self):
        m,c,v=pca_manual(self.X,1);model=PCA(n_components=1,svd_solver='full').fit(self.X)
        np.testing.assert_allclose(m,model.mean_);np.testing.assert_allclose(c.T@c,model.components_.T@model.components_,atol=1e-10)
        np.testing.assert_allclose(v[0],model.explained_variance_[0])
    def test_empty_cluster_kept(self):
        c,_=kmeans_manual(self.X,[[0,0],[1000,1000]])
        np.testing.assert_allclose(c[1],[1000,1000])
    def test_bad_data(self):
        with self.assertRaises(ValueError): kmeans_manual([],[[0,0]])
        with self.assertRaises(ValueError): pca_manual(self.X,3)
        with self.assertRaises(ValueError): pca_manual([[1,2]],1)
    def test_orthogonality(self):
        _,c,_=pca_manual(self.X,2);np.testing.assert_allclose(c@c.T,np.eye(2),atol=1e-12)
if __name__=='__main__':unittest.main()
