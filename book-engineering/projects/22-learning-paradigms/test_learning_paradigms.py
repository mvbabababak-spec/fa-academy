import unittest
from learning_paradigms import TRAIN, VALIDATION, TEST, check_splits, accuracy, fit_threshold

class LearningTests(unittest.TestCase):
    def test_split_ids(self): check_splits(TRAIN,VALIDATION,TEST)
    def test_duplicate_rejected(self):
        with self.assertRaises(ValueError): check_splits(TRAIN,TRAIN)
    def test_empty_rejected(self):
        with self.assertRaises(ValueError): check_splits([])
        with self.assertRaises(ValueError): accuracy([],lambda x:0)
        with self.assertRaises(ValueError): fit_threshold([])
    def test_threshold_training(self): self.assertEqual(fit_threshold(TRAIN),6)
    def test_accuracy(self): self.assertEqual(accuracy([('a',1,0),('b',2,1)],lambda x:0),0.5)
    def test_invalid_label(self):
        with self.assertRaises(ValueError): check_splits([('bad',1,2)])
if __name__ == '__main__': unittest.main()
