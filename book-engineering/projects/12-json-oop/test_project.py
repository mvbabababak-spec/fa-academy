import unittest,json
from session import StudySession
class Tests(unittest.TestCase):
 def test_roundtrip(self):
  a=StudySession(' فارسی ',30);b=json.loads(json.dumps(a.as_dict(),ensure_ascii=False));self.assertEqual(StudySession(**b).as_dict(),a.as_dict())
 def test_boundary(self): self.assertEqual(StudySession('x',1440).minutes,1440)
 def test_invalid(self):
  for topic,n in [('',1),('x',-1),('x',True),('x',1441)]:
   with self.subTest(n=n),self.assertRaises(ValueError): StudySession(topic,n)
