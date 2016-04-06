from testutils import init
init()

import qit  # noqa


def test_domain_map():

    def fn(x):
        return (x + 1) * 10

    d = qit.Range(5).map(fn)
    result = list(d)
    assert result == [10, 20, 30, 40, 50]

    result = list(d.generate(10))
    for x in result:
        assert x in [10, 20, 30, 40, 50]
