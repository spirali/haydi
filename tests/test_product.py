from testutils import init
init()

import qit
import itertools

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
