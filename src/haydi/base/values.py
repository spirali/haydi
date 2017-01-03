from .domain import Domain

import random


class Values(Domain):

    def __init__(self, values, name=None):
        size = len(values)
        super(Values, self).__init__(size, True, size, name)
        self.values = values

    def generate_one(self):
        return random.choice(self.values)

    def create_iter(self, step=0):
        if step:
            # TODO: Lazy []
            return iter(self.values[step:])
        else:
            return iter(self.values)
