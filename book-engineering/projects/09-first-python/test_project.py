import subprocess,sys,unittest
class Tests(unittest.TestCase):
 def run_script(self,stdin=''):
  return subprocess.run([sys.executable,'hello.py'],input=stdin,text=True,capture_output=True,check=True)
 def test_output(self): self.assertEqual(self.run_script().stdout,'Hello, AI engineer!\n2 + 3 = 5\n')
 def test_empty_input(self): self.assertEqual(self.run_script('').returncode,0)
 def test_irrelevant_input(self): self.assertEqual(self.run_script('invalid\n').stdout,self.run_script('').stdout)  # no input contract
