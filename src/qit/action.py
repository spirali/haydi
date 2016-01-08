class Action(object):
    def __init__(self, iterator, session):
        self.iterator = iterator
        self.session = session

    def run(self):
        pass


class CollectAction(Action):
    def __init__(self, iterator, session):
        super(CollectAction, self).__init__(iterator, session)
