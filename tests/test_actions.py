from testutils import init
init()

import qit  # noqa


def test_reduce():
    r = qit.Range(100).iterate().reduce(lambda x, y: x + y, 100).run()
    assert r == 100 + sum(range(100))


def test_first_found():
    r = qit.Range(100).iterate().first(lambda x: x == 50).run()
    assert r == 50


def test_first_not_found():
    r = qit.Range(100).iterate().first(lambda x: x >= 100, -1).run()
    assert r == -1


def test_max_all():
    f = [("A", 10), ("A", 10), ("B", 20), ("C", 10), ("D", 20), ("E", 5)]
    v = qit.Values(f)
    result = v.iterate().max_all(lambda x: x[1]).run()
    assert result == [("B", 20), ("D", 20)]

    result = list(v.iterate().filter(
        lambda x: x[1] < 20).max_all(lambda x: x[1]))
    assert result == [("A", 10), ("A", 10), ("C", 10)]
