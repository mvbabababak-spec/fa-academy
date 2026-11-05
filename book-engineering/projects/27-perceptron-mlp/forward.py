"""Manual perceptron training and fixed-weight XOR MLP forward pass."""
import numpy as np
from sklearn.linear_model import Perceptron
from sklearn.neural_network import MLPClassifier

X=np.array([[0.,0.],[0.,1.],[1.,0.],[1.,1.]])
AND=np.array([0,0,0,1]);XOR=np.array([0,1,1,0])
W1=np.array([[1.,1.],[1.,1.]]);B1=np.array([0.,-1.])
W2=np.array([[1.],[-2.]]);B2=np.array([-0.5])


def train_perceptron(X,y,rate=1.,epochs=100):
    X=np.asarray(X,dtype=float);y=np.asarray(y)
    if X.ndim!=2 or len(X)==0 or y.shape!=(len(X),) or not np.isin(y,[0,1]).all() or rate<=0 or epochs<1:
        raise ValueError('invalid inputs')
    w=np.zeros(X.shape[1]);b=0.
    for _ in range(epochs):
        errors=0
        for x,target in zip(X,y):
            prediction=int(x@w+b>=0);delta=rate*(target-prediction)
            if delta: w+=delta*x;b+=delta;errors+=1
        if not errors: break
    return w,b


def forward(X):
    X=np.asarray(X,dtype=float)
    if X.ndim!=2 or X.shape[1]!=2:raise ValueError('expected shape (n,2)')
    hidden=np.maximum(0,X@W1+B1);z=hidden@W2+B2
    p=1/(1+np.exp(-np.clip(z,-500,500)))
    return hidden,p.ravel()


def library_forward(X):
    # fit initializes sklearn's documented learned attributes; replace them with
    # fixed educational weights. This is not a claim of training convergence.
    model=MLPClassifier(hidden_layer_sizes=(2,),activation='relu',solver='lbfgs',max_iter=1000,random_state=42)
    model.fit(globals()['X'],XOR)
    model.coefs_=[W1.copy(),W2.copy()];model.intercepts_=[B1.copy(),B2.copy()]
    return model.predict_proba(X)[:,1]


def main():
    w,b=train_perceptron(X,AND)
    lib=Perceptron(random_state=42,max_iter=1000,tol=1e-3).fit(X,AND)
    hidden,p=forward(X)
    print('AND_manual=',(X@w+b>=0).astype(int).tolist(),'weight=',w.tolist(),'bias=',b)
    print('AND_library=',lib.predict(X).tolist())
    print('XOR_hidden=',hidden.tolist())
    print('XOR_manual_probabilities=',np.round(p,6).tolist())
    print('XOR_library_probabilities=',np.round(library_forward(X),6).tolist())
    print('XOR_decisions=',(p>=0.5).astype(int).tolist())
    print('all_examples=truth_table_only, no independent generalization test')

if __name__=='__main__':main()
