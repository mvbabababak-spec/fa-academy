"""Linear equations and logarithms with explicit real-domain checks."""
import math


def solve_linear(a, b, c):
    """Solve a*x + b = c; identify unique, none, or infinitely many."""
    if not all(math.isfinite(v) for v in (a, b, c)):
        raise ValueError('coefficients must be finite')
    if a == 0:
        return ('infinite', None) if b == c else ('none', None)
    return ('unique', (c - b) / a)


def log_base(x, base):
    if not math.isfinite(x) or not math.isfinite(base) or x <= 0 or base <= 0 or base == 1:
        raise ValueError('require x > 0 and base > 0, base != 1, all finite')
    return math.log(x, base)


def main():
    kind, x = solve_linear(2, 3, 11)
    print('equation=', kind, 'x=', x)
    print('residual=', 2*x + 3 - 11)
    value = log_base(32, 2)
    print('log2_32=', value)
    print('roundtrip=', math.isclose(2**value, 32, rel_tol=1e-12))


if __name__ == '__main__':
    main()
