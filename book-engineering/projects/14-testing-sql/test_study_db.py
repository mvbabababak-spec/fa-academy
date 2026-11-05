import sqlite3
import unittest
from study_db import setup, add_session, total_for


class StudyDBTests(unittest.TestCase):
    def setUp(self):
        self.db = sqlite3.connect(':memory:')
        setup(self.db)

    def tearDown(self):
        self.db.close()

    def test_sum_and_empty(self):
        add_session(self.db, 'python', 30)
        add_session(self.db, 'python', 45)
        self.assertEqual(total_for(self.db, 'python'), 75)
        self.assertEqual(total_for(self.db, 'math'), 0)

    def test_boundaries_and_invalid(self):
        for value in (0, 1440):
            add_session(self.db, 'x', value)
        for value in (-1, 1441, True, 1.5):
            with self.subTest(value=value), self.assertRaises(ValueError):
                add_session(self.db, 'x', value)
        with self.assertRaises(ValueError):
            add_session(self.db, ' ', 10)

    def test_parameter_is_data(self):
        add_session(self.db, 'python', 30)
        self.assertEqual(total_for(self.db, "python' OR 1=1 --"), 0)
        self.assertEqual(total_for(self.db, 'python'), 30)


if __name__ == '__main__':
    unittest.main()
