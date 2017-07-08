from testutils import init
init()

import haydi as hd # noqa
import itertools  # noqa


def test_product_flags():
    a = hd.ASet(4, "a")
    f = a.filter(lambda x: True)
    m = a.map(lambda x: True)

    p1 = a * a
    p2 = f * a
    p3 = m * a

    assert not p1.filtered
    assert p2.filtered
    assert not p3.filtered

    assert p1.step_jumps
    assert p2.step_jumps
    assert p3.step_jumps

    assert p1.strict
    assert not p2.strict
    assert not p3.strict


def test_product_iterate():
    r1 = hd.Range(4)
    r2 = hd.Range(2)
    p = hd.Product((r1, r1, r2))
    expected = list(itertools.product(range(4), range(4), range(2)))

    assert set(p) == set(expected)
    assert len(list(p)) == len(expected)
    assert p.size == len(expected)


def test_product_generate():
    r1 = hd.Range(4)
    r2 = hd.Range(2)
    p = hd.Product((r1, r1, r2))

    result = list(p.generate(200))
    for r in result:
        assert len(r) == 3
        assert 0 <= r[0] < 4
        assert 0 <= r[1] < 4
        assert 0 <= r[2] < 2


def test_product_mul():
    r1 = hd.Range(4)
    r2 = hd.Range(2)
    result = list((r1 * r2))
    expected = itertools.product(range(4), range(2))
    assert set(result) == set(expected)
    assert len(result) == 8

    result = list((r1 * r2 * r1))
    expected = itertools.product(range(4), range(2), range(4))
    assert set(result) == set(expected)
    assert len(result) == 32


def test_product_step_iter():
    r1 = hd.Range(3)
    r2 = hd.Range(4)
    p = r1 * r2

    a = list(p)
    b = []
    for i in xrange(40):
        it = p.create_step_iter(i)
        l = list(it)
        if l:
            b.append(l[0])
    assert a == b


def test_uproduct_iterate():
    r1 = hd.Range(4)
    p = hd.Product((r1, r1), unordered=True)

    result = list(p)
    assert set(result) == set(
        [(1, 0),
         (2, 0),
         (3, 0),
         (2, 1),
         (3, 1),
         (3, 2)])
    assert len(result) == p.size

    p = hd.Product((r1, r1, r1), unordered=True)
    result = list(p)
    assert set(result) == set(
        [(2, 1, 0),
         (3, 1, 0),
         (3, 2, 0),
         (3, 2, 1),
         ])
    assert len(result) == p.size

    p = hd.Product((r1, r1, r1, r1), unordered=True)
    result = list(p)
    assert set(result) == set([(3, 2, 1, 0)])
    assert len(result) == p.size


def test_uproduct_iter_set():
    r = hd.Range(10)
    p = hd.Product((r, r), unordered=True)

    a = list(p)
    for i in xrange(p.size):
        it = p.create_iter(i)
        l = list(it)
        assert a[i:] == l

    r = hd.Range(899)
    p = hd.Product((r, r), unordered=True)

    a = list(p)
    x = 43211
    it = p.create_iter(x)
    assert list(it) == a[x:]

    x = 403388
    it = p.create_iter(x)
    assert list(it) == a[x:]


def test_named_product():

    r = hd.Range(10)
    a = hd.NamedProduct([("a", r), ("b", r * r)])
    result = list(a)[0]
    assert result.a == 0
    assert result.b == (0, 0)

    r = hd.Range(10)
    a = hd.NamedProduct([("a", r), ("b", r)], unordered=True)
    result = list(a)[0]
    assert result.a == 1
    assert result.b == 0


def test_product_name():
    r = hd.Range(10)
    p = hd.Product((r, r), name="TestProduct")
    assert p.name == "TestProduct"

    r = hd.Range(10)
    p = hd.Product((r, r), name="TestUProduct", unordered=True)
    assert p.name == "TestUProduct"

    p = hd.NamedProduct([("a", r), ("b", r * r)], name="TestNamedProduct")
    assert p.name == "TestNamedProduct"


