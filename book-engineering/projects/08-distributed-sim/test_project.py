import unittest
from simulate import step,energy_kwh
class Tests(unittest.TestCase):
 def test_step(self):
  m,w=step(1,[.2,.4],.1);self.assertAlmostEqual(m,.3);self.assertAlmostEqual(w,.97)
 def test_zero(self): self.assertEqual(energy_kwh(0,5),0)
 def test_invalid(self):
  with self.assertRaises(ValueError): step(1,[],.1)
  with self.assertRaises(ValueError): energy_kwh(-1,1)
