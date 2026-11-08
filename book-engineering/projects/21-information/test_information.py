import math
import unittest
from information import entropy, cross_entropy, kl_divergence


class InformationTests(unittest.TestCase):
    def test_entropy(self):
        self.assertAlmostEqual(entropy([.5, .5]), 1)
        self.assertEqual(entropy([1, 0]), 0)

    def test_identity_and_direction(self):
        p, q = [.5, .5], [.9, .1]
        self.assertAlmostEqual(cross_entropy(p, q), entropy(p) + kl_divergence(p, q))
        self.assertGreater(kl_divergence(p, q), 0)
        self.assertNotAlmostEqual(kl_divergence(p, q), kl_divergence(q, p))
        self.assertAlmostEqual(kl_divergence(p, p), 0)

    def test_zeros(self):
        self.assertTrue(math.isinf(cross_entropy([1, 0], [0, 1])))
        self.assertTrue(math.isinf(kl_divergence([1, 0], [0, 1])))
        self.assertEqual(cross_entropy([1, 0], [1, 0]), 0)

    def test_invalid(self):
        for p in ([], [-.1, 1.1], [.3, .3], [float('nan'), 1]):
            with self.subTest(p=p), self.assertRaises(ValueError): entropy(p)
        with self.assertRaises(ValueError): cross_entropy([1], [.5, .5])


if __name__ == '__main__':
    unittest.main()
