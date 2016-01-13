from context import Context


class SerialContext(Context):
    def run(self, iterator_graph):
        return list(iterator_graph.nodes[0].iterator)

    def post_message(self, message):
        self._notify_message(message)
