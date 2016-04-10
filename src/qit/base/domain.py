
from factory import IteratorFactory
from iterator import GeneratingIterator, Iterator


class Domain(object):

    def __init__(self, size=None, exact_size=False,  name=None):
        self.size = size
        self.exact_size = exact_size
        self.name = name

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

    def __init__(self, domain, fn, name=None):
        super(MapDomain, self).__init__(domain.size, domain.exact_size, name)
        self.domain = domain
        self.fn = fn

    def iterate(self):
        return self.domain.iterate().map(self.fn)

    def generate_one(self):
        return self.fn(self.domain.generate_one())


class FilterDomain(Domain):

    def __init__(self, domain, fn, name=None):
        super(FilterDomain, self).__init__(domain.size, False, name)
        self.domain = domain
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
