from context import Context


class SerialContext(Context):
    def run(self, iterator_graph):
        return list(iterator_graph.nodes[0].iterator)