def test_product_cache_unordered():
    size = 1000

    def test_for_size(cache_size):
        r = hd.Range(10000)
        p = hd.Product((r, r), unordered=True, cache_size=cache_size)
        result = list(p.generate(size))
        cache_pairs = (cache_size * (cache_size - 1)) / 2
        for i in xrange(size / cache_pairs):
            values = set()
            for a, b in result[i * cache_pairs: (i + 1) * cache_pairs]:
                values.add(a)
                values.add(b)
            assert len(values) <= cache_pairs

    test_for_size(3)
    test_for_size(20)


def test_product_cache():
    size = 1000

    def test_for_size(cache_size):
        r = hd.Range(10000)
        p = hd.Product((r, r), cache_size=cache_size)
        result = list(p.generate(size))

        cache_pairs = cache_size * cache_size
        for i in xrange(size / cache_pairs):
            values1 = set()
            values2 = set()
            for a, b in result[i * cache_pairs: (i + 1) * cache_pairs]:
                values1.add(a)
                values2.add(b)
            assert len(values1) <= cache_size and len(values2) <= cache_size

    test_for_size(3)
    test_for_size(20)


def test_product_steps():
    a = hd.Range(4).filter(lambda x: x % 2 == 0)
    p = a * a

    assert p.size == 16
    assert a.step_jumps
    assert p.step_jumps

    a = hd.Range(10).filter(lambda x: x % 2 == 0 and x < 8)
    p = a * a

    assert p.size == 100
    assert a.step_jumps
    assert p.step_jumps

    result = list(p)
    assert len(result) == 16
    items = [0, 2, 4, 6]
    assert set(result) == set(itertools.product(items, items))

    assert list(p.iterate_steps(0, 100)) == result
    assert list(p.iterate_steps(0, 300)) == result

    assert list(p.iterate_steps(0, 1)) == result[0:1]
    assert list(p.iterate_steps(0, 2)) == result[0:1]
    assert list(p.iterate_steps(0, 3)) == result[0:2]
    assert list(p.iterate_steps(0, 4)) == result[0:2]
    assert list(p.iterate_steps(0, 5)) == result[0:3]
    assert list(p.iterate_steps(0, 6)) == result[0:3]
    assert list(p.iterate_steps(0, 10)) == result[0:4]
    assert list(p.iterate_steps(0, 11)) == result[0:4]
    assert list(p.iterate_steps(0, 12)) == result[0:4]

    assert list(p.iterate_steps(0, 20)) == result[0:4]
    assert list(p.iterate_steps(0, 21)) == result[0:5]
    assert list(p.iterate_steps(0, 22)) == result[0:5]

    assert list(p.iterate_steps(1, 1)) == []
    assert list(p.iterate_steps(1, 2)) == []
    assert list(p.iterate_steps(1, 3)) == result[1:2]
    assert list(p.iterate_steps(1, 4)) == result[1:2]

    assert list(p.iterate_steps(1, 1)) == []

    assert list(p.iterate_steps(10, 12)) == []
    assert list(p.iterate_steps(10, 14)) == []
    assert list(p.iterate_steps(10, 24)) == [(2, 0), (2, 2)]
    assert list(p.iterate_steps(30, 34)) == []
    assert list(p.iterate_steps(40, 44)) == [(4, 0), (4, 2)]
    assert list(p.iterate_steps(85, 100)) == []

    assert list(p.iterate_steps(85, 100)) == []


def test_product_empty():
    p = hd.Product(())
    assert list(p) == [()]


def test_product_steps2():
    a = hd.Range(12).filter(lambda x: x in (6, 9))
    b = hd.Range(10).filter(lambda x: x in (2, 3))
    p = a * b

    assert list(p.iterate_steps(53, 60)) == []
    assert list(p.iterate_steps(43, 60)) == []
    assert list(p.iterate_steps(43, 63)) == [(6, 2)]
    assert list(p.iterate_steps(43, 93)) == [(6, 2), (6, 3), (9, 2)]
    assert list(p.iterate_steps(43, 94)) == [(6, 2), (6, 3), (9, 2), (9, 3)]


