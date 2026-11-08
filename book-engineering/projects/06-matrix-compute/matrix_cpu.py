"""Small CPU-only matrix multiplication; educational, not a benchmark."""

def matmul(a, b):
    if not a or not b or not a[0] or not b[0]:
        raise ValueError('matrices must not be empty')
    k = len(a[0])
    n = len(b[0])
    if any(len(row) != k for row in a) or any(len(row) != n for row in b):
        raise ValueError('matrices must be rectangular')
    if k != len(b):
        raise ValueError('inner dimensions must match')
    return [[sum(a[i][t] * b[t][j] for t in range(k))
             for j in range(n)] for i in range(len(a))]


def main():
    a = [[1, 2], [3, 4]]
    b = [[5, 6], [7, 8]]
    result = matmul(a, b)
    print('A x B =', result)
    assert result == [[19, 22], [43, 50]]
    print('correctness=PASS')
    print('fp32_payload_2x2_matrices_bytes=', 3 * 2 * 2 * 4)


if __name__ == '__main__':
    main()
