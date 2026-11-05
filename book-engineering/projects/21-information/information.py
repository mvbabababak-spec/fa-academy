"""Discrete entropy, cross entropy and KL divergence in bits."""
import math


def validate(distribution):
    if not distribution or any(not math.isfinite(p) or p < 0 or p > 1 for p in distribution):
        raise ValueError('probabilities must be finite values in [0, 1]')
    if not math.isclose(math.fsum(distribution), 1.0, rel_tol=0, abs_tol=1e-12):
        raise ValueError('probabilities must sum to one')


def entropy(p):
    validate(p)
    return -math.fsum(x * math.log2(x) for x in p if x > 0)


def cross_entropy(p, q):
    validate(p)
    validate(q)
    if len(p) != len(q):
        raise ValueError('distributions must have the same length')
    if any(x > 0 and y == 0 for x, y in zip(p, q)):
        return math.inf
    return -math.fsum(x * math.log2(y) for x, y in zip(p, q) if x > 0)


def kl_divergence(p, q):
    validate(p)
    validate(q)
    if len(p) != len(q):
        raise ValueError('distributions must have the same length')
    if any(x > 0 and y == 0 for x, y in zip(p, q)):
        return math.inf
    return math.fsum(x * (math.log2(x) - math.log2(y))
                     for x, y in zip(p, q) if x > 0)


def main():
    p, q = [0.5, 0.5], [0.9, 0.1]
    h, ce, kl = entropy(p), cross_entropy(p, q), kl_divergence(p, q)
    print(f'entropy_bits={h:.6f}')
    print(f'cross_entropy_bits={ce:.6f}')
    print(f'kl_bits={kl:.6f}')
    print('identity=', math.isclose(ce, h + kl, abs_tol=1e-12))
    print('zero_q_positive_p=', cross_entropy([1, 0], [0, 1]))


if __name__ == '__main__':
    main()
