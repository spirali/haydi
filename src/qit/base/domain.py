
from factory import IteratorFactory
from iterator import GeneratingIterator, Iterator


class Domain(object):

    exact_size = False

    def __init__(self):
        self.size = None

    def __iter__(self):
        return self.iterate().create()

    def __mul__(self, other):
        return Product((self, other))

    def __add__(self, other):
        return Join((self, other))

    def map(self, fn):
        return MapDomain(self, fn)

    def filter(self, fn):
        return FilterDomain(self, fn)

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


class MapDomain(Domain):

    def __init__(self, domain, fn):
        self.domain = domain
        self.size = domain.size
        self.exact_size = domain.exact_size
        self.fn = fn

    def iterate(self):
        return self.domain.iterate().map(self.fn)

    def generate_one(self):
        return self.fn(self.domain.generate_one())


class FilterDomain(Domain):

    def __init__(self, domain, fn):
        self.domain = domain
        self.size = domain.size
        self.fn = fn

    def iterate(self):
        return self.domain.iterate().filter(self.fn)

    def generate_one(self):
        while True:
            x = self.domain.generate_one()
            if self.fn(x):
                return x


class DomainIterator(Iterator):

    def __init__(self, domain):
        super(DomainIterator, self).__init__()
        self.domain = domain
        self.size = self.domain.size

from product import Product  # noqa
from join import Join  # noqa
