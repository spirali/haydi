from context import Context


class SerialContext(Context):
    def compute_action(self, graph, action):
        self.preprocess_graph(graph)

        for item in graph.create():
            if not action.handle_item(item):
                break

    def preprocess_graph(self, graph):
        """
        Removes all split transformations.
        :type graph: graph.Graph
        """
        skipped = []
        for node in graph.nodes:
            if node.klass.is_split():
                skipped.append(node)

        for skipped_node in skipped:
            graph.skip(skipped_node)
