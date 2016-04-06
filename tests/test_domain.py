from testutils import init
init()

import qit  # noqa


def test_domain_map():

    def fn(x):
        return (x + 1) * 10

    d = qit.Range(5).map(fn)
    result = list(d)
    assert result == [10, 20, 30, 40, 50]

    result = list(d.generate(10))
    for x in result:
        assert x in [10, 20, 30, 40, 50]

    result = list(qit.UnorderedProduct((d, d)))
    assert set(result) == set(((20, 10), (30, 10), (40, 10), (50, 10),
                               (30, 20), (40, 20), (50, 20),
                               (40, 30), (50, 30), (50, 40)))
    assert d.size == 5
    assert d.exact_size


def test_domain_filter():

    def fn(x):
        return x > 2 and x < 5

    r = qit.Range(6)
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

    assert not qit.Sequence(d, 2).exact_size
    assert qit.Sequence(r, 2).exact_size

    assert not qit.Mapping(d, r).exact_size
    assert not qit.Mapping(r, d).exact_size
    assert qit.Mapping(r, r).exact_size

    assert not qit.UnorderedProduct((d, d)).exact_size
    assert qit.UnorderedProduct((r, r)).exact_size

    result = list(qit.UnorderedProduct((d, d)))
    assert set(result) == set(((4, 3),))
