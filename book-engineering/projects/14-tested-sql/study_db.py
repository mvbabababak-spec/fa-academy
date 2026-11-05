"""Small in-memory SQLite study log; no external services or files."""
import sqlite3


def create_database():
    db = sqlite3.connect(':memory:')
    db.execute('CREATE TABLE sessions (topic TEXT NOT NULL, minutes INTEGER NOT NULL CHECK(minutes >= 0))')
    return db


def add_session(db, topic, minutes):
    if not isinstance(topic, str) or not topic.strip():
        raise ValueError('topic must be non-empty')
    if type(minutes) is not int or not 0 <= minutes <= 1440:
        raise ValueError('minutes must be an integer from 0 to 1440')
    with db:
        db.execute('INSERT INTO sessions (topic, minutes) VALUES (?, ?)', (topic.strip(), minutes))


def minutes_for(db, topic):
    row = db.execute('SELECT COALESCE(SUM(minutes), 0) FROM sessions WHERE topic = ?', (topic,)).fetchone()
    return row[0]


def main():
    db = create_database()
    try:
        add_session(db, 'python', 30)
        add_session(db, 'python', 45)
        add_session(db, 'math', 60)
        print('python_minutes=', minutes_for(db, 'python'))
        print('missing_minutes=', minutes_for(db, 'missing'))
    finally:
        db.close()


if __name__ == '__main__':
    main()
