from domain import Domain, DomainIterator
from random import randint
from iterator import EmptyIterator

from copy import copy


class Join(Domain):
    def __init__(self, domains, ratios=None, name=None):
        domains = tuple(domains)
        if all(d.size is not None for d in domains):
            size = sum(d.size for d in domains)
        else:
            size = None
        exact_size = all(d.exact_size for d in domains)
        super(Join, self).__init__(size, exact_size, name)
        self.domains = domains

        if ratios is None:
            ratios = (d.size if d.size is not None else 1
                      for d in domains)

        ratio_sums = []
        s = 0
        for r in ratios:
            s += r
            ratio_sums.append(s)
        self.ratio_sums = ratio_sums

    def create_iterator(self):
        if not self.domains:
            return EmptyIterator()
        else:
            return JoinIterator(self)

    def generate_one(self):
        c = randint(0, self.ratio_sums[-1] - 1)
        for i, r in enumerate(self.ratio_sums):
            if c < r:
                return self.domains[i].generate_one()
        assert 0

    def __add__(self, other):
        return Join(self.domains + (other,))


class JoinIterator(DomainIterator):

    def __init__(self, domain):
        super(JoinIterator, self).__init__(domain)
        self.index = 0
        self.iterators = [d.create_iterator()
                          for d in self.domain.domains]

    def copy(self):
        new = copy(self)
        new.iterators = [it.copy() for it in self.iterators]
        return new

    def reset(self):
        self.index = 0
        for it in self.iterators:
            it.reset()

    def next(self):
        while self.index < len(self.domain.domains):
            try:
                return next(self.iterators[self.index])
            except StopIteration:
                self.index += 1
        raise StopIteration

    def set_step(self, index):
        for i, it in enumerate(self.iterators):
            size = it.size
            if index < size:
                it.set_step(index)
                self.index = i
                return
            index -= size

        self.index = len(self.domain.domains)
        self.iterator = None
