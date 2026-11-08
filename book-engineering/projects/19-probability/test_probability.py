import unittest
from probability import posterior_positive, coin_fraction


class ProbabilityTests(unittest.TestCase):
    def test_bayes(self):
        self.assertAlmostEqual(posterior_positive(.01, .9, .95), 90/585)
        self.assertEqual(posterior_positive(0, .9, .95), 0)
        self.assertEqual(posterior_positive(1, .9, .95), 1)

    def test_invalid_bayes(self):
        for args in [(-.1, .9, .95), (.1, 1.1, .95), (float('nan'), .9, .95), (0, 1, 1)]:
            with self.subTest(args=args), self.assertRaises(ValueError):
                posterior_positive(*args)

    def test_seed_and_range(self):
        self.assertEqual(coin_fraction(1000, 42), coin_fraction(1000, 42))
        self.assertTrue(0 <= coin_fraction(100, 4) <= 1)

    def test_invalid_n(self):
        for n in (0, -1, 2.5, True):
            with self.assertRaises(ValueError): coin_fraction(n)


if __name__ == '__main__':
    unittest.main()
