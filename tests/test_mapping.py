from testutils import init
init()

import haydi as hd # noqa


def dict_to_sorted_items(d):
    return tuple(sorted(d.items()))


def check_eq_list_of_dicts(list1, list2):
    s1 = map(dict_to_sorted_items, list1)
    s2 = map(dict_to_sorted_items, list1)
    assert list(s1) == list(s2)


def test_mapping_int_int():
    r = hd.Range(2)
    m = hd.Mapping(r, r)
    result = list(m)
    check_eq_list_of_dicts(result,
                           [{0: 0, 1: 0}, {0: 1, 1: 0},
                            {0: 0, 1: 1}, {0: 1, 1: 1}])
    assert m.size == 4


def test_mapping_size():
    m = hd.Mapping(hd.Range(10), hd.Range(2))
    assert m.size == 1024


def test_mapping_generate():
    r1 = hd.Range(2)
    p = hd.Mapping(r1, r1)

    result = list(p.generate(200))
    for r in result:
        assert len(r) == 2
        assert r[0] == 0 or r[0] == 1
        assert r[1] == 0 or r[1] == 1


def test_mapping_name():
    r = hd.Range(10)
    m = hd.Mapping(r, r, name="TestMapping")
    assert m.name == "TestMapping"


def test_mapping_exact_size():
    d1 = hd.Range(3)
    d2 = hd.Range(3).filter(lambda x: True)
    assert not hd.Mapping(d1, d2).exact_size
    assert hd.Mapping(d1, d1).exact_size


def test_mapping_set():
    d1 = hd.Range(3)
    d2 = hd.Range(4)
    m = hd.Mapping(d1, d2)

    a = list(m)
    for i in xrange(70):
        it = m.create_iter(i)
        assert list(it) == a[i:]
