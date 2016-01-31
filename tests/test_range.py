from testutils import init
init()

import qit


def test_range_iterate():
    assert list(qit.Range(10)) == list(range(10))
    assert list(qit.Range(0)) == []
    assert list(qit.Range(-1)) == []
    assert list(qit.Range(-5, -1)) == list(range(-5, -1))
    assert list(qit.Range(-5, 10, 2)) == list(range(-5, 10, 2))
    assert list(qit.Range(-5, 11, 2)) == list(range(-5, 11, 2))

def test_range_size():
    assert qit.Range(20).size == 20
    assert qit.Range(0).size == 0
    assert qit.Range(-1).size == 0

def test_range_generate():
    result = list(qit.Range(10).generate().take(200))
    assert len(result) == 200
    for r in result:
        assert 0 <= r < 10

    result = list(qit.Range(-5, 10).generate().take(200))
    assert len(result) == 200
    for r in result:
        assert -5 <= r < 10

    result = list(qit.Range(0, 10, 2).generate().take(200))
    assert len(result) == 200
    for r in result:
        assert 0 <= r < 10
        assert r % 2 == 0

def test_iter_set():
    r = qit.Range(20, 30, 3)
    a = list(r)
    b = []
    for i in xrange(40):
        it = iter(r)
        it.set(i)
        l = list(it)
        if l:
            b.append(l[0])
    assert a == b

def test_range_iter_copy():
    r = qit.Range(3, 10, 2)

    it = r.iterate()
    it2 = it.copy()

    assert list(it) == list(it2)
