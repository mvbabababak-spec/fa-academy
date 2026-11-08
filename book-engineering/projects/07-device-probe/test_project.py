import unittest
from types import SimpleNamespace as N
from device_probe import detect
class Tests(unittest.TestCase):
 def test_missing(self): self.assertEqual(detect(None)[0],'unavailable')
 def test_cpu(self):
  t=N(cuda=N(is_available=lambda:False),backends=N(mps=None));self.assertEqual(detect(t)[0],'cpu')
 def test_rocm_mock(self):
  t=N(cuda=N(is_available=lambda:True),version=N(hip='test'));self.assertEqual(detect(t),('cuda','ROCm/HIP build'))
 def test_bad_object(self):
  with self.assertRaises(AttributeError): detect(object())
