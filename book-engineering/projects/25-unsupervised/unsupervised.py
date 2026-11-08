"""Synthetic K-means and PCA: handwritten foundations and sklearn pipeline."""
import numpy as np
from sklearn.cluster import KMeans
from sklearn.datasets import make_blobs
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler


def kmeans_manual(X, initial, max_iter=100):
    X=np.asarray(X,dtype=float); centers=np.asarray(initial,dtype=float).copy()
    if X.ndim!=2 or centers.ndim!=2 or not len(X) or not len(centers) or X.shape[1]!=centers.shape[1] or max_iter<1:
        raise ValueError('invalid points, centers or iteration count')
    for _ in range(max_iter):
        labels=((X[:,None,:]-centers[None,:,:])**2).sum(axis=2).argmin(axis=1)
        updated=np.array([X[labels==i].mean(axis=0) if np.any(labels==i) else centers[i] for i in range(len(centers))])
        if np.allclose(updated,centers):
            centers=updated;break
        centers=updated
    labels=((X[:,None,:]-centers[None,:,:])**2).sum(axis=2).argmin(axis=1)
    return centers,labels


def pca_manual(X, n_components):
    X=np.asarray(X,dtype=float)
    if X.ndim!=2 or X.shape[0]<2 or not 1<=n_components<=min(X.shape):
        raise ValueError('invalid data or component count')
    mean=X.mean(axis=0); _,s,vt=np.linalg.svd(X-mean,full_matrices=False)
    return mean,vt[:n_components],s*s/(len(X)-1)


def experiment():
    X,_=make_blobs(n_samples=240,centers=[[-3,-2],[3,2]],cluster_std=0.8,random_state=42)
    Xtr,Xte=train_test_split(X,test_size=0.25,random_state=42)
    scaler=StandardScaler().fit(Xtr);tr=scaler.transform(Xtr);te=scaler.transform(Xte)
    pca=PCA(n_components=2,svd_solver='full').fit(tr)
    model=KMeans(n_clusters=2,random_state=42,n_init=10).fit(tr)
    labels=model.predict(te)
    print(f'train={len(tr)} test={len(te)} seed=42 synthetic=true')
    print('explained_variance_ratio=',np.round(pca.explained_variance_ratio_,6).tolist())
    print(f'train_inertia={model.inertia_:.6f} test_silhouette={silhouette_score(te,labels):.6f}')
    print('test_cluster_sizes=',np.bincount(labels,minlength=2).tolist())

if __name__=='__main__':experiment()
