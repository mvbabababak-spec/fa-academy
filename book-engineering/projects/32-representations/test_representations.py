import unittest
import torch
from representations import data,embedding_demo,noise_step,train
class Tests(unittest.TestCase):
 def test_embedding(self):
  a=embedding_demo();self.assertEqual(tuple(a.shape),(3,2));torch.testing.assert_close(a[0],a[2]);torch.testing.assert_close(a[1],torch.tensor([3.,4.]))
 def test_splits(self):
  tr,v,te=data();self.assertEqual((len(tr),len(v),len(te)),(180,60,60));self.assertEqual(tuple(tr.shape[1:]),(4,))
 def test_autoencoder(self):
  r=train();self.assertLess(r['train_after'],r['train_before']);self.assertLess(r['test_mse'],r['test_mean_baseline_mse'])
 def test_reproducible(self):self.assertEqual(train(5),train(5))
 def test_noise(self):
  x=torch.tensor([1.,2.]);e=torch.tensor([0.,1.]);torch.testing.assert_close(noise_step(x,e,1),x);torch.testing.assert_close(noise_step(x,e,0),e)
 def test_errors(self):
  with self.assertRaises(ValueError):noise_step(torch.ones(2),torch.ones(1),.5)
  with self.assertRaises(ValueError):noise_step(torch.ones(2),torch.ones(2),1.1)
  with self.assertRaises(ValueError):train(0)
if __name__=='__main__':unittest.main()
