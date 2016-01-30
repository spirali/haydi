import action
import transform


class IteratorFactory(object):
    def __init__(self, iterator_class, *args, **kwargs):
        self.iterator_class = iterator_class
        self.args = args
        self.kwargs = kwargs
        self.output = None
        self.input = None

    def copy(self):
        return IteratorFactory(self.iterator_class, *self.args, **self.kwargs)

    def create(self):
        return self.iterator_class(*self.args, **self.kwargs)

    def take(self, count):
        return self._create_transformation(transform.TakeTransformation, count)

    def map(self, fn):
        return self._create_transformation(transform.MapTransformation, fn)

    def filter(self, fn):
        return self._create_transformation(transform.FilterTransformation, fn)

    def custom(self, transformation_class, *args, **kwargs):
        return self._create_transformation(transformation_class, *args, **kwargs)

    def progress(self, name, notify_count):
        assert notify_count > 0

        return self._create_transformation(transform.ProgressTransformation, name, notify_count)

    def split(self, process_count):
        assert process_count > 0

        return self._create_transformation(transform.SplitTransformation, process_count)

    def collect(self):
        return action.CollectAction(self)

    def prepend(self, factory):
        assert isinstance(factory, IteratorFactory)

        self.input.output = factory
        factory.input = self.input
        self.input = factory
        factory.output = self

    def append(self, factory):
        assert isinstance(factory, IteratorFactory)

        if self.output:
            self.output.input = factory
        factory.output = self.output
        self.output = factory
        factory.input = self

    def skip(self):
        self.input.output = self.output

        if self.output:
            self.output.input = self.input

    def replace(self, replacement):
        assert isinstance(replacement, IteratorFactory)

        self.input.output = replacement
        replacement.input = self.input
        if self.output:
            self.output.input = replacement
        replacement.output = self.output

    def _create_transformation(self, klass, *args, **kwargs):
        fac = TransformationFactory(self, klass, *args, **kwargs)
        self.output = fac
        return fac

    def __repr__(self):
        return "Factory of {}".format(self.iterator_class)

class TransformationFactory(IteratorFactory):
    def __init__(self, parent, iterator_class, *args, **kwargs):
        super(TransformationFactory, self).__init__(iterator_class, *args, **kwargs)
        self.input = parent

    def copy(self):
        assert self.input

        parent = self.input.copy()
        parent.output = TransformationFactory(parent, self.iterator_class, *self.args, **self.kwargs)
        return parent.output

    def create(self):
        assert self.input

        return self.iterator_class(self.input.create(), *self.args, **self.kwargs)
