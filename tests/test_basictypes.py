from testutils import init
init()

from haydi.base import basictypes as hdt  # noqa
from haydi import ASet  # noqa


def test_aset_flags():
    ax = ASet(3, "a")
    assert not ax.filtered
    assert ax.step_jumps
    assert ax.strict


def test_compare_atoms():
    ax = ASet(3, "a")
    bx = ASet(5, "b")

    a1, a2, a3 = ax.all()
    b3 = bx.get(3)
    b4 = bx.get(4)

    assert hdt.compare(a1, a1) == 0
    assert hdt.compare(a2, a2) == 0
    assert hdt.compare(a3, a3) == 0
    assert hdt.compare(b3, b3) == 0
    assert hdt.compare(b4, b4) == 0

    assert hdt.compare(a1, a2) == -1
    assert hdt.compare(a1, a3) == -1
    assert hdt.compare(a2, a3) == -1
    assert hdt.compare(a1, b3) == -1
    assert hdt.compare(b3, b4) == -1
    assert hdt.compare(a3, b3) == -1

    assert hdt.compare(a2, a1) == 1
    assert hdt.compare(a3, a1) == 1
    assert hdt.compare(a3, a2) == 1
    assert hdt.compare(b3, a1) == 1
    assert hdt.compare(b4, b3) == 1
    assert hdt.compare(b3, a3) == 1


def test_compare_lists():
    ax = ASet(3, "a")
    bx = ASet(5, "b")

    a1, a2, a3 = ax.all()
    b3 = bx.get(3)
    b4 = bx.get(4)

    assert hdt.compare((), ()) == 0
    assert hdt.compare((a1,), (a1,)) == 0
    assert hdt.compare((a1, b3), (a1, b3)) == 0
    assert hdt.compare((a2, a2), (a2, a2)) == 0

    assert hdt.compare((a1,), (a2,)) == -1
    assert hdt.compare((a1, b3), (b3, a1)) == -1
    assert hdt.compare((a1, a1), (a1, a2)) == -1

    assert hdt.compare((a2,), (a1,)) == 1
    assert hdt.compare((a3, b3), (a1, a1)) == 1
    assert hdt.compare((a1, a3), (a1, a2)) == 1

    assert hdt.compare((a2,), (a1, a3)) == -1
    assert hdt.compare((a2,), (a3, a3)) == -1
    assert hdt.compare((b3, b4), ()) == 1
    assert hdt.compare((b3, b4), (a1,)) == 1


def test_compare_consts():
    hdt.compare(1, 2) == -1
    hdt.compare(2, 2) == 0
    hdt.compare(3, 2) == 1

    hdt.compare("a", "AAA") == -1
    hdt.compare("z", "z") == 0
    hdt.compare("z", "a") == 1

    hdt.compare(True, False) == -1
    hdt.compare(True, True) == 0
    hdt.compare(False, False) == 0
    hdt.compare(False, True) == 1

    hdt.compare(None, None) == 0


def test_compare_maps():
    ax = ASet(3, "a")
    bx = ASet(5, "b")

    a1, a2, a3 = ax.all()
    b3 = bx.get(3)
    b4 = bx.get(4)

    m1 = hdt.Map((
        (a1, a2), (a2, a1), (a3, a3)
    ))

    m2 = hdt.Map((
        (a1, a1), (a2, a2), (a3, a3)
    ))

    m3 = hdt.Map((
        (a1, a1), (b3, a1), (a3, a1)
    ))

    m4 = hdt.Map((
        (a1, a1), (b3, a1), (a3, a1), (b4, a1)
    ))

    assert hdt.compare(m1, m1) == 0
    assert hdt.compare(m2, m2) == 0
    assert hdt.compare(m1, m2) == 1
    assert hdt.compare(m2, m1) == -1

    assert hdt.compare(m3, m1) == -1
    assert hdt.compare(m1, m3) == 1
    assert hdt.compare(m1, m4) == -1
    assert hdt.compare(m4, m1) == 1
    assert hdt.compare(m3, m4) == -1
    assert hdt.compare(m4, m2) == 1


