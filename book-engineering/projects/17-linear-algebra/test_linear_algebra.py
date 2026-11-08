import unittest
import numpy as np
from linear_algebra import matmul


class LinearAlgebraTests(unittest.TestCase):
    def test_rectangular_product(self):
        self.assertEqual(matmul([[1, 2, 3], [4, 5, 6]], [[1, 0], [0, 1], [1, 1]]), [[4, 5], [10, 11]])

    def test_against_numpy(self):
        a, b = [[1, -1], [2, 3]], [[2], [4]]
        self.assertTrue(np.array_equal(matmul(a, b), np.array(a) @ np.array(b)))

    def test_invalid_shapes(self):
        for a, b in [([], [[1]]), ([[1, 2]], [[1]]), ([[1], [2, 3]], [[1]])]:
            with self.subTest(a=a, b=b), self.assertRaises(ValueError):
                matmul(a, b)

    def test_eigenpairs(self):
        a = np.array([[2., 0.], [0., 3.]])
        w, v = np.linalg.eig(a)
        self.assertTrue(np.allclose(a @ v, v * w))
        self.assertTrue(np.allclose(sorted(w), [2, 3]))


if __name__ == '__main__':
    unittest.main()
