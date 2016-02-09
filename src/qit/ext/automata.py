
from qit.base.graph import Graph

def transition_fn_to_graph(mapping, rule_to_arc_fn):
    graph = Graph()
    for key, value in mapping.items():
        state1, label, state2 = rule_to_arc_fn(key, value)
        node1 = graph.node(state1)
        node2 = graph.node(state2)
        node1.add_arc(node2, str(label))
    graph.merge_arcs(lambda a, b: a + ";" + b)
    return graph
