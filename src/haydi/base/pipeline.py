
from copy import copy
from . import action
from .haydisession import session


class Pipeline(object):

    def __init__(self, domain, method):
        self.domain = domain
        self.method = method
        self.transformations = ()
        self.action = None
        self.take_count = None

    def __iter__(self):
        return iter(self.run())

    def collect(self):
        pipeline = copy(self)
        pipeline.action = action.Collect()
        return pipeline

    def max_all(self, key_fn):
        pipeline = copy(self)
        pipeline.action = action.MaxAll(key_fn)
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

    def run(self, parallel=False, timeout=None,
            dump_jobs=False, otf_trace=False):
        """
        :type parallel: bool
        :type timeout: int
        :type dump_jobs: bool
        :type otf_trace: bool
        :return: Returns the computed result.
        """
        a = self.action
        if a is None:
            a = action.Collect()
        ctx = session.get_context(parallel)
        result = ctx.run(self.domain,
                         self.method,
                         self.transformations,
                         self.take_count,
                         a.worker_reduce_fn,
                         a.worker_reduce_init,
                         a.global_reduce_fn,
                         a.global_reduce_init,
                         timeout,
                         dump_jobs,
                         otf_trace)
        return a.postprocess(result)

    def filter(self, fn, strict=False):
        return self.add_transformation(
            transform.FilterTransformation(fn, strict))

    def map(self, fn):
        return self.add_transformation(
            transform.MapTransformation(fn))


from . import transform  # noqa
