import unittest,struct,subprocess,sys
class Tests(unittest.TestCase):
 def test_script(self):
  r=subprocess.run([sys.executable,'storage_demo.py'],capture_output=True,text=True,check=True);self.assertIn('file_bytes=16',r.stdout)
 def test_float_size(self): self.assertEqual(struct.calcsize('<f'),4)
 def test_invalid_unpack(self):
  with self.assertRaises(struct.error): struct.unpack('<4f',b'\x00')
