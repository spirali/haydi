from testutils import init
init()

import qit  # noqa


def test_join_range_iterate():
    d1 = qit.Range(3)
    d2 = qit.Range(0)
    d3 = qit.Range(0)
    d4 = qit.Range(5)

    expected = list(range(3)) + list(range(5))
    j = d1 + d2 + d3 + d4
    result = list(j)
    assert expected == result
    assert j.size == 8
    assert j.exact_size


def test_join_non_exact_size():
    d1 = qit.Range(3)
    d2 = qit.Range(3).filter(lambda x: True)
    j = d1 + d2
    assert j.size == 6
    assert not j.exact_size


def test_join_empty_iterate():
    d2 = qit.Range(0)
    d3 = qit.Range(0)

    j = d2 + d3
    result = list(j)
    assert [] == result


def test_join_int_generate():
    r1 = qit.Range(2)
    r2 = qit.Range(2, 4)
    j = r1 + r2

    result = list(j.generate().take(1000))
    assert set(result) == set(range(4))


def test_join_int_generate2():
    r1 = qit.Values([5000])
    r2 = qit.Range(1000)
    r3 = qit.Values([5001, 5002])

    j = r1 + r2 + r3

    result = list(j.generate().take(3000))
    assert result.count(5000) < 100
    assert result.count(5001) < 100
    assert result.count(5002) < 100


def test_join_int_generate3():
    r1 = qit.Range(2)
    r2 = qit.Range(2, 4)
    r3 = qit.Range(4, 6)

    j = qit.Join((r1, r2, r3), ratios=(1, 0, 1))

    result = list(j.generate().take(1000))
    assert set(result) == set((0, 1, 4, 5))


def test_join_iter_set():
    r1 = qit.Values([5000])
    r2 = qit.Range(10)
    r3 = qit.Values([5001, 5002])
    p = r1 + r2 + r3
    a = list(p)
    b = []
    for i in xrange(p.size + 10):
        it = iter(p)
        it.set(i)
        l = list(it)
        if l:
            b.append(l[0])
    assert a == b


def test_join_copy():
    r1 = qit.Range(0, 5)
    r2 = qit.Range(5, 10)
    r3 = qit.Range(10, 15)

    p = r1 + r2 + r3

    it = iter(p)
    it2 = it.copy()
    assert list(it) == list(it2)


def test_join_name():
    j = qit.Join((qit.Range(10), qit.Range(10)), name="TestJoin")
    assert j.name == "TestJoin"
