
from testutils import init
init()

import qit
import itertools

def test_sequence_iterate():
    s = qit.Sequence(qit.Range(3), 2)
    result = list(s)
    expected = list(itertools.product(range(3), range(3)))
    assert set(result) == set(expected)
    assert len(result) == len(expected)
    s.size == len(expected)

def test_sequence_iterate_empty():
    assert list(qit.Sequence(qit.Range(3), 0)) == [()]

def test_sequence_generate():
    s = qit.Sequence(qit.Range(3), 5)
    result = list(s.generate(200))
    assert len(result)
    for r in result:
        assert len(r) == 5
        for x in r:
            assert 0 <=  x < 3
