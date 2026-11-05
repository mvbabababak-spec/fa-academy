import subprocess,sys,unittest
from tempfile import TemporaryDirectory
from local_workflow import git
class Tests(unittest.TestCase):
 def test_workflow(self):
  r=subprocess.run([sys.executable,'local_workflow.py'],capture_output=True,text=True,check=True);self.assertIn('worktree_clean= True',r.stdout);self.assertIn('network=not used',r.stdout)
 def test_invalid_git_subcommand(self):
  with TemporaryDirectory() as d,self.assertRaises(subprocess.CalledProcessError): git(d,'not-a-git-command')
 def test_empty_repo_status(self):
  with TemporaryDirectory() as d:
   git(d,'init','-q');self.assertEqual(git(d,'status','--porcelain'),'')
