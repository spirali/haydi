
from domain import Domain, DomainIterator


class Sequence(Domain):

    def __init__(self, domain, length):
        self.length = length
        self.domain = domain

    def iterate(self):
        return SequenceIterator(self)

    def generate_one(self):
        return tuple(self.domain.generate_one() for i in xrange(self.length))

    @property
    def size(self):
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
        self.iterators = [ domain.domain.iterate() for i in xrange(domain.length) ]
        self.current = None

    def reset(self):
        for it in self.iterators:
            it.reset()
        self.current = None

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
           self.current = [ next(i) for i in self.iterators ]
           return tuple(self.current)
