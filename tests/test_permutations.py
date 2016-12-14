from testutils import init
init()

import haydi as hd # noqa


def test_permutations_iterate():
    v = hd.Values(("A", "B", "C"))
    p = hd.Permutations(v)
    assert p.size == 6

    result = set(p)
    expected = set([('A', 'B', 'C'), ('A', 'C', 'B'), ('B', 'A', 'C'),
                    ('B', 'C', 'A'), ('C', 'A', 'B'), ('C', 'B', 'A')])
    assert result == expected
