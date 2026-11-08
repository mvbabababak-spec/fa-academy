import unittest
from rule_baseline import classify
class Tests(unittest.TestCase):
 def test_flag(self): self.assertTrue(classify('رمز عبور'))
 def test_empty(self): self.assertFalse(classify('  '))
 def test_invalid(self):
  with self.assertRaises(AttributeError): classify(None)
