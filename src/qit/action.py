from graph import IteratorGraph


class Action(object):
    def __init__(self, iterator):
        self.iterator = iterator

    def run(self, session):
        raise NotImplementedError()


class CollectAction(Action):
    def __init__(self, iterator):
        super(CollectAction, self).__init__(iterator)

    def run(self, session):
        with session.create_context() as ctx:
            self.iterator.set_context(ctx)

            graph = IteratorGraph(self.iterator)
            split = None
            last = None

            from transform import SplitTransformation, JoinTransformation, Transformation

            for node in graph:  # TODO
                if isinstance(node.data[0], SplitTransformation):
                    assert not split
                    split = node.data[0]
                elif isinstance(node.data[0], JoinTransformation):
                    assert split
                    node.data[0].split = split
                    split.join = node.data[0]
                    split = None

                if last:
                    last.child = node.data[0]

                if isinstance(node.data[0], Transformation):
                    last = node.data[0]

            assert not split

            result = ctx.run(self.iterator)

        return result
