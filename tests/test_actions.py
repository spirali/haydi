from testutils import init
init()

import haydi as hd  # noqa


def test_collect():
    result = hd.Range(10).iterate().collect().run()
    expected = range(10)
    assert result == expected


def test_collect2():
    result = hd.Range(10).collect().run()
    expected = range(10)
    assert result == expected


def test_reduce():
    r = hd.Range(100).reduce(lambda x, y: x + y, 100).run()
    expected = sum(range(100)) + 100
    assert r == expected


def test_first_found():
    r = hd.Range(100).first(lambda x: x == 50).run()
    assert r == 50


def test_first_not_found():
    r = hd.Range(100).first(lambda x: x >= 100, -1).run()
    assert r == -1


def test_max_all():
    f = [("A", 10), ("A", 10), ("B", 20), ("C", 10), ("D", 20), ("E", 5)]
    v = hd.Values(f)
    result = v.max_all(lambda x: x[1]).run()
    assert result == [("B", 20), ("D", 20)]

    result = list(v.filter(
        lambda x: x[1] < 20).max_all(lambda x: x[1]))
    assert result == [("A", 10), ("A", 10), ("C", 10)]


def test_samples():
    f = [("A", 10), ("A", 10), ("B", 20),
         ("C", 10), ("D", 20), ("E", 5), ("Z", None), ("S", 10)]
    v = hd.Values(f)
    result = v.groups(lambda x: x[1], 2).run()
    expected = {
        10: [("A", 10), ("A", 10)],
        20: [("B", 20), ("D", 20)],
        5: [("E", 5)],
    }
    assert expected == result


def test_samples_counts():
    f = [("A", 10), ("A", 10), ("B", 20),
         ("C", 10), ("D", 20), ("E", 5), ("Z", None), ("S", 10)]
    v = hd.Values(f)
    result = v.groups_counts(lambda x: x[1], 2).run()
    expected = {
        10: [4, ("A", 10), ("A", 10)],
        20: [2, ("B", 20), ("D", 20)],
        5: [1, ("E", 5)],
    }
    assert expected == result
