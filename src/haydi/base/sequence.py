
from .domain import Domain, DomainIterator

from copy import copy


class Sequence(Domain):

    def __init__(self, domain, length, name=None):
        size = self._compute_size(domain.size, length)
        steps = self._compute_size(domain.steps, length)
        super(Sequence, self).__init__(size, domain.exact_size, steps, name)
        self.length = length
        self.domain = domain

    def create_iterator(self):
        return SequenceIterator(self)

    def generate_one(self):
        return tuple(self.domain.generate_one() for i in xrange(self.length))

    def _compute_size(self, size, length):
        if size is None:
            return None
        result = 1
        for i in xrange(length):
            result *= size
        return result


class SequenceIterator(DomainIterator):

    def __init__(self, domain):
        super(SequenceIterator, self).__init__(domain)
        self.iterators = [domain.domain.create_iterator()
                          for i in xrange(domain.length)]
        self.current = None

    def reset(self):
        for it in self.iterators:
            it.reset()
        self.current = None

    def copy(self):
        new = copy(self)
        new.iterators = [it.copy() for it in self.iterators]
        return new

    def next(self):
        if self.current is not None:
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

    def set_step(self, index):
        self.current = None
        if index >= self.steps:
            for it in self.iterators:
                it.set_step(it.steps)
            return
        for it in self.iterators:
            steps = it.size
            it.set_step(index % steps)
            index /= steps
