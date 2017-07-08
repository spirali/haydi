from .domain import Domain

from math import factorial
import itertools
import random


class Permutations(Domain):

    def __init__(self, domain, name=None):
        super(Permutations, self).__init__(name)
        self._set_flags_from_domain(domain)
        self.step_jumps = False  # not implemented yet
        self.domain = domain

    def _compute_size(self):
        return factorial(self.domain.size)

    def create_iter(self, step=0):
        assert step == 0  # nonzero step implemented yet
        items = tuple(self.domain)
        return itertools.permutations(items)

    def generate_one(self):
        return random.shuffle(tuple(self.domain))

    def _remap_domains(self, transformation):
        return Permutations(transformation(self.domain), self.name)
