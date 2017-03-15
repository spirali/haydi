
from .domain import Domain, StepSkip, skip1

import itertools


class Transformation(Domain):

    def __init__(self, parent):
        name = type(self).__name__
        super(Transformation, self).__init__(name)
        self.parent = parent
        self.filtered = parent.filtered
        self.step_jumps = parent.step_jumps
        self.strict = False

    def _compute_size(self):
        return self.parent.size


class TakeTransformation(Transformation):

    def __init__(self, parent, count):
        super(TakeTransformation, self).__init__(parent)
        self.count = count
        if self.filtered:
            self.step_jumps = False

    def _compute_size(self):
        size = self.parent.size
        if size is not None:
            return min(size, self.count)
        else:
            return self.count

    def generate_one(self):
        return self.parent.generate_one()

    def create_iter(self, step=0):
        return itertools.islice(self.parent.create_iter(step),
                                self.size - step)

    def create_step_iter(self, step):
        assert not self.filtered

        it = self.parent.create_step_iter(step)
        count = self.size - step

        while count > 0:
            v = next(it)
            yield v
            if not isinstance(v, StepSkip):
                count -= 1


class MapTransformation(Transformation):

    def __init__(self, domain, fn):
        super(MapTransformation, self).__init__(domain)
        self.fn = fn

    def generate_one(self):
        return self.fn(self.parent.generate_one())

    def create_iter(self, step=0):
        fn = self.fn
        return (fn(x) for x in self.parent.create_iter(step))

    def create_skip_iter(self, step=0):
        fn = self.fn
        for v in self.parent.create_step_iter(step):
            if isinstance(v, StepSkip):
                yield v
            else:
                yield fn(v)


class FilterTransformation(Transformation):

    def __init__(self, domain, fn, strict):
        super(FilterTransformation, self).__init__(domain)
        self.fn = fn
        self.filtered = True
        self.strict = strict

    def create_cn_iter(self):
        for v in self.parent.create_cn_iter():
            if self.fn(v):
                yield v

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
