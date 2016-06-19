from testutils import init
init()

import qit  # noqa


def test_lts_basic():
    class MyLTS(qit.DLTS):
        def step(self, state, action):
            if action == 0:
                return state * 10
            elif action == 1 and state % 2 == 1:
                return state + 1
            elif action == 2 and state % 2 == 1:
                return state + 2
            elif action == 3:
                return -state

    s = MyLTS(qit.Range(4))
    result = list(s.bfs(10, 0))
    assert result == [10]

    result = list(s.bfs(10, 1))
    assert set(result) == set([10, 100, -10])

    result = list(s.bfs(11, 2))
    assert set(result) == set([11, 110, 12, 13, -11, -110, -10,
                               -9, 130, 14, 15, -13, 120, -12, 1100])


def test_lts_product():
    class MyLTS1(qit.DLTS):
        def __init__(self):
            qit.DLTS.__init__(self, qit.Range(1))

        def step(self, state, action):
            assert action == 0
            return state + 1

    class MyLTS2(qit.DLTS):
        def __init__(self):
            qit.DLTS.__init__(self, qit.Range(1))

        def step(self, state, action):
            assert action == 0
            return state + 2

    s = MyLTS1() * MyLTS2()

    result = list(s.bfs((3, 7), 2))
    assert result == [(3, 7), (4, 9), (5, 11)]


def test_lts_graph():
    class MyLTS(qit.DLTS):
        def __init__(self):
            qit.DLTS.__init__(self, qit.Range(2))

        def step(self, state, action):
            if action == 0:
                return state + 1
            if action == 1:
                return state - 1

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
