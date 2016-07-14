from testutils import init
init()

import qit  # noqa


def dict_to_sorted_items(d):
    return tuple(sorted(d.items()))


def check_eq_list_of_dicts(list1, list2):
    s1 = map(dict_to_sorted_items, list1)
    s2 = map(dict_to_sorted_items, list1)
    assert list(s1) == list(s2)


def test_mapping_int_int():
    r = qit.Range(2)
    m = qit.Mapping(r, r)
    result = list(m)
    check_eq_list_of_dicts(result,
                           [{0: 0, 1: 0}, {0: 1, 1: 0},
                            {0: 0, 1: 1}, {0: 1, 1: 1}])
    assert m.size == 4


def test_mapping_size():
    m = qit.Mapping(qit.Range(10), qit.Range(2))
    assert m.size == 1024


def test_mapping_generate():
    r1 = qit.Range(2)
    p = qit.Mapping(r1, r1)

    result = list(p.generate(200))
    for r in result:
        assert len(r) == 2
        assert r[0] == 0 or r[0] == 1
        assert r[1] == 0 or r[1] == 1


def test_mapping_copy():
    r1 = qit.Range(4)
    r2 = qit.Range(3)
    p = qit.Mapping(r1, r2)

    it = iter(p)
    it2 = it.copy()

    assert list(it) == list(it2)


def test_mapping_name():
    r = qit.Range(10)
    m = qit.Mapping(r, r, name="TestMapping")
    assert m.name == "TestMapping"


def test_mapping_exact_size():
    d1 = qit.Range(3)
    d2 = qit.Range(3).filter(lambda x: True)
    assert not qit.Mapping(d1, d2).exact_size
    assert qit.Mapping(d1, d1).exact_size


def test_mapping_set():
    d1 = qit.Range(3)
    d2 = qit.Range(4)
    m = qit.Mapping(d1, d2)

    a = list(m)
    for i in xrange(65):
        it = iter(m)
        it.set(i)
        assert list(it) == a[i:]
