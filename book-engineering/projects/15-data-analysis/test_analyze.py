import unittest
from analyze import DATA, analyze

class AnalysisTests(unittest.TestCase):
    def test_summary(self):
        missing, totals, mean = analyze(DATA)
        self.assertEqual(missing, 1)
        self.assertEqual(totals.to_dict(), {'math': 60.0, 'python': 75.0})
        self.assertEqual(mean, 45.0)

    def test_invalid_data(self):
        for data in ['topic,minutes\na,-1\n', 'topic,minutes\na,\n', 'wrong,minutes\na,2\n']:
            with self.subTest(data=data), self.assertRaises(ValueError):
                analyze(data)

if __name__ == '__main__':
    unittest.main()