def test_product_steps3():
    a = hd.Range(10).filter(lambda x: False)
    b = hd.Range(0).filter(lambda x: False)
    p = a * b

    assert list(p.iterate_steps(0, 0)) == []


def test_uproduct_steps():

    items = (1, 2, 7, 8)
    a = hd.Range(10).filter(lambda x: x in items)
    p = hd.Product((a, a), unordered=True)

    assert p.size == 45

    for i in xrange(9):
        assert list(p.iterate_steps(0, i)) == []
    assert list(p.iterate_steps(0, 10)) == [(2, 1)]
    assert list(p.iterate_steps(0, 14)) == [(2, 1)]
    assert list(p.iterate_steps(0, 15)) == [(2, 1), (7, 1)]
    assert list(p.iterate_steps(0, 16)) == [(2, 1), (7, 1), (8, 1)]
    assert list(p.iterate_steps(0, 21)) == [(2, 1), (7, 1), (8, 1)]
    assert list(p.iterate_steps(0, 22)) == [(2, 1), (7, 1), (8, 1), (7, 2)]
    assert list(p.iterate_steps(0, 23)) == [
        (2, 1), (7, 1), (8, 1), (7, 2), (8, 2)]
    assert list(p.iterate_steps(0, 42)) == [
        (2, 1), (7, 1), (8, 1), (7, 2), (8, 2)]
    assert list(p.iterate_steps(0, 43)) == [
        (2, 1), (7, 1), (8, 1), (7, 2), (8, 2), (8, 7)]
    assert list(p.iterate_steps(0, 45)) == [
        (2, 1), (7, 1), (8, 1), (7, 2), (8, 2), (8, 7)]

    assert list(p.iterate_steps(6, 16)) == [(2, 1), (7, 1), (8, 1)]
    assert list(p.iterate_steps(9, 16)) == [(2, 1), (7, 1), (8, 1)]
    assert list(p.iterate_steps(10, 16)) == [(7, 1), (8, 1)]
    assert list(p.iterate_steps(14, 16)) == [(7, 1), (8, 1)]
    assert list(p.iterate_steps(15, 16)) == [(8, 1)]


def test_uproduct_steps2():
    a = hd.Range(3).filter(lambda x: x != 2)
    b = (a * a).filter(lambda x: x[0] + x[1] > 0)
    c = hd.Product((b, b), unordered=True)

    assert list(b) == [(0, 1), (1, 0), (1, 1)]
    assert list(c.iterate_steps(0, 9)) == []
    assert list(c.iterate_steps(0, 10)) == [((1, 0), (0, 1))]
    assert list(c.iterate_steps(0, 11)) == [((1, 0), (0, 1)), ((1, 1), (0, 1))]
    assert set(c.iterate_steps(0, 36)) == \
        set((((1, 0), (0, 1)), ((1, 1), (1, 0)), ((1, 1), (0, 1))))

    assert list(c.iterate_steps(8, 9)) == []
    assert list(c.iterate_steps(9, 10)) == [((1, 0), (0, 1))]
    assert list(c.iterate_steps(0, 11)) == [((1, 0), (0, 1)), ((1, 1), (0, 1))]
    assert list(c.iterate_steps(14, 20)) == []
    assert list(c.iterate_steps(14, 26)) == [((1, 1), (1, 0))]
    assert set(c.iterate_steps(8, 36)) == \
        set((((1, 0), (0, 1)), ((1, 1), (1, 0)), ((1, 1), (0, 1))))


def test_product_to_values():
    r = hd.Range(10)
    p = r * r

    v = p.to_values()

    assert isinstance(v, hd.Values)
    assert list(v) == list(p)


def test_product_to_values_maxsize():
    r = hd.Range(10)
    p = r * r

    v = p.to_values(max_size=r.size)

    assert isinstance(v, hd.Product)
    assert all(isinstance(d, hd.Values) for d in v.domains)
    assert list(v) == list(p)
