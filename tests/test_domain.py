import haydi as hd


def test_domain_map():

    def fn(x):
        return (x + 1) * 10

    d = hd.Range(5).map(fn)
    result = list(d)
    assert result == [10, 20, 30, 40, 50]

    result = list(d.generate(10))
    for x in result:
        assert x in [10, 20, 30, 40, 50]

    result = list(hd.Product((d, d), unordered=True))
    assert set(result) == {(20, 10), (30, 10), (40, 10), (50, 10), (30, 20),
                           (40, 20), (50, 20), (40, 30), (50, 30), (50, 40)}
    assert d.size == 5
    assert not d.filtered
    assert d.step_jumps


def test_domain_filter():

    def fn(x):
        return x > 2 and x < 5

    r = hd.Range(6)
    d = r.filter(fn)
    result = list(d)
    assert result == [3, 4]

    result = list(d.generate(5))
    assert len(result) == 5
    for x in result:
        assert x in [3, 4]

    assert d.filtered
    assert not r.filtered
    assert d.size == 6

    p = d * d
    result = list(p)
    assert set(result) == {(3, 3), (4, 3), (3, 4), (4, 4)}

    assert p.filtered
    assert not (r * r).filtered

    assert hd.Sequences(d, 2).filtered
    assert not hd.Sequences(r, 2).filtered

    assert not hd.Mappings(d, r).filtered
    assert hd.Mappings(r, d).filtered
    assert not hd.Mappings(r, r).filtered

    assert hd.Product((d, d), unordered=True).filtered
    assert not hd.Product((r, r), unordered=True).filtered

    result = list(hd.Product((d, d), unordered=True))
    assert set(result) == {(4, 3)}


def test_domain_repr():
    domain = hd.Values([])
    assert repr(domain) == "<Values size=0 {}>"

    domain = hd.Values(["a"])
    assert repr(domain) == "<Values size=1 {'a'}>"

    domain = hd.Values(["a" * 1000])
    assert repr(domain) == "<Values size=1 {'aaaaaaaaa ... aaaaaaaa'}>"

    domain = hd.Values(["a", "b"])
    assert repr(domain) == "<Values size=2 {'a', 'b'}>"

    domain = hd.Values(["a" * 1000, "b" * 1000])
    assert repr(domain) == \
        "<Values size=2 {'aaaaaaaaa ... aaaaaaaa', " \
        "'bbbbbbbb ... bbbbbbb'}>"

    domain = hd.Values(["a", "b"] * 1000)
    assert repr(domain) == \
        "<Values size=2000 {'a', 'b', 'a', 'b', 'a', ...}>"

    domain = hd.Values(["a" * 1000, "b" * 1000] * 1000)
    assert repr(domain) == \
        "<Values size=2000 {'aaaaaaaaa ... aaaaaaaa', " \
        "'bbbbbbbb ... bbbbbbb', ...}>"

    domain = hd.Range(2) * hd.Values(["a", "b", "c"]) * hd.Values(["x", "y"])
    assert repr(domain) == \
        ("<Product size=12 {(0, 'a', 'x'), (0, 'a', 'y'), "
         "(0, 'b', 'x'), ...}>")

    domain = hd.Values([], name="MyName")
    assert repr(domain) == "<MyName size=0 {}>"


def test_generate_one_transformed_domain():
    r1 = hd.Range(10).filter(lambda x: x == 7 or x == 1)
    r2 = hd.Range(3).map(lambda x: x * 10)
    p = r1 * r2
    expected = {(1, 0), (1, 10), (1, 20), (7, 0), (7, 10), (7, 20)}
    assert set(p) == expected

    result = p.generate(160)
    assert set(result) == expected
