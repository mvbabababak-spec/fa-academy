import math
import unittest
from gradient_descent import loss, gradient, optimize


class OptimizationTests(unittest.TestCase):
    def test_gradient(self):
        self.assertEqual(gradient(0), -6)
        self.assertEqual(gradient(3), 0)
        h = 1e-5
        self.assertTrue(math.isclose((loss(1+h)-loss(1-h))/(2*h), gradient(1), rel_tol=1e-9))

    def test_descent_and_divergence(self):
        good = optimize(0, .1, 20)
        bad = optimize(0, 1.1, 20)
        self.assertLess(loss(good[-1]), loss(good[0]))
        self.assertGreater(loss(bad[-1]), loss(bad[0]))
        self.assertEqual(len(good), 21)

    def test_boundary_rates(self):
        self.assertEqual(optimize(0, 1, 2), [0.0, 6.0, 0.0])
        self.assertEqual(optimize(2, .1, 0), [2.0])

    def test_invalid(self):
        for args in [(0, 0, 1), (0, -1, 1), (0, float('nan'), 1), (float('inf'), .1, 1), (0, .1, True)]:
            with self.subTest(args=args), self.assertRaises(ValueError): optimize(*args)


if __name__ == '__main__':
    unittest.main()
