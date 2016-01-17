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

    def progress(self, name, notify_count):
        assert notify_count > 0

        return TransformationFactory(self, ProgressTransformation, name, notify_count)

    def split(self, process_count):
        assert process_count > 0

        return TransformationFactory(self, SplitTransformation, process_count)

    def join(self):
        return TransformationFactory(self, JoinTransformation)

    def collect(self):
        return CollectAction(self.create())


class TransformationFactory(IteratorFactory):
    def __init__(self, parent, transformation, *args, **kwargs):
        super(TransformationFactory, self).__init__(transformation, *args, **kwargs)
        self.parent = parent

    def create(self):
        return self.iterator_class(self.parent.create(), *self.args, **self.kwargs)


class Iterator(object):
    ID_COUNTER = 0

    def __init__(self):
        self.id = Iterator.ID_COUNTER
        Iterator.ID_COUNTER += 1

        self.context = None
        self.size = None

    def __iter__(self):
        return self

    def create(self):
        return self

    def first(self, default=None):
        try:
            return next(self)
        except StopIteration:
            return default

    def reduce(self, fn):
        return functools.reduce(fn, self)

    def reset(self):
        raise NotImplementedError()

    def get_parents(self):
        return []

    def skip(self, start_index, count):
        raise NotImplementedError()

    def set_context(self, context):
        self.context = context

        for parent in self.get_parents():
            parent.set_context(context)

    def to_list(self):
        return list(self)


class GeneratingIterator(Iterator):

    def __init__(self, generator_fn):
        super(GeneratingIterator, self).__init__()
        self.generator_fn = generator_fn

    def next(self):
        return self.generator_fn()

    def reset(self):
        pass


class EmptyIterator(Iterator):

    def __init__(self):
        super(EmptyIterator, self).__init__()

    def next(self):
        raise StopIteration()

    def reset(self):
        pass


from transform import TakeTransformation, ProgressTransformation, SplitTransformation, JoinTransformation
from transform import MapTransformation
from transform import FilterTransformation
