from domain import Domain, DomainIterator
from copy import copy


class Mapping(Domain):

    def __init__(self, key_domain, value_domain, name=None):
        size = value_domain.size ** key_domain.size
        steps = value_domain.steps ** key_domain.steps
        exact_size = key_domain.exact_size and value_domain.exact_size
        super(Mapping, self).__init__(size, exact_size, steps, name)
        self.key_domain = key_domain
        self.value_domain = value_domain

    def create_iterator(self):
        return MappingIterator(self)

    def generate_one(self):
        result = {}
        value_domain = self.value_domain
        for key in self.key_domain:
            result[key] = value_domain.generate_one()
        return result


class MappingIterator(DomainIterator):

    def __init__(self, domain):
        super(MappingIterator, self).__init__(domain)
        self.keys = tuple(domain.key_domain)
        self.iterators = [domain.value_domain.create_iterator()
                          for key in self.keys]
        self.current = None

    def copy(self):
        new = copy(self)
        new.iterators = [it.copy() for it in self.iterators]
        new.current = copy(self.current)
        return new

    def reset(self):
        for it in self.iterators:
            it.reset()
        self.current = None

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

    def next(self):
        if self.current is not None:
            for key, it in zip(self.keys, self.iterators):
                try:
                    self.current[key] = next(it)
                    return self.current.copy()
                except StopIteration:
                    it.reset()
                    self.current[key] = next(it)
            raise StopIteration()
        else:
            self.current = {}
            for key, it in zip(self.keys, self.iterators):
                self.current[key] = next(it)
            return self.current.copy()
