from haydi import Values
from testutils import init
init()

import haydi as hd # noqa


def test_values_flags():
    a = hd.Values(["a", "b", "c"])
    assert not a.filtered
    assert a.step_jumps
    assert not a.strict


def test_values_iterate():

    a = hd.Values(["a", "b", "c"])

    assert not a.filtered
    assert a.step_jumps
    assert a.size == 3
    assert list(a) == ["a", "b", "c"]
    for x in a.generate(100):
        assert x in ("a", "b", "c")

    b = hd.Values([])
    assert b.size == 0
    assert list(b) == []


def test_values_set():
    a = hd.Values(["a", "b", "c", "d"])
    i = a.create_iter(2)
    assert list(i) == ["c", "d"]


def test_values_name():
    a = hd.Values(["a", "b", "c", "d"], name="ListTest")
    assert a.name == "ListTest"


def test_cnfs_values():
    ax = hd.ASet(3, "a")
    a0, a1, a2 = ax
    assert list(hd.CnfValues((a0,)).create_cn_iter()) == [a0]
    assert list(hd.CnfValues((a0,))) == [a0, a1, a2]


def test_values_repr():
    v = hd.Values(("abc", 321, (2.2, 1)))
    assert repr(v) == "<Values size=3 {'abc', 321, (2.2, 1)}>"


def test_to_values():
    a = hd.Range(10)
    assert isinstance(a.to_values(), Values)

    c = a * a
    assert isinstance(c.to_values(), Values)


def test_to_values_max_size():
    a = hd.Range(10)
    assert a.to_values(max_size=a.size - 1) == a

    b = a * a
    c = b.to_values(max_size=a.size)
    assert b != c
    assert (isinstance(d, Values) for d in c.domains)
