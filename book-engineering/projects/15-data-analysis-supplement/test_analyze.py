import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from PIL import Image
from analyze import DATA, analyze, make_plot


class AnalysisTests(unittest.TestCase):
    def test_summary(self):
        clean, totals, missing = analyze(DATA)
        self.assertEqual((len(clean), missing), (3, 1))
        self.assertEqual(totals.to_dict(), {'math': 60.0, 'python': 75.0})
        self.assertEqual(clean['minutes'].mean(), 45.0)

    def test_invalid(self):
        for data in ('topic,minutes\nx,-1\n', 'topic,minutes\nx,inf\n',
                     'topic,minutes\nx,\n', 'topic,minutes\n,5\n'):
            with self.subTest(data=data), self.assertRaises(ValueError):
                analyze(data)

    def test_webp(self):
        _, totals, _ = analyze(DATA)
        with TemporaryDirectory() as folder:
            p = Path(folder) / 'chart.webp'
            make_plot(totals, p)
            with Image.open(p) as image:
                self.assertEqual(image.format, 'WEBP')
                image.verify()


if __name__ == '__main__':
    unittest.main()
