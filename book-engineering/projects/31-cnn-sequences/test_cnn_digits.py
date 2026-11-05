import unittest
import numpy as np
import torch
from cnn_digits import split,model,fit
class Tests(unittest.TestCase):
 def test_splits(self):
  x,y,tr,v,te=split();self.assertEqual(x.shape,(1797,1,8,8));self.assertEqual(len(set(tr)&set(v)),0);self.assertEqual(len(set(tr)&set(te)),0);self.assertEqual(len(set(v)&set(te)),0);self.assertEqual(len(tr)+len(v)+len(te),len(y))
 def test_shape_and_conv(self):
  x=torch.ones((2,1,8,8));self.assertEqual(tuple(model()(x).shape),(2,10));self.assertEqual(tuple(model()[0](x).shape),(2,8,8,8))
 def test_training_and_confusion(self):
  _,r=fit();self.assertGreater(r['test_accuracy'],.8);self.assertEqual(r['confusion'].sum(),r['test_n']);self.assertEqual(len(r['errors']),int(r['test_n']-np.trace(r['confusion'])))
 def test_reproducibility(self):
  _,a=fit(1);_,b=fit(1);np.testing.assert_array_equal(a['confusion'],b['confusion'])
 def test_invalid_epoch(self):
  with self.assertRaises(ValueError):fit(0)
 def test_sequence_shapes(self):
  x=torch.randn(3,5,2)
  for layer in (torch.nn.RNN(2,4,batch_first=True),torch.nn.LSTM(2,4,batch_first=True),torch.nn.GRU(2,4,batch_first=True)):
   out,state=layer(x);self.assertEqual(tuple(out.shape),(3,5,4));h=state[0] if isinstance(state,tuple) else state;self.assertEqual(tuple(h.shape),(1,3,4))
if __name__=='__main__':unittest.main()
