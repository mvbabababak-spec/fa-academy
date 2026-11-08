import unittest
from matrix_cpu import matmul
class Tests(unittest.TestCase):
 def test_product(self): self.assertEqual(matmul([[1,2],[3,4]],[[5,6],[7,8]]),[[19,22],[43,50]])
 def test_single(self): self.assertEqual(matmul([[0]],[[4]]),[[0]])
 def test_bad(self):
  for a,b in [([],[[1]]),([[1,2]],[[1]]),([[1],[1,2]],[[1]])]:
   with self.subTest(a=a),self.assertRaises(ValueError): matmul(a,b)
