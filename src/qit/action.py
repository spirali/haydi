class Action(object):
    def __init__(self, iterator):
        self.iterator = iterator

    def run(self, session):
        raise NotImplementedError()


class CollectAction(Action):
    def __init__(self, iterator):
        super(CollectAction, self).__init__(iterator)

    def run(self, session):
        with session.create_context(self.iterator) as ctx:
            graph = session.create_graph(self.iterator)
            result = ctx.run(graph)

        return result
