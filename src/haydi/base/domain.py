import utils
from copy import copy


def cache_transform(transformation):
    cache = {}

    def fn(domain):
        cached = cache.get(domain)
        if cached is None:
            cached = transformation(domain)
            cache[domain] = cached
        return cached

    return fn


class Domain(object):
    """
    Base class for domains
    """

    filtered = False
    step_jumps = False
    strict = False

    def __init__(self, name=None):
        self._name = name
        self._size = -1

    @property
    def name(self):
        """ Name of domain. Serves only for debugging purpose. """
        if self._name:
            return self._name
        else:
            return self.__class__.__name__

    @property
    def size(self):
        """Number of elements in domain.

        If the size is ``None`` then number of elements cannot be determined.
        If the domain is non-filtered and the size is int then it is the exact
        number of elements. If the domain is filtered and the size is int then
        it is an upper bound for the number of elements.
        """
        s = self._size
        if s == -1:
            s = self._compute_size()
            self._size = s
        return s

    def set_name(self, name):
        """Creates a copy of domain with changed name.
        """
        domain = copy(self)
        domain._name = name
        return domain

    def _compute_size(self):
        """Computes the size of domain

        Each domain where size can be determined should overload this method.
        """
        return None

    def __mul__(self, other):
        """Creates a cartesian product of domains.

        It is equivalent to ``Product((self, other))``, see
        :class:`haydi.Product`

        """
        return Product((self, other))

    def __add__(self, other):
        """Join two domains

        It is equivalent to ``Join((self, other))``, see :class:`haydi.Join`
        """
        return Join((self, other))

    def iterate_steps(self, start, end):
        """Create iterator over a given range of steps

        It internally calls ``create_skip_iter()`` and ignores StepSkips.

        Args:
            start (int): Index of first step
            end (int): Index of the last step

        Examples:

            >>> list(hd.Range(10).iterate_steps(1, 7))
            [1, 2, 3, 4, 5, 6]
            >>> list(hd.Range(10).filter(lambda x: x % 3 == 0).iterate_steps(1, 7))
            [3, 6]
        """
        i = start
        it = self.create_skip_iter(start)
        while i < end:
            v = next(it)
            if isinstance(v, StepSkip):
                i += v.value
            else:
                yield v
                i += 1

    # Internal

    def _set_flags_from_domain(self, domain):
        self.filtered = domain.filtered
        self.step_jumps = domain.step_jumps
        self.strict = domain.strict

    def _set_flags_from_domains(self, domains):
        self.filtered = any(d.filtered for d in domains)
        self.step_jumps = all(d.step_jumps for d in domains)
        self.strict = all(d.strict for d in domains)

    # Actions

    def max(self, value_fn=None, size=None):
        """
        Shortcut for ``.iterate().max(...)``
        """
        return self.iterate().max(value_fn, size)

    def groups(self, key_fn, max_items_per_group=None):
        """
        Shortcut for ``.iterate().groups(...)``
        """
        return self.iterate().groups(key_fn, max_items_per_group)

    def groups_counts(self, key_fn, max_items_per_group):
        """
        Shortcut for ``.iterate().group_counts(...)``
        """
        return self.iterate().groups_counts(key_fn, max_items_per_group)

    def collect(self):
        """
        Shortcut for ``.iterate().collect()``

        Example:
            >>> hd.Range(4).collect().run()
            [0, 1, 2, 3]
        """
        return self.iterate().collect()

    def reduce(self, reduce_fn, init_value=0, associative=True):
        """
        Shortcut for ``.iterate().reduce(...)``
        """
        return self.iterate().reduce(reduce_fn, init_value, associative)

    def take(self, count):
        """
        Shortcut for ``.iterate().take(count)``
        """
        return self.iterate().take(count)

    def first(self, default=None):
        """
        Shortcut for ``.iterate().first(default)``
        """
        return self._make_pipeline("iterate").first(default)

    # Transformations

    def map(self, fn):
        """
        Transformation: Map a function `fn` over elements of domain

        Example:
            >>> list(hd.Range(4).map(lambda x: x + 10))
            [10, 11, 12, 13]
        """
        return TransformedDomain(self, transform.MapTransformation(fn))

    def filter(self, fn, strict=False):
        """
        Transformation: Filters elements from domain

        It calls function `fn` on each element, if the function
        returns ``False`` then the element is filtered out.

        Note, that the resulting domain has `filtered` set to ``True``,

        Example:
            >>> list(hd.Range(4).filter(lambda x: x % 2 == 1))
            [1, 3]
        """
        return TransformedDomain(
            self, transform.FilterTransformation(fn, strict))

    # Others
    def run(self, ctx=None, timeout=None):
        """A shortcut for ``self.collect().run(ctx, timeout)``"""
        return self.collect().run(ctx, timeout)

    # Shortcuts
    # def take(self, count):
    #     return transform.iterate().take(count)

    def _make_iter(self, step):
        """Creates an interator over elements of the domain

        Each domain implementation should override this method.
        """
        raise NotImplementedError()

    def _make_skip_iter(self, step):
        """Create a skip iterator over elements of the domain

        Each (potentially) filtered domain implementation should override this
        method.
        """
        raise NotImplementedError()

    def create_iter(self, step=0):
        return self._make_iter(step)

    def create_skip_iter(self, step=0):
        if self.filtered:
            return self._make_skip_iter(step)
        else:
            return self._make_iter(step)

    def __iter__(self):
        return self.create_iter()

    def _make_pipeline(self, method):
        return Pipeline(self, method)

    def generate_one(self):
        """Generate a random element from the domain"""
        raise Exception("Domain {} do not support generation"
                        .format(type(self).__name__))

    def iterate(self):
        """Create a pipeline that iterates over all elements in the domain

        The method returns instance of :class:`haydi.Pipeline` with "iterate"
        method.
        """
        return self._make_pipeline("iterate")

    def generate(self, count=None):
        """Create a pipeline that generates random element from the domain

        The method returns instance of :class:`haydi.Pipeline` with "generate"
        method.

        Args:
            count (int or None): The number of generated elements in the
                                 pipeline, if ``count`` is ``None`` then the
                                 pipeline generates an infinite number of
                                 elements.
        """

        pipeline = self._make_pipeline("generate")
        if count is None:
            return pipeline
        else:
            return pipeline.take(count)

    def cnfs(self):
        """Create a pipeline iterating over canonical elements in the domain

        The method returns instance of :class:`haydi.Pipeline` with "cnfs"
        method.

        This works only for *strict* domains. If called on a non-strict domain,
        then an exception is thrown.
        """
        return self._make_pipeline("cnfs")

    def to_values(self, max_size=None):
        """Materialize the domain (or its subdomains)

        This method serves as an optimization for caching elements of
        heavily-used small domains.

        If the argument ``max_size`` is ``None`` or ``self.size`` is at most
        ``max_size`` then the call is equivalent to ``hd.Values(tuple(self))``.
        Otherwise the method is applied on subdomains recursively.

        Example:

        >>> p = hd.Range(3) * hd.Range(5) * hd.Range(6)
        >>> q = p.to_values(5)

        ``q`` is the same as writing::

        >>> hd.Values((0, 1, 2)) * hd.Values((0, 1, 2, 3, 4)) * hd.Range(6)

        Args:
            max_size (int or None): The size limit for materialization

        """
        if max_size is None:
            max_size = self.size

        if self.size <= max_size:
            return Values(tuple(self.create_iter()))
        else:
            return self._remap_domains(cache_transform(lambda d: d.to_values(max_size)))

    def to_cnf_values(self, max_size=None):
        if max_size is None:
            max_size = self.size

        if self.size <= max_size:
            return CnfValues(tuple(self.cnfs()), _check=False)
        else:
            return self._remap_domains(cache_transform(lambda d: d.to_cnfs_values(max_size)))

    def _remap_domains(self, fn):
        """
        Returns an instance of the current domain with subdomains
        transformed with the given transformation.

        Domains with subdomains should override this method.

        Args:
            fn (callable): A function called on each subdomain
        Returns:
            An instance of :class:`haydi.Domain`
        """
        return self

    def __repr__(self):
        ITEMS_LIMIT = 5
        ITEM_CHAR_LIMIT = 24
        CHAR_LIMIT = 48

        size = self.size
        if size == 0:
            extra = " {}"
        elif not self.filtered and size is not None:
            it = self.create_iter()
            remaining = CHAR_LIMIT

            tokens = [" {"]
            last = size - 1

            for i in xrange(ITEMS_LIMIT):
                try:
                    item_repr = repr(it.next())
                except StopIteration:
                    tokens = ["size of domain is not consistent with iterator"]
                    break
                item_repr = utils.limit_string_length(
                    item_repr, min(remaining, ITEM_CHAR_LIMIT))
                remaining -= len(item_repr)
                tokens.append(item_repr)
                if i == last:
                    tokens.append("}")
                    break
                else:
                    tokens.append(", ")
                    remaining -= 2

                if remaining <= 6:
                    tokens.append("...}")
                    break
            else:
                tokens.append("...}")

            extra = "".join(tokens)
        else:
            if self.filtered:
                extra = " filtered"
            else:
                extra = ""
        return "<{} size={}{}>".format(self.name, self.size, extra)


