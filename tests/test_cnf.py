from testutils import init
init()

import haydi as hd # noqa
from haydi.base import canonicals as hdc # noqa
from haydi.base import basictypes as hdt # noqa
from haydi import ASet # noqa


def test_atom_is_canonical():
    ax = ASet(3, "a")

    c = [a for a in ax.all() if hdc.is_canonical(a)]
    assert c == [ax.get(0)]


def test_product_is_canonical():

    ax = ASet(5, "a")
    bx = ASet(2, "b")
    cx = ASet(1, "c")

    a1 = ax.get(0)
    a2 = ax.get(1)
    b1 = bx.get(0)
    c1 = cx.get(0)

    p = ax * ax
    c = [a for a in p if hdc.is_canonical(a)]
    assert c == [(a1, a1), (a1, a2)]

    p = ax * bx
    c = [a for a in p if hdc.is_canonical(a)]
    assert c == [(a1, b1)]

    p = cx * cx
    c = [a for a in p if hdc.is_canonical(a)]
    assert c == [(c1, c1)]


def test_map_is_canonical():
    ax = ASet(2, "a")
    a1, a2 = ax.all()
    bx = ASet(2, "b")
    b1, b2 = bx.all()

    ms = hd.Mapping(ax, bx)
    c = [item for item in ms if hdc.is_canonical(item)]

    m1 = hd.Map(((a1, b1), (a2, b1)))
    m2 = hd.Map(((a1, b1), (a2, b2)))
    assert hdt.compare_sequence([m1, m2], c) == 0

    ms = hd.Mapping(ax, ax)
    c = [item for item in ms if hdc.is_canonical(item)]
    m1 = hd.Map(((a1, a1), (a2, a1)))
    m2 = hd.Map(((a1, a1), (a2, a2)))
    m3 = hd.Map(((a1, a2), (a2, a1)))
    assert hdt.compare_sequence([m1, m2, m3], c) == 0


def test_candidates():
    ax = ASet(3, "a")
    a0, a1, a2 = ax.all()
    bx = ASet(5, "b")
    b0, b1, b2, b3, b5 = bx.all()

    result = hdc.create_candidates(a0, {})
    assert list(result) == [a0]

    result = hdc.create_candidates(a0, {bx: 1})
    assert list(result) == [a0]

    result = hdc.create_candidates(a0, {ax: 1})
    assert list(result) == [a0, a1]

    result = hdc.create_candidates(a0, {ax: 2})
    assert list(result) == [a0, a1, a2]

    result = hdc.create_candidates(a0, {ax: 3})
    assert list(result) == [a0, a1, a2]

    result = hdc.create_candidates((a0, a1), {})
    assert list(result) == [(a0, a1), (a1, a0)]

    result = hdc.create_candidates((a0, a1), {bx: 1})
    assert list(result) == [(a0, a1), (a1, a0)]

    result = hdc.create_candidates((a0, a1), {ax: 1})
    assert set(result) == set([(a0, a1), (a1, a0),
                               (a1, a2), (a2, a1)])

    result = hdc.create_candidates((a1, a2), {ax: 2})
    assert set(result) == set([(a0, a1), (a1, a0),
                               (a0, a2), (a2, a0),
                               (a1, a2), (a2, a1)])

    result = hdc.create_candidates((a1, a2), {ax: 3})
    assert set(result) == set([(a0, a1), (a1, a0),
                               (a0, a2), (a2, a0),
                               (a1, a2), (a2, a1)])

    result = hdc.create_candidates((b0, b1), {bx: 2})
    assert set(result) == set([(b0, b1), (b0, b1), (b0, b2),
                               (b1, b0), (b1, b2),
                               (b2, b0), (b2, b1),
                               (b2, b3), (b3, b2)])

    result = hdc.create_candidates((a0, b0), {ax: 1, bx: 2})
    assert set(result) == set([(a0, b0), (a0, b1), (a0, b2),
                               (a1, b0), (a1, b1), (a1, b2)])


def test_canonical_product():
    ax = ASet(3, "a")
    a0, a1, a2 = ax.all()

    bx = ASet(2, "b")
    b0, b1 = bx.all()

    result = list(hd.Product((ax,)).create_cn_iter())
    assert result == [(a0,)]

    result = list((ax * ax).create_cn_iter())
    assert result == [(a0, a0), (a0, a1)]

    result = list((ax * ax * ax).create_cn_iter())
    assert result == [(a0, a0, a0), (a0, a0, a1),
                      (a0, a1, a0), (a0, a1, a1), (a0, a1, a2)]

    result = list((bx * bx * bx).create_cn_iter())
    assert result == [(b0, b0, b0), (b0, b0, b1),
                      (b0, b1, b0), (b0, b1, b1)]

    result = list((ax * bx * bx).create_cn_iter())
    assert result == [(a0, b0, b0), (a0, b0, b1)]


