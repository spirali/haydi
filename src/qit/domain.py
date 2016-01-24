
from iterator import Iterator, GeneratingIterator, IteratorFactory


class Domain(object):

    def __init__(self):
        pass

    def __iter__(self):
        return self.iterate()

    def __mul__(self, other):
        return Product((self, other))

    def __add__(self, other):
        return Join((self, other))

    @property
    def size(self):
        return None

    def iterate(self):
        raise NotImplementedError()

    def generate_one(self):
        raise NotImplementedError()

    def generate(self, count=None):
        g = IteratorFactory(GeneratingIterator, self.generate_one)
        if count is None:
            return g
        else:
            return g.take(count)


class DomainIterator(Iterator):

    def __init__(self, domain):
        super(DomainIterator, self).__init__()
        self.domain = domain
        self.size = domain.size

from product import Product  # flake8: noqa
from join import Join  # flake8: noqa
