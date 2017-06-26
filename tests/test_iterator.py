from testutils import init
init()

import haydi as hd # noqa


def test_iterator_first():
    assert 0 == hd.Range(10).first(-1).run()
    assert -1 == hd.Range(0).first(-1).run()


def test_iterator_reduce():
    expected = sum(range(10))
    result = hd.Range(10).reduce(lambda x, y: x + y).run()
    assert expected == result

    expected = max(range(10))
    result = hd.Range(10).reduce(max).run()
    assert expected == result
