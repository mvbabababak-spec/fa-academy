import unittest
import numpy as np
from forward import X,AND,XOR,train_perceptron,forward,library_forward

class Tests(unittest.TestCase):
    def test_and(self):
        w,b=train_perceptron(X,AND);np.testing.assert_array_equal((X@w+b>=0).astype(int),AND)
    def test_xor_hidden(self):
        h,p=forward(X);np.testing.assert_array_equal(h,[[0,0],[1,0],[1,0],[2,1]])
        np.testing.assert_array_equal((p>=.5).astype(int),XOR)
    def test_library_probabilities(self):np.testing.assert_allclose(forward(X)[1],library_forward(X),atol=1e-12)
    def test_one_row_shape(self):self.assertEqual(forward([[1,0]])[0].shape,(1,2))
    def test_reject_bad_inputs(self):
        with self.assertRaises(ValueError):forward([[1,2,3]])
        with self.assertRaises(ValueError):train_perceptron(X,[0,1,3,1])
        with self.assertRaises(ValueError):train_perceptron(X,AND,rate=0)
    def test_sigmoid_at_zero(self):
        _,p=forward([[0.5,0]]);self.assertAlmostEqual(p[0],0.5)
if __name__=='__main__':unittest.main()
