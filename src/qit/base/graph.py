class Arc(object):

    def __init__(self, node, data):
        self.node = node
        self.data = data


class Node(object):

    def __init__(self, key):
        self.key = key
        self.arcs = []

    def add_arc(self, node, data=None):
        self.arcs.append(Arc(node, data))

    def merge_arcs(self, merge_fn):
        if len(self.arcs) < 2:
            return
        node_to_arcs = {}
        for arc in self.arcs[:]:
            a = node_to_arcs.get(arc.node)
            if a is None:
                node_to_arcs[arc.node] = arc
            else:
                self.arcs.remove(arc)
                a.data = merge_fn(a.data, arc.data)


    def __repr__(self):
        return "<Node {}>".format(self.key)


class Graph(object):

    def __init__(self):
        self.nodes = {}

    @property
    def size(self):
        return len(self.nodes)

    def node_check(self, key):
        node = self.nodes.get(key)
        if node is not None:
            return (node, True)
        node = Node(key)
        self.nodes[key] = node
        return (node, False)

    def node(self, key):
        node = self.nodes.get(key)
        if node is not None:
            return node
        node = Node(key)
        self.nodes[key] = node
        return node

    def make_dot(self, comment=None):
        import graphviz
        dot = graphviz.Digraph(comment=comment)
        for node in self.nodes.values():
            key = str(node.key)
            dot.node(key, key)
            for arc in node.arcs:
                dot.edge(key, str(arc.node.key), label=str(arc.data))
        return dot

    def show(self):
        dot = self.make_dot()
        dot.render(view=True)

    def merge_arcs(self, merge_fn):
        for node in self.nodes.values():
            node.merge_arcs(merge_fn)
