
from domain import Domain, DomainIterator
from factory import IteratorFactory
from copy import copy


class Sequence(Domain):

    def __init__(self, domain, length):
        super(Sequence, self).__init__()
        self.length = length
        self.domain = domain
        self.size = self._compute_size()

    def iterate(self):
        return IteratorFactory(SequenceIterator, self)

    def generate_one(self):
        return tuple(self.domain.generate_one() for i in xrange(self.length))

    def _compute_size(self):
        if not self.domain:
            return 0
        result = 1
        size = self.domain.size
        for i in xrange(self.length):
            result *= size
        return result


class SequenceIterator(DomainIterator):

    def __init__(self, domain):
        super(SequenceIterator, self).__init__(domain)
        self.iterators = [domain.domain.iterate for i in xrange(domain.length)]
        self.current = None

    def reset(self):
        for it in self.iterators:
            it.reset()
        self.current = None

    def copy(self):
        new = copy(self)
        new.iterators = [ it.copy() for it in self.iterators ]
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
