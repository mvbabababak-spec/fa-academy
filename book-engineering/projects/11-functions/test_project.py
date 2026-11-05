import unittest
from study_stats import total_minutes,average_minutes,count_topics
class Tests(unittest.TestCase):
 def test_total(self): self.assertEqual(total_minutes([30,60,90]),180)
 def test_empty_total(self): self.assertEqual(total_minutes([]),0)
 def test_invalid(self):
  with self.assertRaises(ValueError): average_minutes([])
  with self.assertRaises(ValueError): total_minutes([-1])
 def test_count(self): self.assertEqual(count_topics(['a','a','b']),{'a':2,'b':1})
