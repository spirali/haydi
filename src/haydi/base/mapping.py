from .domain import Domain
from .domain import Product
from .basictypes import Map, compare
from .canonicals import canonical_builder, get_bounds


class Mapping(Domain):

    def __init__(self, key_domain, value_domain, name=None):
        assert key_domain.exact_size
        product = Product((value_domain,) * key_domain.size)
        super(Mapping, self).__init__(product.size,
                                      product.exact_size,
                                      product.steps,
                                      name)
        self.key_domain = key_domain
        self.value_domain = value_domain
        self.product = product

    def create_iter(self, step=0):
        keys = tuple(self.key_domain)
        for values in self.product.create_iter(step):
            yield Map(zip(keys, values))

    def generate_one(self):
        return Map(zip(self.key_domain, self.product.generate_one()))

    def canonicals(self):
        keys = sorted(self.key_domain, cmp=compare)
        value_domain = self.value_domain

        def make_fn(map_item, candidate):
            new_items = map_item.items[:]
            new_items.append((keys[len(new_items)], candidate))
            m = Map(new_items)
            if len(new_items) == len(keys):
                return m, None, True, None
            return m, value_domain, False, get_bounds(keys[len(new_items)])
        return canonical_builder(
            value_domain, Map(()), make_fn, get_bounds(keys[0]))
