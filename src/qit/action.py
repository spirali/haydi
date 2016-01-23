class Action(object):
    def __init__(self, iterator_factory):
        self.iterator_factory = iterator_factory

    def run(self, session):
        raise NotImplementedError()


class CollectAction(Action):
    def __init__(self, iterator_factory):
        super(CollectAction, self).__init__(iterator_factory)

    def run(self, session):
        iterator = self.iterator_factory.create()
        with session.create_context(iterator) as ctx:
            graph = session.create_graph(iterator)
            result = ctx.run(graph)

        return result
