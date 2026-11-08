import unittest
from threshold_model import predict, errors, fit, train
class Tests(unittest.TestCase):
 def test_fit(self): self.assertEqual(fit(train), 3)
 def test_boundary(self): self.assertEqual(predict(3, 3), 1)
 def test_empty_fit_contract(self): self.assertEqual(fit([]), 0)  # tie-break; no empty-data validation
 def test_bad_row(self):
  with self.assertRaises((TypeError,ValueError)): errors([(1,)],3)
