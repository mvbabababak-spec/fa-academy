import math
import unittest
from algebra import solve_linear, log_base


class AlgebraTests(unittest.TestCase):
    def test_unique_solution(self):
        kind, x = solve_linear(2, 3, 11)
        self.assertEqual(kind, 'one')
        self.assertTrue(math.isclose(x, 4))
        self.assertTrue(math.isclose(2*x+3, 11))

    def test_zero_coefficient(self):
        self.assertEqual(solve_linear(0, 3, 3), ('all', None))
        self.assertEqual(solve_linear(0, 3, 4), ('none', None))

    def test_logs(self):
        self.assertTrue(math.isclose(log_base(8, 2), 3))
        self.assertTrue(math.isclose(log_base(0.25, 2), -2))
        self.assertTrue(math.isclose(log_base(8, 0.5), -3))
        for x, base in [(0, 2), (-1, 2), (2, 1), (2, -1), (float('inf'), 2)]:
            with self.subTest(x=x, base=base), self.assertRaises(ValueError):
                log_base(x, base)

    def test_nonfinite_equation(self):
        with self.assertRaises(ValueError):
            solve_linear(float('nan'), 0, 1)


if __name__ == '__main__':
    unittest.main()
