class Action(object):
    def __init__(self, iterator_factory):
        self.iterator_factory = iterator_factory

    def run(self, session):
        raise NotImplementedError()


class CollectAction(Action):
    def __init__(self, iterator_factory):
        super(CollectAction, self).__init__(iterator_factory)

    def run(self, parallel=False):
        from session import session

        with session.create_context(parallel) as ctx:
            result = ctx.run(self.iterator_factory.copy())
            session.destroy_context(ctx)

        return result
