from testutils import init
init()

import haydi as hd # noqa


def test_iterate():
    x = hd.Range(7).iterate()
    x = x.map(lambda x: x * 10)
    x = x.filter(lambda y: y != 20)
    assert list(x) == [0, 10, 30, 40, 50, 60]


def test_cnfs():
    x = hd.Range(10)
    assert list(x.cnfs()) == range(10)

    ax = hd.ASet(4, "a")
    bx = hd.ASet(2, "b")

    result = (ax * (ax + bx)).cnfs().filter(lambda x: x[1].parent == bx).run()
    assert result == [(ax.get(0), bx.get(0))]
