import haydi as hd
from haydi.base import cnf as hdc
from haydi.base import basictypes as hdt
from haydi import USet


def test_atom_is_canonical():
    ax = USet(3, "a")

    c = [a for a in ax.all() if hdc.is_canonical(a)]
    assert c == [ax.get(0)]


def test_const_is_canonical():

    assert hdc.is_canonical(0)
    assert hdc.is_canonical(1)
    assert hdc.is_canonical(2)

    assert hdc.is_canonical("data")

    assert hdc.is_canonical(True)
    assert hdc.is_canonical(False)

    assert hdc.is_canonical(None)


def test_product_is_canonical():

    ax = USet(5, "a")
    bx = USet(2, "b")
    cx = USet(1, "c")

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
    ax = USet(2, "a")
    a1, a2 = ax.all()
    bx = USet(2, "b")
    b1, b2 = bx.all()

    ms = hd.Mappings(ax, bx)
    c = [item for item in ms if hdc.is_canonical(item)]

    m1 = hd.Map(((a1, b1), (a2, b1)))
    m2 = hd.Map(((a1, b1), (a2, b2)))
    assert hdt.compare_sequence([m1, m2], c) == 0

    ms = hd.Mappings(ax, ax)
    c = [item for item in ms if hdc.is_canonical(item)]
    m1 = hd.Map(((a1, a1), (a2, a1)))
    m2 = hd.Map(((a1, a1), (a2, a2)))
    m3 = hd.Map(((a1, a2), (a2, a1)))
    assert hdt.compare_sequence([m1, m2, m3], c) == 0


def test_candidates():
    ax = USet(3, "a")
    a0, a1, a2 = ax.all()
    bx = USet(5, "b")
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
    assert set(result) == {(a0, a1), (a1, a0), (a1, a2), (a2, a1)}

    result = hdc.create_candidates((a1, a2), {ax: 2})
    assert set(result) == {(a0, a1), (a1, a0), (a0, a2), (a2, a0), (a1, a2),
                           (a2, a1)}

    result = hdc.create_candidates((a1, a2), {ax: 3})
    assert set(result) == {(a0, a1), (a1, a0), (a0, a2), (a2, a0), (a1, a2),
                           (a2, a1)}

    result = hdc.create_candidates((b0, b1), {bx: 2})
    assert set(result) == {(b0, b1), (b0, b1), (b0, b2), (b1, b0), (b1, b2),
                           (b2, b0), (b2, b1), (b2, b3), (b3, b2)}

    result = hdc.create_candidates((a0, b0), {ax: 1, bx: 2})
    assert set(result) == {(a0, b0), (a0, b1), (a0, b2), (a1, b0), (a1, b1),
                           (a1, b2)}


def test_canonical_product():
    ax = USet(3, "a")
    a0, a1, a2 = ax.all()

    bx = USet(2, "b")
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
    ax = USet(3, "a")
    a0, a1, a2 = ax.all()

    bx = USet(2, "b")
    b0, b1 = bx.all()

    m1 = hd.Map([(b0, b0), (b1, b0)])
    m2 = hd.Map([(b0, b0), (b1, b1)])
    m3 = hd.Map([(b0, b1), (b1, b0)])
    result = list(hd.Mappings(bx, bx).create_cn_iter())
    assert result == [m1, m2, m3]

    m1 = hd.Map([(b0, a0), (b1, a0)])
    m2 = hd.Map([(b0, a0), (b1, a1)])
    result = list(hd.Mappings(bx, ax).create_cn_iter())
    assert result == [m1, m2]

    m1 = hd.Map([(0, a0), (1, a0)])
    m2 = hd.Map([(0, a0), (1, a1)])
    result = list(hd.Mappings(hd.Range(2), ax).create_cn_iter())
    assert result == [m1, m2]

    m1 = hd.Map([(0, b0), (1, b0)])
    m2 = hd.Map([(0, b0), (1, b1)])
    result = list(hd.Mappings(hd.Range(2), bx).create_cn_iter())
    assert result == [m1, m2]


def bf_check(domain):
    result = list(domain.create_cn_iter())
    hdc.sort(result)
    bf = [x for x in domain if hdc.is_canonical_naive(x)]
    hdc.sort(bf)
    assert result == bf


def test_cannonical_prod_map():
    ax = USet(3, "a")
    bx = USet(2, "b")

    pb = bx * bx
    pab = ax * bx

    m = hd.Mappings(bx, pb)
    bf_check(m)

    m = hd.Mappings(pb, bx)
    bf_check(m)

    m = hd.Mappings(pb, pb)
    bf_check(m)

    m = hd.Mappings(pab, bx)
    bf_check(m)


def test_canonical_map_prod():
    ax = USet(3, "a")
    bx = USet(2, "b")
    cx = USet(1, "b")

    m1 = hd.Mappings(bx, cx)
    m2 = hd.Mappings(ax, ax)
    m3 = hd.Mappings(ax, bx)

    bf_check(m1 * bx)
    bf_check(m1 * cx)
    bf_check(bx * m1)
    bf_check(cx * m1)
    bf_check(m1 * m1)

    bf_check(m3 * m3)
    bf_check(m3 * m3 * m3)
    bf_check(m2 * m3)


def test_canonical_map_map():
    ax = USet(2, "a")
    bx = USet(2, "b")

    m1 = hd.Mappings(ax, bx)
    m2 = hd.Mappings(ax, ax)

    m = hd.Mappings(m1, m2)
    bf_check(m)

    m = hd.Mappings(m1, m1)
    bf_check(m)

    m = hd.Mappings(m2, m1)
    bf_check(m)


def test_canonical_sequence():
    ax = USet(2, "a")

    s = hd.Sequences(ax, 0, 4)
    bf_check(s)

    s = hd.Sequences(ax * ax, 0, 4)
    bf_check(s)


def test_canonical_sets():
    ax = USet(4, "a")
    s = hd.Subsets(ax, 2)
    bf_check(s)
    s = hd.Subsets(ax, 0, 2)
    bf_check(s)


def test_canonize():
    ax = USet(1000, "a")
    a0 = ax.get(0)
    a1 = ax.get(1)
    a2 = ax.get(2)
    a900 = ax.get(900)

    bx = USet(2, "b")
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
    ax = USet(3, "a")
    a0, a1, a2 = ax
    assert set(hd.expand(a0)) == {a1, a2, a0}
    assert set(hd.expand(a1)) == {a1, a2, a0}
    assert set(hd.expand(a2)) == {a1, a2, a0}

    assert set(hd.expand((a1, a1))) == {(a0, a0), (a1, a1), (a2, a2)}
    assert set(hd.expand((a0, a0))) == {(a0, a0), (a1, a1), (a2, a2)}

    assert set(hd.expand((a1, a2))) == {(a0, a1), (a0, a2), (a1, a0), (a1, a2),
                                        (a2, a0), (a2, a1)}


def test_is_isomoprhic():

    assert hd.is_isomorphic(0, 0)
    assert not hd.is_isomorphic(0, 1)
    assert not hd.is_isomorphic("a", 1)

    a0, a1 = USet(2, "a")
    b0, b1 = USet(2, "b")

    assert not hd.is_isomorphic(a0, b0)
    assert not hd.is_isomorphic(a1, b0)
    assert hd.is_isomorphic(a0, a1)
    assert hd.is_isomorphic(b0, b1)

    x = (a0, a1)
    y = (a1, a0)
    z = (a0, a0)
    w = (b0, a0)

    assert hd.is_isomorphic(x, y)
    assert not hd.is_isomorphic(x, z)
    assert not hd.is_isomorphic(x, w)
