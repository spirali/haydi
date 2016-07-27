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

    def __init__(self, domain, size, exact_size):
        name = type(self).__name__
        super(Transformation, self).__init__(size, exact_size, name)
        self.domain = domain

    def create_iterator(self):
        return self.iterator_class(self, self.domain.create_iterator())


class TakeIterator(TransformationIterator):

    def __init__(self, domain, parent):
        super(TakeIterator, self).__init__(domain, parent)
        self.count = domain.size

    def next(self):
        if self.count <= 0:
            raise StopIteration()
        self.count -= 1
        return next(self.parent)

    def next_step(self):
        v = self.parent.next_step()
        if v is not NoValue:
            self.count -= 1
        return v

    def set_step(self, index):
        self.parent.set_step(index)

    def __repr__(self):
        return "Take {} items".format(self.count)


class TakeTransformation(Transformation):

    iterator_class = TakeIterator

    def __init__(self, parent, count):
        super(TakeTransformation, self).__init__(parent,
                                                 parent.size,
                                                 parent.exact_size)
        if parent.size is not None:
            size = min(parent.size, count)
        else:
            size = count
        self.size = size
        if self.steps is None:
            self.steps = self.size  # set steps for generators

    def create_iterator(self):
        return TakeIterator(self, self.domain.create_iterator())


class MapIterator(TransformationIterator):

    def __init__(self, domain, parent):
        super(MapIterator, self).__init__(domain, parent)
        self.fn = domain.fn

    def next(self):
        return self.fn(next(self.parent))

    def next_step(self):
        v = self.parent.next_step()
        if v is NoValue:
            return v
        else:
            return self.fn(v)


class MapTransformation(Transformation):

    iterator_class = MapIterator

    def __init__(self, domain, fn):
        super(MapTransformation, self).__init__(
            domain, domain.size, domain.exact_size)
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

    def next_step(self):
        v = self.parent.next_step()
        if self.fn(v):
            return v
        else:
            return NoValue


class FilterTransformation(Transformation):

    iterator_class = FilterIterator

    def __init__(self, domain, fn):
        super(FilterTransformation, self).__init__(
            domain, domain.size, False)
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
