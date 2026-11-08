"""Toy autoencoder; embedding lookup and one forward noising step (not a diffusion model)."""
import numpy as np
import torch
from torch import nn

def data():
    rng=np.random.default_rng(42);latent=rng.normal(size=(300,2)).astype('float32');mix=np.array([[1,.4,-.3,.5],[-.2,.8,.7,-.4]],dtype='float32');X=latent@mix+.03*rng.normal(size=(300,4)).astype('float32')
    return torch.from_numpy(X[:180]),torch.from_numpy(X[180:240]),torch.from_numpy(X[240:])

def embedding_demo():
    embedding=nn.Embedding(4,2)
    with torch.no_grad():embedding.weight.copy_(torch.tensor([[0.,0.],[1.,2.],[3.,4.],[-1.,1.]]))
    return embedding(torch.tensor([1,2,1]))

def noise_step(x,epsilon,alpha_bar):
    if x.shape!=epsilon.shape or not 0<=alpha_bar<=1:raise ValueError('invalid noise parameters')
    return alpha_bar**.5*x+(1-alpha_bar)**.5*epsilon

def train(steps=500):
    if steps<1:raise ValueError('steps must be positive')
    torch.manual_seed(7);torch.set_num_threads(1);tr,val,test=data()
    encoder=nn.Sequential(nn.Linear(4,2));decoder=nn.Sequential(nn.Linear(2,4));opt=torch.optim.Adam(list(encoder.parameters())+list(decoder.parameters()),lr=.02);loss=nn.MSELoss()
    with torch.no_grad():before=loss(decoder(encoder(tr)),tr).item()
    for _ in range(steps):
        opt.zero_grad();l=loss(decoder(encoder(tr)),tr);l.backward();opt.step()
    with torch.no_grad():
        return {'train_before':before,'train_after':loss(decoder(encoder(tr)),tr).item(),'val_mse':loss(decoder(encoder(val)),val).item(),'test_mse':loss(decoder(encoder(test)),test).item(),'test_mean_baseline_mse':loss(tr.mean(0).expand_as(test),test).item()}

def main():
    result=train()
    for key,value in result.items():print(f'{key}={value:.9f}')
    print('embedding=',embedding_demo().detach().numpy().tolist())
    print('noise_example=',noise_step(torch.tensor([1.,2.]),torch.tensor([0.,1.]),.81).tolist())
if __name__=='__main__':main()
