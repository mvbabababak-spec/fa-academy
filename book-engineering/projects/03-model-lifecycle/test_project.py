import unittest
from lifecycle import predict,mse,train,TRAIN,TEST
class Tests(unittest.TestCase):
 def test_prediction(self): self.assertEqual(predict(2,2,1),5)
 def test_mse_zero(self): self.assertEqual(mse(TEST,2,1),0)
 def test_empty_mse(self):
  with self.assertRaises(ZeroDivisionError): mse([],1,1)
 def test_zero_steps(self): self.assertEqual(train(TRAIN,.1,0),(0.,0.))
