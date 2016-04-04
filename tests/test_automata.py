from testutils import init
init()

from qit.ext.automata import transition_fn_to_graph  # noqa


def test_automata_tfn_to_graph():
    automaton = {
        (0, "a", 1): (1, ()),
        (0, "b", 1): (0, (0, 0)),
        (1, "a", 1): (1, (0,)),
        (1, "b", 1): (1, (0, 1)),
    }

    def rule_to_arc((q, a, s), (nq, ns)):
        return (q, "{},{},{}".format(a, s, ns), nq)

    g = transition_fn_to_graph(automaton, rule_to_arc)
    assert g.size == 2
    n = g.node(0)
    assert len(n.arcs) == 2
    n = g.node(1)
    assert len(n.arcs) == 1
