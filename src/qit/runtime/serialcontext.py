from context import Context
from message import Message, MessageTag
from qit.transform import SplitTransformation


class SerialContext(Context):
    def run(self, iterator_graph):
        self.preprocess_graph(iterator_graph)
        self.post_message(Message(MessageTag.CONTEXT_START))

        result = list(iterator_graph.nodes[0].iterator)

        self.post_message(Message(MessageTag.CONTEXT_STOP))

        return result

    def preprocess_graph(self, iterator_graph):
        """
        Removes all split transformations.
        :type iterator_graph: graph.Graph
        """
        skipped = []
        for node in iterator_graph.nodes:
            if isinstance(node.iterator, SplitTransformation):
                skipped.append(node)

        for skipped_node in skipped:
            iterator_graph.skip(skipped_node)

    def post_message(self, message):
        self._notify_message(message)
