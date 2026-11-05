"""Gradient descent on a known quadratic; educational CPU example."""
import math


def loss(x):
    return (x - 3.0) ** 2


def gradient(x):
    return 2.0 * (x - 3.0)


def optimize(start, learning_rate, steps):
    if not math.isfinite(start):
        raise ValueError('start must be finite')
    if not math.isfinite(learning_rate) or learning_rate <= 0:
        raise ValueError('learning_rate must be positive and finite')
    if type(steps) is not int or steps < 0:
        raise ValueError('steps must be a non-negative integer')
    path = [float(start)]
    for _ in range(steps):
        x = path[-1] - learning_rate * gradient(path[-1])
        if not math.isfinite(x):
            raise ValueError('non-finite update')
        path.append(x)
    return path


def main():
    for rate in (0.1, 1.1):
        path = optimize(0, rate, 20)
        print(f'rate={rate} final_x={path[-1]:.6f} final_loss={loss(path[-1]):.6f}')
    print('float_0.1_plus_0.2=', 0.1 + 0.2)
    print('close_to_0.3=', math.isclose(0.1 + 0.2, 0.3))


if __name__ == '__main__':
    main()
