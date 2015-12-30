import functools

class Iterator(object):

    def __iter__(self):
        return self

    def take(self, count):
        return TakeTransformation(self, count)

    def map(self, fn):
        return MapTransformation(self, fn)

    def filter(self, fn):
        return FilterTransformation(self, fn)

    def first(self, default=None):
        try:
            return next(self)
        except StopIteration:
            return default

    def reduce(self, fn):
        return functools.reduce(fn, self)

    def reset(self):
        raise NotImplementedError()


class GeneratingIterator(Iterator):

    def __init__(self, generator_fn):
        self.generator_fn = generator_fn

    def next(self):
        return self.generator_fn()

    def reset(self):
        pass


class EmptyIterator(Iterator):

    def next(self):
        raise StopIteration()

    def reset(self):
        pass


from transform import TakeTransformation
from transform import MapTransformation
from transform import FilterTransformation
