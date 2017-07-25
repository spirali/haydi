import haydi.base.graph


def test_graph_merge_args():
    g = haydi.base.graph.Graph()
    n1 = g.node("A")
    n2 = g.node("B")
    n3 = g.node("C")

    n1.add_arc(n1, "1")
    n1.add_arc(n1, "2")
    n1.add_arc(n2, "3")
    n1.add_arc(n1, "4")
    n1.add_arc(n2, "5")

    n2.add_arc(n3, "6")
    n2.add_arc(n1, "7")

    g.merge_arcs(lambda a, b: a + ";" + b)

    n = g.node("A")
    assert len(n.arcs) == 2
    assert n.arcs[0].data == "1;2;4"
    assert n.arcs[1].data == "3;5"

    n = g.node("B")
    assert len(n.arcs) == 2
    assert n.arcs[0].data == "6"
    assert n.arcs[1].data == "7"
