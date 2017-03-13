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
    assert not d.filtered
    assert d.step_jumps


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

    assert d.filtered
    assert not r.filtered
    assert d.size == 6

    p = d * d
    result = list(p)
    assert set(result) == set(((3, 3), (4, 3), (3, 4), (4, 4)))

    assert p.filtered
    assert not (r * r).filtered

    assert hd.Sequence(d, 2).filtered
    assert not hd.Sequence(r, 2).filtered

    assert not hd.Mapping(d, r).filtered
    assert hd.Mapping(r, d).filtered
    assert not hd.Mapping(r, r).filtered

    assert hd.Product((d, d), unordered=True).filtered
    assert not hd.Product((r, r), unordered=True).filtered

    result = list(hd.Product((d, d), unordered=True))
    assert set(result) == set(((4, 3),))
