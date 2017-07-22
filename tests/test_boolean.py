from testutils import init
init()

import haydi as hd  # noqa


def test_bool_flags():
    a = hd.Boolean()
    assert not a.filtered
    assert a.step_jumps
    assert a.strict


def test_bool_iter():
    a = hd.Boolean()

    assert list(a) == [False, True]
    assert list(a.cnfs()) == [False, True]
