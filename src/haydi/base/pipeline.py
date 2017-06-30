
from copy import copy
from . import action
from .haydisession import session


class Pipeline(object):

    action = action.Collect()

    def __init__(self, domain, method):
        self.domain = domain
        self.method = method
        self.transformations = ()
        self.take_count = None

    def __iter__(self):
        return iter(self.run())

    def collect(self):
        pipeline = copy(self)
        pipeline.action = action.Collect()
        return pipeline

    def max(self, key_fn=None, size=None):
        pipeline = copy(self)
        pipeline.action = action.Max(key_fn, size)
        return pipeline

    def groups(self, key_fn, max_items_per_group=None):
        """
        Action: It groups elements by keys

        Args:
            key_fn(callable): Function applied on each element to get the key
            max_items_per_group(int): The limit of elements for each group.
               Elements over the limit are thrown away.
        """
        pipeline = copy(self)
        pipeline.action = action.Groups(key_fn, max_items_per_group)
        return pipeline

    def groups_counts(self, key_fn, max_items_per_group):
        """
        Action: The same idea as method :meth:`groups` but remembers also total
        count of all elements (even forgotten)
        """
        pipeline = copy(self)
        pipeline.action = action.GroupsAndCounts(key_fn, max_items_per_group)
        return pipeline

    def reduce(self, reduce_fn, init_value=0, associative=True):
        pipeline = copy(self)
        pipeline.action = action.Reduce(reduce_fn, init_value, associative)
        return pipeline

    def take(self, count):
        pipeline = copy(self)
        pipeline.take_count = count
        return pipeline

    def first(self, filter_fn=None, default=None):
        if filter_fn:
            pipeline = self.filter(filter_fn)
        else:
            pipeline = copy(self)
        pipeline.take_count = 1
        pipeline.action = action.Collect()
        pipeline.action.postprocess = lambda x: x[0] if x else default
        return pipeline

    def add_transformation(self, transformation):
        pipeline = copy(self)
        pipeline.transformations += (transformation,)
        return pipeline

    def run(self, parallel=False, timeout=None, otf_trace=False):
        """
        :type parallel: bool
        :type timeout: int
        :type otf_trace: bool
        :return: Returns the computed result.
        """
        ctx = session.get_context(parallel)
        result = ctx.run(self,
                         timeout,
                         otf_trace)
        return self.action.postprocess(result)

    def filter(self, fn, strict=False):
        return self.add_transformation(
            transform.FilterTransformation(fn, strict))

    def map(self, fn):
        return self.add_transformation(
            transform.MapTransformation(fn))

    def __repr__(self):
        s = "<Pipeline for {}: method={}".format(self.domain.name,
                                                 self.method)
        if self.transformations:
            s += " ts=[{}]".format(
                ", ".join(t.__class__.__name__ for t in self.transformations))

        if self.action:
            s += " action={}".format(self.action.__class__.__name__)

        s += ">"
        return s

from . import transform  # noqa
