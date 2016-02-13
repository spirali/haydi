from qit.exception import TooManySplits
from qit.factory import TransformationFactory
from qit.graph import Graph
from qit.runtime.message import Message, MessageTag
from qit.session import session
from qit.transform import SplitTransformation, JoinTransformation


class Context(object):
    def __enter__(self):
        self.init()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.shutdown()

    def is_parallel(self):
        return False

    def run(self, iterator_factory, action):
        session.post_message(Message(MessageTag.CONTEXT_START))
        self.compute_action(Graph(iterator_factory), action)
        session.post_message(Message(MessageTag.CONTEXT_STOP))

        return action.get_result()

    def compute_action(self, iterator_factory, action):
        raise NotImplementedError()

    def init(self):
        pass

    def shutdown(self):
        pass


class ParallelContext(Context):
    def is_parallel(self):
        return True

    def is_master(self):
        raise NotImplementedError()

    def transmit_to_master(self, message):
        raise NotImplementedError()

    def preprocess_splits(self, graph):
        if not graph.has_transformations():
            return

        process_count = 4  # TODO

        node = graph.first_transformation
        user_splits = self._count_user_splits(graph)

        if user_splits > 1:
            raise TooManySplits()
        elif user_splits == 0:
            graph.prepend(node, TransformationFactory(SplitTransformation,
                                                      process_count))

        master = True

        while True:
            iterator = node.factory.klass
            if iterator.is_split():
                if not master:
                    graph.skip(node)  # ignore splits in worker region
                else:
                    master = False
            else:
                if master and not iterator.is_stateful():  # split here
                    graph.prepend(node,
                                  TransformationFactory(SplitTransformation,
                                                        process_count))
                    master = False
                elif not master and iterator.is_stateful():  # join here
                    graph.prepend(node,
                                  TransformationFactory(JoinTransformation))
                    master = True

            if node.output:
                node = node.output
            else:
                break

        if not master:
            graph.append(node, TransformationFactory(JoinTransformation))

        skipped = []
        for node in graph.nodes:  # remove immediate split-joins
            if node.factory.klass.is_join():
                if node.input.factory.klass.is_split():
                    skipped += [node, node.input]

        for skipped_node in skipped:
            graph.skip(skipped_node)

    def _count_user_splits(self, graph):
        splits = 0

        for node in graph.nodes:
            if node.factory.klass.is_split():
                splits += 1

        return splits
