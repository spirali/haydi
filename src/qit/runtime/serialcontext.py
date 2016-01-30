from context import Context
from message import Message, MessageTag
from qit.session import session
from qit.transform import SplitTransformation


class SerialContext(Context):
    def get_result(self, iterator_factory):
        self.preprocess_graph(iterator_factory)

        return list(iterator_factory.create())

    def preprocess_graph(self, iterator_factory):
        """
        Removes all split transformations.
        :type iterator_factory: graph.Graph
        """
        skipped = []
        node = iterator_factory
        while node:
            if node.iterator_class.is_split():
                skipped.append(node)
            node = node.input

        for skipped_node in skipped:
            skipped_node.skip()
