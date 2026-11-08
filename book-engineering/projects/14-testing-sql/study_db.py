"""A small in-memory study tracker; no network or persistent files."""
import sqlite3


def setup(connection):
    connection.execute('CREATE TABLE sessions (topic TEXT NOT NULL, minutes INTEGER NOT NULL)')


def add_session(connection, topic, minutes):
    if not isinstance(topic, str) or not topic.strip():
        raise ValueError('topic must be a non-empty string')
    if type(minutes) is not int or not 0 <= minutes <= 1440:
        raise ValueError('minutes must be an integer between 0 and 1440')
    connection.execute('INSERT INTO sessions (topic, minutes) VALUES (?, ?)',
                       (topic.strip(), minutes))
    connection.commit()


def total_for(connection, topic):
    row = connection.execute('SELECT COALESCE(SUM(minutes), 0) FROM sessions WHERE topic = ?',
                             (topic,)).fetchone()
    return row[0]


def main():
    connection = sqlite3.connect(':memory:')
    try:
        setup(connection)
        add_session(connection, 'python', 30)
        add_session(connection, 'python', 45)
        add_session(connection, 'math', 20)
        print('python_minutes=', total_for(connection, 'python'))
        print('unknown_minutes=', total_for(connection, 'unknown'))
    finally:
        connection.close()


if __name__ == '__main__':
    main()
