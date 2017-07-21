from testutils import init
init()

import haydi as hd # noqa


def test_sets_strict():
    r = hd.Range(2)
    s = hd.Subsets(r, 0)
    assert s.strict


def test_sets_iter():
    r = hd.Range(2)
    s = hd.Subsets(r, 0)

    assert list(s) == [hd.Set(())]

    s = hd.Subsets(r, 1)
    assert list(s) == [hd.Set((0,)), hd.Set((1,))]

    s = hd.Subsets(r, 2)
    assert list(s) == [hd.Set((0, 1))]

    s = hd.Subsets(r, 3)
    assert list(s) == []

    r3 = hd.Range(3)

    s = hd.Subsets(r3, 0, 1)
    assert list(s) == [hd.Set(()), hd.Set((0,)), hd.Set((1,)), hd.Set((2,))]

    s = hd.Subsets(r3, 0, 2)
    assert list(s) == [hd.Set(()),
                       hd.Set((0,)), hd.Set((0, 1)), hd.Set((0, 2)),
                       hd.Set((1,)), hd.Set((1, 2)),
                       hd.Set((2,))]

    s = hd.Subsets(r3, 1, 2)
    assert list(s) == [hd.Set((0,)), hd.Set((0, 1)), hd.Set((0, 2)),
                       hd.Set((1,)), hd.Set((1, 2)), hd.Set((2,))]


def test_sets_size():
    r = hd.Range(3)
    assert hd.Subsets(r, 2).size == 3
    assert hd.Subsets(r, 0).size == 1
    s = hd.Subsets(r * r, 1, 3)
    assert s.size == len(list(s))
    assert s.size == 129


def test_sets_repr():
    r = hd.Range(10)
    assert repr(hd.Subsets(r)) == \
        "<Subsets size=1024 " \
        "{{}, {0}, {0, 1}, {0, 1, 2}, {0, 1, 2, 3}, ...}>"


def test_sets_to_values():
    r = hd.Range(4)
    s = hd.Subsets(r)

    v = s.to_values()

    assert isinstance(v, hd.Values)
    assert list(v) == list(s)


def test_sets_to_values_maxsize():
    r = hd.Range(4)
    s = hd.Subsets(r)

    v = s.to_values(r.size)

    assert isinstance(v, hd.Subsets)
    assert isinstance(v.domain, hd.Values)
    assert list(v) == list(s)


def test_sets_set_class():
    r = hd.Range(2)
    s = hd.Subsets(r, set_class=frozenset)
    assert not s.strict
    result = set(s)
    expected = set([frozenset(), frozenset((0,)),
                    frozenset((1,)), frozenset((0, 1))])
    assert result == expected
