from copy import copy
from domain import Domain, DomainIterator


class TransformationIterator(DomainIterator):

    def __init__(self, domain, parent):
        super(TransformationIterator, self).__init__(domain)
        self.parent = parent

    def reset(self):
        self.parent.reset()

    def set(self, index):
        self.parent.set(index)

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
        self.count = domain.count

    def next(self):
        if self.count <= 0:
            raise StopIteration()
        self.count -= 1
        return next(self.parent)

    def set(self, index):
        assert index < self.count
        self.parent.set(index)

    def __repr__(self):
        return "Take {} items".format(self.count)


class TakeTransformation(Transformation):

    iterator_class = TakeIterator

    def __init__(self, parent, count):
        if parent.size is not None:
            size = max(parent.size, count)
        else:
            size = count
        self.count = count
        super(TakeTransformation, self).__init__(parent,
                                                 size,
                                                 parent.exact_size)

    def create_iterator(self):
        return TakeIterator(self, self.domain.create_iterator())


class MapIterator(TransformationIterator):

    def __init__(self, domain, parent):
        super(MapIterator, self).__init__(domain, parent)
        self.fn = domain.fn

    def next(self):
        return self.fn(next(self.parent))


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
