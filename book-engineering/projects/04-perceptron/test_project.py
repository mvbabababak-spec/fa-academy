import unittest
from perceptron import predict,train
class Tests(unittest.TestCase):
 def test_threshold(self): self.assertEqual(predict(0,0,[0,0],0),1)
 def test_and(self):
  rows=[(0,0,0),(0,1,0),(1,0,0),(1,1,1)];w,b=train(rows);self.assertEqual([predict(a,c,w,b) for a,c,_ in rows],[0,0,0,1])
 def test_zero_epochs(self): self.assertEqual(train([],0),([0,0],0))
 def test_invalid_weights(self):
  with self.assertRaises(IndexError): predict(1,2,[],0)
