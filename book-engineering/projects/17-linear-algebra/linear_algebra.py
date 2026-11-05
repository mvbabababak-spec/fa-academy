"""Matrix products from scratch and eigenpairs using NumPy."""
import numpy as np


def matmul(a, b):
    if not a or not b or not a[0] or not b[0]:
        raise ValueError('matrices must be nonempty')
    inner = len(a[0])
    columns = len(b[0])
    if any(len(row) != inner for row in a) or any(len(row) != columns for row in b):
        raise ValueError('matrices must be rectangular')
    if inner != len(b):
        raise ValueError('inner dimensions must match')
    return [[sum(a[i][k] * b[k][j] for k in range(inner))
             for j in range(columns)] for i in range(len(a))]


def main():
    a = [[1, 2, 3], [4, 5, 6]]
    b = [[1, 0], [0, 1], [1, 1]]
    manual = matmul(a, b)
    print('product=', manual)
    print('numpy_matches=', bool(np.array_equal(manual, np.array(a) @ np.array(b))))
    matrix = np.array([[2., 0.], [0., 3.]])
    values, vectors = np.linalg.eig(matrix)
    print('eigenvalues_sorted=', sorted(values.tolist()))
    print('eigenpair_check=', bool(np.allclose(matrix @ vectors, vectors * values)))


if __name__ == '__main__':
    main()
