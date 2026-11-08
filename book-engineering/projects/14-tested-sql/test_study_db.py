import unittest
from study_db import create_database, add_session, minutes_for


class StudyTests(unittest.TestCase):
    def setUp(self):
        self.db = create_database()

    def tearDown(self):
        self.db.close()

    def test_sum_and_missing(self):
        add_session(self.db, 'python', 30)
        add_session(self.db, 'python', 45)
        self.assertEqual(minutes_for(self.db, 'python'), 75)
        self.assertEqual(minutes_for(self.db, 'math'), 0)

    def test_invalid_values(self):
        for topic, minutes in [('', 1), ('x', -1), ('x', True), ('x', 1441)]:
            with self.subTest(topic=topic, minutes=minutes):
                with self.assertRaises(ValueError):
                    add_session(self.db, topic, minutes)

    def test_untrusted_value_is_literal(self):
        add_session(self.db, 'python', 30)
        self.assertEqual(minutes_for(self.db, "python' OR 1=1 --"), 0)
        self.assertEqual(minutes_for(self.db, 'python'), 30)


if __name__ == '__main__':
    unittest.main()
