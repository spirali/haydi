
from domain import Domain, DomainIterator
from values import Values

from copy import copy
import math
from collections import namedtuple


class Product(Domain):

    _generator_cache = None

    def __init__(self,
                 domains,
                 name=None,
                 unordered=False,
                 cache_size=0):
        domains = tuple(domains)
        size = self._compute_size([d.size for d in domains], unordered)
        steps = self._compute_size([d.steps for d in domains], unordered)
        exact_size = all(d.exact_size for d in domains)
        super(Product, self).__init__(size, exact_size, steps, name)
        self.domains = tuple(domains)
        self.unordered = unordered
        self.cache_size = max(len(domains), cache_size) if cache_size else 0

        if unordered:
            if len(set(domains)) > 1:
                raise Exception("Not implemented for discitinct domains")

    def create_iterator(self, use_steps):
        if self.unordered:
            return UnorderedProductIterator(self, use_steps)
        else:
            return ProductIterator(self, use_steps)

    def generate_one(self):
        if self._generator_cache:
            try:
                return next(self._generator_cache)
            except StopIteration:
                pass  # Let us generate new one

        if self.cache_size:
            if self.unordered:
                values = Values(
                    tuple(self.domains[0].generate(self.cache_size)))
                self._generator_cache = iter(Product(
                    (values,) * len(self.domains), unordered=True))
            else:
                if self._generator_cache:
                    try:
                        return next(self._generator_cache)
                    except StopIteration:
                        pass  # Let us generate new one
                values = [Values(tuple(d.generate(self.cache_size)))
                          for d in self.domains]
                self._generator_cache = iter(Product(values))

            return self._generator_cache.next()
        else:
            return tuple(d.generate_one() for d in self.domains)

    def _compute_size(self, sizes, unordered):
        if any(s is None for s in sizes):
            return None
        result = 1

        if unordered:
            for i, s in enumerate(sizes):
                result *= s - i
            return result / math.factorial(len(sizes))
        else:
            for s in sizes:
                result *= s
            return result

    def __mul__(self, other):
        return Product(self.domains + (other,))


class ProductIterator(DomainIterator):

    def __init__(self, domain, use_steps):
        super(ProductIterator, self).__init__(domain)
        self.iterators = [d.create_iterator(use_steps) for d in domain.domains]
        self.current = None
        self.use_steps = use_steps

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

    def set_step(self, index):
        self.current = None
        if index >= self.size:
            for it in self.iterators:
                it.set_step(it.size)
            return
        for it in self.iterators:
            size = it.size
            it.set_step(index % size)
            index /= size


class UnorderedProductIterator(DomainIterator):

    def __init__(self, domain, use_steps):
        super(UnorderedProductIterator, self).__init__(domain)
        assert len(set(domain.domains)) == 1
        self.iterators = None
        self.current = None
        self.use_steps = use_steps

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
            it = self.domain.domains[0].create_iterator(self.use_steps)
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

    def set_step(self, index):
        assert len(self.domain.domains) == 2
        size = self.domain.domains[1].size - 1  # -1 to ignore diagonal
        assert index < self.size
        # The root of y * size - ((y - 1) * y) / 2 - index
        # y * size = full rectangle
        # ((y-1) * y) / 2 = missing elements to full rectangle
        y = int(0.5 * (-math.sqrt(-8 * index + 4 * size**2 + 4 * size + 1) +
                       2 * size + 1))
        x = index - y * size + ((y - 1) * y / 2) + y

        if not self.current:
            iterators = [d.create_iterator(self.use_steps)
                         for d in self.domain.domains]
        else:
            iterators = self.iterators
        iterators[0].set_step(x)
        iterators[1].set_step(y)
        self.current = [next(it) for it in iterators]
        self.iterators = iterators


def NamedProduct(named_domains,
                 type_name=None,
                 name=None,
                 unordered=False):
    def make_instance(value):
        return ntuple(*value)

    if type_name is None:
        if name is None:
            type_name = "NamedProduct"
        else:
            type_name = name
    ntuple = namedtuple(type_name, [n for n, d in named_domains])
    domain = Product([d for n, d in named_domains], unordered=unordered)
    domain = domain.map(make_instance)
    domain.name = name
    del n
    del d
    return domain
