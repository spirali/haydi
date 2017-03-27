from testutils import init
init()

import haydi as hd # noqa


def test_sets_iter():
    r = hd.Range(2)
    s = hd.Sets(r, 0)

    assert list(s) == [hd.Set(())]

    s = hd.Sets(r, 1)
    assert list(s) == [hd.Set((0,)), hd.Set((1,))]

    s = hd.Sets(r, 2)
    assert list(s) == [hd.Set((0, 1))]

    s = hd.Sets(r, 3)
    assert list(s) == []

    r3 = hd.Range(3)

    s = hd.Sets(r3, 0, 1)
    assert list(s) == [hd.Set(()), hd.Set((0,)), hd.Set((1,)), hd.Set((2,))]

    s = hd.Sets(r3, 0, 2)
    assert list(s) == [hd.Set(()),
                       hd.Set((0,)), hd.Set((0, 1)), hd.Set((0, 2)),
                       hd.Set((1,)), hd.Set((1, 2)),
                       hd.Set((2,))]

    s = hd.Sets(r3, 1, 2)
    assert list(s) == [hd.Set((0,)), hd.Set((0, 1)), hd.Set((0, 2)),
                       hd.Set((1,)), hd.Set((1, 2)), hd.Set((2,))]


def test_size():
    r = hd.Range(3)
    assert hd.Sets(r, 2).size == 3
    assert hd.Sets(r, 0).size == 1
    s = hd.Sets(r * r, 1, 3)
    assert s.size == len(list(s))
    assert s.size == 129
