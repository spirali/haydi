import operator as op


def ncr(n, r):
    """Returns a combination number (n, r)"""
    r = min(r, n-r)
    if r == 0:
        return 1
    if r < 0:
        return 0
    numer = reduce(op.mul, xrange(n, n-r, -1))
    denom = reduce(op.mul, xrange(1, r+1))
    return numer / denom


def identity(x):
    return x


def limit_string_length(string, length):
    assert length > 5
    strlen = len(string)
    if strlen <= length:
        return string

    half = length / 2
    return (string[:half - 2] + " ... " +
            string[strlen - half + 3 - length % 2:])
