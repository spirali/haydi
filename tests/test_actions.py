from testutils import init
init()

import qit

def test_all_max():
    f = [ ("A", 10), ("A", 10), ("B", 20), ("C", 10), ("D", 20), ("E", 5) ]
    v = qit.Values(f)
    result = v.iterate().all_max(lambda x: x[1])
    assert result == [ ("B", 20), ("D", 20) ]

    result = v.iterate().filter(lambda x: x[1] < 20).all_max(lambda x: x[1])
    assert result == [ ("A", 10), ("A", 10), ("C", 10) ]
