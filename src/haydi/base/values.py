from .domain import Domain

import random


class Values(Domain):

    step_jumps = True

    def __init__(self, values, name=None):
        super(Values, self).__init__(name)
        values = tuple(values)
        self._size = len(values)
        self.values = values

    def generate_one(self):
        return random.choice(self.values)

    def create_iter(self, step=0):
        if step:
            # TODO: Lazy []
            return iter(self.values[step:])
        else:
            return iter(self.values)


class StrictValues(Domain):

    def __init__(self, values, name=None):
        super(StrictValues, self).__init__(name)
        values = tuple(values)
        self._size = len(values)
        self.values = values

    def create_cn_iter(self):
        return iter(self.values)
