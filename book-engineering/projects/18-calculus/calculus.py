"""Analytic and numerical calculus checks for a smooth polynomial."""
import math


def f(x, y):
    return x*x + 3*x*y + y*y


def gradient(x, y):
    return (2*x + 3*y, 3*x + 2*y)


def numerical_gradient(x, y, h=1e-5):
    if not math.isfinite(h) or h <= 0:
        raise ValueError('h must be finite and positive')
    dx = (f(x+h, y) - f(x-h, y)) / (2*h)
    dy = (f(x, y+h) - f(x, y-h)) / (2*h)
    return dx, dy


def midpoint_integral(func, a, b, n):
    if type(n) is not int or n <= 0:
        raise ValueError('n must be a positive integer')
    width = (b - a) / n
    return sum(func(a + (i + 0.5)*width) for i in range(n)) * width


def main():
    exact = gradient(1, 2)
    numeric = numerical_gradient(1, 2)
    print('analytic_gradient=', exact)
    print('numeric_gradient=', tuple(round(v, 6) for v in numeric))
    print('gradient_matches=', all(math.isclose(a, b, rel_tol=1e-8, abs_tol=1e-8)
                                   for a, b in zip(exact, numeric)))
    area = midpoint_integral(lambda x: x*x, 0, 2, 1000)
    print('integral_x2_0_2=', round(area, 6))
    print('exact_integral=', round(8/3, 6))


if __name__ == '__main__':
    main()
