"""Scalar SGD, Adam and AdamW compared with PyTorch on supplied gradients."""
import math
import torch

GRADS=[0.3,-0.2,0.5]

def manual(method,gradients,lr=0.01,decay=0.1,b1=0.9,b2=0.999,eps=1e-8):
    if method not in ('sgd','adam','adamw') or lr<=0 or decay<0 or not (0<=b1<1 and 0<=b2<1) or eps<=0:
        raise ValueError('invalid optimizer options')
    theta=1.;m=0.;v=0.;out=[]
    for t,g in enumerate(gradients,1):
        if method=='sgd':theta-=lr*g
        else:
            if method=='adam':g=g+decay*theta
            m=b1*m+(1-b1)*g;v=b2*v+(1-b2)*g*g
            mh=m/(1-b1**t);vh=v/(1-b2**t)
            if method=='adamw':theta*=1-lr*decay
            theta-=lr*mh/(math.sqrt(vh)+eps)
        out.append(theta)
    return out

def library(method,gradients,lr=.01,decay=.1):
    if method not in ('sgd','adam','adamw'):raise ValueError('unknown optimizer')
    theta=torch.nn.Parameter(torch.tensor(1.,dtype=torch.float64))
    if method=='sgd': opt=torch.optim.SGD([theta],lr=lr,weight_decay=0)
    elif method=='adam':opt=torch.optim.Adam([theta],lr=lr,weight_decay=decay,foreach=False)
    else:opt=torch.optim.AdamW([theta],lr=lr,weight_decay=decay,foreach=False)
    out=[]
    for g in gradients:
        opt.zero_grad();theta.grad=torch.tensor(g,dtype=torch.float64);opt.step();out.append(theta.item())
    return out

def main():
    for method in ('sgd','adam','adamw'):
        a=manual(method,GRADS);b=library(method,GRADS)
        print(f'{method}: final_manual={a[-1]:.9f} final_torch={b[-1]:.9f} max_diff={max(abs(x-y) for x,y in zip(a,b)):.3e}')
    dropout=torch.nn.Dropout(p=.5);v=torch.ones(8)
    torch.manual_seed(42);dropout.train();print('dropout_train=',dropout(v).tolist())
    dropout.eval();print('dropout_eval=',dropout(v).tolist())
    print('note=predefined gradients, not a model training benchmark')
if __name__=='__main__':main()
