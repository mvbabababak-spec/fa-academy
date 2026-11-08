"""Linear equations and real logarithms for modest finite numeric inputs."""
import math


def solve_linear(a, b, c):
    """Solve a*x + b = c; classify the degenerate a == 0 cases."""
    if not all(math.isfinite(v) for v in (a, b, c)):
        raise ValueError('inputs must be finite')
    if a == 0:
        return ('all', None) if b == c else ('none', None)
    x = (c - b) / a
    if not math.isfinite(x):
        raise ValueError('solution overflowed')
    return 'one', x


def log_base(x, base):
    if not (math.isfinite(x) and math.isfinite(base)):
        raise ValueError('inputs must be finite')
    if x <= 0 or base <= 0 or base == 1:
        raise ValueError('require x > 0, base > 0, base != 1')
    return math.log(x) / math.log(base)


def main():
    kind, x = solve_linear(2, 3, 11)
    print('solution=', x, 'kind=', kind)
    print('check=', math.isclose(2 * x + 3, 11))
    print('log2_8=', log_base(8, 2))
    print('zero_coefficient_cases=', solve_linear(0, 3, 3)[0], solve_linear(0, 3, 4)[0])


if __name__ == '__main__':
    main()
