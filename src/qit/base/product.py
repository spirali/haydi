
from domain import Domain, DomainIterator, MapDomain
from factory import IteratorFactory

from copy import copy
import math
from collections import namedtuple


class Product(Domain):

    def __init__(self, domains, name=None):
        domains = tuple(domains)
        size = self._compute_size(domains)
        exact_size = all(d.exact_size for d in domains)
        super(Product, self).__init__(size, exact_size, name)
        self.domains = tuple(domains)

    def iterate(self):
        return IteratorFactory(ProductIterator, self)

    def generate_one(self):
        return tuple(d.generate_one() for d in self.domains)

    def _compute_size(self, domains):
        if (not domains or
                not all([domain.size is not None for domain in domains])):
            return None
        result = 1
        for domain in domains:
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
        new.iterators = [it.copy() for it in self.iterators]
        new.current = copy(self.current)
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

    def __init__(self, domains, name=None):
        domains = tuple(domains)
        size = self._compute_size(domains)
        exact_size = all(d.exact_size for d in domains)
        super(UnorderedProduct, self).__init__(size, exact_size, name)
        self.domains = domains
        if len(set(domains)) > 1:
            raise Exception("Not implemented for discitinct domains")

    def iterate(self):
        return IteratorFactory(UnorderedProductIterator, self)

    def generate_one(self):
        return tuple(d.generate_one() for d in self.domains)

    def _compute_size(self, domains):
        if not domains:
            return 0
        result = 1
        for i, domain in enumerate(domains):
            result *= domain.size - i
        return result / math.factorial(len(domains))


class UnorderedProductIterator(DomainIterator):

    def __init__(self, domain):
        super(UnorderedProductIterator, self).__init__(domain)
        assert len(set(domain.domains)) == 1
        self.iterators = None
        self.current = None

    def copy(self):
        new = copy(self)
        if self.iterators is not None:
            new.iterators = [it.copy() for it in self.iterators]
        new.current = copy(self.current)
        return new

    def reset(self):
        for it in self.iterators:
            it.reset()
        for i in xrange(len(self.indices) - 1):
            self.nexts[i] = None
        self.current = None

    def next(self):
        current = self.current
        if current:
            for i, it in enumerate(self.iterators):
                try:
                    current[i] = next(it)
                    if i == 0:
                        return tuple(current)
                    for j in xrange(i - 1, -1, -1):
                        it = it.copy()
                        self.iterators[j] = it
                        current[j] = next(it)
                    return tuple(current)
                except StopIteration:
                    continue
            raise StopIteration()
        else:
            it = self.domain.domains[0].iterate().create()
            iterators = []
            current = []
            for d in self.domain.domains:
                iterators.append(it)
                current.append(next(it))
                it = it.copy()
            iterators.reverse()
            current.reverse()
            self.iterators = iterators
            self.current = current
            return tuple(self.current)

    def set(self, index):
        assert len(self.domain.domains) == 2
        size = self.domain.domains[1].size - 1  # -1 to ignore diagonal
        # The root of y * size - ((y - 1) * y) / 2 - index
        # y * size = full rectangle
        # ((y-1) * y) / 2 = missing elements to full rectangle
        y = int(0.5 * (-math.sqrt(-8 * index + 4 * size**2 + 4 * size + 1) +
                       2 * size + 1))
        x = index - y * size + ((y - 1) * y / 2) + y

        if not self.current:
            iterators = [d.iterate().create() for d in self.domain.domains]
        else:
            iterators = self.iterators
        iterators[0].set(x)
        iterators[1].set(y)
        self.current = [next(it) for it in iterators]
        self.iterators = iterators


class NamedProduct(MapDomain):

    def __init__(self, named_domains, type_name=None, name=None):
        if type_name is None:
            if name is None:
                type_name = "Tuple" + str(id(self))
            else:
                type_name = name
        domain = Product([d for n, d in named_domains])
        super(NamedProduct, self).__init__(domain, self.make_instance, name)
        self.type = namedtuple(type_name, [n for n, d in named_domains])

    def make_instance(self, value):
        return self.type(*value)
