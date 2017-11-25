import haydi as hd


def test_sequence_flags():
    a = hd.USet(4, "a")
    f = a.filter(lambda x: True)
    m = a.map(lambda x: True)

    p1 = hd.Sequences(a, 2)
    p2 = hd.Sequences(f, 2)
    p3 = hd.Sequences(m, 2)

    assert not p1.filtered
    assert p2.filtered
    assert not p3.filtered

    assert p1.step_jumps
    assert p2.step_jumps
    assert p3.step_jumps

    assert p1.strict
    assert not p2.strict
    assert not p3.strict


def test_sequence_iterate():
    s = hd.Sequences(hd.Range(3), 0, 2)

    expected = [(), (0,), (1,), (2,),
                (0, 0), (0, 1), (0, 2),
                (1, 0), (1, 1), (1, 2),
                (2, 0), (2, 1), (2, 2)]

    result = list(s)
    assert set(result) == set(expected)
    assert len(result) == len(expected)
    assert s.size == len(expected)


def test_sequence_iterate_empty():
    assert list(hd.Sequences(hd.Range(3), 0)) == [()]


def test_sequence_generate():
    s = hd.Sequences(hd.Range(3), 5)
    result = list(s.generate(200))
    assert len(result)
    for r in result:
        assert len(r) == 5
        for x in r:
            assert 0 <= x < 3


def test_sequence_iter_set():
    r2 = hd.Range(4)
    p = hd.Sequences(r2, 3)

    a = list(p)
    b = []
    for i in xrange(p.size + 10):
        it = p.create_iter(i)
        result = list(it)
        if result:
            b.append(result[0])
    assert a == b


def test_sequence_name():
    s = hd.Sequences(hd.Range(10), 2, name="TestSequence")
    assert s.name == "TestSequence"


def test_sequence_to_values():
    s = hd.Sequences(hd.Range(3), 0, 2)

    v = s.to_values()

    assert isinstance(v, hd.Values)
    assert list(s) == list(v)


def test_sequence_to_values_maxsize():
    s = hd.Sequences(hd.Range(3), 0, 2)

    v = s.to_values(max_size=3)

    assert isinstance(v, hd.Sequences)
    assert isinstance(v.domain, hd.Values)
    assert list(s) == list(v)


def test_sequence_operator():
    r = hd.Range(3)

    s1 = hd.Sequences(r, 4)
    s2 = r ** 4

    assert list(s1) == list(s2)
