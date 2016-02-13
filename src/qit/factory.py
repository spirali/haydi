import action
import transform


class Factory(object):
    def __init__(self, klass, *args, **kwargs):
        self.klass = klass
        self.args = args
        self.kwargs = kwargs

    def copy(self):
        return self.__class__(self.klass, *self.args, **self.kwargs)

    def create(self):
        return self.klass(*self.args, **self.kwargs)

    def __repr__(self):
        return "Factory of {}".format(self.klass)


class IteratorFactory(Factory):
    def __init__(self, klass, *args, **kwargs):
        super(IteratorFactory, self).__init__(klass, *args, **kwargs)
        self.transformations = []

    def copy(self):
        cp = super(IteratorFactory, self).copy()
        for trans in self.transformations:
            cp.transformations.append(trans.copy())

        return cp

    def create(self):
        iter = self.klass(*self.args, **self.kwargs)
        parent = iter
        for tr in self.transformations:
            transformation = tr.create(parent)
            parent = transformation

        return parent

    def take(self, count):
        return self._create_transformation(transform.TakeTransformation, count)

    def map(self, fn):
        return self._create_transformation(transform.MapTransformation, fn)

    def filter(self, fn):
        return self._create_transformation(transform.FilterTransformation, fn)

    def progress(self, name, notify_count):
        assert notify_count > 0

        return self._create_transformation(transform.ProgressTransformation,
                                           name,
                                           notify_count)

    def split(self, process_count):
        assert process_count > 0

        return self._create_transformation(transform.SplitTransformation,
                                           process_count)

    def timeout(self, timeout):
        return self._create_transformation(transform.TimeoutTransformation,
                                           timeout)

    def best(self, *args, **kwargs):
        return ActionFactory(action.Best, self, *args, **kwargs)

    def collect(self, *args, **kwargs):
        return ActionFactory(action.Collect, self, *args, **kwargs)

    def first(self, *args, **kwargs):
        return ActionFactory(action.First, self, *args, **kwargs)

    def reduce(self, *args, **kwargs):
        return ActionFactory(action.Reduce, self, *args, **kwargs)

    def _create_transformation(self, klass, *args, **kwargs):
        cp = self.copy()
        fac = TransformationFactory(klass, *args, **kwargs)
        cp.transformations.append(fac)
        return cp


class TransformationFactory(Factory):
    def __init__(self, klass, *args, **kwargs):
        super(TransformationFactory, self).__init__(klass, *args, **kwargs)

    def create(self, parent):
        return self.klass(parent, *self.args, **self.kwargs)


class ActionFactory(Factory):
    def __init__(self, klass, iterator_factory, *args, **kwargs):
        super(ActionFactory, self).__init__(klass, *args, **kwargs)
        self.iterator_factory = iterator_factory

    def create(self):
        return self.klass(self.iterator_factory, *self.args, **self.kwargs)

    def run(self, *args, **kwargs):
        return self.create().run(*args, **kwargs)
