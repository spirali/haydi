import haydi as hd


def test_range_iterate():
    assert list(hd.Range(10)) == list(range(10))
    assert list(hd.Range(0)) == []
    assert list(hd.Range(-1)) == []
    assert list(hd.Range(-5, -1)) == list(range(-5, -1))
    assert list(hd.Range(-5, 10, 2)) == list(range(-5, 10, 2))
    assert list(hd.Range(-5, 11, 2)) == list(range(-5, 11, 2))


def test_range_size_and_flags():
    assert hd.Range(20).size == 20
    assert hd.Range(0).size == 0
    assert hd.Range(-1).size == 0
    assert not hd.Range(1).filtered
    assert hd.Range(1).step_jumps
    assert hd.Range(1).strict


def test_range_generate():
    result = list(hd.Range(10).generate().take(200))
    assert len(result) == 200
    for r in result:
        assert 0 <= r < 10

    result = list(hd.Range(-5, 10).generate().take(200))
    assert len(result) == 200
    for r in result:
        assert -5 <= r < 10

    result = list(hd.Range(0, 10, 2).generate().take(200))
    assert len(result) == 200
    for r in result:
        assert 0 <= r < 10
        assert r % 2 == 0

    result = list(hd.Range(0, 10, 3).generate().take(200))
    assert len(result) == 200
    for r in result:
        assert 0 <= r < 10
        assert r % 3 == 0


def test_iter_set():
    r = hd.Range(20, 30, 3)
    a = list(r)
    b = []
    for i in xrange(40):
        it = r.create_skip_iter(i)
        l = list(it)
        if l:
            b.append(l[0])
    assert a == b


def test_range_name():
    r = hd.Range(3, 10, 5, name="Test")
    assert r.name == "Test"


def test_range_repr():
    r = hd.Range(10)
    assert repr(r) == "<Range size=10 {0, 1, 2, 3, 4, ...}>"


def test_range_to_values():
    r = hd.Range(10)
    v = r.to_values()

    assert isinstance(v, hd.Values)
    assert list(v) == list(r)


def test_range_to_values_maxsize():
    r = hd.Range(100)
    v = r.to_values(max_size=r.size - 1)

    assert r == v
