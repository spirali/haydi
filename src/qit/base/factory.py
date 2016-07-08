import action
import transform
from qit.base import session


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
        """
        :rtype: IteratorFactory
        """
        cp = super(IteratorFactory, self).copy()
        cp.transformations = [tf.copy() for tf in self.transformations]
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

    def split(self, process_count):
        assert process_count > 0

        return self._create_transformation(transform.SplitTransformation,
                                           process_count)

    def timeout(self, timeout):
        return self._create_transformation(transform.TimeoutTransformation,
                                           timeout)

    def max_all(self, key_fn):
        return ActionFactory(action.MaxAll, self, key_fn)

    def collect(self):
        return ActionFactory(action.Collect, self)

    def first(self, fn=None, default=None):
        return ActionFactory(action.First, self, fn, default)

    def reduce(self, fn, init=0):
        return ActionFactory(action.Reduce, self, fn, init)

    def run(self):
        return self.collect().run()

    def _create_transformation(self, klass, *args, **kwargs):
        cp = self.copy()
        fac = TransformationFactory(klass, *args, **kwargs)
        cp.transformations.append(fac)
        return cp

    def __iter__(self):
        return iter(self.run())


class TransformationFactory(Factory):

    def __init__(self, klass, *args, **kwargs):
        super(TransformationFactory, self).__init__(klass, *args, **kwargs)

    def create(self, parent):
        return self.klass(parent, *self.args, **self.kwargs)


class ActionFactory(Factory):

    def __init__(self, klass, iterator_factory, *args, **kwargs):
        super(ActionFactory, self).__init__(klass, *args, **kwargs)
        self.iterator_factory = iterator_factory

    def copy(self):
        """
        :rtype: ActionFactory
        """
        return ActionFactory(self.klass, self.iterator_factory.copy(),
                             *self.args, **self.kwargs)

    def create(self):
        return self.klass(self.iterator_factory, *self.args, **self.kwargs)

    def run(self, parallel=False):
        ctx = session.session.get_context(parallel)
        return ctx.run(self)

    def __iter__(self):
        return iter(self.run())
