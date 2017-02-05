
from . import action


class Domain(object):
    """
    Base class for all domains

    If you do not want to create a domain by yourself,
    you do not have to care about parameters of the constructor.

    Args:
        size(Optional[int]): The number of elements in domain
            (for exact meaning) see the next argument
        exact_size(bool): The argument has the following meaning:

            - If `size` is ``int``
                - If `exact_size` is ``True`` then `size` is the number
                  of elements in the domain.
                - If `exact_size` is ``False`` then `size` is the upperbound
                  of elements in the domain.
            - If `size` is ``None``
                - If `exact_size` is ``True`` then domain is infinite.
                - If `exact_size` is ``False`` then the number of elements
                  is not a priori known.
        steps(int): Number of internal steps of domain
        name(Optional[str]): Name of domain (for debug messages)
    """

    def __init__(self, size=None, exact_size=False, steps=None, name=None):
        self.size = size
        self.exact_size = exact_size
        self.steps = steps
        self.name = name

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

    # Actions

    def max_all(self, key_fn):
        """
        Action: Get all maximal elements from domain
        """
        return action.MaxAll(self, key_fn)

    def groups(self, key_fn, max_items_per_group=None):
        """
        Action: It groups elements by keys

        Args:
            key_fn(callable): Function applied on each element to get the key
            max_items_per_group(int): The limit of elements for each group.
               Elements over the limit are thrown away.
        """
        return action.Groups(self, key_fn, max_items_per_group)

    def groups_counts(self, key_fn, max_items_per_group):
        """
        Action: The same idea as method :meth:`groups` but remembers also total
        count of all elements (even forgotten)
        """
        return action.GroupsAndCounts(self, key_fn, max_items_per_group)

    def collect(self, postprocess_fn=None):
        """
        Action: Materialize all elements in domain.

        Example:
            >>> hd.Range(4).collect().run()
            [0, 1, 2, 3]
        """
        return action.Collect(self, postprocess_fn)

    def first(self, fn=None, default=None):
        """
        Action: Take the first element of the collection

        Takes first element of collection. If `fn` is not ``None`` then
        collection is first filtered by `fn`.

        If domain is empty then `default` is returned.
        """
        def helper(value):
            if value:
                return value[0]
            else:
                return default
        f = self
        if fn is not None:
            f = f.filter(fn)
        return f.take(1).collect(postprocess_fn=helper)

    def reduce(self, reduce_fn, init_value=0, associative=True):
        """
        Action: Reduce domain

        Example:
            >>> hd.Range(4).reduce(lambda x, y: x + y, init_value=10).run()
            16
        """
        return action.Reduce(self, reduce_fn, init_value, associative)

    # Transformations

    def take(self, count):
        """
        Transformation: Take first `count` elements from domain

        Example:
            >>> list(hd.Range(10).take(3))
            [0, 1, 2]
        """
        return transform.TakeTransformation(self, count)

    def map(self, fn):
        """
        Transformation: Map a function `fn` over elements of domain

        Example:
            >>> list(hd.Range(4).map(lambda x: x + 10))
            [10, 11, 12, 13]
        """
        return transform.MapTransformation(self, fn)

    def filter(self, fn):
        """
        Transformation: Filters elements from domain

        It calls function `fn` on each element, if the function
        returns ``False`` then the element is filtered out.

        Note, that the resulting domain has `exact_size` set to ``False``,
        since we do not know in advance how many elements is filtered out.

        Example:
            >>> list(hd.Range(4).filter(lambda x: x % 2 == 1))
            [1, 3]
        """
        return transform.FilterTransformation(self, fn)

    # Others
    def run(self, parallel=False, timeout=None):
        """A shortuct for ``self.collect.run(parallel)``"""
        return self.collect().run(parallel, timeout)

    def create_iter(self, step=0):
        """Creates an interator over all elements of domain"""
        raise NotImplementedError()

    def create_skip_iter(self, step=0):
        raise NotImplementedError()

    def create_step_iter(self, step):
        if self.exact_size:
            return self.create_iter(step)
        else:
            return self.create_skip_iter(step)

    def __iter__(self):
        return self.create_iter()

    def generate_one(self):
        """Generate a random element from the domain"""
        raise NotImplementedError()

    def generate(self, count=None):
        """
        Create a domain from random elements of `self`

        If `count` is ``None`` then the resulting domain is infinite, otherwise
        `count` serves as the number of elements for domain.

        Example:
           >>> list(hd.Range(4).generate(5)) # doctest: +SKIP
           [1, 3, 3, 2, 0]
        """
        domain = GeneratingDomain(self.generate_one)
        if count is None:
            return domain
        else:
            # The following may be considered as hack,
            # but it is quite ok for now:)
            domain.steps = count
            return domain.take(count)

    def __repr__(self):
        ITEMS_LIMIT = 4
        ITEMS_CHAR_LIMIT = 50
        if self.name:
            name = self.name
        else:
            name = self.__class__.__name__

        if self.exact_size and self.size is not None:
            items = ", ".join(map(str, self.take(ITEMS_LIMIT)))
            if len(items) > ITEMS_CHAR_LIMIT:
                items = items[:ITEMS_CHAR_LIMIT - 5]
                items += ", ..."
            elif self.size > ITEMS_LIMIT:
                items += ", ..."
            extra = "{{{0}}}".format(items)
        else:
            if not self.exact_size:
                extra = "not exact_size"
            else:
                extra = ""
        return "<{} size={} {}>".format(name, self.size, extra)


class StepSkip(object):

    def __init__(self, value=1):
        self.value = value

    def __repr__(self):
        return "<StepSkip {}>".format(self.value)

    def __eq__(self, other):
        return isinstance(other, StepSkip) and other.value == self.value

    def __ne__(self, other):
        return not self.__eq__(other)


skip1 = StepSkip(1)


class GeneratingDomain(Domain):

    def __init__(self, generate_fn, name=None):
        Domain.__init__(self, None, True, None, name=name)
        self.generate_fn = generate_fn

    def create_iter(self, step=0):
        while True:
            yield self.generate_fn()

    def create_step_iter(self, step):
        return self.create_iter()


from .product import Product  # noqa
from .join import Join  # noqa
from . import transform  # noqa
