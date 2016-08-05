from copy import copy
from domain import Domain, DomainIterator
from qit.base.iterator import NoValue


class TransformationIterator(DomainIterator):

    def __init__(self, domain, parent):
        super(TransformationIterator, self).__init__(domain)
        self.parent = parent

    def reset(self):
        self.parent.reset()

    def set_step(self, index):
        self.parent.set_step(index)

    def copy(self):
        new = copy(self)
        new.parent = self.parent.copy()
        return new


class Transformation(Domain):

    iterator_class = None

    def __init__(self, domain, size, exact_size, steps):
        name = type(self).__name__
        super(Transformation, self).__init__(size, exact_size, steps, name)
        self.domain = domain

    def create_iterator(self):
        return self.iterator_class(self,
                                   self.domain.create_iterator())


class TakeIterator(TransformationIterator):

    def __init__(self, domain, parent):
        super(TakeIterator, self).__init__(domain, parent)
        self.count = domain.size

    def reset(self):
        self.count = self.domain.size
        self.parent.reset()

    def next(self):
        if self.count <= 0:
            raise StopIteration()
        self.count -= 1
        return self.parent.next()

    def step(self):
        if self.count <= 0:
            raise StopIteration()
        value = self.parent.step()
        if value is not NoValue:
            self.count -= 1
        return value


class TakeTransformation(Transformation):

    iterator_class = TakeIterator

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


class MapIterator(TransformationIterator):

    def __init__(self, domain, parent):
        super(MapIterator, self).__init__(domain, parent)
        self.fn = domain.fn

    def next(self):
        return self.fn(next(self.parent))

    def step(self):
        v = self.parent.step()
        if v is NoValue:
            return v
        else:
            return self.fn(v)


class MapTransformation(Transformation):

    iterator_class = MapIterator

    def __init__(self, domain, fn):
        super(MapTransformation, self).__init__(
            domain, domain.size, domain.exact_size, domain.steps)
        self.fn = fn

    def generate_one(self):
        return self.fn(self.domain.generate_one())


class FilterIterator(TransformationIterator):

    def __init__(self, domain, parent):
        super(FilterIterator, self).__init__(domain, parent)
        self.fn = domain.fn

    def next(self):
        v = next(self.parent)
        while not self.fn(v):
            v = next(self.parent)
        return v

    def step(self):
        v = self.parent.step()
        if v is NoValue or self.fn(v):
            return v
        else:
            return NoValue


class FilterTransformation(Transformation):

    iterator_class = FilterIterator

    def __init__(self, domain, fn):
        super(FilterTransformation, self).__init__(
            domain, domain.size, False, domain.steps)
        self.fn = fn

    def generate_one(self):
        while True:
            x = self.domain.generate_one()
            if self.fn(x):
                return x

"""
class TimeoutTransformation(Transformation):
    def __init__(self, parent, timeout):
        super(TimeoutTransformation, self).__init__(parent)
        self.timeout = timeout
        self.start = None

    def next(self):
        if not self.start:
            self.start = time.time()

        if time.time() - self.start >= self.timeout:
            raise StopIteration()
        else:
            return next(self.parent)
"""
