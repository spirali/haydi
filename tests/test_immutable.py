from testutils import init
init()

import qit  # noqa


def test_immutable_domain():
    r = qit.Range(10)
    a = list(r)
    b = list(r)

    assert a == b == range(10)


def test_immutable_iterate():
    r = qit.Range(10).iterate()
    a = list(r)
    b = list(r)

    assert a == b == range(10)


def test_immutable_factory():
    r = qit.Range(10).iterate().filter(lambda x: x % 2 == 0)
    a = r.map(lambda x: x + 1)

    assert list(r) == [0, 2, 4, 6, 8]
    assert list(a) == [1, 3, 5, 7, 9]


def test_immutable_action():
    r = qit.Range(10).iterate().collect()
    a = list(r)
    b = list(r)

    assert a == b == range(10)
