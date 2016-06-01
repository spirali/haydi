from testutils import init
init()

import qit  # noqa
import itertools  # noqa


def test_product_iterate():
    r1 = qit.Range(4)
    r2 = qit.Range(2)
    p = qit.Product((r1, r1, r2))
    expected = list(itertools.product(range(4), range(4), range(2)))

    assert set(p) == set(expected)
    assert len(list(p)) == len(expected)
    assert p.size == len(expected)


def test_product_generate():
    r1 = qit.Range(4)
    r2 = qit.Range(2)
    p = qit.Product((r1, r1, r2))

    result = list(p.generate(200))
    for r in result:
        assert len(r) == 3
        assert 0 <= r[0] < 4
        assert 0 <= r[1] < 4
        assert 0 <= r[2] < 2


def test_product_mul():
    r1 = qit.Range(4)
    r2 = qit.Range(2)
    result = list((r1 * r2).iterate())
    expected = itertools.product(range(4), range(2))
    assert set(result) == set(expected)
    assert len(result) == 8

    result = list((r1 * r2 * r1).iterate())
    expected = itertools.product(range(4), range(2), range(4))
    assert set(result) == set(expected)
    assert len(result) == 32


def test_product_iter_set():
    r1 = qit.Range(3)
    r2 = qit.Range(4)
    p = r1 * r2

    a = list(p)
    b = []
    for i in xrange(40):
        it = iter(p)
        it.set(i)
        l = list(it)
        if l:
            b.append(l[0])
    assert a == b


def test_uproduct_iterate():
    r1 = qit.Range(4)
    p = qit.Product((r1, r1), unordered=True)

    result = list(p.iterate())
    assert set(result) == set(
        [(1, 0),
         (2, 0),
         (3, 0),
         (2, 1),
         (3, 1),
         (3, 2)])
    assert len(result) == p.size

    p = qit.Product((r1, r1, r1), unordered=True)
    result = list(p.iterate())
    assert set(result) == set(
        [(2, 1, 0),
         (3, 1, 0),
         (3, 2, 0),
         (3, 2, 1),
         ])
    assert len(result) == p.size

    p = qit.Product((r1, r1, r1, r1), unordered=True)
    result = list(p.iterate())
    assert set(result) == set([(3, 2, 1, 0)])
    assert len(result) == p.size


def test_product_iter_copy():

    r1 = qit.Range(3)
    r2 = qit.Range(10)
    p = r1 * r2

    it = p.iterate()
    it2 = it.copy()

    assert list(it) == list(it2)


def test_uproduct_iter_copy():

    r1 = qit.Range(10)
    p = qit.Product((r1, r1), unordered=True)

    it = p.iterate()
    it2 = it.copy()

    assert list(it) == list(it2)


def test_uproduct_iter_set():
    r = qit.Range(10)
    p = qit.Product((r, r), unordered=True)

    a = list(p)
    it = iter(p)
    for i in xrange(p.size):
        it.set(i)
        l = list(it)
        assert a[i:] == l

    r = qit.Range(899)
    p = qit.Product((r, r), unordered=True)

    a = list(p)
    it = iter(p)
    x = 43211
    it.set(x)
    assert list(it) == a[x:]

    x = 403388
    it.set(x)
    assert list(it) == a[x:]


def test_named_product():

    r = qit.Range(10)
    a = qit.NamedProduct([("a", r), ("b", r * r)])
    result = list(a)[0]
    assert result.a == 0
    assert result.b == (0, 0)

    r = qit.Range(10)
    a = qit.NamedProduct([("a", r), ("b", r)], unordered=True)
    result = list(a)[0]
    assert result.a == 1
    assert result.b == 0


def test_product_name():
    r = qit.Range(10)
    p = qit.Product((r, r), name="TestProduct")
    assert p.name == "TestProduct"

    r = qit.Range(10)
    p = qit.Product((r, r), name="TestUProduct", unordered=True)
    assert p.name == "TestUProduct"

    p = qit.NamedProduct([("a", r), ("b", r * r)], name="TestNamedProduct")
    assert p.name == "TestNamedProduct"


def test_product_cache():
    def test_for_size(cache_size):
        r = qit.Range(10000)
        p = qit.Product((r, r), unordered=True, cache_size=cache_size)
        result = list(p.generate(1000))
        cache_pairs = (cache_size * (cache_size - 1)) / 2
        for i in xrange(100 / cache_pairs):
            values = set()
            for a, b in result[i * cache_pairs: (i + 1) * cache_pairs]:
                values.add(a)
                values.add(b)
            assert len(values) <= cache_pairs
    test_for_size(3)
    test_for_size(20)
