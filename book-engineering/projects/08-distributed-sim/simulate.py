"""Sequential simulation of gradient averaging; not a distributed implementation."""

def step(weight, gradients, learning_rate):
    if not gradients:
        raise ValueError('at least one gradient required')
    mean_gradient = sum(gradients) / len(gradients)
    return mean_gradient, weight - learning_rate * mean_gradient


def energy_kwh(power_watts, hours):
    if power_watts < 0 or hours < 0:
        raise ValueError('power and duration must be non-negative')
    return power_watts / 1000 * hours


def main():
    mean, updated = step(1.0, [0.2, 0.4], 0.1)
    energy = energy_kwh(600, 5)
    print(f'mean_gradient={mean:.2f}')
    print(f'updated_weight={updated:.2f}')
    print(f'energy_kwh={energy:.2f}')
    assert abs(mean - 0.3) < 1e-9
    assert abs(updated - 0.97) < 1e-9
    assert abs(energy - 3.0) < 1e-9
    print('checks=PASS')


if __name__ == '__main__':
    main()
