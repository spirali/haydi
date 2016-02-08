from testutils import init
init()

import qit

def test_lts_basic():
    class MyLTS(qit.LTS):
        def step(self, state):
            result = []
            result.append(state * 10)
            if state % 2 == 1:
                result.append(state + 1)
                result.append(state + 2)
            result.append(-state)
            return result

    s = MyLTS()
    result = list(s.bfs(10, 0))
    assert result == [10]

    result = list(s.bfs(10, 1))
    assert set(result) == set([10, 100, -10])

    result = list(s.bfs(11, 2))
    assert set(result) == set([11, 110, 12, 13, -11, -110, -10,
                               -9, 130, 14, 15, -13, 120, -12, 1100])

def test_lts_product():
    class MyLTS1(qit.LTS):
        def step(self, state):
            return [state+1]

    class MyLTS2(qit.LTS):
        def step(self, state):
            return [state+2]

    s = MyLTS1() * MyLTS2()

    result = list(s.bfs((3, 7), 2))
    assert result == [(3,7), (4,9), (5, 11)]
