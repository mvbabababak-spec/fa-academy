import math
import unittest
from calculus import f, gradient, numerical_gradient, midpoint_integral


class CalculusTests(unittest.TestCase):
    def test_gradient(self):
        self.assertEqual(gradient(1, 2), (8, 7))
        for a, b in zip(gradient(1, 2), numerical_gradient(1, 2)):
            self.assertTrue(math.isclose(a, b, rel_tol=1e-8, abs_tol=1e-8))

    def test_other_point(self):
        self.assertEqual(gradient(0, 0), (0, 0))
        self.assertEqual(numerical_gradient(0, 0), (0, 0))

    def test_integral(self):
        self.assertAlmostEqual(midpoint_integral(lambda x: x*x, 0, 2, 1000), 8/3, delta=1e-6)
        self.assertAlmostEqual(midpoint_integral(lambda x: x, 2, 0, 100), -2)

    def test_invalid(self):
        for h in (0, -1, float('nan')):
            with self.assertRaises(ValueError): numerical_gradient(1, 2, h)
        for n in (0, -1, True, 2.5):
            with self.assertRaises(ValueError): midpoint_integral(f, 0, 1, n)


if __name__ == '__main__':
    unittest.main()
