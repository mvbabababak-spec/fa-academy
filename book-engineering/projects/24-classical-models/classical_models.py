"""Small transparent KNN and leak-resistant model selection on synthetic data."""
import math
from collections import Counter
import numpy as np
from sklearn.datasets import make_classification
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score
from sklearn.model_selection import GridSearchCV, StratifiedKFold, train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier


def knn_predict(rows, query, k):
    """Rows are (numeric-vector, integer-label); deterministic tie handling."""
    if not rows or not 1 <= k <= len(rows) or not query:
        raise ValueError('invalid data or k')
    if any(len(x) != len(query) or not isinstance(y, int) for x,y in rows):
        raise ValueError('inconsistent dimension or non-integer label')
    neighbors = sorted(((math.dist(x,query), i, y) for i,(x,y) in enumerate(rows)))[:k]
    counts = Counter(y for _,_,y in neighbors)
    return min(counts, key=lambda label: (-counts[label],label))


def split_data():
    X,y=make_classification(n_samples=400,n_features=8,n_informative=4,n_redundant=2,
                            weights=[0.6,0.4],class_sep=1.0,random_state=42)
    return train_test_split(X,y,test_size=0.25,stratify=y,random_state=42)


def build_search():
    pipe=Pipeline([('scale',StandardScaler()),('select',SelectKBest(f_classif)),('model',DummyClassifier())])
    grid=[
        {'select__k':[4,'all'],'model':[DummyClassifier(strategy='most_frequent')]},
        {'select__k':[4,'all'],'model':[DecisionTreeClassifier(random_state=42)],'model__max_depth':[3,6]},
        {'select__k':[4,'all'],'model':[RandomForestClassifier(n_estimators=50,random_state=42,n_jobs=1)],'model__max_depth':[3,None]},
        {'select__k':[4,'all'],'model':[SVC()],'model__C':[0.5,2.0]},
        {'select__k':[4,'all'],'model':[KNeighborsClassifier()],'model__n_neighbors':[3,7]},
    ]
    cv=StratifiedKFold(n_splits=4,shuffle=True,random_state=42)
    return GridSearchCV(pipe,grid,scoring='f1',cv=cv,refit=True,n_jobs=1,error_score='raise')


def main():
    X_train,X_test,y_train,y_test=split_data()
    search=build_search().fit(X_train,y_train)
    # Test is read once, after selecting and refitting on training data.
    prediction=search.predict(X_test)
    print('train=%d test=%d cv_folds=4 seed=42 synthetic=true' % (len(y_train),len(y_test)))
    print('selected_model=',type(search.best_estimator_.named_steps['model']).__name__)
    print('best_params=',search.best_params_)
    print('best_cv_f1=%.6f' % search.best_score_)
    print('test_accuracy=%.6f test_f1=%.6f' % (accuracy_score(y_test,prediction),f1_score(y_test,prediction,zero_division=0)))
    print('test_confusion_matrix=',confusion_matrix(y_test,prediction,labels=[0,1]).tolist())
    print('manual_knn_example=',knn_predict([([0.0],0),([1.0],0),([3.0],1)],[0.4],3))

if __name__=='__main__': main()