class StepSkip(object):

    def __init__(self, value=1):
        self.value = value

    def __repr__(self):
        return "<StepSkip {}>".format(self.value)

    def __eq__(self, other):
        return isinstance(other, StepSkip) and other.value == self.value

    def __ne__(self, other):
        return not self.__eq__(other)


class TransformedDomain(Domain):

    def __init__(self, parent, transformation):
        name = type(transformation).__name__
        super(TransformedDomain, self).__init__(name)
        self.parent = parent
        self.transformation = transformation
        transformation.init_transformed_domain(self, parent)

    def _compute_size(self):
        return self.transformation.size_of_transformed_domain(self.parent.size)

    def _make_iter(self, step):
        return self.transformation.transform_iter(
            self.parent.create_iter(step))

    def _make_skip_iter(self, step):
        return self.transformation.transform_skip_iter(
            self.parent.create_skip_iter(step))

    def _make_pipeline(self, method):
        pipeline = self.parent._make_pipeline(method)
        return pipeline._add_transformation(self.transformation)

    def generate_one(self):
        pipeline = self.parent.generate()._add_transformation(
            self.transformation)
        return pipeline.first().run()


skip1 = StepSkip(1)


from .product import Product  # noqa
from .join import Join  # noqa
from . import transform  # noqa
from .pipeline import Pipeline  # noqa
from .values import Values, CnfValues  # noqa
