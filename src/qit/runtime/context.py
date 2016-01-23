from qit.graph import Node
from qit.transform import Transformation, SplitTransformation, JoinTransformation


class Context(object):
    def __init__(self):
        self.msg_callbacks = []

    def __enter__(self):
        self.init()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.shutdown()

    def run(self, iterator_graph):
        raise NotImplementedError()

    def init(self):
        pass

    def shutdown(self):
        pass

    def on_message_received(self, callback):
        self.msg_callbacks.append(callback)

    def post_message(self, message):
        raise NotImplementedError()

    def _notify_message(self, message):
        for callback in self.msg_callbacks:
            callback(message)


class ParallelContext(Context):
    def preprocess_splits(self, iterator_graph):
        process_count = 4  # TODO

        node = self._find_first_transform(iterator_graph)
        iterator_graph.insert_before(node, Node(SplitTransformation(node.inputs[0].iterator, process_count)))

        master = True

        while True:
            iterator = node.iterator
            if isinstance(iterator, SplitTransformation):
                if not master:
                    iterator_graph.skip(node)  # ignore splits in worker region
                else:
                    master = False
            else:
                if master and not iterator.is_stateful():  # split here
                    iterator_graph.insert_before(node, Node(SplitTransformation(node.inputs[0].iterator, process_count)))
                    master = False
                elif not master and iterator.is_stateful():  # join here
                    iterator_graph.insert_before(node, Node(JoinTransformation(node.inputs[0].iterator)))
                    master = True

            if node.output:
                node = node.output
            else:
                break

        if not master:
            iterator_graph.insert_after(node, Node(JoinTransformation(node.iterator)))

        skipped = []

        for node in iterator_graph.nodes:  # remove immediate split-joins
            if isinstance(node.iterator, JoinTransformation):
                if isinstance(node.inputs[0].iterator, SplitTransformation):
                    skipped += [node, node.inputs[0]]

        for skipped_node in skipped:
            iterator_graph.skip(skipped_node)

    def _find_first_transform(self, iterator_graph):
        node = iterator_graph.nodes[0]

        while isinstance(node.iterator, Transformation):
            node = node.inputs[0]

        return node.output
