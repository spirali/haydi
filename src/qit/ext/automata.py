
from qit.base.graph import Graph


def transition_fn_to_graph(
        mapping, rule_to_arc_fn, init_state=None, final_states=()):
    graph = Graph()
    for key, value in mapping.items():
        state1, label, state2 = rule_to_arc_fn(key, value)
        node1 = graph.node(state1)
        node1.label = str(state1)
        node2 = graph.node(state2)
        node1.add_arc(node2, str(label))
    graph.merge_arcs(lambda a, b: a + ";" + b)

    if init_state is not None:
        node = graph.node(init_state)
        node.fillcolor = "gray"
    for fs in final_states:
        node = graph.node(fs)
        node.shape = "doublecircle"
    return graph
