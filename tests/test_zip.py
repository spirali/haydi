import itertools

from testutils import init
init()

import haydi as hd # noqa


def test_zip_range_iterate():
    d1 = hd.Range(1, 3)
    d2 = hd.Range(4, 5)
    d3 = hd.Range(6, 7)

    expected = zip(d1, d2, d3)
    result = list(hd.Zip((d1, d2, d3)))
    assert expected == result


def test_zip_range_generate():
    d1 = hd.Range(1, 10)
    d2 = hd.Range(20, 30)

    result = list(hd.Zip((d1, d2)).generate(10))
    for v in result:
        assert v[0] >= 1
        assert v[0] < 10
        assert v[1] >= 20
        assert v[1] < 30


def test_zip_range_size():
    d1 = hd.Range(1, 2)
    d2 = hd.Range(1, 100)

    z = hd.Zip((d1, d2))
    assert z.size == d1.size

    result = list(z)
    assert len(result) == d1.size


def test_zip_product_iterate():
    a = hd.Range(1, 3)
    b = hd.Values(["a", "b"])
    c = a * b

    result = list(hd.Zip((hd.Range(4), c)))
    assert result == zip(xrange(4), itertools.product(xrange(1, 3),
                                                      ["a", "b"]))


def test_zip_steps_attributes():
    r = hd.Range(5)
    v = hd.Values(("A", "B", "C"))

    z = hd.Zip((r, v))

    assert z.step_jumps
    assert not z.filtered
    assert not z.strict

    r2 = r.filter(lambda x: x % 2 == 0)
    z2 = hd.Zip((r2, v))

    assert not z2.step_jumps
    assert z2.filtered
