import subprocess,sys,unittest
class Tests(unittest.TestCase):
 def run_input(self,text): return subprocess.run([sys.executable,'study_planner.py'],input=text,text=True,capture_output=True,check=True).stdout
 def test_normal(self): self.assertIn('Total: 180 minutes',self.run_input('30\n60\n90\n'))
 def test_boundary(self): self.assertIn('Total: 0 minutes',self.run_input('0\n0\n0\n'))
 def test_invalid_retry(self): self.assertIn('Enter a whole number',self.run_input('bad\n0\n0\n0\n'))
 def test_eof(self): self.assertIn('no result calculated',self.run_input(''))
