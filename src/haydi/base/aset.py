from basictypes import Atom
from domain import Domain


class ASet(Domain):

    counter = 1

    def __init__(self, size, name):
        Domain.__init__(self, size, True, size, name)
        self.aset_id = ASet.counter
        self.cache = tuple(Atom(self, i) for i in xrange(self.size))
        ASet.counter += 1

    def get(self, index):
        assert index >= 0 and index < self.size
        return self.cache[index]

    def all(self):
        return self.cache

    def generate_one(self):
        raise Exception("TODO")

    def create_iter(self):
        return iter(self.cache)

    def canonicals(self):
        yield self.cache[0]

    def __repr__(self):
        return "<ASet id={} size={} name={}>".format(
            self.aset_id, self.size, self.name)
