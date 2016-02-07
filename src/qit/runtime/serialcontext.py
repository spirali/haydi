from context import Context
from message import Message, MessageTag
from qit.session import session
from qit.transform import SplitTransformation


class SerialContext(Context):
    def get_result(self, graph):
        self.preprocess_graph(graph)

        return list(graph.create())

    def preprocess_graph(self, graph):
        """
        Removes all split transformations.
        :type graph: graph.Graph
        """
        skipped = []
        for node in graph.nodes:
            if node.factory.klass.is_split():
                skipped.append(node)

        for skipped_node in skipped:
            graph.skip(skipped_node)
