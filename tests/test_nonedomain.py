import haydi as hd


def test_none_flags():
    a = hd.NoneDomain()
    assert not a.filtered
    assert a.step_jumps
    assert a.strict


def test_none_iter():
    a = hd.NoneDomain()

    assert list(a) == [None]
    assert list(a.cnfs()) == [None]
