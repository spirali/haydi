
from .domain import StepSkip, skip1


class Transformation(object):

    def init_transformed_domain(self, domain, parent):
        domain.filtered = parent.filtered
        domain.step_jumps = parent.step_jumps
        domain.strict = False

    def size_of_transformed_domain(self, size):
        return size


class MapTransformation(Transformation):

    def __init__(self, fn):
        self.fn = fn

    def transform_iter(self, iterator):
        fn = self.fn
        return (fn(x) for x in iterator)

    def transform_skip_iter(self, iterator):
        fn = self.fn
        for v in iterator:
            if isinstance(v, StepSkip):
                yield v
            else:
                yield fn(v)


class FilterTransformation(Transformation):

    def __init__(self, fn, strict):
        self.fn = fn
        self.filtered = True
        self.strict = strict

    def init_transformed_domain(self, domain, parent):
        super(FilterTransformation, self).init_transformed_domain(
            domain, parent)
        domain.filtered = True
        domain.strict = self.strict and parent.strict

    def transform_iter(self, iterator):
        for v in iterator:
            if self.fn(v):
                yield v

    def transform_skip_iter(self, iterator):
        for v in iterator:
            if isinstance(v, StepSkip):
                yield v
            elif self.fn(v):
                yield v
            else:
                yield skip1
