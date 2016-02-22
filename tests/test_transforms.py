from testutils import init
init()

import qit  # noqa


def test_take():
    r = qit.Range(10)

    assert range(10) == list(r.iterate().take(100))
    assert range(5) == list(r.iterate().take(5))


def test_map():
    r = qit.Range(5)
    assert [0, 2, 4, 6, 8] == list(r.iterate().map(lambda x: x * 2))


def test_filter():
    r = qit.Range(10)

    assert list(r.iterate().filter(lambda x: False)) == []
    assert list(r.iterate().filter(lambda x: True)) == range(10)
    assert list(r.iterate().filter(lambda x: x % 2 == 1)) == [1, 3, 5, 7, 9]
