from testutils import init
init()

import haydi as hd # noqa


def test_join_range_iterate():
    d1 = hd.Range(3)
    d2 = hd.Range(0)
    d3 = hd.Range(0)
    d4 = hd.Range(5)

    expected = list(range(3)) + list(range(5))
    j = d1 + d2 + d3 + d4
    result = list(j)
    assert expected == result
    assert j.size == 8
    assert not j.filtered
    assert j.step_jumps


def test_join_filtered_size():
    d1 = hd.Range(3)
    d2 = hd.Range(3).filter(lambda x: True)
    j = d1 + d2
    assert j.size == 6
    assert j.filtered
    assert j.step_jumps


def test_join_empty_iterate():
    d2 = hd.Range(0)
    d3 = hd.Range(0)

    j = d2 + d3
    result = list(j)
    assert [] == result


def test_join_int_generate():
    r1 = hd.Range(2)
    r2 = hd.Range(2, 4)
    j = r1 + r2

    result = list(j.generate().take(1000))
    assert set(result) == set(range(4))


def test_join_int_generate2():
    r1 = hd.Values([5000])
    r2 = hd.Range(1000)
    r3 = hd.Values([5001, 5002])

    j = r1 + r2 + r3

    result = list(j.generate().take(3000))
    assert result.count(5000) < 100
    assert result.count(5001) < 100
    assert result.count(5002) < 100


def test_join_int_generate3():
    r1 = hd.Range(2)
    r2 = hd.Range(2, 4)
    r3 = hd.Range(4, 6)

    j = hd.Join((r1, r2, r3), ratios=(1, 0, 1))

    result = list(j.generate().take(1000))
    assert set(result) == set((0, 1, 4, 5))


def test_join_iter_set():
    r1 = hd.Values([5000])
    r2 = hd.Range(10)
    r3 = hd.Values([5001, 5002])
    p = r1 + r2 + r3
    a = list(p)
    b = []
    for i in xrange(p.size + 10):
        it = p.create_iter(i)
        l = list(it)
        if l:
            b.append(l[0])
    assert a == b


def test_join_name():
    j = hd.Join((hd.Range(10), hd.Range(10)), name="TestJoin")
    assert j.name == "TestJoin"
