from .domain import Domain

from math import factorial
import itertools
import random


class Permutations(Domain):

    def __init__(self, domain, name=None):
        size = factorial(domain.size)
        steps = factorial(domain.steps)
        exact_size = domain.exact_size
        super(Permutations, self).__init__(size, exact_size, steps, name)
        self.domain = domain

    def create_iter(self, step=0):
        if step >= self.steps:
            return

        items = tuple(self.domain)
        if step == 0:
            return itertools.permutations(items)
        assert 0  # nonzero step implemented yet

    def generate_one(self):
        return random.shuffle(tuple(self.domain))
