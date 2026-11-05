"""Educational binary perceptron; deterministic AND/XOR comparison."""

def predict(x1, x2, weights, bias):
    return int(weights[0] * x1 + weights[1] * x2 + bias >= 0)


def train(rows, epochs=20, rate=1):
    weights, bias = [0, 0], 0
    for _ in range(epochs):
        for x1, x2, label in rows:
            error = label - predict(x1, x2, weights, bias)
            weights[0] += rate * error * x1
            weights[1] += rate * error * x2
            bias += rate * error
    return weights, bias


def main():
    inputs = [(0, 0), (0, 1), (1, 0), (1, 1)]
    for name, labels in [('AND', [0, 0, 0, 1]), ('XOR', [0, 1, 1, 0])]:
        rows = [(x1, x2, y) for (x1, x2), y in zip(inputs, labels)]
        weights, bias = train(rows)
        outputs = [predict(x1, x2, weights, bias) for x1, x2 in inputs]
        mistakes = sum(a != b for a, b in zip(outputs, labels))
        print(f'{name} weights={weights} bias={bias} outputs={outputs} errors={mistakes}')


if __name__ == '__main__':
    main()