def test_canonical_mapping():
    ax = ASet(3, "a")
    a0, a1, a2 = ax.all()

    bx = ASet(2, "b")
    b0, b1 = bx.all()

    m1 = hd.Map([(b0, b0), (b1, b0)])
    m2 = hd.Map([(b0, b0), (b1, b1)])
    m3 = hd.Map([(b0, b1), (b1, b0)])
    result = list(hd.Mapping(bx, bx).create_cn_iter())
    assert result == [m1, m2, m3]

    m1 = hd.Map([(b0, a0), (b1, a0)])
    m2 = hd.Map([(b0, a0), (b1, a1)])
    result = list(hd.Mapping(bx, ax).create_cn_iter())
    assert result == [m1, m2]

    m1 = hd.Map([(0, a0), (1, a0)])
    m2 = hd.Map([(0, a0), (1, a1)])
    result = list(hd.Mapping(hd.Range(2), ax).create_cn_iter())
    assert result == [m1, m2]

    m1 = hd.Map([(0, b0), (1, b0)])
    m2 = hd.Map([(0, b0), (1, b1)])
    result = list(hd.Mapping(hd.Range(2), bx).create_cn_iter())
    assert result == [m1, m2]


def bf_check(domain):
    result = list(domain.create_cn_iter())
    hdc.sort(result)
    bf = [x for x in domain if hdc.is_canonical_naive(x)]
    hdc.sort(bf)
    assert result == bf


def test_cannonical_prod_map():
    ax = ASet(3, "a")
    bx = ASet(2, "b")

    pb = bx * bx
    pab = ax * bx

    m = hd.Mapping(bx, pb)
    bf_check(m)

    m = hd.Mapping(pb, bx)
    bf_check(m)

    m = hd.Mapping(pb, pb)
    bf_check(m)

    m = hd.Mapping(pab, bx)
    bf_check(m)


def test_canonical_map_prod():
    ax = ASet(3, "a")
    bx = ASet(2, "b")
    cx = ASet(1, "b")

    m1 = hd.Mapping(bx, cx)
    m2 = hd.Mapping(ax, ax)
    m3 = hd.Mapping(ax, bx)

    bf_check(m1 * bx)
    bf_check(m1 * cx)
    bf_check(bx * m1)
    bf_check(cx * m1)
    bf_check(m1 * m1)

    bf_check(m3 * m3)
    bf_check(m3 * m3 * m3)
    bf_check(m2 * m3)


def test_canonical_map_map():
    ax = ASet(2, "a")
    bx = ASet(2, "b")

    m1 = hd.Mapping(ax, bx)
    m2 = hd.Mapping(ax, ax)

    m = hd.Mapping(m1, m2)
    bf_check(m)

    m = hd.Mapping(m1, m1)
    bf_check(m)

    m = hd.Mapping(m2, m1)
    bf_check(m)


def test_canonical_sequence():
    ax = ASet(2, "a")

    s = hd.Sequence(ax, 0, 4)
    bf_check(s)

    s = hd.Sequence(ax * ax, 0, 4)
    bf_check(s)


def test_canonical_sets():
    ax = ASet(4, "a")
    s = hd.Subsets(ax, 2)
    bf_check(s)
    s = hd.Subsets(ax, 0, 2)
    bf_check(s)


def test_canonize():
    ax = ASet(1000, "a")
    a0 = ax.get(0)
    a1 = ax.get(1)
    a2 = ax.get(2)
    a900 = ax.get(900)

    bx = ASet(2, "b")
    b0 = bx.get(0)
    b1 = bx.get(1)

    assert hd.canonize(a0) == a0
    assert hd.canonize(a1) == a0
    assert hd.canonize(a900) == a0

    assert hd.canonize((a900, a0, a1, a1, 100)) == (a0, a1, a2, a2, 100)
    assert hd.canonize((a0, b1, b1)) == (a0, b0, b0)
    assert hd.canonize((a0, b0, b1)) == (a0, b0, b1)
    assert hd.canonize((a0, b1, b0)) == (a0, b0, b1)
    assert hd.canonize((a900, b1, b0)) == (a0, b0, b1)

def test_expand():
    assert hd.expand(10) == [10]
    ax = ASet(3, "a")
    a0, a1, a2 = ax
    assert set(hd.expand(a0)) == set((a1, a2, a0))
    assert set(hd.expand(a1)) == set((a1, a2, a0))
    assert set(hd.expand(a2)) == set((a1, a2, a0))

    assert set(hd.expand((a1, a1))) == set(((a0, a0), (a1, a1), (a2, a2)))
    assert set(hd.expand((a0, a0))) == set(((a0, a0), (a1, a1), (a2, a2)))

    assert set(hd.expand((a1, a2))) == set(((a0, a1), (a0, a2), (a1, a0),
                                            (a1, a2), (a2, a0), (a2, a1)))
