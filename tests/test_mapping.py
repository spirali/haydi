from testutils import init
init()

import haydi as hd # noqa


def test_mapping_strict():
    r = hd.Range(2)
    s = hd.Mappings(r, r)
    assert s.strict


def test_mapping_int_int():
    r = hd.Range(2)
    m = hd.Mappings(r, r)
    result = list(m)

    e1 = hd.Map(((0, 0), (1, 0)))
    e2 = hd.Map(((0, 0), (1, 1)))
    e3 = hd.Map(((0, 1), (1, 0)))
    e4 = hd.Map(((0, 1), (1, 1)))

    assert result == [e1, e2, e3, e4]
    assert m.size == 4


def test_mapping_size():
    m = hd.Mappings(hd.Range(10), hd.Range(2))
    assert m.size == 1024


def test_mapping_generate():
    r1 = hd.Range(2)
    p = hd.Mappings(r1, r1)

    result = list(p.generate(200))
    for r in result:
        assert len(r) == 2
        assert r.get(0) == 0 or r.get(0) == 1
        assert r.get(1) == 0 or r.get(1) == 1


def test_mapping_name():
    r = hd.Range(10)
    m = hd.Mappings(r, r, name="TestMappings")
    assert m.name == "TestMappings"


def test_mapping_flags():
    d1 = hd.Range(3)
    d2 = hd.Range(3).filter(lambda x: True)
    assert hd.Mappings(d1, d2).filtered
    assert not hd.Mappings(d1, d1).filtered


def test_mapping_set():
    d1 = hd.Range(3)
    d2 = hd.Range(4)
    m = hd.Mappings(d1, d2)

    a = list(m)
    for i in xrange(70):
        it = m.create_iter(i)
        assert list(it) == a[i:]


def test_mapping_to_values():
    a = hd.Range(5)
    b = hd.Range(6)
    c = hd.Mappings(a, b)

    v = c.to_values()

    assert isinstance(v, hd.Values)
    assert list(c) == list(v)


def test_mapping_to_values_maxsize():
    a = hd.Range(5)
    b = hd.Range(6)
    c = hd.Mappings(a, b)

    v = c.to_values(max_size=6)

    assert isinstance(v, hd.Mappings)
    assert isinstance(v.key_domain, hd.Values)
    assert isinstance(v.value_domain, hd.Values)
    assert list(c) == list(v)


def test_mappings_map_class():
    r = hd.Range(2)
    m = hd.Mappings(r, r, map_class=tuple)
    assert m.strict
    result = set(m)
    expected = set([((0, 0), (1, 0)),
                    ((0, 0), (1, 1)),
                    ((0, 1), (1, 0)),
                    ((0, 1), (1, 1))])
    assert result == expected

    m = hd.Mappings(r, r, map_class=dict)
    assert not m.strict

