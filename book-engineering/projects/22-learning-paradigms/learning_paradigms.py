"""Synthetic classification with an isolated train/validation/test split."""
from sklearn.dummy import DummyClassifier
from sklearn.tree import DecisionTreeClassifier

# Each row: unique ID, numeric feature, hand-made label. Never real user data.
TRAIN = [('tr1',1,0),('tr2',2,0),('tr3',3,0),('tr4',4,0),('tr5',6,1),('tr6',7,1),('tr7',8,1),('tr8',9,1)]
VALIDATION = [('v1',2.5,0),('v2',4.5,0),('v3',5.5,1),('v4',8.5,1)]
TEST = [('t1',1.5,0),('t2',3.5,0),('t3',6.5,1),('t4',9.5,1)]


def check_splits(*splits):
    seen = set()
    for rows in splits:
        if not rows:
            raise ValueError('empty split')
        for row_id, x, y in rows:
            if row_id in seen:
                raise ValueError('duplicate ID across splits')
            if y not in (0, 1):
                raise ValueError('labels must be binary')
            seen.add(row_id)


def accuracy(rows, predict):
    if not rows:
        raise ValueError('empty evaluation split')
    return sum(int(predict(x) == y) for _, x, y in rows) / len(rows)


def fit_threshold(rows):
    if not rows:
        raise ValueError('empty training data')
    candidates = [float('-inf')] + sorted({float(row[1]) for row in rows}) + [float('inf')]
    return min(candidates, key=lambda t: (sum((x >= t) != y for _, x, y in rows), t))


def main():
    check_splits(TRAIN, VALIDATION, TEST)
    threshold = fit_threshold(TRAIN)
    manual = lambda x: int(x >= threshold)
    baseline = DummyClassifier(strategy='most_frequent').fit([[x] for _,x,_ in TRAIN], [y for _,_,y in TRAIN])
    tree = DecisionTreeClassifier(max_depth=1, random_state=42).fit([[x] for _,x,_ in TRAIN], [y for _,_,y in TRAIN])
    models = [('baseline', lambda x: int(baseline.predict([[x]])[0])), ('manual', manual), ('tree', lambda x: int(tree.predict([[x]])[0]))]
    scored = [(name, accuracy(VALIDATION, predict), predict) for name, predict in models]
    # Ties use listed order, not the held-out test data.
    name, val, predict = max(scored, key=lambda item: item[1])
    print('train=%d validation=%d test=%d' % (len(TRAIN),len(VALIDATION),len(TEST)))
    print('manual_threshold=', threshold)
    for label, score, _ in scored: print(f'{label}_validation_accuracy={score:.3f}')
    print('selected=', name)
    print(f'test_accuracy={accuracy(TEST, predict):.3f}')
    print('warning=synthetic demonstration, not production evaluation')

if __name__ == '__main__':
    main()
