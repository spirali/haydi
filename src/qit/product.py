
from domain import Domain, DomainIterator
from factory import IteratorFactory

from copy import copy


class Product(Domain):

    def __init__(self, domains):
        super(Product, self).__init__()
        self.domains = tuple(domains)

    def iterate(self):
        return IteratorFactory(ProductIterator, self)

    def generate_one(self):
        return tuple(d.generate_one() for d in self.domains)

    @property
    def size(self):
        if (not self.domains or
                not all([domain.size is not None for domain in self.domains])):
            return None
        result = 1
        for domain in self.domains:
            result *= domain.size
        return result

    def __mul__(self, other):
        return Product(self.domains + (other,))


class ProductIterator(DomainIterator):

    def __init__(self, domain):
        super(ProductIterator, self).__init__(domain)
        self.iterators = [d.iterate().create() for d in domain.domains]
        self.current = None

    def reset(self):
        for it in self.iterators:
            it.reset()
        self.current = None

    def get_parents(self):
        return list(self.iterators)

    def copy(self):
        new = copy(self)
        new.iterators = [ it.copy() for it in self.iterators ]
        return new

    def next(self):
        if self.current:
            for i, it in enumerate(self.iterators):
                try:
                    self.current[i] = next(it)
                    return tuple(self.current)
                except StopIteration:
                    it.reset()
                    self.current[i] = next(it)
            raise StopIteration()
        else:
            self.current = [next(i) for i in self.iterators]
            return tuple(self.current)

    def __repr__(self):
        return "Product"

    def set(self, index):
        self.current = None
        if index >= self.size:
            for it in self.iterators:
                it.set(it.size)
            return
        for it in self.iterators:
            size = it.size
            it.set(index % size)
            index /= size


class UnorderedProduct(Domain):

    def __init__(self, domains):
        self.domains = tuple(domains)
        if len(set(domains)) > 1:
            raise Exception("Not implemented for discitinct domains")
        self.size = self._compute_size()

    def iterate(self):
        return UnorderedProductIterator(self)

    def generate_one(self):
        return tuple(d.generate_one() for d in self.domains)

    def _compute_size(self):
        if not self.domains:
            return 0
        result = 1
        for i, domain in enumerate(self.domains):
            result *= domain.size - i
        return result


class UnorderedProductIterator(DomainIterator):

    def __init__(self, domain):
        super(UnorderedProductIterator, self).__init__(domain)
        self.iterators = [ d.iterate() for d in domain.domains ]
        self.current = None
        self.indices = [0] * (len(self.iterators) - 1)

    def reset(self):
        for it in self.iterators:
            it.reset()
        for i in xrange(len(self.indices) - 1):
            self.indices[i] = 0
        self.current = None

    def next(self):
        if self.current:
           for i, it in enumerate(self.iterators):
               try:
                   self.current[i] = next(it)
                   return tuple(self.current)
               except StopIteration:
                   if i == len(self.iterators) - 1:
                       raise StopIteration()
                   self.indices[i] += 1
                   it.set(self.indices[i])
                   self.current[i] = next(it)
           raise StopIteration()
        else:
           self.current = [ next(i) for i in self.iterators ]
           return tuple(self.current)

    def set(self, index):
        raise NotImplementedError()
