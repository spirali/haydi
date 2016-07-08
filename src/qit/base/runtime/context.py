from qit.base.exception import TooManySplits
from qit.base.computegraph import ComputeGraph


class Context(object):
    def is_parallel(self):
        return False

    def run(self, action_factory):
        action = action_factory.create()
        try:
            self.compute_action(ComputeGraph(action_factory), action)
        except KeyboardInterrupt:
            self.finish_computation()
            print("Returning what I've got so far...")

        return action.get_result()

    def finish_computation(self):
        pass

    def compute_action(self, computegraph, action):
        raise NotImplementedError()


class ParallelContext(Context):
    def __init__(self):
        self.has_computation = False

    def compute_action(self, computegraph, action):
        try:
            self.has_computation = True
            self.do_computation(computegraph, action)
        finally:
            self.has_computation = False

    def do_computation(self, computegraph, action):
        raise NotImplementedError()

    def is_parallel(self):
        return True

    def preprocess_splits(self, graph):
        """
        :type graph: qit.base.computegraph.ComputeGraph
        """
        from qit.base.factory import TransformationFactory
        from qit.base.transform import SplitTransformation, JoinTransformation

        if not graph.has_transformations():
            return

        first_node = graph.first_transformation
        user_splits = len([node for node in graph.transformations
                           if node.klass.is_split()])

        if user_splits > 1:
            raise TooManySplits()
        elif user_splits == 0:
            graph.prepend(first_node,
                          TransformationFactory(SplitTransformation))

        graph.append(graph.last_transformation,
                     TransformationFactory(JoinTransformation))
