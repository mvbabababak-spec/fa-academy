"""A deterministic, synthetic lifecycle demonstration; no external packages."""

TRAIN = [(0.0, 1.0), (1.0, 3.0), (2.0, 5.0), (3.0, 7.0)]
VALIDATION = [(4.0, 9.0)]
TEST = [(5.0, 11.0), (6.0, 13.0)]


def predict(x, weight, bias):
    return weight * x + bias


def mse(rows, weight, bias):
    return sum((predict(x, weight, bias) - y) ** 2 for x, y in rows) / len(rows)


def train(rows, learning_rate, steps):
    weight, bias = 0.0, 0.0
    for _ in range(steps):
        grad_w = sum(2 * (predict(x, weight, bias) - y) * x for x, y in rows) / len(rows)
        grad_b = sum(2 * (predict(x, weight, bias) - y) for x, y in rows) / len(rows)
        weight -= learning_rate * grad_w
        bias -= learning_rate * grad_b
    return weight, bias


def main():
    candidates = []
    for rate in (0.01, 0.1):
        weight, bias = train(TRAIN, rate, steps=500)
        val_loss = mse(VALIDATION, weight, bias)
        candidates.append((val_loss, rate, weight, bias))
        print(f"lr={rate:.2f} val_mse={val_loss:.8f}")

    val_loss, rate, weight, bias = min(candidates)
    print(f"selected_lr={rate:.2f}")
    print(f"weight={weight:.6f} bias={bias:.6f}")
    print(f"test_mse={mse(TEST, weight, bias):.8f}")
    print(f"inference_x_7={predict(7.0, weight, bias):.6f}")


if __name__ == '__main__':
    main()
