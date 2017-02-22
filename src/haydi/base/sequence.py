
from .domain import Domain
from .product import Product
from .join import Join
from .canonicals import canonical_builder


class Sequence(Domain):

    def __init__(self, domain, min_length, max_length=None, name=None):
        if max_length is None:
            max_length = min_length

        helper = Join([Product((domain,) * i)
                       for i in range(min_length, max_length + 1)])

        super(Sequence, self).__init__(helper.size,
                                       domain.exact_size,
                                       helper.steps,
                                       name)
        self.min_length = min_length
        self.max_length = max_length
        self.domain = domain
        self.helper = helper

    def canonicals(self):
        def make_fn(item, candidate):
            item += (candidate,)
            if len(item) == max_length:
                return item, None, True, None
            return item, domain, item >= min_length, None
        domain = self.domain
        max_length = self.max_length
        min_length = self.min_length
        if min_length == 0:
            yield ()
        for item in canonical_builder(domain, (), make_fn, None):
            yield item

    def create_iter(self, step=0):
        return self.helper.create_iter(step)

    def generate_one(self):
        return self.helper.generate_one()
