
from domain import Domain, DomainIterator
import random

from factory import IteratorFactory


class Values(Domain):

    def __init__(self, values):
        super(Values, self).__init__()
        self.values = values

    def generate_one(self):
        return random.choice(self.values)

    @property
    def iterate(self):
        return IteratorFactory(ValuesIterator, self)

    @property
    def size(self):
        return len(self.values)


class ValuesIterator(DomainIterator):

    def __init__(self, domain):
        super(ValuesIterator, self).__init__(domain)
        self.index = 0

    def next(self):
        if self.index < len(self.domain.values):
            v = self.domain.values[self.index]
            self.index += 1
            return v
        raise StopIteration()

    def set(self, index):
        self.index = index
