import haydi as hd


def test_immutable_domain():
    r = hd.Range(10)
    a = list(r)
    b = list(r)

    assert a == b == range(10)


def test_immutable_iterate():
    r = hd.Range(10)
    a = list(r)
    b = list(r)

    assert a == b == range(10)


def test_immutable_factory():
    r = hd.Range(10).filter(lambda x: x % 2 == 0)
    a = r.map(lambda x: x + 1)

    assert list(r) == [0, 2, 4, 6, 8]
    assert list(a) == [1, 3, 5, 7, 9]


def test_immutable_action():
    r = hd.Range(10).collect()
    a = list(r)
    b = list(r)

    assert a == b == range(10)
