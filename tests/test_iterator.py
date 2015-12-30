from testutils import init
init()

import qit

def test_iterator_first():
    assert 0 == qit.Range(10).iterate().first(-1)
    assert -1 == qit.Range(0).iterate().first(-1)

def test_iterator_reduce():
    expected = sum(range(10))
    result = qit.Range(10).iterate().reduce(lambda x, y: x + y)
    assert expected == result

    expected = max(range(10))
    result = qit.Range(10).iterate().reduce(max)
    assert expected == result
