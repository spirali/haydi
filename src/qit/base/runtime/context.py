from qit.base.exception import TooManySplits
from qit.base.factorylist import FactoryList


class Context(object):
    def is_parallel(self):
        return False

    def run(self, action_factory):
        action = action_factory.create()
        try:
            self.compute_action(FactoryList(action_factory.iterator_factory),
                                action, action_factory)
        except KeyboardInterrupt:
            self.finish_computation()
            print("Returning what I've got so far...")

        return action.get_result()

    def finish_computation(self):
        pass

    def compute_action(self, iterator_graph, action, action_factory):
        raise NotImplementedError()


class ParallelContext(Context):
    def __init__(self):
        self.has_computation = False

    def compute_action(self, iterator_graph, action, action_factory):
        try:
            self.has_computation = True
            self.do_computation(iterator_graph, action, action_factory)
        finally:
            self.has_computation = False

    def do_computation(self, iterator_graph, action, action_factory):
        raise NotImplementedError()

    def is_parallel(self):
        return True

    def is_master(self):
        raise NotImplementedError()

    def transmit_to_master(self, message):
        raise NotImplementedError()

    def preprocess_splits(self, graph):
        from qit.base.factory import TransformationFactory
        from qit.base.transform import JoinTransformation, SplitTransformation

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
            iterator = node.klass
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

            output = graph.get_next_node(node)
            if output:
                node = output
            else:
                break

        if not master:
            graph.append(node, TransformationFactory(JoinTransformation))

        skipped = []
        for node in graph.nodes:  # remove immediate split-joins
            if node.klass.is_join():
                previous = graph.get_previous_node(node)
                if previous.klass.is_split():
                    skipped += [node, previous]

        for skipped_node in skipped:
            graph.skip(skipped_node)

    def _count_user_splits(self, graph):
        splits = 0

        for node in graph.nodes:
            if node.klass.is_split():
                splits += 1

        return splits
