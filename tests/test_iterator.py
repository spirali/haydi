from testutils import init
init()

import qit  # noqa


def test_iterator_first():
    assert 0 == qit.Range(10).iterate().first(lambda x: True, -1).run()
    assert -1 == qit.Range(0).iterate().first(lambda x: True, -1).run()


def test_iterator_reduce():
    expected = sum(range(10))
    result = qit.Range(10).iterate().reduce(lambda x, y: x + y).run()
    assert expected == result

    expected = max(range(10))
    result = qit.Range(10).iterate().reduce(max).run()
    assert expected == result
