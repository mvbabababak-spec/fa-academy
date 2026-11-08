"""Synthetic polynomial regression: CV selection without preprocessing leakage."""
import numpy as np
from sklearn.dummy import DummyRegressor
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.model_selection import GridSearchCV, KFold, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import PolynomialFeatures, StandardScaler


def ridge_objective(X,y,w,alpha):
    X=np.asarray(X,dtype=float);y=np.asarray(y,dtype=float);w=np.asarray(w,dtype=float)
    if X.ndim!=2 or X.shape!=(len(y),len(w)) or len(y)==0 or alpha<0: raise ValueError('invalid inputs')
    return float(np.sum((X@w-y)**2)+alpha*np.sum(w*w))


def dataset():
    rng=np.random.default_rng(42);X=rng.uniform(-2,2,size=(160,1));y=np.sin(2*X[:,0])+rng.normal(0,0.15,160)
    return train_test_split(X,y,test_size=0.25,random_state=42)


def build_search():
    pipe=Pipeline([('poly',PolynomialFeatures(include_bias=False)),('scale',StandardScaler()),('ridge',Ridge())])
    return GridSearchCV(pipe,{'poly__degree':[1,3,9],'ridge__alpha':[0.01,1.0,100.0]},
                        scoring='neg_mean_squared_error',cv=KFold(n_splits=5,shuffle=True,random_state=42),
                        refit=True,error_score='raise',n_jobs=1)


def main():
    Xtr,Xte,ytr,yte=dataset();baseline=DummyRegressor(strategy='mean').fit(Xtr,ytr)
    search=build_search().fit(Xtr,ytr);pred=search.predict(Xte)
    print(f'train={len(Xtr)} test={len(Xte)} synthetic=true seed=42')
    print('best_params=',search.best_params_)
    print(f'best_cv_mse={-search.best_score_:.6f}')
    print(f'test_mse={mean_squared_error(yte,pred):.6f} test_mae={mean_absolute_error(yte,pred):.6f}')
    print(f'baseline_test_mse={mean_squared_error(yte,baseline.predict(Xte)):.6f}')
    for name,mask in [('negative_x',Xte[:,0]<0),('nonnegative_x',Xte[:,0]>=0)]:
        print(f'{name}: n={mask.sum()} mae={mean_absolute_error(yte[mask],pred[mask]):.6f}')

if __name__=='__main__':main()
