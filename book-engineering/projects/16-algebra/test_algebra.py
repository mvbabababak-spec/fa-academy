import math
import unittest
from algebra import solve_linear, log_base

class AlgebraTests(unittest.TestCase):
    def test_equations(self):
        self.assertEqual(solve_linear(2, 3, 11), ('unique', 4))
        self.assertEqual(solve_linear(0, 3, 3), ('infinite', None))
        self.assertEqual(solve_linear(0, 3, 4), ('none', None))
        with self.assertRaises(ValueError):
            solve_linear(math.inf, 1, 2)

    def test_logarithms(self):
        self.assertTrue(math.isclose(log_base(32, 2), 5, rel_tol=1e-12))
        self.assertTrue(math.isclose(log_base(0.25, 2), -2, rel_tol=1e-12))
        for x, b in [(0, 2), (-1, 2), (2, 1), (2, 0), (math.inf, 2)]:
            with self.subTest(x=x, base=b), self.assertRaises(ValueError):
                log_base(x, b)

if __name__ == '__main__':
    unittest.main()
