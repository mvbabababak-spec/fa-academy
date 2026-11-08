"""Small CPU CNN on sklearn digits, fixed train/validation/test split."""
import numpy as np
import torch
from torch import nn
from sklearn.datasets import load_digits
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix

def split():
    digits=load_digits();X=digits.images.astype('float32')[:,None,:,:]/16.0;y=digits.target.astype('int64')
    idx=np.arange(len(y));trainval,test=train_test_split(idx,test_size=.2,random_state=42,stratify=y)
    train,val=train_test_split(trainval,test_size=.25,random_state=43,stratify=y[trainval])
    return X,y,train,val,test

def model():
    return nn.Sequential(nn.Conv2d(1,8,3,padding=1),nn.ReLU(),nn.MaxPool2d(2),nn.Flatten(),nn.Linear(8*4*4,10))

def fit(epochs=8):
    if epochs<1:raise ValueError('epochs must be positive')
    torch.manual_seed(42);torch.set_num_threads(1)
    X,y,tr,val,te=split();X=torch.from_numpy(X);y=torch.from_numpy(y);net=model();opt=torch.optim.Adam(net.parameters(),lr=.01);criterion=nn.CrossEntropyLoss()
    generator=torch.Generator().manual_seed(42)
    loader=torch.utils.data.DataLoader(torch.utils.data.TensorDataset(X[tr],y[tr]),batch_size=64,shuffle=True,generator=generator)
    net.train()
    for _ in range(epochs):
        for xb,yb in loader:
            opt.zero_grad(); loss=criterion(net(xb),yb);loss.backward();opt.step()
    net.eval()
    with torch.no_grad():
        v=net(X[val]);z=net(X[te]);pred=z.argmax(1);acc=(pred==y[te]).float().mean().item();v_loss=criterion(v,y[val]).item()
    cm=confusion_matrix(y[te].numpy(),pred.numpy(),labels=list(range(10)))
    wrong=[(int(te[i]),int(y[te][i]),int(pred[i])) for i in range(len(te)) if pred[i]!=y[te][i]]
    return net,{'train_n':len(tr),'val_n':len(val),'test_n':len(te),'val_loss':v_loss,'test_accuracy':acc,'confusion':cm,'errors':wrong}

def main():
    _,r=fit();print('train_n',r['train_n'],'val_n',r['val_n'],'test_n',r['test_n']);print('val_loss',round(r['val_loss'],6),'test_accuracy',round(r['test_accuracy'],6));print('confusion_matrix\n',r['confusion']);print('errors count',len(r['errors']),'first five (dataset index, true, predicted):',r['errors'][:5])
if __name__=='__main__':main()
