from testutils import init
init()

import haydi as hd # noqa


def test_values_iterate():

    a = hd.Values(["a", "b", "c"])

    assert a.exact_size
    assert a.size == 3
    assert list(a) == ["a", "b", "c"]
    for x in a.generate(100):
        assert x in ("a", "b", "c")

    b = hd.Values([])
    assert b.size == 0
    assert list(b) == []


def test_values_set():
    a = hd.Values(["a", "b", "c", "d"])
    i = iter(a)
    i.set_step(2)
    assert list(i) == ["c", "d"]


def test_values_name():
    a = hd.Values(["a", "b", "c", "d"], name="ListTest")
    assert a.name == "ListTest"
