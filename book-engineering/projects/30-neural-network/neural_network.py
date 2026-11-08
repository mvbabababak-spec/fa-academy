"""Train matching NumPy and PyTorch MLPs on synthetic independent splits."""
from pathlib import Path
from tempfile import TemporaryDirectory
import numpy as np
import torch
from torch import nn


def data():
    rng=np.random.default_rng(42); X=rng.uniform(-1,1,(300,2));y=(X[:,0]+0.7*X[:,1]>0).astype(float)[:,None]
    return (X[:180],y[:180]),(X[180:240],y[180:240]),(X[240:],y[240:])

def init():
    rng=np.random.default_rng(7)
    return {'W1':rng.normal(0,.3,(2,4)),'b1':np.zeros(4),'W2':rng.normal(0,.3,(4,1)),'b2':np.zeros(1)}

def logits(X,p):return np.tanh(X@p['W1']+p['b1'])@p['W2']+p['b2']

def loss_grad(X,y,p):
    if X.ndim!=2 or X.shape[1]!=2 or y.shape!=(len(X),1) or len(X)==0:raise ValueError('invalid shapes')
    h=np.tanh(X@p['W1']+p['b1']);z=h@p['W2']+p['b2'];loss=float(np.mean(np.logaddexp(0,z)-y*z))
    dz=(1/(1+np.exp(-np.clip(z,-500,500)))-y)/len(X); da=(dz@p['W2'].T)*(1-h*h)
    return loss,{'W1':X.T@da,'b1':da.sum(0),'W2':h.T@dz,'b2':dz.sum(0)}

def numerical_gradient(X,y,p,eps=1e-6):
    if eps<=0:raise ValueError('positive epsilon required')
    result={}
    for k,v in p.items():
        g=np.zeros_like(v)
        for i in np.ndindex(v.shape):
            a={n:x.copy() for n,x in p.items()};b={n:x.copy() for n,x in p.items()}
            a[k][i]+=eps;b[k][i]-=eps
            g[i]=(loss_grad(X,y,a)[0]-loss_grad(X,y,b)[0])/(2*eps)
        result[k]=g
    return result

def make_torch(p):
    model=nn.Sequential(nn.Linear(2,4),nn.Tanh(),nn.Linear(4,1)).double()
    with torch.no_grad():
        model[0].weight.copy_(torch.from_numpy(p['W1'].T.copy()));model[0].bias.copy_(torch.from_numpy(p['b1'].copy()))
        model[2].weight.copy_(torch.from_numpy(p['W2'].T.copy()));model[2].bias.copy_(torch.from_numpy(p['b2'].copy()))
    return model

def train_pair(X,y,steps=300,rate=.3):
    if steps<1 or rate<=0:raise ValueError('invalid training parameters')
    p=init();model=make_torch(p);X_t=torch.from_numpy(X);y_t=torch.from_numpy(y)
    optimizer=torch.optim.SGD(model.parameters(),lr=rate);criterion=nn.BCEWithLogitsLoss();first=loss_grad(X,y,p)[0]
    for _ in range(steps):
        _,g=loss_grad(X,y,p);p={k:p[k]-rate*g[k] for k in p}
        optimizer.zero_grad();loss=criterion(model(X_t),y_t);loss.backward();optimizer.step()
    return p,model,first,loss_grad(X,y,p)[0]

def reload_weights(model,path):
    torch.save(model.state_dict(),path);reloaded=make_torch(init())
    reloaded.load_state_dict(torch.load(path,map_location='cpu',weights_only=True));reloaded.eval();return reloaded

def main():
    (X,y),(Xv,yv),(Xt,yt)=data();p,model,first,last=train_pair(X,y);model.eval()
    val_loss=loss_grad(Xv,yv,p)[0];test_logits=logits(Xt,p)
    with torch.no_grad():torch_logits=model(torch.from_numpy(Xt)).numpy()
    accuracy=np.mean((test_logits>=0)==yt)
    with TemporaryDirectory() as tmp:
        restored=reload_weights(model,Path(tmp)/'weights.pt')
        with torch.no_grad():reloaded=restored(torch.from_numpy(Xt)).numpy()
    print(f'train_loss_before={first:.9f} train_loss_after={last:.9f} val_loss={val_loss:.9f}')
    print(f'test_accuracy={accuracy:.6f} samples train=180 val=60 test=60')
    print(f'max_numpy_torch_logit_diff={np.max(np.abs(test_logits-torch_logits)):.3e}')
    print(f'max_reload_logit_diff={np.max(np.abs(reloaded-torch_logits)):.3e}')
    print('fixed_protocol=true synthetic=true seed_data=42 seed_weights=7 device=CPU')
if __name__=='__main__':main()
