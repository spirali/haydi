from testutils import init
init()

import haydi as hd # noqa


def test_domain_map():

    def fn(x):
        return (x + 1) * 10

    d = hd.Range(5).map(fn)
    result = list(d)
    assert result == [10, 20, 30, 40, 50]

    result = list(d.generate(10))
    for x in result:
        assert x in [10, 20, 30, 40, 50]

    result = list(hd.Product((d, d), unordered=True))
    assert set(result) == set(((20, 10), (30, 10), (40, 10), (50, 10),
                               (30, 20), (40, 20), (50, 20),
                               (40, 30), (50, 30), (50, 40)))
    assert d.size == 5
    assert d.exact_size


def test_domain_filter():

    def fn(x):
        return x > 2 and x < 5

    r = hd.Range(6)
    d = r.filter(fn)
    result = list(d)
    assert result == [3, 4]

    result = list(d.generate(5))
    assert len(result) == 5
    for x in result:
        assert x in [3, 4]

    assert not d.exact_size
    assert r.exact_size
    assert d.size == 6

    p = d * d
    result = list(p)
    assert set(result) == set(((3, 3), (4, 3), (3, 4), (4, 4)))

    assert not p.exact_size
    assert (r * r).exact_size

    assert not hd.Sequence(d, 2).exact_size
    assert hd.Sequence(r, 2).exact_size

    assert not hd.Mapping(d, r).exact_size
    assert not hd.Mapping(r, d).exact_size
    assert hd.Mapping(r, r).exact_size

    assert not hd.Product((d, d), unordered=True).exact_size
    assert hd.Product((r, r), unordered=True).exact_size

    result = list(hd.Product((d, d), unordered=True))
    assert set(result) == set(((4, 3),))
