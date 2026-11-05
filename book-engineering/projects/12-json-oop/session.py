"""Validate a study session and round-trip it through a temporary JSON file."""
import json
from pathlib import Path
from tempfile import TemporaryDirectory


class StudySession:
    def __init__(self, topic, minutes):
        if not isinstance(topic, str) or not topic.strip():
            raise ValueError('topic must be a non-empty string')
        if type(minutes) is not int or not 0 <= minutes <= 1440:
            raise ValueError('minutes must be an integer from 0 to 1440')
        self.topic = topic.strip()
        self.minutes = minutes

    def as_dict(self):
        return {'topic': self.topic, 'minutes': self.minutes}


def main():
    session = StudySession('python', 45)
    with TemporaryDirectory() as folder:
        path = Path(folder) / 'session.json'
        with path.open('w', encoding='utf-8') as file:
            json.dump(session.as_dict(), file, ensure_ascii=False)
        with path.open('r', encoding='utf-8') as file:
            loaded = json.load(file)
        restored = StudySession(loaded['topic'], loaded['minutes'])
        print('topic=', restored.topic)
        print('minutes=', restored.minutes)
        assert restored.as_dict() == session.as_dict()
        print('roundtrip=PASS')


if __name__ == '__main__':
    main()
