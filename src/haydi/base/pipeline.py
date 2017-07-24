
from copy import copy

from .runtime.serialcontext import SerialContext
from . import action


class Pipeline(object):
    """Computational pipeline over a domain.

    Pipeline machinery is described in :doc:`Pipeline`.

    The user should never instantiate this class manualy. It should
    be created by one of methods on a domain.

    Examples:

    >>> p = hd.Range(3) * hd.Range(5)
    >>> p.iterate()  # Pipeline that iterates over all elements
    <Pipeline for Product: method=iterate action=Collect>

    >>> p.generate(10)  # Pipelines on 10 random elements from the domain
    <Pipeline for Product: method=generate action=Collect>

    Create a pipeline, apply a transformation, action, and then run the whole
    thing::

    >>> p.map(lambda x: x[0] + x[1]).max().run()
    [6]

    """

    action = action.Collect()

    def __init__(self, domain, method):
        if method == "cnfs" and not domain.strict:
            raise Exception(
                "Canonical forms cannot be iterated only on non-strict domains"
                "; domain '{}' is not strict".format(domain))
        self.domain = domain
        self.method = method
        self.transformations = ()
        self.take_count = None

    def __iter__(self):
        """Run the domain and iterate over the result.

        Warning: Not all actions in the pipeline returns iterable result
        (e.g. first() on Range).
        """
        return iter(self.run())

    def collect(self):
        """
        Action: Collect all elements into list.

        This is the default action.
        """
        pipeline = copy(self)
        pipeline.action = action.Collect()
        return pipeline

    def max(self, value_fn=None, size=None):
        """Action: Find maximal elements in the pipeline.

        The number of the returned elements can be limited. What elements are
        thrown away is not specified.

        Args:
            value_fn (callable or None): The function applied on each element
                to get the value of elements. If None, then identity is used.
            size (int or None): The limit of maximal elements.
                If size if ``None`` then no limit is used and all maximal
                elements are returned.

        """
        pipeline = copy(self)
        pipeline.action = action.Max(value_fn, size)
        return pipeline

    def groups(self, key_fn, max_items_per_group=None):
        """
        Action: Group elements by keys

        The size of the returned group can be limited. What elements are
        thrown away is not specified.

        Args:
            key_fn(callable): Function applied on each element to get the key
            max_items_per_group(int): The limit of elements for each group.
               Elements over the limit are thrown away.

        Examples:

            >>> p = hd.Range(3) * hd.Range(5)
            >>> p.iterate().groups(lambda x: x[0] + x[1]).run()
            {0: [(0, 0)],
            1: [(0, 1), (1, 0)],
            2: [(0, 2), (1, 1), (2, 0)],
            3: [(0, 3), (1, 2), (2, 1)],
            4: [(0, 4), (1, 3), (2, 2)],
            5: [(1, 4), (2, 3)],
            6: [(2, 4)]}


            >>> p.iterate().groups(lambda x: x[0] + x[1], 1).run()
            {0: [(0, 0)], 1: [(0, 1)], 2: [(0, 2)], 3: [(0, 3)],
             4: [(0, 4)], 5: [(1, 4)], 6: [(2, 4)]}
        """
        pipeline = copy(self)
        pipeline.action = action.Groups(key_fn, max_items_per_group)
        return pipeline

    def groups_counts(self, key_fn, max_items_per_group):
        """
        Action: Group elements by keys and return elements and counts

        The same idea as method :meth:`groups` but returns also total
        count of all elements in groups (includes the elements over the limit)
        """
        pipeline = copy(self)
        pipeline.action = action.GroupsAndCounts(key_fn, max_items_per_group)
        return pipeline

    def reduce(self, reduce_fn, init_value=0, associative=True):
        """
        Action: Apply a function to reduce stream to a single value (left fold)

        Examples:

        >>> hd.Range(10).iterate().reduce(lambda x, y: x + y).run()
        45
        """
        pipeline = copy(self)
        pipeline.action = action.Reduce(reduce_fn, init_value, associative)
        return pipeline

    def take(self, count):
        """
        Transformation: Take a first n elements from the pipeline.
        """
        pipeline = copy(self)
        pipeline.take_count = count
        return pipeline

    def first(self, default=None):
        """
        Action: Take the first element from the pipeline

        If the domain is empty, then ``default`` argument is returned.
        """

        pipeline = copy(self)
        pipeline.take_count = 1
        pipeline.action = action.Collect()
        pipeline.action.postprocess = lambda x: x[0] if x else default
        return pipeline

    def _add_transformation(self, transformation):
        pipeline = copy(self)
        pipeline.transformations += (transformation,)
        return pipeline

    def run(self, ctx=None, timeout=None, otf_trace=False):
        """
        Run the pipeline

        Args:
            ctx(haydi.Context or None): Context of execution.
                                        If ``None`` then the serial context is used.
            timeout(float or timedelta): Time limit for the computation.
            otf_trace(bool): Write tracing log in OTF format.
        """
        if not ctx:
            ctx = SerialContext()

        result = ctx.run(self, timeout, otf_trace)
        return self.action.postprocess(result)

    def filter(self, fn, strict=False):
        """Transformation: Filter elements from the pipeline"""
        return self._add_transformation(
            transform.FilterTransformation(fn, strict))

    def map(self, fn):
        """Transformation: Map function on each elements in the pipeline"""
        return self._add_transformation(
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
