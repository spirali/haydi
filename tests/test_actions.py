from testutils import init
init()

import qit  # noqa


def test_all_max():
    f = [("A", 10), ("A", 10), ("B", 20), ("C", 10), ("D", 20), ("E", 5)]
    v = qit.Values(f)
    result = v.iterate().best(lambda x: x[1]).run()
    assert result == [("B", 20), ("D", 20)]

    result = list(v.iterate().filter(lambda x: x[1] < 20).best(lambda x: x[1]))
    assert result == [("A", 10), ("A", 10), ("C", 10)]
