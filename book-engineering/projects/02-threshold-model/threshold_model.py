# داده مصنوعی: (امتیاز نشانه ها، برچسب بازبینی)
train = [(0, 0), (1, 0), (2, 0), (4, 1), (5, 1), (6, 1)]
test = [(0.5, 0), (2.5, 0), (3.5, 1), (6.5, 1)]

def predict(x, threshold):
    return int(x >= threshold)

def errors(rows, threshold):
    return sum(predict(x, threshold) != label for x, label in rows)

def fit(rows):
    candidates = range(0, 8)
    return min(candidates, key=lambda t: (errors(rows, t), t))

def main():
    threshold = fit(train)
    mistakes = errors(test, threshold)
    print(f"threshold={threshold}")
    print(f"test_errors={mistakes}/{len(test)}")
    print(f"test_accuracy={(len(test)-mistakes)/len(test):.0%}")
    print(f"prediction_for_3.5={predict(3.5, threshold)}")

if __name__ == "__main__":
    main()
