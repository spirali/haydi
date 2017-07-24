from .basictypes import Atom
from .domain import Domain


class ASet(Domain):
    """
    A domain of anonymous objects.

    ASet is a domain of :class:``haydi.Atom``. It is a basic block for
    canonical forms. See section TODO ref.
    """

    step_jumps = True
    strict = True

    counter = 1

    def __init__(self, size, name):
        Domain.__init__(self, name)
        self._size = size
        self.aset_id = ASet.counter
        self.cache = tuple(Atom(self, i) for i in xrange(size))
        ASet.counter += 1

    def get(self, index):
        assert index >= 0 and index < self._size
        return self.cache[index]

    def all(self):
        return self.cache

    def generate_one(self):
        raise Exception("TODO")

    def _make_iter(self, step):
        if step == 0:
            return iter(self.cache)
        else:
            return iter(self.cache[step:])

    def create_cn_iter(self):
        yield self.cache[0]

    def __repr__(self):
        return "<ASet id={} size={} name={}>".format(
            self.aset_id, self._size, self.name)
