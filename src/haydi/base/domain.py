import utils


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
        if self._name:
            return self._name
        else:
            return self.__class__.__name__

    @property
    def size(self):
        s = self._size
        if s == -1:
            s = self._compute_size()
            self._size = s
        return s

    def set_name(self, name):
        self._name = name

    def _compute_size(self):
        return None

    def __mul__(self, other):
        """Creates a cartesian product of domains.

        It is equivalent to
        ``Product((self, other))``, see :class:`haydi.Product`
        """
        return Product((self, other))

    def __add__(self, other):
        """Join two domains

        It is equivalent to
        ``Join((self, other))``, see :class:`haydi.Join`
        """
        return Join((self, other))

    def iterate_steps(self, start, end):
        i = start
        it = self.create_step_iter(start)
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

    def max(self, key_fn=None, size=None):
        """
        Action: Get all maximal elements from domain
        """
        return self.iterate().max(key_fn, size)

    def groups(self, key_fn, max_items_per_group=None):
        return self.iterate().groups(key_fn, max_items_per_group)

    def groups_counts(self, key_fn, max_items_per_group):
        return self.iterate().groups_counts(key_fn, max_items_per_group)

    def collect(self):
        """
        The method is shortcut for ``.iterate().collect()``

        Example:
            >>> hd.Range(4).collect().run()
            [0, 1, 2, 3]
        """
        return self.iterate().collect()

    def reduce(self, reduce_fn, init_value=0, associative=True):
        return self.iterate().reduce(reduce_fn, init_value, associative)

    # Prefixes

    def take(self, count):
        return self.iterate().take(count)

    def first(self, default=None):
        return self.make_pipeline("iterate").first(default)

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

    def create_iter(self, step=0):
        """Creates an interator over all elements of domain"""
        raise NotImplementedError()

    def create_skip_iter(self, step=0):
        raise NotImplementedError()

    def create_step_iter(self, step):
        if self.filtered:
            return self.create_skip_iter(step)
        else:
            return self.create_iter(step)

    def __iter__(self):
        return self.create_iter()

    def make_pipeline(self, method):
        return Pipeline(self, method)

    def generate_one(self):
        """Generate a random element from the domain"""
        raise Exception("Domain {} do not support generation"
                        .format(type(self).__name__))

    def iterate(self):
        return self.make_pipeline("iterate")

    def generate(self, count=None):
        pipeline = self.make_pipeline("generate")
        if count is None:
            return pipeline
        else:
            return pipeline.take(count)

    def cnfs(self):
        return self.make_pipeline("cnfs")

    def to_values(self, max_size=None):
        if max_size is None:
            max_size = self.size

        if self.size <= max_size:
            return Values(tuple(iter(self)))
        else:
            return self._remap_domains(lambda d: d.to_values(max_size))

    def to_cnf_values(self, max_size=None):
        if max_size is None:
            max_size = self.size

        if self.size <= max_size:
            return CnfValues(tuple(self.cnfs()))
        else:
            return self._remap_domains(lambda d: d.to_cnfs_values(max_size))

    def _remap_domains(self, transformation):
        """
        Should return a instance of the current domain with subdomains
        transformed with the given transformation.
        :param transformation: callable
        :return: haydi.Domain
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

    def create_iter(self, step=0):
        return self.transformation.transform_iter(
            self.parent.create_iter(step))

    def create_skip_iter(self, step=0):
        return self.transformation.transform_skip_iter(
            self.parent.create_step_iter(step))

    def make_pipeline(self, method):
        pipeline = self.parent.make_pipeline(method)
        return pipeline.add_transformation(self.transformation)

    """ For debugging purpose now disabled
    def generate_one(self):
        return self.generate().first().run()
    """


skip1 = StepSkip(1)


from .product import Product  # noqa
from .join import Join  # noqa
from . import transform  # noqa
from .pipeline import Pipeline  # noqa
from .values import Values, CnfValues  # noqa