def test_compare2_atoms():
    ax = ASet(3, "a")

    a1, a2, a3 = ax.all()

    assert hdt.compare2(a1, {}, a1, {}) == 0
    assert hdt.compare2(a2, {}, a2, {}) == 0
    assert hdt.compare2(a2, {}, a2, {a2: a1}) == 1
    assert hdt.compare2(a1, {}, a2, {a1: a2}) == -1
    assert hdt.compare2(a1, {a1: a2}, a2, {a2: a1}) == 1


def test_compare2_tuples():
    ax = ASet(3, "a")
    bx = ASet(2, "b")

    a1, a2, a3 = ax.all()
    b1, b2 = bx.all()

    assert hdt.compare2((a1, b1), {}, (a1, b1), {}) == 0
    assert hdt.compare2((a1, b1), {}, (a2, b2), {}) == -1
    assert hdt.compare2((a1, b1), {b1: b2}, (a2, b2), {}) == -1
    assert hdt.compare2((a1, b1), {b1: b2, a1: a2}, (a2, b2), {}) == 0


def test_compare2_maps():
    ax = ASet(3, "a")
    bx = ASet(2, "b")

    a1, a2, a3 = ax.all()
    b1, b2 = bx.all()

    m1 = hdt.Map(
        [(a1, a1), (a2, a2), (a3, a3)])

    m2 = hdt.Map(
        [(a1, b1), (a2, b2), (a3, b1)])

    assert hdt.compare2(m1, {}, m1, {}) == 0
    assert hdt.compare2(m1, {}, m2, {}) == -1
    assert hdt.compare2(m1, {}, m1, {a1: a2, a2: a1}) == 0
    assert hdt.compare2(m2, {}, m2, {a1: a2, a2: a1}) == -1
    assert hdt.compare2(m2, {a1: a3, a3: a1}, m2, {a1: a2, a2: a1}) == -1


def test_compare_types():
    ax = ASet(3, "a")
    a1 = ax.get(1)

    assert hdt.compare(a1, 10) == -1
    assert hdt.compare(a1, "A") == -1
    assert hdt.compare(a1, (a1,)) == -1
    assert hdt.compare("B", hdt.Map((a1, a1))) == -1
    assert hdt.compare((a1,), "C") == 1


def test_collect_atoms():
    ax = ASet(3, "a")

    a = ax.get(0)
    b = ax.get(1)
    assert set((a,)) == set(hdt.collect_atoms(((a,), (a, a))))
    assert set((a, b)) == set(hdt.collect_atoms(((b,), (b, a))))
    assert set() == set(hdt.collect_atoms((1, 2, 3)))


def test_replace_atoms():
    ax = ASet(3, "a")

    a, b, c = ax.all()
    assert ((b,), (b, b)) == hdt.replace_atoms([[a], [a, a]], lambda x: b)
    assert ((c, a), ((c, c), a)) == hdt.replace_atoms(
        [[b, a], [[b, b], c]],
        lambda x: c if x == b else a)


def test_map_hash():
    ax = ASet(3, "a")
    m1 = hdt.Map((
        (ax.get(2), 11), ("b", 12)
    ))
    m2 = hdt.Map((
        (ax.get(2), 11), ("b", 12)
    ))
    assert m1 == m2
    assert hash(m1) == hash(m2)


def test_set_hash():
    ax = ASet(3, "a")
    m1 = hdt.Set((ax.get(2), 11))
    m2 = hdt.Set((ax.get(2), 11))
    assert m1 == m2
    assert hash(m1) == hash(m2)


def test_set_contains():
    s = hdt.Set(("a", "c", "b"))
    assert s.contains("a")
    assert not s.contains("d")


def test_map_conversion():
    m = hdt.Map((
        ("a", 11), ("b", 12)
    ))
    assert m.to_dict() == {"a": 11, "b": 12}


def test_set_conversion():
    s = hdt.Set(("a", "c", "b"))
    assert s.to_set() == {"a", "b", "c"}
    assert s.to_frozenset() == frozenset(("a", "b", "c"))
