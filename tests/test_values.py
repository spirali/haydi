from testutils import init
init()

import qit  # noqa


def test_values_iterate():

    a = qit.Values(["a", "b", "c"])

    assert a.size == 3
    assert list(a.iterate()) == ["a", "b", "c"]
    for x in a.generate(100):
        assert x in ("a", "b", "c")

    b = qit.Values([])
    assert b.size == 0
    assert list(b.iterate()) == []


def test_iter_set():
    a = qit.Values(["a", "b", "c", "d"])
    i = iter(a)
    i.set(2)
    assert list(i) == ["c", "d"]
