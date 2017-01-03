
from .domain import Domain, StepSkip, skip1

import itertools


class Transformation(Domain):

    def __init__(self, parent, size, exact_size, steps):
        name = type(self).__name__
        super(Transformation, self).__init__(size, exact_size, steps, name)
        self.parent = parent


class TakeTransformation(Transformation):

    def __init__(self, parent, count):
        if parent.size is not None:
            size = min(parent.size, count)
        else:
            size = count
        self.size = size

        if parent.exact_size and parent.steps:
            steps = min(size, parent.steps)
        else:
            steps = parent.steps

        super(TakeTransformation, self).__init__(parent,
                                                 size,
                                                 parent.exact_size,
                                                 steps)

    def generate_one(self):
        return self.parent.generate_one()

    def create_iter(self, step=0):
        return itertools.islice(self.parent.create_iter(step),
                                self.size - step)

    def create_step_iter(self, step):
        assert self.exact_size

        it = self.parent.create_step_iter(step)
        count = self.size - step

        while count > 0:
            v = next(it)
            yield v
            if not isinstance(v, StepSkip):
                count -= 1


class MapTransformation(Transformation):

    def __init__(self, domain, fn):
        super(MapTransformation, self).__init__(
            domain, domain.size, domain.exact_size, domain.steps)
        self.fn = fn

    def generate_one(self):
        return self.fn(self.parent.generate_one())

    def create_iter(self, step=0):
        fn = self.fn
        return (fn(x) for x in self.parent.create_iter(step))

    def create_skip_iter(self, step=0):
        fn = self.fn
        return (fn(x) for x in self.parent.create_step_iter(step))


class FilterTransformation(Transformation):

    def __init__(self, domain, fn):
        super(FilterTransformation, self).__init__(
            domain, domain.size, False, domain.steps)
        self.fn = fn

    def create_iter(self, step=0):
        for v in self.parent.create_iter(step):
            if self.fn(v):
                yield v

    def create_step_iter(self, step):
        for v in self.parent.create_step_iter(step):
            if isinstance(v, StepSkip):
                yield v
            elif self.fn(v):
                yield v
            else:
                yield skip1

    def generate_one(self):
        while True:
            x = self.parent.generate_one()
            if self.fn(x):
                return x
