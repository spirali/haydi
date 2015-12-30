from testutils import init
init()

import qit


def test_values_iterate():

    a = qit.Values(["a", "b", "c"])

    assert a.size == 3
    assert list(a.iterate()) == [ "a", "b", "c"]
    for x in a.generate(100):
        assert x in ("a", "b", "c")

    b = qit.Values([])
    assert b.size == 0
    assert list(b.iterate()) == []
