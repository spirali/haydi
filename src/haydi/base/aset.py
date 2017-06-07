from .basictypes import Atom
from .domain import Domain
from threading import Lock

aset_names = set()
aset_names_mutex = Lock()


class ASet(Domain):

    step_jumps = True
    strict = True

    counter = 1

    def __init__(self, size, name, ensure_uniqueness=True):
        if ensure_uniqueness:
            with aset_names_mutex:
                if name in aset_names:
                    raise Exception("Aset name is not unique")
                aset_names.add(name)
        else:
            name += "#{}".format(id(self))

        Domain.__init__(self, name)
        self.unique = ensure_uniqueness
        self._size = size
        self.aset_id = ASet.counter
        self.cache = tuple(Atom(self, i) for i in xrange(size))
        ASet.counter += 1

    def __del__(self):
        if self.unique:
            with aset_names_mutex:
                aset_names.remove(self.name)

    def get(self, index):
        assert index >= 0 and index < self._size
        return self.cache[index]

    def all(self):
        return self.cache

    def generate_one(self):
        raise Exception("TODO")

    def create_iter(self, step=0):
        if step == 0:
            return iter(self.cache)
        else:
            return iter(self.cache[step:])

    def create_cn_iter(self):
        yield self.cache[0]

    def __repr__(self):
        return "<ASet id={} size={} name={}>".format(
            self.aset_id, self._size, self.name)
