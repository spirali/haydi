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


def test_lts_graph():
    class MyLTS(qit.LTS):

        def step(self, state):
            return [ state + 1, state - 1]

    s = MyLTS()
    g = s.make_graph(10, 2)

    assert g.size == 5

    node = g.node(10)
    assert len(node.arcs) == 2
    assert node.arcs[0].node == g.node(11)
    assert node.arcs[1].node == g.node(9)

    node = g.node(9)
    assert len(node.arcs) == 2
    assert node.arcs[0].node == g.node(10)
    assert node.arcs[1].node == g.node(8)

    node = g.node(8)
    assert len(node.arcs) == 0

    node = g.node(11)
    assert len(node.arcs) == 2
    assert node.arcs[0].node == g.node(12)
    assert node.arcs[1].node == g.node(10)

    node = g.node(12)
    assert len(node.arcs) == 0
