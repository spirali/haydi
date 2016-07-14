
from iterator import GeneratingIterator, Iterator
import action


class Domain(object):

    def __init__(self, size=None, exact_size=False, name=None):
        self.size = size
        self.exact_size = exact_size
        self.name = name

    def __mul__(self, other):
        return Product((self, other))

    def __add__(self, other):
        return Join((self, other))

    # Actions

    def max_all(self, key_fn):
        return action.MaxAll(self, key_fn)

    def collect(self, postprocess_fn=None):
        return action.Collect(self, postprocess_fn)

    def first(self, fn=None, default=None):
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
        return action.Reduce(self, reduce_fn, init_value, associative)

    # Transformations

    def take(self, count):
        return transform.TakeTransformation(self, count)

    def map(self, fn):
        return transform.MapTransformation(self, fn)

    def filter(self, fn):
        return transform.FilterTransformation(self, fn)

    def timeout(self, timeout):
        return transform.TimeoutTransformation(self, timeout)

    # Others

    def run(self, parallel=False):
        return self.collect().run(parallel)

    def __iter__(self):
        return self.create_iterator()

    def generate_one(self):
        raise NotImplementedError()

    def generate(self, count=None):
        domain = GeneratingDomain(self.generate_one)
        if count is None:
            return domain
        else:
            return domain.take(count)

    def __repr__(self):
        ITEMS_LIMIT = 4
        ITEMS_CHAR_LIMIT = 50
        if self.name:
            name = self.name
        else:
            name = self.__class__.__name__

        if self.exact_size and self.size is not None:
            items = ", ".join(map(str, self.iterate().take(ITEMS_LIMIT)))
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


class GeneratingDomain(Domain):

    def __init__(self, generate_fn, name=None):
        Domain.__init__(self, None, True, name)
        self.generate_fn = generate_fn

    def create_iterator(self):
        return GeneratingIterator(self.generate_fn)


class DomainIterator(Iterator):

    def __init__(self, domain):
        super(DomainIterator, self).__init__()
        self.domain = domain
        self.size = self.domain.size
        self.exact_size = self.domain.exact_size

from product import Product  # noqa
from join import Join  # noqa
import transform  # noqa
