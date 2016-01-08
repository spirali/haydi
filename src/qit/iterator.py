import functools

from action import CollectAction


class IteratorFactory(object):
    def __init__(self, iterator_class, *args, **kwargs):
        self.iterator_class = iterator_class
        self.args = args
        self.kwargs = kwargs

    def create(self):
        return self.iterator_class(*self.args, **self.kwargs)

    def take(self, count):
        return TransformationFactory(self, TakeTransformation, count)

    def map(self, fn):
        return TransformationFactory(self, MapTransformation, fn)

    def filter(self, fn):
        return TransformationFactory(self, FilterTransformation, fn)

    def collect(self, session):
        return CollectAction(self.create(), session)


class TransformationFactory(IteratorFactory):
    def __init__(self, parent, transformation, *args, **kwargs):
        super(TransformationFactory, self).__init__(transformation, *args, **kwargs)
        self.parent = parent

    def create(self):
        return self.iterator_class(self.parent.create(), *self.args, **self.kwargs)


class Iterator(object):

    def __iter__(self):
        return self

    def create(self):
        return self

    def take(self, count):
        return IteratorFactory(TakeTransformation, self, count)

    def map(self, fn):
        return IteratorFactory(MapTransformation, self, fn)

    def filter(self, fn):
        return IteratorFactory(FilterTransformation, self, fn)

    def first(self, default=None):
        try:
            return next(self)
        except StopIteration:
            return default

    def reduce(self, fn):
        return functools.reduce(fn, self)

    def reset(self):
        raise NotImplementedError()

    def collect(self, session):
        return IteratorFactory(CollectAction, self, session)

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
