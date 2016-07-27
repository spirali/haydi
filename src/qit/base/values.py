from domain import Domain, DomainIterator

from copy import copy
import random


class Values(Domain):

    def __init__(self, values, name=None):
        super(Values, self).__init__(len(values), True, name)
        self.values = values

    def generate_one(self):
        return random.choice(self.values)

    def create_iterator(self):
        return ValuesIterator(self)


class ValuesIterator(DomainIterator):

    def __init__(self, domain):
        super(ValuesIterator, self).__init__(domain)
        self.index = 0

    def reset(self):
        self.index = 0

    def copy(self):
        return copy(self)

    def next(self):
        if self.index < len(self.domain.values):
            v = self.domain.values[self.index]
            self.index += 1
            return v
        raise StopIteration()

    def set_step(self, index):
        self.index = index
