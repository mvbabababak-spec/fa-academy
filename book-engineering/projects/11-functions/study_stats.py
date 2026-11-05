"""Small reusable functions for a synthetic study log."""

def total_minutes(entries):
    if any(value < 0 for value in entries):
        raise ValueError('minutes must be non-negative')
    return sum(entries)


def average_minutes(entries):
    if not entries:
        raise ValueError('at least one entry is required')
    return total_minutes(entries) / len(entries)


def count_topics(topics):
    counts = {}
    for topic in topics:
        counts[topic] = counts.get(topic, 0) + 1
    return counts


def main():
    entries = [30, 60, 90]
    topics = ['python', 'math', 'python']
    print('total=', total_minutes(entries))
    print('average=', average_minutes(entries))
    print('topics=', count_topics(topics))


if __name__ == '__main__':
    main()
