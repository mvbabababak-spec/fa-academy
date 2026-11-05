"""One hidden tanh layer; stable binary loss, analytical and numerical gradients."""
import numpy as np

X=np.array([[0.2,-0.4],[0.7,0.3],[-0.5,0.8]],dtype=np.float64)
y=np.array([[1.],[0.],[1.]],dtype=np.float64)

def parameters():
    return {'W1':np.array([[.3,-.2],[.1,.4]]),'b1':np.array([.2,-.1]),
            'W2':np.array([[.5],[-.6]]),'b2':np.array([.15])}

def loss_grad(X,y,p):
    X=np.asarray(X,dtype=float);y=np.asarray(y,dtype=float)
    if X.ndim!=2 or y.shape!=(len(X),1) or len(X)==0 or not np.isin(y,[0,1]).all():raise ValueError('invalid X or y')
    h=np.tanh(X@p['W1']+p['b1']);z=h@p['W2']+p['b2']
    loss=float(np.mean(np.logaddexp(0,z)-y*z))
    prob=1/(1+np.exp(-np.clip(z,-500,500)))
    dz=(prob-y)/len(X);dW2=h.T@dz;db2=dz.sum(axis=0)
    dh=dz@p['W2'].T;dhidden=dh*(1-h*h)
    return loss,{'W1':X.T@dhidden,'b1':dhidden.sum(axis=0),'W2':dW2,'b2':db2}

def numerical(X,y,p,eps=1e-6):
    if not np.isscalar(eps) or not np.isfinite(eps) or not 0 < eps <= 1e-2:raise ValueError('eps must be finite and in (0, 1e-2]')
    gradients={}
    for name,param in p.items():
        g=np.zeros_like(param)
        for idx in np.ndindex(param.shape):
            plus={k:v.copy() for k,v in p.items()};minus={k:v.copy() for k,v in p.items()}
            plus[name][idx]+=eps;minus[name][idx]-=eps
            g[idx]=(loss_grad(X,y,plus)[0]-loss_grad(X,y,minus)[0])/(2*eps)
        gradients[name]=g
    return gradients

def main():
    p=parameters();loss,analytic=loss_grad(X,y,p);numeric=numerical(X,y,p)
    error=max(float(np.max(np.abs(analytic[k]-numeric[k]))) for k in p)
    updated={k:p[k]-0.1*analytic[k] for k in p}
    print(f'loss_before={loss:.9f} loss_after_one_step={loss_grad(X,y,updated)[0]:.9f}')
    print(f'max_abs_gradient_difference={error:.3e} checked_parameters={sum(v.size for v in p.values())}')
    print('data=synthetic device=CPU dtype=float64')
if __name__=='__main__':main()
