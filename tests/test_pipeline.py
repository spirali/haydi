import pytest
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


def test_cnfs_exception():

    class X(object):
        pass

    x = hd.Values((X(), X(), X()))
    with pytest.raises(Exception):
        x.cnfs()


def test_pipeline_repr():
    r = hd.Range(4)
    assert repr(r.iterate()) == \
        "<Pipeline for Range: method=iterate action=Collect>"

    p = r.cnfs().map(lambda x: x + 1).filter(lambda x: x % 2).max(0)
    assert repr(p) == \
        "<Pipeline for Range: method=cnfs ts=[MapTransformation, " \
        "FilterTransformation] action=Max>"
